from decimal import Decimal
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.catalog import Product
from app.models.commerce import Cart, CartItem, WishlistItem, CustomerAddress, Order, OrderItem
from app.schemas.commerce import (
    AddressCreate, AddressRead, AddressUpdate, CartAddItem, CartRead, CartUpdateItem,
    CheckoutRequest, CartMergeRequest, OrderRead, WishlistItemRead
)

router = APIRouter(prefix="/commerce", tags=["commerce"])


def product_mini(product: Product) -> dict:
    return {
        "id": product.id,
        "slug": product.slug,
        "name": product.name,
        "brand": product.brand.name if product.brand else None,
        "price": product.price,
        "currency": product.currency,
        "image_url": product.images[0].url if product.images else None,
    }


def get_or_create_cart(db: Session, user: User) -> Cart:
    cart = db.scalar(
        select(Cart).options(selectinload(Cart.items)).where(Cart.user_id == user.id)
    )
    if cart:
        return cart
    cart = Cart(user_id=user.id)
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart


def cart_payload(db: Session, cart: Cart) -> dict:
    items = db.scalars(
        select(CartItem)
        .where(CartItem.cart_id == cart.id)
    ).all()
    # SQLAlchemy cannot selectinload a bare FK. Load products explicitly for clarity.
    product_ids = [i.product_id for i in items]
    products = {}
    if product_ids:
        rows = db.scalars(
            select(Product)
            .options(selectinload(Product.brand), selectinload(Product.images))
            .where(Product.id.in_(product_ids))
        ).all()
        products = {p.id: p for p in rows}
    subtotal = Decimal("0.00")
    payload_items = []
    for item in items:
        product = products.get(item.product_id)
        if not product:
            continue
        line_total = product.price * item.quantity
        subtotal += line_total
        payload_items.append({
            "id": item.id,
            "product_id": item.product_id,
            "quantity": item.quantity,
            "product": product_mini(product),
            "line_total": line_total,
        })
    return {"id": cart.id, "currency": cart.currency, "items": payload_items, "subtotal": subtotal, "item_count": sum(i["quantity"] for i in payload_items)}


@router.get("/cart", response_model=CartRead)
def get_cart(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cart = get_or_create_cart(db, user)
    return cart_payload(db, cart)


@router.post("/cart/items", response_model=CartRead)
def add_cart_item(payload: CartAddItem, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    product = db.get(Product, payload.product_id)
    if not product or product.status != "published":
        raise HTTPException(status_code=404, detail="Product not found")
    cart = get_or_create_cart(db, user)
    item = db.scalar(select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == product.id))
    if item:
        item.quantity = min(99, item.quantity + payload.quantity)
    else:
        item = CartItem(cart_id=cart.id, product_id=product.id, quantity=payload.quantity)
        db.add(item)
    db.commit()
    return cart_payload(db, cart)


@router.patch("/cart/items/{item_id}", response_model=CartRead)
def update_cart_item(item_id: UUID, payload: CartUpdateItem, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cart = get_or_create_cart(db, user)
    item = db.scalar(select(CartItem).where(CartItem.id == item_id, CartItem.cart_id == cart.id))
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    if payload.quantity == 0:
        db.delete(item)
    else:
        item.quantity = payload.quantity
    db.commit()
    return cart_payload(db, cart)


@router.delete("/cart/items/{item_id}", response_model=CartRead)
def delete_cart_item(item_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cart = get_or_create_cart(db, user)
    item = db.scalar(select(CartItem).where(CartItem.id == item_id, CartItem.cart_id == cart.id))
    if item:
        db.delete(item)
        db.commit()
    return cart_payload(db, cart)


@router.post("/cart/merge", response_model=CartRead)
def merge_guest_cart(payload: CartMergeRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Merge a browser/localStorage guest cart into the authenticated user cart.

    The client stores a small guest cart before login. After login it posts that
    list here, and this endpoint upserts quantities into the persistent DB cart.
    """
    cart = get_or_create_cart(db, user)
    if not payload.items:
        return cart_payload(db, cart)

    product_ids = [item.product_id for item in payload.items]
    products = db.scalars(
        select(Product).where(Product.id.in_(product_ids), Product.status == "published")
    ).all()
    valid_ids = {p.id for p in products}

    for incoming in payload.items:
        if incoming.product_id not in valid_ids:
            continue
        item = db.scalar(
            select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == incoming.product_id)
        )
        if item:
            item.quantity = min(99, item.quantity + incoming.quantity)
        else:
            db.add(CartItem(cart_id=cart.id, product_id=incoming.product_id, quantity=incoming.quantity))
    db.commit()
    return cart_payload(db, cart)


@router.get("/wishlist", response_model=list[WishlistItemRead])
def get_wishlist(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.scalars(select(WishlistItem).where(WishlistItem.user_id == user.id).order_by(WishlistItem.created_at.desc())).all()
    product_ids = [r.product_id for r in rows]
    products = {}
    if product_ids:
        ps = db.scalars(select(Product).options(selectinload(Product.brand), selectinload(Product.images)).where(Product.id.in_(product_ids))).all()
        products = {p.id: p for p in ps}
    return [{"id": r.id, "product_id": r.product_id, "product": product_mini(products[r.product_id])} for r in rows if r.product_id in products]


@router.post("/wishlist/{product_id}", response_model=list[WishlistItemRead])
def add_wishlist(product_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    product = db.get(Product, product_id)
    if not product or product.status != "published":
        raise HTTPException(status_code=404, detail="Product not found")
    exists = db.scalar(select(WishlistItem).where(WishlistItem.user_id == user.id, WishlistItem.product_id == product_id))
    if not exists:
        db.add(WishlistItem(user_id=user.id, product_id=product_id))
        db.commit()
    return get_wishlist(db, user)


@router.delete("/wishlist/{product_id}", response_model=list[WishlistItemRead])
def remove_wishlist(product_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.scalar(select(WishlistItem).where(WishlistItem.user_id == user.id, WishlistItem.product_id == product_id))
    if item:
        db.delete(item)
        db.commit()
    return get_wishlist(db, user)


@router.get("/addresses", response_model=list[AddressRead])
def list_addresses(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.scalars(select(CustomerAddress).where(CustomerAddress.user_id == user.id).order_by(CustomerAddress.is_default.desc(), CustomerAddress.created_at.desc())).all()


def clear_default_addresses(db: Session, user: User):
    for addr in db.scalars(select(CustomerAddress).where(CustomerAddress.user_id == user.id, CustomerAddress.is_default == True)).all():  # noqa: E712
        addr.is_default = False


@router.post("/addresses", response_model=AddressRead, status_code=status.HTTP_201_CREATED)
def create_address(payload: AddressCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if payload.is_default:
        clear_default_addresses(db, user)
    addr = CustomerAddress(user_id=user.id, **payload.model_dump())
    db.add(addr)
    db.commit()
    db.refresh(addr)
    return addr


@router.patch("/addresses/{address_id}", response_model=AddressRead)
def update_address(address_id: UUID, payload: AddressUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    addr = db.scalar(select(CustomerAddress).where(CustomerAddress.id == address_id, CustomerAddress.user_id == user.id))
    if not addr:
        raise HTTPException(status_code=404, detail="Address not found")
    data = payload.model_dump(exclude_unset=True)
    if data.get("is_default"):
        clear_default_addresses(db, user)
    for key, value in data.items():
        setattr(addr, key, value)
    db.commit()
    db.refresh(addr)
    return addr


@router.delete("/addresses/{address_id}")
def delete_address(address_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    addr = db.scalar(select(CustomerAddress).where(CustomerAddress.id == address_id, CustomerAddress.user_id == user.id))
    if addr:
        db.delete(addr)
        db.commit()
    return {"ok": True}


@router.post("/checkout", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def checkout(payload: CheckoutRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cart = get_or_create_cart(db, user)
    cart_data = cart_payload(db, cart)
    if not cart_data["items"]:
        raise HTTPException(status_code=400, detail="Cart is empty")

    address = None
    if payload.shipping_address_id:
        address = db.scalar(select(CustomerAddress).where(CustomerAddress.id == payload.shipping_address_id, CustomerAddress.user_id == user.id))
        if not address:
            raise HTTPException(status_code=404, detail="Address not found")
    elif payload.address:
        address = CustomerAddress(user_id=user.id, **payload.address.model_dump())
        db.add(address)
        db.flush()
    else:
        address = db.scalar(select(CustomerAddress).where(CustomerAddress.user_id == user.id, CustomerAddress.is_default == True))  # noqa: E712
        if not address:
            raise HTTPException(status_code=400, detail="Shipping address required")

    subtotal = cart_data["subtotal"]
    shipping_total = Decimal(str(payload.shipping_total)) if payload.shipping_total is not None else (Decimal("0.00") if subtotal >= Decimal("70.00") else Decimal("6.95"))
    tax_total = Decimal("0.00")
    grand_total = subtotal + shipping_total + tax_total

    order = Order(
        user_id=user.id,
        email=user.email,
        status="pending_payment",
        payment_status="unpaid",
        fulfillment_status="unfulfilled",
        subtotal=subtotal,
        shipping_total=shipping_total,
        tax_total=tax_total,
        grand_total=grand_total,
        currency=cart_data["currency"],
        shipping_address_id=address.id,
        shipping_name=address.full_name,
        shipping_phone=address.phone,
        shipping_line1=address.line1,
        shipping_line2=address.line2,
        shipping_city=address.city,
        shipping_state=address.state,
        shipping_postal_code=address.postal_code,
        shipping_country=address.country,
        notes=payload.notes,
        shipping_rate_id=payload.shipping_rate_id,
        shipping_carrier=payload.shipping_carrier,
        shipping_service=payload.shipping_service,
    )
    db.add(order)
    db.flush()
    for item in cart_data["items"]:
        db.add(OrderItem(
            order_id=order.id,
            product_id=item["product_id"],
            product_name=item["product"].get("name"),
            quantity=item["quantity"],
            unit_price=item["product"].get("price"),
            line_total=item["line_total"],
        ))
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    return get_order_payload(db, order.id, user)


def get_order_payload(db: Session, order_id: UUID, user: User) -> dict:
    order = db.scalar(select(Order).options(selectinload(Order.items)).where(Order.id == order_id, Order.user_id == user.id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {
        "id": order.id,
        "email": order.email,
        "status": order.status,
        "payment_status": order.payment_status,
        "fulfillment_status": order.fulfillment_status,
        "subtotal": order.subtotal,
        "shipping_total": order.shipping_total,
        "tax_total": order.tax_total,
        "grand_total": order.grand_total,
        "currency": order.currency,
        "shipping_name": order.shipping_name,
        "shipping_line1": order.shipping_line1,
        "shipping_city": order.shipping_city,
        "shipping_state": order.shipping_state,
        "shipping_postal_code": order.shipping_postal_code,
        "shipping_country": order.shipping_country,
        "shipping_rate_id": getattr(order, "shipping_rate_id", None),
        "shipping_carrier": getattr(order, "shipping_carrier", None),
        "shipping_service": getattr(order, "shipping_service", None),
        "tracking_code": getattr(order, "tracking_code", None),
        "notes": order.notes,
        "items": [{"id": i.id, "product_id": i.product_id, "product_name": i.product_name, "quantity": i.quantity, "unit_price": i.unit_price, "line_total": i.line_total} for i in order.items],
    }


@router.get("/orders", response_model=list[OrderRead])
def list_orders(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.scalars(select(Order).where(Order.user_id == user.id).order_by(Order.created_at.desc()).limit(50)).all()
    return [get_order_payload(db, r.id, user) for r in rows]


@router.get("/orders/{order_id}", response_model=OrderRead)
def get_order(order_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return get_order_payload(db, order_id, user)


@router.post("/checkout/start", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def checkout_start(payload: CheckoutRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return checkout(payload, db, user)
