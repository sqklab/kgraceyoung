from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, func
from app.db.session import get_db
from app.models.catalog import Product, Brand, Category

router = APIRouter(prefix="/catalog", tags=["catalog"])


def product_payload(p: Product) -> dict:
    return {
        "id": str(p.id),
        "slug": p.slug,
        "name": p.name,
        "brand": p.brand.name if p.brand else None,
        "brand_slug": p.brand.slug if p.brand else None,
        "price": float(p.price),
        "currency": p.currency,
        "description": p.short_description,
        "image_url": p.images[0].url if p.images else None,
        "images": [{"id": str(img.id), "url": img.url, "alt_text": img.alt_text, "sort_order": img.sort_order} for img in sorted(p.images, key=lambda x: x.sort_order)],
        "categories": [c.slug for c in p.categories],
        "status": p.status,
    }

@router.get("/summary")
def catalog_summary(db: Session = Depends(get_db)):
    return {
        "products": db.scalar(select(func.count(Product.id))) or 0,
        "brands": db.scalar(select(func.count(Brand.id))) or 0,
        "categories": db.scalar(select(func.count(Category.id))) or 0,
    }

@router.get("/categories")
def public_categories(db: Session = Depends(get_db)):
    rows = db.scalars(select(Category).order_by(Category.sort_order, Category.name)).all()
    return [{"id": str(c.id), "slug": c.slug, "name": c.name, "sort_order": c.sort_order} for c in rows]

@router.get("/products")
def public_products(limit: int = 24, offset: int = 0, category: str | None = None, q: str | None = None, db: Session = Depends(get_db)):
    stmt = select(Product).options(selectinload(Product.brand), selectinload(Product.images), selectinload(Product.categories)).where(Product.status == "published")
    if category:
        stmt = stmt.join(Product.categories).where(Category.slug == category)
    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(Product.name.ilike(like))
    rows = db.scalars(stmt.order_by(Product.created_at.desc()).offset(offset).limit(limit)).all()
    return [product_payload(p) for p in rows]

@router.get("/products/{slug}")
def public_product_detail(slug: str, db: Session = Depends(get_db)):
    product = db.scalar(
        select(Product)
        .options(selectinload(Product.brand), selectinload(Product.images), selectinload(Product.categories), selectinload(Product.translations))
        .where(Product.slug == slug, Product.status == "published")
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    related = db.scalars(
        select(Product)
        .options(selectinload(Product.brand), selectinload(Product.images), selectinload(Product.categories))
        .where(Product.status == "published", Product.id != product.id)
        .order_by(Product.created_at.desc())
        .limit(4)
    ).all()
    payload = product_payload(product)
    payload.update({
        "ingredients": "Water, botanical extracts, glycerin, niacinamide, panthenol, and fragrance-free skin conditioning agents.",
        "how_to_use": "Apply a small amount after cleansing. Use morning and evening. Follow with sunscreen during daytime.",
        "shipping_note": "Free shipping over $70+. Standard shipping usually ships within 2 business days.",
        "related": [product_payload(p) for p in related],
    })
    return payload

@router.get("/curation-sections")
def curation_sections():
    return [
        {"key": "dark-spots", "title": "Dark Spots & Melasma", "accent": "#FF7A6B"},
        {"key": "acne-marks", "title": "Acne Marks & Blemish Care", "accent": "#8FAF8A"},
        {"key": "daily-spf", "title": "Daily SPF & Sun Defense", "accent": "#D8A24A"},
        {"key": "sensitive", "title": "Sensitive & Barrier Care", "accent": "#E6D6BF"},
        {"key": "firming", "title": "Firming & Age-Defying", "accent": "#C98F7A"},
    ]
