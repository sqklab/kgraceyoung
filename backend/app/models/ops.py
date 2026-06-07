import uuid
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    provider: Mapped[str] = mapped_column(String(40), default="stripe")
    provider_session_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    provider_payment_intent_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="created")
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    checkout_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = mapped_column(DateTime(timezone=True), server_default=text("now()"), onupdate=text("now()"))


class Shipment(Base):
    __tablename__ = "shipments"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    provider: Mapped[str] = mapped_column(String(40), default="manual")
    carrier: Mapped[str | None] = mapped_column(String(80), nullable=True)
    service: Mapped[str | None] = mapped_column(String(120), nullable=True)
    rate: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    tracking_code: Mapped[str | None] = mapped_column(String(120), nullable=True)
    label_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="rate_selected")
    raw_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=text("now()"))


class Banner(Base):
    __tablename__ = "banners"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    placement: Mapped[str] = mapped_column(String(80), default="home_hero", index=True)
    title: Mapped[str] = mapped_column(String(240))
    subtitle: Mapped[str | None] = mapped_column(String(320), nullable=True)
    image_url: Mapped[str] = mapped_column(Text)
    link_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    button_label: Mapped[str | None] = mapped_column(String(80), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=text("now()"))
