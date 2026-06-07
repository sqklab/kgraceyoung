from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field


class ProductMini(BaseModel):
    id: UUID
    slug: str
    name: str
    brand: str | None = None
    price: Decimal
    currency: str = "USD"
    image_url: str | None = None


class AddressBase(BaseModel):
    label: str = "Home"
    full_name: str
    phone: str | None = None
    line1: str
    line2: str | None = None
    city: str
    state: str | None = None
    postal_code: str
    country: str = Field(default="US", min_length=2, max_length=2)
    is_default: bool = False


class AddressCreate(AddressBase):
    pass


class AddressUpdate(BaseModel):
    label: str | None = None
    full_name: str | None = None
    phone: str | None = None
    line1: str | None = None
    line2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    is_default: bool | None = None


class AddressRead(AddressBase):
    id: UUID
    class Config:
        from_attributes = True


class CartAddItem(BaseModel):
    product_id: UUID
    quantity: int = Field(default=1, ge=1, le=99)


class CartUpdateItem(BaseModel):
    quantity: int = Field(ge=0, le=99)


class CartItemRead(BaseModel):
    id: UUID
    product_id: UUID
    quantity: int
    product: ProductMini
    line_total: Decimal


class CartRead(BaseModel):
    id: UUID
    currency: str
    items: list[CartItemRead]
    subtotal: Decimal
    item_count: int


class WishlistItemRead(BaseModel):
    id: UUID
    product_id: UUID
    product: ProductMini


class CheckoutRequest(BaseModel):
    shipping_address_id: UUID | None = None
    address: AddressCreate | None = None
    shipping_rate_id: str | None = None
    shipping_carrier: str | None = None
    shipping_service: str | None = None
    shipping_total: Decimal | None = None
    notes: str | None = None


class OrderItemRead(BaseModel):
    id: UUID
    product_id: UUID | None = None
    product_name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class OrderRead(BaseModel):
    id: UUID
    email: str
    status: str
    payment_status: str
    fulfillment_status: str
    subtotal: Decimal
    shipping_total: Decimal
    tax_total: Decimal
    grand_total: Decimal
    currency: str
    shipping_name: str | None = None
    shipping_line1: str | None = None
    shipping_city: str | None = None
    shipping_state: str | None = None
    shipping_postal_code: str | None = None
    shipping_country: str | None = None
    shipping_rate_id: str | None = None
    shipping_carrier: str | None = None
    shipping_service: str | None = None
    tracking_code: str | None = None
    notes: str | None = None
    items: list[OrderItemRead]
