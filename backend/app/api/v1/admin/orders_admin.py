from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.api.v1.auth import require_admin
from app.db.session import get_db
from app.models.user import User
from app.models.commerce import Order

router = APIRouter(prefix="/admin/orders", tags=["admin-orders"])


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
        "shipping_country": order.shipping_country,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "items": [{"product_name": i.product_name, "quantity": i.quantity, "unit_price": float(i.unit_price), "line_total": float(i.line_total)} for i in order.items],
    }


@router.get("")
def list_orders(limit: int = 50, offset: int = 0, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    rows = db.scalars(select(Order).options(selectinload(Order.items)).order_by(Order.created_at.desc()).offset(offset).limit(limit)).all()
    return [order_payload(o) for o in rows]


@router.get("/{order_id}")
def get_order(order_id: UUID, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    order = db.scalar(select(Order).options(selectinload(Order.items)).where(Order.id == order_id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order_payload(order)
