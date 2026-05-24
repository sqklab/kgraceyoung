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
from decimal import Decimal
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont
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

def seed(reset: bool = False):
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
    args = parser.parse_args()
    seed(reset=args.reset)
