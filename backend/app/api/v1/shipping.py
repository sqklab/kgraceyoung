from decimal import Decimal
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from app.api.v1.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/shipping", tags=["shipping"])

class ShippingAddressPayload(BaseModel):
    full_name: str = "Grace Customer"
    line1: str
    line2: str | None = None
    city: str
    state: str | None = None
    postal_code: str
    country: str = Field(default="US", min_length=2, max_length=2)

class ShippingRateRequest(BaseModel):
    address: ShippingAddressPayload
    subtotal: Decimal = Decimal("0.00")
    item_count: int = 1

@router.post("/validate-address")
def validate_address(payload: ShippingAddressPayload, _: User = Depends(get_current_user)):
    warnings = []
    if len(payload.postal_code.strip()) < 3:
        warnings.append("Postal code looks short")
    if payload.country.upper() not in {"US", "CA", "MX", "BR", "KR"}:
        warnings.append("Country is supported by manual shipping only in this demo")
    return {"valid": len(warnings) == 0, "normalized": payload.model_dump(), "warnings": warnings}

@router.post("/rates")
def shipping_rates(payload: ShippingRateRequest, _: User = Depends(get_current_user)):
    subtotal = Decimal(payload.subtotal or 0)
    free = subtotal >= Decimal("70.00")
    base = Decimal("0.00") if free else Decimal("6.95")
    return {
        "currency": "USD",
        "rates": [
            {"id": "standard", "provider": "grace", "carrier": "Grace Logistics", "service": "Standard", "amount": float(base), "estimated_days": "4-7", "free_shipping": free},
            {"id": "express", "provider": "grace", "carrier": "Grace Logistics", "service": "Express", "amount": float(Decimal("14.95")), "estimated_days": "2-3", "free_shipping": False},
            {"id": "priority", "provider": "grace", "carrier": "Grace Logistics", "service": "Priority", "amount": float(Decimal("24.95")), "estimated_days": "1-2", "free_shipping": False},
        ]
    }
