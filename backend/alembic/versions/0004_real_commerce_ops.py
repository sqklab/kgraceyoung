"""phase6_9 real commerce operations

Revision ID: 0004_real_commerce_ops
Revises: 0003_phase5_commerce
Create Date: 2026-05-25
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004_real_commerce_ops"
down_revision = "0003_phase5_commerce"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(40), nullable=False, server_default="stripe"),
        sa.Column("provider_session_id", sa.String(255), nullable=True),
        sa.Column("provider_payment_intent_id", sa.String(255), nullable=True),
        sa.Column("status", sa.String(40), nullable=False, server_default="created"),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("checkout_url", sa.Text(), nullable=True),
        sa.Column("raw_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_payments_order_id", "payments", ["order_id"])
    op.create_index("ix_payments_provider_session_id", "payments", ["provider_session_id"])

    op.create_table(
        "shipments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(40), nullable=False, server_default="manual"),
        sa.Column("carrier", sa.String(80), nullable=True),
        sa.Column("service", sa.String(120), nullable=True),
        sa.Column("rate", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("tracking_code", sa.String(120), nullable=True),
        sa.Column("label_url", sa.Text(), nullable=True),
        sa.Column("status", sa.String(40), nullable=False, server_default="rate_selected"),
        sa.Column("raw_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_shipments_order_id", "shipments", ["order_id"])

    op.create_table(
        "banners",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("placement", sa.String(80), nullable=False, server_default="home_hero"),
        sa.Column("title", sa.String(240), nullable=False),
        sa.Column("subtitle", sa.String(320), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=False),
        sa.Column("link_url", sa.Text(), nullable=True),
        sa.Column("button_label", sa.String(80), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_banners_placement", "banners", ["placement"])

    op.add_column("orders", sa.Column("shipping_rate_id", sa.String(120), nullable=True))
    op.add_column("orders", sa.Column("shipping_carrier", sa.String(80), nullable=True))
    op.add_column("orders", sa.Column("shipping_service", sa.String(120), nullable=True))
    op.add_column("orders", sa.Column("stripe_checkout_session_id", sa.String(255), nullable=True))
    op.add_column("orders", sa.Column("tracking_code", sa.String(120), nullable=True))
    op.add_column("orders", sa.Column("shipped_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    for col in ["shipped_at", "tracking_code", "stripe_checkout_session_id", "shipping_service", "shipping_carrier", "shipping_rate_id"]:
        op.drop_column("orders", col)
    op.drop_index("ix_banners_placement", table_name="banners")
    op.drop_table("banners")
    op.drop_index("ix_shipments_order_id", table_name="shipments")
    op.drop_table("shipments")
    op.drop_index("ix_payments_provider_session_id", table_name="payments")
    op.drop_index("ix_payments_order_id", table_name="payments")
    op.drop_table("payments")
