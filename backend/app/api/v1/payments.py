from decimal import Decimal
from uuid import UUID
import hmac, hashlib, json
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.v1.auth import get_current_user
from app.core.config import get_settings
from app.db.session import get_db
from app.models.commerce import Order
from app.models.ops import Payment
from app.models.user import User

router = APIRouter(prefix="/payments", tags=["payments"])
settings = get_settings()

class CheckoutSessionRequest(BaseModel):
    order_id: UUID

@router.post("/stripe/checkout-session")
def create_stripe_checkout_session(payload: CheckoutSessionRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    order = db.scalar(select(Order).where(Order.id == payload.order_id, Order.user_id == user.id))
    if not order:
        raise HTTPException(404, "Order not found")
    if order.payment_status == "paid":
        return {"order_id": str(order.id), "checkout_url": f"{settings.client_origin}/checkout/success?order_id={order.id}", "mock": True}

    # Stripe real mode when STRIPE_SECRET_KEY is present. Otherwise local mock mode.
    checkout_url = f"{settings.client_origin}/checkout/success?order_id={order.id}&mock=1"
    session_id = f"mock_cs_{str(order.id).replace('-', '')[:24]}"
    raw_payload = {"mode": "mock", "reason": "STRIPE_SECRET_KEY not configured"}

    if settings.stripe_secret_key:
        form = {
            "mode": "payment",
            "success_url": f"{settings.client_origin}/checkout/success?order_id={order.id}&session_id={{CHECKOUT_SESSION_ID}}",
            "cancel_url": f"{settings.client_origin}/cart",
            "customer_email": order.email,
            "metadata[order_id]": str(order.id),
            "line_items[0][price_data][currency]": order.currency.lower(),
            "line_items[0][price_data][product_data][name]": f"Grace Young Order {str(order.id)[:8]}",
            "line_items[0][price_data][unit_amount]": int(Decimal(order.grand_total) * 100),
            "line_items[0][quantity]": 1,
        }
        try:
            r = httpx.post("https://api.stripe.com/v1/checkout/sessions", data=form, auth=(settings.stripe_secret_key, ""), timeout=20)
            data = r.json()
            if r.status_code >= 400:
                raise HTTPException(status_code=502, detail=data)
            checkout_url = data["url"]
            session_id = data["id"]
            raw_payload = data
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(502, f"Stripe session failed: {e}")

    order.status = "pending_payment"
    order.payment_status = "pending"
    order.stripe_checkout_session_id = session_id
    payment = Payment(order_id=order.id, provider="stripe", provider_session_id=session_id, status="created", amount=order.grand_total, currency=order.currency, checkout_url=checkout_url, raw_payload=raw_payload)
    db.add(payment); db.commit()
    return {"order_id": str(order.id), "checkout_url": checkout_url, "session_id": session_id, "mock": not bool(settings.stripe_secret_key)}

@router.post("/stripe/mock-paid/{order_id}")
def mock_paid(order_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    order = db.scalar(select(Order).where(Order.id == order_id, Order.user_id == user.id))
    if not order: raise HTTPException(404, "Order not found")
    order.status = "paid"
    order.payment_status = "paid"
    db.commit()
    return {"ok": True, "order_id": str(order.id), "payment_status": order.payment_status}

@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    body = await request.body()
    event = json.loads(body.decode() or "{}")
    event_type = event.get("type")
    obj = event.get("data", {}).get("object", {})
    order_id = obj.get("metadata", {}).get("order_id")
    if event_type == "checkout.session.completed" and order_id:
        order = db.get(Order, order_id)
        if order:
            order.status = "paid"
            order.payment_status = "paid"
            order.stripe_checkout_session_id = obj.get("id")
            db.commit()
    return {"received": True}
