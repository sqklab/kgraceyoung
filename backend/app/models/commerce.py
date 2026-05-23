import uuid
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class CustomerAddress(Base):
    __tablename__ = "customer_addresses"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    label: Mapped[str] = mapped_column(String(80), default="Home")
    full_name: Mapped[str] = mapped_column(String(160))
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    line1: Mapped[str] = mapped_column(String(240))
    line2: Mapped[str | None] = mapped_column(String(240), nullable=True)
    city: Mapped[str] = mapped_column(String(120))
    state: Mapped[str | None] = mapped_column(String(120), nullable=True)
    postal_code: Mapped[str] = mapped_column(String(40))
    country: Mapped[str] = mapped_column(String(2), default="US")
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=text("now()"))


class Cart(Base):
    __tablename__ = "carts"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    created_at = mapped_column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = mapped_column(DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()"))

    items: Mapped[list["CartItem"]] = relationship(back_populates="cart", cascade="all, delete-orphan")


class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = (UniqueConstraint("cart_id", "product_id", name="uq_cart_item_product"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    cart_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("carts.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    created_at = mapped_column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = mapped_column(DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()"))

    cart: Mapped[Cart] = relationship(back_populates="items")


class WishlistItem(Base):
    __tablename__ = "wishlist_items"
    __table_args__ = (UniqueConstraint("user_id", "product_id", name="uq_wishlist_user_product"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), index=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=text("now()"))


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    email: Mapped[str] = mapped_column(String(320))
    status: Mapped[str] = mapped_column(String(32), default="pending")
    payment_status: Mapped[str] = mapped_column(String(32), default="unpaid")
    fulfillment_status: Mapped[str] = mapped_column(String(32), default="unfulfilled")
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12,2), default=0)
    shipping_total: Mapped[Decimal] = mapped_column(Numeric(12,2), default=0)
    tax_total: Mapped[Decimal] = mapped_column(Numeric(12,2), default=0)
    grand_total: Mapped[Decimal] = mapped_column(Numeric(12,2), default=0)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    shipping_address_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("customer_addresses.id"), nullable=True)
    shipping_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    shipping_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    shipping_line1: Mapped[str | None] = mapped_column(String(240), nullable=True)
    shipping_line2: Mapped[str | None] = mapped_column(String(240), nullable=True)
    shipping_city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    shipping_state: Mapped[str | None] = mapped_column(String(120), nullable=True)
    shipping_postal_code: Mapped[str | None] = mapped_column(String(40), nullable=True)
    shipping_country: Mapped[str | None] = mapped_column(String(2), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=text("now()"))

    items: Mapped[list["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"))
    product_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    product_name: Mapped[str] = mapped_column(String(240))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12,2))
    line_total: Mapped[Decimal] = mapped_column(Numeric(12,2), default=0)

    order: Mapped[Order] = relationship(back_populates="items")
