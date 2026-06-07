from __future__ import annotations
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from pydantic import BaseModel, Field
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session, selectinload

from app.api.v1.auth import require_admin
from app.db.session import get_db
from app.models.user import User
from app.models.catalog import Product, Brand, Category, ProductImage
from app.models.commerce import Order, OrderItem, CustomerAddress, WishlistItem, Cart, CartItem
from app.models.ops import Payment, Shipment, Banner
from app.models.reels import Reel, ReelProduct
from app.models.admin_ops import InventoryMovement, Coupon, Review, StoreSetting, AuditLog
from app.services.storage import upload_file
from pathlib import Path
import tempfile

router = APIRouter(prefix="/admin", tags=["admin-backoffice"])


def audit(db: Session, admin: User, action: str, entity_type: str | None = None, entity_id: str | None = None, payload: dict | None = None):
    db.add(AuditLog(actor_id=admin.id, action=action, entity_type=entity_type, entity_id=entity_id, payload=payload or {}))


def dec(v) -> float:
    return float(v or 0)


def product_payload(p: Product) -> dict:
    return {
        "id": str(p.id), "slug": p.slug, "name": p.name, "brand": p.brand.name if p.brand else None,
        "brand_id": str(p.brand_id) if p.brand_id else None,
        "category_ids": [str(c.id) for c in p.categories], "categories": [c.name for c in p.categories],
        "short_description": p.short_description, "price": dec(p.price), "compare_at_price": dec(getattr(p, "compare_at_price", 0)),
        "cost_price": dec(getattr(p, "cost_price", 0)), "currency": p.currency, "status": p.status,
        "sku": getattr(p, "sku", None), "barcode": getattr(p, "barcode", None),
        "inventory_quantity": getattr(p, "inventory_quantity", 0), "low_stock_threshold": getattr(p, "low_stock_threshold", 0),
        "weight_grams": getattr(p, "weight_grams", 0), "tags": getattr(p, "tags", None),
        "skin_concerns": getattr(p, "skin_concerns", None), "ingredients": getattr(p, "ingredients", None), "how_to_use": getattr(p, "how_to_use", None),
        "image_urls": [img.url for img in sorted(p.images, key=lambda x: x.sort_order)],
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }


def order_payload(o: Order) -> dict:
    return {
        "id": str(o.id), "email": o.email, "status": o.status, "payment_status": o.payment_status,
        "fulfillment_status": o.fulfillment_status, "subtotal": dec(o.subtotal), "shipping_total": dec(o.shipping_total),
        "tax_total": dec(o.tax_total), "grand_total": dec(o.grand_total), "currency": o.currency,
        "shipping_name": o.shipping_name, "shipping_phone": o.shipping_phone, "shipping_line1": o.shipping_line1,
        "shipping_line2": o.shipping_line2, "shipping_city": o.shipping_city, "shipping_state": o.shipping_state,
        "shipping_postal_code": o.shipping_postal_code, "shipping_country": o.shipping_country,
        "shipping_carrier": getattr(o, "shipping_carrier", None), "shipping_service": getattr(o, "shipping_service", None),
        "tracking_code": getattr(o, "tracking_code", None), "notes": o.notes, "created_at": o.created_at.isoformat() if o.created_at else None,
        "items": [{"id": str(i.id), "product_id": str(i.product_id) if i.product_id else None, "product_name": i.product_name, "quantity": i.quantity, "unit_price": dec(i.unit_price), "line_total": dec(i.line_total)} for i in o.items],
    }


class ProductIn(BaseModel):
    slug: str
    name: str
    brand_id: UUID | None = None
    category_ids: list[UUID] = []
    short_description: str | None = None
    price: Decimal = Decimal("0")
    compare_at_price: Decimal | None = None
    cost_price: Decimal | None = None
    currency: str = "USD"
    status: str = "published"
    sku: str | None = None
    barcode: str | None = None
    inventory_quantity: int = 100
    low_stock_threshold: int = 10
    weight_grams: int = 120
    tags: str | None = None
    skin_concerns: str | None = None
    ingredients: str | None = None
    how_to_use: str | None = None
    image_urls: list[str] = []


class ProductPatch(BaseModel):
    slug: str | None = None
    name: str | None = None
    brand_id: UUID | None = None
    category_ids: list[UUID] | None = None
    short_description: str | None = None
    price: Decimal | None = None
    compare_at_price: Decimal | None = None
    cost_price: Decimal | None = None
    currency: str | None = None
    status: str | None = None
    sku: str | None = None
    barcode: str | None = None
    inventory_quantity: int | None = None
    low_stock_threshold: int | None = None
    weight_grams: int | None = None
    tags: str | None = None
    skin_concerns: str | None = None
    ingredients: str | None = None
    how_to_use: str | None = None
    image_urls: list[str] | None = None


class InventoryAdjust(BaseModel):
    quantity_delta: int
    movement_type: str = "adjustment"
    reason: str | None = None


class OrderPatch(BaseModel):
    status: str | None = None
    payment_status: str | None = None
    fulfillment_status: str | None = None
    tracking_code: str | None = None
    notes: str | None = None


class LabelCreate(BaseModel):
    carrier: str = "Grace Logistics"
    service: str = "Standard"
    tracking_code: str | None = None


class BannerIn(BaseModel):
    placement: str = "home_hero"
    title: str
    subtitle: str | None = None
    image_url: str
    link_url: str | None = None
    button_label: str | None = "SHOP NOW"
    sort_order: int = 0
    is_active: bool = True

class CouponIn(BaseModel):
    code: str
    name: str
    discount_type: str = "percent"
    discount_value: Decimal = Decimal("10")
    minimum_order_amount: Decimal = Decimal("0")
    usage_limit: int | None = None
    per_customer_limit: int | None = None
    is_active: bool = True

class ReelIn(BaseModel):
    title: str
    video_url: str
    thumbnail_url: str | None = None
    locale: str = "en"
    status: str = "published"
    product_ids: list[UUID] = []

class ReviewPatch(BaseModel):
    status: str

class SettingIn(BaseModel):
    value: dict


@router.get("/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    order_count = db.scalar(select(func.count(Order.id))) or 0
    paid_sales = db.scalar(select(func.coalesce(func.sum(Order.grand_total), 0)).where(Order.payment_status == "paid")) or 0
    pending = db.scalar(select(func.count(Order.id)).where(Order.fulfillment_status.in_(["unfulfilled", "fulfillment_pending"]))) or 0
    products = db.scalar(select(func.count(Product.id))) or 0
    low_stock = db.scalar(select(func.count(Product.id)).where(Product.inventory_quantity <= Product.low_stock_threshold)) or 0
    customers = db.scalar(select(func.count(User.id)).where(User.role == "customer")) or 0
    return {"orders": order_count, "paid_sales": dec(paid_sales), "pending_orders": pending, "products": products, "low_stock": low_stock, "customers": customers}

@router.get("/dashboard/recent-orders")
def recent_orders(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    rows = db.scalars(select(Order).options(selectinload(Order.items)).order_by(Order.created_at.desc()).limit(8)).all()
    return [order_payload(o) for o in rows]

@router.get("/dashboard/best-sellers")
def best_sellers(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    rows = db.execute(select(OrderItem.product_name, func.sum(OrderItem.quantity).label("units"), func.sum(OrderItem.line_total).label("revenue")).group_by(OrderItem.product_name).order_by(func.sum(OrderItem.quantity).desc()).limit(8)).all()
    return [{"product_name": r[0], "units": int(r[1] or 0), "revenue": dec(r[2])} for r in rows]


@router.get("/products")
def admin_products(q: str | None = None, status: str | None = None, limit: int = 80, offset: int = 0, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    stmt = select(Product).options(selectinload(Product.brand), selectinload(Product.categories), selectinload(Product.images)).order_by(Product.created_at.desc()).offset(offset).limit(limit)
    if q:
        like = f"%{q.strip()}%"; stmt = stmt.where(or_(Product.name.ilike(like), Product.slug.ilike(like), Product.sku.ilike(like)))
    if status:
        stmt = stmt.where(Product.status == status)
    return [product_payload(p) for p in db.scalars(stmt).all()]

@router.post("/products", status_code=status.HTTP_201_CREATED)
def admin_create_product(data: ProductIn, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    item = Product(**data.model_dump(exclude={"category_ids", "image_urls"}))
    if data.category_ids:
        item.categories = db.scalars(select(Category).where(Category.id.in_(data.category_ids))).all()
    for idx, url in enumerate(data.image_urls):
        item.images.append(ProductImage(url=url, alt_text=data.name, sort_order=idx))
    db.add(item); audit(db, admin, "product.create", "product", None, {"slug": data.slug}); db.commit(); db.refresh(item)
    return product_payload(db.scalar(select(Product).options(selectinload(Product.brand), selectinload(Product.categories), selectinload(Product.images)).where(Product.id == item.id)))

@router.get("/products/{product_id}")
def admin_get_product(product_id: UUID, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    item = db.scalar(select(Product).options(selectinload(Product.brand), selectinload(Product.categories), selectinload(Product.images)).where(Product.id == product_id))
    if not item: raise HTTPException(404, "Product not found")
    return product_payload(item)

@router.patch("/products/{product_id}")
def admin_update_product(product_id: UUID, data: ProductPatch, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    item = db.get(Product, product_id)
    if not item: raise HTTPException(404, "Product not found")
    body = data.model_dump(exclude_unset=True, exclude={"category_ids", "image_urls"})
    for k, v in body.items(): setattr(item, k, v)
    if data.category_ids is not None: item.categories = db.scalars(select(Category).where(Category.id.in_(data.category_ids))).all() if data.category_ids else []
    if data.image_urls is not None: item.images = [ProductImage(url=url, alt_text=item.name, sort_order=i) for i, url in enumerate(data.image_urls)]
    audit(db, admin, "product.update", "product", str(item.id), body); db.commit()
    return admin_get_product(product_id, db, admin)

@router.delete("/products/{product_id}")
def admin_delete_product(product_id: UUID, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    item = db.get(Product, product_id)
    if item:
        db.delete(item); audit(db, admin, "product.delete", "product", str(product_id)); db.commit()
    return {"ok": True}

@router.post("/uploads/image")
async def admin_upload_image(file: UploadFile = File(...), admin: User = Depends(require_admin)):
    suffix = Path(file.filename or "upload.png").suffix or ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read()); tmp_path = Path(tmp.name)
    key = f"admin-uploads/{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{tmp_path.stem}{suffix}"
    url = upload_file(tmp_path, key, content_type=file.content_type or "application/octet-stream")
    tmp_path.unlink(missing_ok=True)
    return {"url": url}


@router.get("/inventory")
def inventory_list(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    rows = db.scalars(select(Product).options(selectinload(Product.brand), selectinload(Product.images)).order_by(Product.inventory_quantity.asc(), Product.name).limit(300)).all()
    return [product_payload(p) for p in rows]

@router.post("/inventory/{product_id}/adjust")
def inventory_adjust(product_id: UUID, data: InventoryAdjust, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    p = db.get(Product, product_id)
    if not p: raise HTTPException(404, "Product not found")
    p.inventory_quantity = max(0, int(p.inventory_quantity or 0) + data.quantity_delta)
    m = InventoryMovement(product_id=p.id, movement_type=data.movement_type, quantity_delta=data.quantity_delta, reason=data.reason, created_by=admin.id)
    db.add(m); audit(db, admin, "inventory.adjust", "product", str(p.id), data.model_dump()); db.commit(); db.refresh(p)
    return product_payload(db.scalar(select(Product).options(selectinload(Product.brand), selectinload(Product.categories), selectinload(Product.images)).where(Product.id == p.id)))

@router.get("/inventory/movements")
def inventory_movements(limit: int = 100, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    rows = db.scalars(select(InventoryMovement).order_by(InventoryMovement.created_at.desc()).limit(limit)).all()
    return [{"id": str(r.id), "product_id": str(r.product_id), "movement_type": r.movement_type, "quantity_delta": r.quantity_delta, "reason": r.reason, "created_at": r.created_at.isoformat() if r.created_at else None} for r in rows]


@router.get("/orders")
def admin_orders(status_filter: str | None = None, q: str | None = None, limit: int = 80, offset: int = 0, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    stmt = select(Order).options(selectinload(Order.items)).order_by(Order.created_at.desc()).offset(offset).limit(limit)
    if status_filter: stmt = stmt.where(Order.status == status_filter)
    if q: stmt = stmt.where(or_(Order.email.ilike(f"%{q}%"), Order.tracking_code.ilike(f"%{q}%")))
    return [order_payload(o) for o in db.scalars(stmt).all()]

@router.get("/orders/{order_id}")
def admin_order(order_id: UUID, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    o = db.scalar(select(Order).options(selectinload(Order.items)).where(Order.id == order_id))
    if not o: raise HTTPException(404, "Order not found")
    return order_payload(o)

@router.patch("/orders/{order_id}")
def admin_patch_order(order_id: UUID, data: OrderPatch, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    o = db.get(Order, order_id)
    if not o: raise HTTPException(404, "Order not found")
    for k, v in data.model_dump(exclude_unset=True).items(): setattr(o, k, v)
    if data.tracking_code:
        o.fulfillment_status = "shipped"; o.status = "shipped"; o.shipped_at = datetime.now(timezone.utc)
    audit(db, admin, "order.update", "order", str(o.id), data.model_dump(exclude_unset=True)); db.commit()
    return admin_order(order_id, db, admin)

@router.post("/orders/{order_id}/shipping-label")
def admin_shipping_label(order_id: UUID, data: LabelCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    o = db.get(Order, order_id)
    if not o: raise HTTPException(404, "Order not found")
    tracking = data.tracking_code or f"GY{str(o.id).replace('-', '')[:12].upper()}"
    label_url = f"https://api.kgraceyoung.com/mock-labels/{tracking}.pdf"
    db.add(Shipment(order_id=o.id, provider="manual", carrier=data.carrier, service=data.service, rate=o.shipping_total or Decimal("0"), currency=o.currency, tracking_code=tracking, label_url=label_url, status="label_created"))
    o.tracking_code = tracking; o.fulfillment_status = "shipped"; o.status = "shipped"; o.shipped_at = datetime.now(timezone.utc)
    audit(db, admin, "order.shipping_label", "order", str(o.id), {"tracking": tracking}); db.commit()
    return {"order_id": str(o.id), "tracking_code": tracking, "label_url": label_url, "status": o.status}

@router.get("/orders/{order_id}/packing-slip")
def admin_packing_slip(order_id: UUID, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    o = admin_order(order_id, db, admin)
    lines = [f"Grace Young Packing Slip", f"Order: {o['id'][:8]}", f"Ship to: {o.get('shipping_name') or o['email']}", f"Address: {o.get('shipping_line1')}, {o.get('shipping_city')} {o.get('shipping_postal_code')}", "", "Items:"]
    for item in o["items"]: lines.append(f"- {item['quantity']} x {item['product_name']}")
    return {"text": "\n".join(lines), "order": o}


@router.get("/customers")
def customers(q: str | None = None, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    stmt = select(User).where(User.role == "customer").order_by(User.created_at.desc()).limit(300)
    if q: stmt = stmt.where(or_(User.email.ilike(f"%{q}%"), User.full_name.ilike(f"%{q}%")))
    rows = db.scalars(stmt).all()
    result = []
    for u in rows:
        total = db.scalar(select(func.coalesce(func.sum(Order.grand_total), 0)).where(Order.user_id == u.id, Order.payment_status == "paid")) or 0
        count = db.scalar(select(func.count(Order.id)).where(Order.user_id == u.id)) or 0
        result.append({"id": str(u.id), "email": u.email, "full_name": u.full_name, "locale": u.locale, "is_active": u.is_active, "created_at": u.created_at.isoformat() if u.created_at else None, "order_count": count, "total_spend": dec(total)})
    return result

@router.get("/customers/{user_id}")
def customer_detail(user_id: UUID, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    u = db.get(User, user_id)
    if not u: raise HTTPException(404, "Customer not found")
    orders = db.scalars(select(Order).options(selectinload(Order.items)).where(Order.user_id == u.id).order_by(Order.created_at.desc()).limit(20)).all()
    addresses = db.scalars(select(CustomerAddress).where(CustomerAddress.user_id == u.id).order_by(CustomerAddress.created_at.desc())).all()
    wish_count = db.scalar(select(func.count(WishlistItem.id)).where(WishlistItem.user_id == u.id)) or 0
    return {"id": str(u.id), "email": u.email, "full_name": u.full_name, "locale": u.locale, "is_active": u.is_active, "orders": [order_payload(o) for o in orders], "addresses": [{"id": str(a.id), "label": a.label, "full_name": a.full_name, "line1": a.line1, "city": a.city, "country": a.country} for a in addresses], "wishlist_count": wish_count}

@router.patch("/customers/{user_id}")
def customer_patch(user_id: UUID, is_active: bool | None = None, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    u = db.get(User, user_id)
    if not u: raise HTTPException(404, "Customer not found")
    if is_active is not None: u.is_active = is_active
    audit(db, admin, "customer.update", "user", str(u.id), {"is_active": is_active}); db.commit(); return {"ok": True}


@router.get("/banners")
def banners(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return [{"id": str(b.id), "placement": b.placement, "title": b.title, "subtitle": b.subtitle, "image_url": b.image_url, "link_url": b.link_url, "button_label": b.button_label, "sort_order": b.sort_order, "is_active": b.is_active} for b in db.scalars(select(Banner).order_by(Banner.placement, Banner.sort_order)).all()]

@router.post("/banners", status_code=status.HTTP_201_CREATED)
def banners_create(data: BannerIn, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    b = Banner(**data.model_dump()); db.add(b); audit(db, admin, "banner.create", "banner", None, data.model_dump()); db.commit(); db.refresh(b); return banners(db, admin)[0] if False else {"id": str(b.id), **data.model_dump()}

@router.patch("/banners/{banner_id}")
def banners_patch(banner_id: UUID, data: BannerIn, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    b = db.get(Banner, banner_id)
    if not b: raise HTTPException(404, "Banner not found")
    for k, v in data.model_dump(exclude_unset=True).items(): setattr(b, k, v)
    audit(db, admin, "banner.update", "banner", str(b.id), data.model_dump()); db.commit(); return {"ok": True}

@router.delete("/banners/{banner_id}")
def banners_delete(banner_id: UUID, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    b = db.get(Banner, banner_id)
    if b: db.delete(b); audit(db, admin, "banner.delete", "banner", str(banner_id)); db.commit()
    return {"ok": True}


@router.get("/reels")
def reels(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return [{"id": str(r.id), "title": r.title, "video_url": r.video_url, "thumbnail_url": r.thumbnail_url, "locale": r.locale, "status": r.status, "view_count": r.view_count, "like_count": r.like_count, "created_at": r.created_at.isoformat() if r.created_at else None} for r in db.scalars(select(Reel).order_by(Reel.created_at.desc())).all()]

@router.post("/reels", status_code=status.HTTP_201_CREATED)
def reels_create(data: ReelIn, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    r = Reel(title=data.title, video_url=data.video_url, thumbnail_url=data.thumbnail_url, locale=data.locale, status=data.status)
    db.add(r); db.flush()
    for i, pid in enumerate(data.product_ids): db.add(ReelProduct(reel_id=r.id, product_id=pid, display_order=i))
    audit(db, admin, "reel.create", "reel", None, data.model_dump()); db.commit(); db.refresh(r); return {"id": str(r.id), "title": r.title}

@router.patch("/reels/{reel_id}")
def reels_update(reel_id: UUID, data: ReelIn, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    r = db.get(Reel, reel_id)
    if not r: raise HTTPException(404, "Reel not found")
    for k in ["title", "video_url", "thumbnail_url", "locale", "status"]: setattr(r, k, getattr(data, k))
    db.query(ReelProduct).filter(ReelProduct.reel_id == r.id).delete()
    for i, pid in enumerate(data.product_ids): db.add(ReelProduct(reel_id=r.id, product_id=pid, display_order=i))
    audit(db, admin, "reel.update", "reel", str(r.id), data.model_dump()); db.commit(); return {"ok": True}

@router.delete("/reels/{reel_id}")
def reels_delete(reel_id: UUID, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    r = db.get(Reel, reel_id)
    if r: db.delete(r); audit(db, admin, "reel.delete", "reel", str(reel_id)); db.commit()
    return {"ok": True}


@router.get("/coupons")
def coupons(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return [{"id": str(c.id), "code": c.code, "name": c.name, "discount_type": c.discount_type, "discount_value": dec(c.discount_value), "minimum_order_amount": dec(c.minimum_order_amount), "usage_limit": c.usage_limit, "per_customer_limit": c.per_customer_limit, "is_active": c.is_active, "created_at": c.created_at.isoformat() if c.created_at else None} for c in db.scalars(select(Coupon).order_by(Coupon.created_at.desc())).all()]

@router.post("/coupons", status_code=status.HTTP_201_CREATED)
def coupons_create(data: CouponIn, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    c = Coupon(**data.model_dump(), code=data.code.upper()); db.add(c); audit(db, admin, "coupon.create", "coupon", None, data.model_dump()); db.commit(); db.refresh(c); return {"id": str(c.id), "code": c.code}

@router.patch("/coupons/{coupon_id}")
def coupons_update(coupon_id: UUID, data: CouponIn, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    c = db.get(Coupon, coupon_id)
    if not c: raise HTTPException(404, "Coupon not found")
    for k, v in data.model_dump().items(): setattr(c, k, v.upper() if k == "code" and isinstance(v, str) else v)
    audit(db, admin, "coupon.update", "coupon", str(c.id), data.model_dump()); db.commit(); return {"ok": True}

@router.delete("/coupons/{coupon_id}")
def coupons_delete(coupon_id: UUID, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    c = db.get(Coupon, coupon_id)
    if c: db.delete(c); audit(db, admin, "coupon.delete", "coupon", str(coupon_id)); db.commit()
    return {"ok": True}


@router.get("/shipping/settings")
def shipping_settings(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    row = db.get(StoreSetting, "shipping")
    return row.value if row and row.value else {"free_shipping_minimum": 70, "rates": [{"id": "standard", "name": "Standard", "amount": 7.99}, {"id": "express", "name": "Express", "amount": 15.99}]}

@router.put("/shipping/settings")
def shipping_settings_put(data: SettingIn, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    row = db.get(StoreSetting, "shipping") or StoreSetting(key="shipping")
    row.value = data.value; db.add(row); audit(db, admin, "settings.shipping", "setting", "shipping", data.value); db.commit(); return row.value

@router.get("/payments")
def payments(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    rows = db.scalars(select(Payment).order_by(Payment.created_at.desc()).limit(200)).all()
    return [{"id": str(p.id), "order_id": str(p.order_id), "provider": p.provider, "status": p.status, "amount": dec(p.amount), "currency": p.currency, "checkout_url": p.checkout_url, "created_at": p.created_at.isoformat() if p.created_at else None} for p in rows]

@router.post("/payments/{payment_id}/refund")
def payment_refund(payment_id: UUID, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    p = db.get(Payment, payment_id)
    if not p: raise HTTPException(404, "Payment not found")
    p.status = "refunded"
    order = db.get(Order, p.order_id)
    if order: order.payment_status = "refunded"; order.status = "refunded"
    audit(db, admin, "payment.refund", "payment", str(p.id)); db.commit(); return {"ok": True}

@router.get("/reviews")
def reviews(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    rows = db.scalars(select(Review).order_by(Review.created_at.desc()).limit(200)).all()
    return [{"id": str(r.id), "product_id": str(r.product_id), "user_id": str(r.user_id) if r.user_id else None, "rating": r.rating, "title": r.title, "body": r.body, "status": r.status, "image_url": r.image_url, "created_at": r.created_at.isoformat() if r.created_at else None} for r in rows]

@router.patch("/reviews/{review_id}")
def review_moderate(review_id: UUID, data: ReviewPatch, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    r = db.get(Review, review_id)
    if not r: raise HTTPException(404, "Review not found")
    r.status = data.status; audit(db, admin, "review.moderate", "review", str(r.id), {"status": data.status}); db.commit(); return {"ok": True}

@router.get("/settings")
def settings_list(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    rows = db.scalars(select(StoreSetting).order_by(StoreSetting.key)).all()
    base = {"store": {"name": "Grace Young", "currency": "USD", "locales": ["en", "fr", "es", "ko"]}}
    for r in rows: base[r.key] = r.value
    return base

@router.put("/settings/{key}")
def settings_put(key: str, data: SettingIn, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    row = db.get(StoreSetting, key) or StoreSetting(key=key)
    row.value = data.value; db.add(row); audit(db, admin, "settings.update", "setting", key, data.value); db.commit(); return {"key": key, "value": row.value}
