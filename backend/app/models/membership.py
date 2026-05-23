import uuid
from decimal import Decimal
from sqlalchemy import Numeric, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class MembershipTier(Base):
    __tablename__ = "membership_tiers"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    code: Mapped[str] = mapped_column(String(40), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    annual_spend_min: Mapped[Decimal] = mapped_column(Numeric(12,2), default=0)
    point_rate: Mapped[Decimal] = mapped_column(Numeric(5,2), default=0)
