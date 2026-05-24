"""Seed Phase 2 catalog data for Grace Young.

Creates:
- 5 categories
- 25 category-specific brands, 5 per category
- 250 products, 10 per brand
- 250 generated product package images uploaded to MinIO
- optional Meilisearch product index

Usage:
  cd backend
  cp ../.env.example .env
  alembic upgrade head
  python scripts/seed_phase2_catalog.py

Options:
  python scripts/seed_phase2_catalog.py --reset
"""
from __future__ import annotations
import argparse
import hashlib
import os
import random
import re
import sys
import tempfile
from io import BytesIO
from decimal import Decimal
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont, ImageOps
from sqlalchemy import delete, select

# Allow running from backend/scripts without installing the package.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.session import SessionLocal
from app.models.catalog import Brand, Category, Product, ProductImage, product_categories
from app.models.membership import MembershipTier
from app.models.user import User
from app.core.security import get_password_hash
from app.services.storage import upload_file, ensure_bucket
from app.core.config import get_settings

try:
    import meilisearch
except Exception:  # pragma: no cover
    meilisearch = None

try:
    import httpx
except Exception:  # pragma: no cover
    httpx = None

settings = get_settings()
random.seed(42)

CATEGORIES = [
    {
        "slug": "skincare",
        "name": "Skincare",
        "concerns": ["Sensitive Barrier", "Glass Glow", "Dark Spots"],
        "ingredients": ["Cica", "Rice", "Heartleaf", "Niacinamide", "Green Tea"],
        "types": ["Serum", "Toner", "Cream", "Ampoule", "Cleanser"],
    },
    {
        "slug": "suncare",
        "name": "Suncare",
        "concerns": ["Daily SPF", "Melasma", "After Sun"],
        "ingredients": ["Aloe", "Green Tea", "Cica", "Birch Juice", "Vitamin C"],
        "types": ["Sunscreen", "Sun Stick", "Sun Serum", "After Sun Gel", "Tone-Up SPF"],
    },
    {
        "slug": "face-masks",
        "name": "Face Masks",
        "concerns": ["Hydration", "Acne Marks", "Firming"],
        "ingredients": ["Collagen", "Ginseng", "Rice", "Propolis", "Pomegranate"],
        "types": ["Sheet Mask", "Sleeping Mask", "Hydrogel Mask", "Peel Pad", "Patch Set"],
    },
    {
        "slug": "makeup",
        "name": "Makeup",
        "concerns": ["Natural Glow", "Even Tone", "Long Wear"],
        "ingredients": ["Peach", "Jade Powder", "Lotus", "Silk", "Rose"],
        "types": ["Cushion", "Lip Tint", "Blush", "Primer", "Brow Gel"],
    },
    {
        "slug": "k-beauty-devices",
        "name": "K-Beauty Devices",
        "concerns": ["Firming", "Device Routine", "Scalp Care"],
        "ingredients": ["LED", "EMS", "Galvanic", "RF", "Microcurrent"],
        "types": ["LED Mask", "EMS Lifter", "Galvanic Wand", "RF Device", "Scalp Massager"],
    },
]

BRAND_PREFIX = {
    "skincare": ["Seoul Cica Lab", "Luna Rice", "Jade Heartleaf", "Grace Barrier", "Nabi Glow"],
    "suncare": ["Aloe Sun Seoul", "Daylight Cica", "Lumi SPF", "Birch Glow", "Golden Shield"],
    "face-masks": ["Ginseng Ritual", "Rice Veil", "Pomegranate Moon", "Propolis Seoul", "Hydro Lotus"],
    "makeup": ["Peach Seoul", "Silk Hue", "Luna Tint", "Jade Muse", "Grace Color"],
    "k-beauty-devices": ["GlowTech Seoul", "Lumi Device", "Jade Lift", "Grace Sonic", "Nabi Device Lab"],
}

PALETTES = [
    ("#FFF7F0", "#FF7A6B", "#2B1E1A"),
    ("#F6F1EA", "#8FAF8A", "#2B1E1A"),
    ("#FFF9EA", "#D8A24A", "#2B1E1A"),
    ("#F8EEEE", "#C98F7A", "#2B1E1A"),
    ("#F5F7F2", "#A6B7A1", "#2B1E1A"),
]


PUBLIC_SEARCHES = [
    ("skincare", ["serum", "face cream", "toner", "cleanser", "moisturizer"]),
    ("suncare", ["sunscreen", "sun stick", "spf", "after sun", "sun cream"]),
    ("face-masks", ["sheet mask", "face mask", "hydrogel mask", "patch", "toner pad"]),
    ("makeup", ["lipstick", "mascara", "foundation", "blush", "eyeliner"]),
    ("k-beauty-devices", ["beauty device", "facial device", "skin device", "led mask", "massager"]),
]


def safe_text(value, fallback: str = "") -> str:
    if isinstance(value, list):
        value = ", ".join(str(v) for v in value if v)
    value = str(value or fallback).strip()
    return value[:240]


def public_image_to_square(url: str, out_path: Path) -> bool:
    if not httpx or not url:
        return False
    try:
        with httpx.Client(timeout=12, follow_redirects=True, headers={"User-Agent": "GraceYoungSeed/0.1"}) as client:
            response = client.get(url)
            response.raise_for_status()
        img = Image.open(BytesIO(response.content)).convert("RGB")
        img = ImageOps.contain(img, (820, 820), method=Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (900, 900), "#f8f3ef")
        canvas.paste(img, ((900 - img.width) // 2, (900 - img.height) // 2))
        out_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(out_path, "JPEG", quality=88, optimize=True)
        return True
    except Exception:
        return False


def fetch_openbeautyfacts_records(limit: int = 250) -> list[dict]:
    """Fetch open cosmetic product records with image URLs from Open Beauty Facts.

    Open Beauty Facts is an open, collaborative cosmetic database. The seed keeps a
    fallback generated image path, so local/offline deployments still work.
    """
    if not httpx:
        return []
    records: list[dict] = []
    seen: set[str] = set()
    fields = "product_name,brands,image_front_url,image_url,categories_tags,categories,code"
    with httpx.Client(timeout=14, follow_redirects=True, headers={"User-Agent": "GraceYoungSeed/0.1"}) as client:
        for category_slug, terms in PUBLIC_SEARCHES:
            for term in terms:
                if len(records) >= limit:
                    return records[:limit]
                try:
                    res = client.get(
                        "https://world.openbeautyfacts.org/cgi/search.pl",
                        params={
                            "search_terms": term,
                            "search_simple": 1,
                            "action": "process",
                            "json": 1,
                            "page_size": 40,
                            "fields": fields,
                        },
                    )
                    res.raise_for_status()
                    data = res.json()
                except Exception:
                    continue
                for item in data.get("products", []):
                    name = safe_text(item.get("product_name"))
                    brand = safe_text(item.get("brands"), "Open Beauty Brand").split(",")[0].strip() or "Open Beauty Brand"
                    image_url = item.get("image_front_url") or item.get("image_url")
                    code = str(item.get("code") or f"{brand}-{name}")
                    if not name or not image_url or code in seen:
                        continue
                    seen.add(code)
                    records.append({
                        "category_slug": category_slug,
                        "brand": brand[:80],
                        "name": name[:140],
                        "image_url": image_url,
                        "description": safe_text(item.get("categories"), "Open cosmetic product data with public product imagery."),
                    })
                    if len(records) >= limit:
                        return records[:limit]
    return records[:limit]


def seed_public_catalog(db, categories: dict[str, Category], tmp_dir: Path, limit: int = 250) -> list[Product]:
    records = fetch_openbeautyfacts_records(limit=limit)
    if not records:
        return []
    created: list[Product] = []
    brand_cache: dict[str, Brand] = {}
    for idx, rec in enumerate(records, start=1):
        category = categories.get(rec["category_slug"]) or next(iter(categories.values()))
        brand_name = rec["brand"] or "Open Beauty Brand"
        brand_slug = slugify(brand_name) or f"open-beauty-brand-{idx}"
        brand = brand_cache.get(brand_slug)
        if not brand:
            brand = db.scalar(select(Brand).where(Brand.slug == brand_slug))
        if not brand:
            brand = Brand(
                slug=brand_slug,
                name=brand_name,
                country="Public Data",
                description="Public cosmetic product record imported for Grace Young demo catalog.",
                is_active=True,
            )
            db.add(brand)
            db.flush()
        brand_cache[brand_slug] = brand

        product_slug = slugify(f"{brand_name}-{rec['name']}") or f"public-product-{idx:03d}"
        if db.scalar(select(Product).where(Product.slug == product_slug)):
            product_slug = f"{product_slug}-{idx:03d}"
        local_img = tmp_dir / f"public-{product_slug}.jpg"
        if not public_image_to_square(rec.get("image_url", ""), local_img):
            make_product_image(rec["name"], brand_name, category.name, local_img)
            content_type = "image/png"
            object_key = f"public-products/{category.slug}/{product_slug}.png"
        else:
            content_type = "image/jpeg"
            object_key = f"public-products/{category.slug}/{product_slug}.jpg"
        image_url = upload_file(local_img, object_key, content_type, settings.minio_bucket_products)
        price = Decimal(str(round(random.uniform(8, 75), 2)))
        if category.slug == "k-beauty-devices":
            price = Decimal(str(round(random.uniform(59, 199), 2)))
        product = Product(
            brand_id=brand.id,
            slug=product_slug,
            name=rec["name"],
            short_description=rec.get("description") or "Public cosmetic product data curated for Grace Young demo commerce.",
            price=price,
            currency="USD",
            status="published",
        )
        product.brand = brand
        product.categories = [category]
        product.images = [ProductImage(url=image_url, alt_text=f"{brand_name} {rec['name']}", sort_order=0)]
        db.add(product)
        created.append(product)
    return created

def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")

def color_from_text(text: str) -> tuple[str, str, str]:
    digest = hashlib.sha1(text.encode()).hexdigest()
    return PALETTES[int(digest[:2], 16) % len(PALETTES)]

def font(size: int):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()

def wrap_text(draw: ImageDraw.ImageDraw, text: str, width: int, fnt) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        if draw.textbbox((0, 0), trial, font=fnt)[2] <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines[:4]

def make_product_image(product_name: str, brand_name: str, category_name: str, out_path: Path) -> None:
    bg, accent, ink = color_from_text(product_name + brand_name)
    img = Image.new("RGB", (900, 900), bg)
    draw = ImageDraw.Draw(img)
    title_font = font(54)
    brand_font = font(34)
    small_font = font(26)
    tiny_font = font(22)

    # Soft package shadow
    draw.rounded_rectangle((230, 100, 670, 790), radius=44, fill="#FFFFFF", outline=accent, width=6)
    draw.rounded_rectangle((260, 135, 640, 755), radius=34, fill=bg, outline="#FFFFFF", width=3)
    draw.rounded_rectangle((310, 185, 590, 245), radius=24, fill=accent)
    draw.text((450, 204), "GRACE YOUNG", fill="#FFFFFF", anchor="mm", font=small_font)

    y = 315
    draw.text((450, y), brand_name, fill=ink, anchor="mm", font=brand_font)
    y += 62
    for line in wrap_text(draw, product_name, 330, title_font):
        draw.text((450, y), line, fill=ink, anchor="mm", font=title_font)
        y += 62

    draw.line((310, 620, 590, 620), fill=accent, width=4)
    draw.text((450, 665), category_name.upper(), fill=ink, anchor="mm", font=tiny_font)
    draw.text((450, 715), "K-BEAUTY CURATION", fill=accent, anchor="mm", font=tiny_font)

    # Small decorative circles
    for x, y, r in [(130, 150, 35), (760, 210, 24), (150, 740, 28), (770, 700, 42)]:
        draw.ellipse((x-r, y-r, x+r, y+r), fill=accent)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG", optimize=True)

def create_demo_users(db):
    demo_users = [
        {"email": "admin@kgraceyoung.com", "password": "Admin123!", "full_name": "Grace Young Admin", "role": "admin", "locale": "en"},
        {"email": "customer@kgraceyoung.com", "password": "Customer123!", "full_name": "Grace Young Customer", "role": "customer", "locale": "en"},
    ]
    for item in demo_users:
        user = db.scalar(select(User).where(User.email == item["email"]))
        if not user:
            db.add(User(
                email=item["email"],
                hashed_password=get_password_hash(item["password"]),
                full_name=item["full_name"],
                role=item["role"],
                locale=item["locale"],
                is_active=True,
            ))
        else:
            user.role = item["role"]
            user.hashed_password = get_password_hash(item["password"])
            user.is_active = True


def create_membership(db):
    if db.query(MembershipTier).first():
        return
    db.add_all([
        MembershipTier(code="starter", name="Grace Starter", annual_spend_min=0, point_rate=1),
        MembershipTier(code="glow", name="Grace Glow", annual_spend_min=200, point_rate=3),
        MembershipTier(code="plus", name="Grace Plus", annual_spend_min=500, point_rate=5),
        MembershipTier(code="vip", name="Grace VIP", annual_spend_min=1000, point_rate=7),
    ])

def reset_catalog(db):
    db.execute(delete(product_categories))
    db.execute(delete(ProductImage))
    db.execute(delete(Product))
    db.execute(delete(Brand))
    db.execute(delete(Category))
    db.commit()

def index_products(products: Iterable[Product]):
    if not meilisearch:
        return
    try:
        client = meilisearch.Client(settings.meili_url, settings.meili_master_key)
        index = client.index("products")
        docs = []
        for p in products:
            docs.append({
                "id": str(p.id),
                "slug": p.slug,
                "name": p.name,
                "brand": p.brand.name if p.brand else None,
                "price": float(p.price),
                "currency": p.currency,
                "categories": [c.name for c in p.categories],
                "image_url": p.images[0].url if p.images else None,
                "description": p.short_description or "",
            })
        if docs:
            index.add_documents(docs)
            index.update_filterable_attributes(["brand", "categories", "currency"])
            index.update_sortable_attributes(["price"])
    except Exception as exc:
        print(f"[WARN] Meilisearch indexing skipped: {exc}")

def seed(reset: bool = False, public_data: bool = False):
    ensure_bucket(settings.minio_bucket_products)
    created_products: list[Product] = []
    with SessionLocal() as db:
        if reset:
            reset_catalog(db)

        create_demo_users(db)
        create_membership(db)

        categories: dict[str, Category] = {}
        for order, cat in enumerate(CATEGORIES):
            category = db.scalar(select(Category).where(Category.slug == cat["slug"]))
            if not category:
                category = Category(slug=cat["slug"], name=cat["name"], sort_order=order)
                db.add(category)
                db.flush()
            categories[cat["slug"]] = category

        tmp_dir = Path(tempfile.gettempdir()) / "grace_young_phase2_images"
        tmp_dir.mkdir(parents=True, exist_ok=True)

        if public_data:
            public_products = seed_public_catalog(db, categories, tmp_dir)
            if public_products:
                db.commit()
                products = db.scalars(select(Product)).all()
                index_products(products)
                summary = {
                    "categories": db.query(Category).count(),
                    "brands": db.query(Brand).count(),
                    "products": db.query(Product).count(),
                    "images": db.query(ProductImage).count(),
                    "bucket": settings.minio_bucket_products,
                    "source": "Open Beauty Facts public data",
                }
                print("Public cosmetics seed completed:")
                for k, v in summary.items():
                    print(f"  - {k}: {v}")
                return
            print("[WARN] Public cosmetic data fetch failed; falling back to generated sample data.")

        for cat in CATEGORIES:
            category = categories[cat["slug"]]
            for brand_idx, brand_name in enumerate(BRAND_PREFIX[cat["slug"]], start=1):
                brand_slug = slugify(brand_name)
                brand = db.scalar(select(Brand).where(Brand.slug == brand_slug))
                if not brand:
                    brand = Brand(
                        slug=brand_slug,
                        name=brand_name,
                        country="Korea",
                        description=f"Sample K-beauty brand curated for {cat['name']} routines in the Grace Young Phase 2 catalog.",
                        is_active=True,
                    )
                    db.add(brand)
                    db.flush()

                for product_idx in range(1, 11):
                    ingredient = cat["ingredients"][(product_idx + brand_idx) % len(cat["ingredients"])]
                    ptype = cat["types"][(product_idx - 1) % len(cat["types"])]
                    concern = cat["concerns"][(product_idx + 2) % len(cat["concerns"])]
                    product_name = f"{ingredient} {ptype} {product_idx:02d}"
                    product_slug = slugify(f"{brand_name}-{product_name}")
                    existing = db.scalar(select(Product).where(Product.slug == product_slug))
                    if existing:
                        created_products.append(existing)
                        continue

                    price = Decimal(str(round(random.uniform(12, 89), 2)))
                    if cat["slug"] == "k-beauty-devices":
                        price = Decimal(str(round(random.uniform(69, 249), 2)))

                    local_img = tmp_dir / f"{product_slug}.png"
                    make_product_image(product_name, brand_name, cat["name"], local_img)
                    object_key = f"sample-products/{cat['slug']}/{product_slug}.png"
                    image_url = upload_file(local_img, object_key, "image/png", settings.minio_bucket_products)

                    product = Product(
                        brand_id=brand.id,
                        slug=product_slug,
                        name=product_name,
                        short_description=f"A Grace Young sample product for {concern}. Featuring {ingredient} in a K-beauty routine-ready {ptype.lower()} format.",
                        price=price,
                        currency="USD",
                        status="published",
                    )
                    product.brand = brand
                    product.categories = [category]
                    product.images = [ProductImage(url=image_url, alt_text=f"{brand_name} {product_name}", sort_order=0)]
                    db.add(product)
                    created_products.append(product)

        db.commit()
        # Reload products with relationships for indexing.
        products = db.scalars(select(Product)).all()
        index_products(products)
        summary = {
            "categories": db.query(Category).count(),
            "brands": db.query(Brand).count(),
            "products": db.query(Product).count(),
            "images": db.query(ProductImage).count(),
            "bucket": settings.minio_bucket_products,
        }
        print("Phase 2 seed completed:")
        for k, v in summary.items():
            print(f"  - {k}: {v}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Delete existing catalog rows before seeding")
    parser.add_argument("--public-data", action="store_true", help="Fetch public cosmetic product data and images from Open Beauty Facts when internet is available")
    args = parser.parse_args()
    seed(reset=args.reset, public_data=args.public_data)
