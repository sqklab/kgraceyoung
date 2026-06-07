from uuid import UUID
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.api.v1.auth import require_admin
from app.db.session import get_db
from app.models.user import User
from app.models.commerce import Order
from app.models.ops import Shipment

router = APIRouter(prefix="/admin/orders", tags=["admin-orders"])

class OrderStatusPatch(BaseModel):
    status: str | None = None
    payment_status: str | None = None
    fulfillment_status: str | None = None
    tracking_code: str | None = None
    notes: str | None = None

class LabelCreate(BaseModel):
    carrier: str = "Grace Logistics"
    service: str = "Standard"
    tracking_code: str | None = None

def order_payload(order: Order) -> dict:
    return {
        "id": str(order.id),
        "email": order.email,
        "status": order.status,
        "payment_status": order.payment_status,
        "fulfillment_status": order.fulfillment_status,
        "subtotal": float(order.subtotal),
        "shipping_total": float(order.shipping_total),
        "tax_total": float(order.tax_total),
        "grand_total": float(order.grand_total),
        "currency": order.currency,
        "shipping_name": order.shipping_name,
        "shipping_phone": order.shipping_phone,
        "shipping_line1": order.shipping_line1,
        "shipping_line2": order.shipping_line2,
        "shipping_city": order.shipping_city,
        "shipping_state": order.shipping_state,
        "shipping_postal_code": order.shipping_postal_code,
        "shipping_country": order.shipping_country,
        "shipping_carrier": getattr(order, "shipping_carrier", None),
        "shipping_service": getattr(order, "shipping_service", None),
        "tracking_code": getattr(order, "tracking_code", None),
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "items": [{"product_name": i.product_name, "quantity": i.quantity, "unit_price": float(i.unit_price), "line_total": float(i.line_total)} for i in order.items],
    }

@router.get("")
def list_orders(status_filter: str | None = None, limit: int = 50, offset: int = 0, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    stmt = select(Order).options(selectinload(Order.items)).order_by(Order.created_at.desc()).offset(offset).limit(limit)
    if status_filter:
        stmt = stmt.where(Order.status == status_filter)
    rows = db.scalars(stmt).all()
    return [order_payload(o) for o in rows]

@router.get("/{order_id}")
def get_order(order_id: UUID, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    order = db.scalar(select(Order).options(selectinload(Order.items)).where(Order.id == order_id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order_payload(order)

@router.patch("/{order_id}/status")
def update_order_status(order_id: UUID, payload: OrderStatusPatch, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(order, key, value)
    if payload.tracking_code:
        order.fulfillment_status = "shipped"
        order.status = "shipped"
        order.shipped_at = datetime.now(timezone.utc)
    db.commit(); db.refresh(order)
    order = db.scalar(select(Order).options(selectinload(Order.items)).where(Order.id == order.id))
    return order_payload(order)

@router.post("/{order_id}/shipping-label")
def create_shipping_label(order_id: UUID, payload: LabelCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    tracking = payload.tracking_code or f"GY{str(order.id).replace('-', '')[:12].upper()}"
    label_url = f"https://api.kgraceyoung.com/mock-labels/{tracking}.pdf"
    shipment = Shipment(order_id=order.id, provider="manual", carrier=payload.carrier, service=payload.service, rate=order.shipping_total or Decimal("0"), currency=order.currency, tracking_code=tracking, label_url=label_url, status="label_created")
    order.tracking_code = tracking
    order.fulfillment_status = "shipped"
    order.status = "shipped"
    order.shipped_at = datetime.now(timezone.utc)
    db.add(shipment); db.commit()
    return {"order_id": str(order.id), "tracking_code": tracking, "label_url": label_url, "status": order.status}
