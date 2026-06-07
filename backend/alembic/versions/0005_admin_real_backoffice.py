"""admin real backoffice

Revision ID: 0005_admin_real_backoffice
Revises: 0004_real_commerce_ops
Create Date: 2026-06-07
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0005_admin_real_backoffice"
down_revision = "0004_real_commerce_ops"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("products") as batch:
        batch.add_column(sa.Column("sku", sa.String(120), nullable=True))
        batch.add_column(sa.Column("barcode", sa.String(120), nullable=True))
        batch.add_column(sa.Column("compare_at_price", sa.Numeric(12, 2), nullable=True))
        batch.add_column(sa.Column("cost_price", sa.Numeric(12, 2), nullable=True))
        batch.add_column(sa.Column("inventory_quantity", sa.Integer(), nullable=False, server_default="100"))
        batch.add_column(sa.Column("low_stock_threshold", sa.Integer(), nullable=False, server_default="10"))
        batch.add_column(sa.Column("weight_grams", sa.Integer(), nullable=False, server_default="120"))
        batch.add_column(sa.Column("tags", sa.Text(), nullable=True))
        batch.add_column(sa.Column("skin_concerns", sa.Text(), nullable=True))
        batch.add_column(sa.Column("ingredients", sa.Text(), nullable=True))
        batch.add_column(sa.Column("how_to_use", sa.Text(), nullable=True))
    op.create_index("ix_products_sku", "products", ["sku"], unique=False)

    op.create_table(
        "inventory_movements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("variant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("movement_type", sa.String(40), nullable=False, server_default="adjustment"),
        sa.Column("quantity_delta", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reason", sa.String(240), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_inventory_movements_product_id", "inventory_movements", ["product_id"])

    op.create_table(
        "coupons",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("code", sa.String(80), nullable=False),
        sa.Column("name", sa.String(180), nullable=False),
        sa.Column("discount_type", sa.String(32), nullable=False, server_default="percent"),
        sa.Column("discount_value", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("minimum_order_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("usage_limit", sa.Integer(), nullable=True),
        sa.Column("per_customer_limit", sa.Integer(), nullable=True),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_coupons_code", "coupons", ["code"], unique=True)

    op.create_table(
        "coupon_redemptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("coupon_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("coupons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("orders.id"), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_coupon_redemptions_coupon_id", "coupon_redemptions", ["coupon_id"])

    op.create_table(
        "reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("title", sa.String(200), nullable=True),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_reviews_product_id", "reviews", ["product_id"])

    op.create_table(
        "store_settings",
        sa.Column("key", sa.String(120), primary_key=True),
        sa.Column("value", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(160), nullable=False),
        sa.Column("entity_type", sa.String(80), nullable=True),
        sa.Column("entity_id", sa.String(120), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("store_settings")
    op.drop_index("ix_reviews_product_id", table_name="reviews")
    op.drop_table("reviews")
    op.drop_index("ix_coupon_redemptions_coupon_id", table_name="coupon_redemptions")
    op.drop_table("coupon_redemptions")
    op.drop_index("ix_coupons_code", table_name="coupons")
    op.drop_table("coupons")
    op.drop_index("ix_inventory_movements_product_id", table_name="inventory_movements")
    op.drop_table("inventory_movements")
    op.drop_index("ix_products_sku", table_name="products")
    with op.batch_alter_table("products") as batch:
        for col in ["how_to_use", "ingredients", "skin_concerns", "tags", "weight_grams", "low_stock_threshold", "inventory_quantity", "cost_price", "compare_at_price", "barcode", "sku"]:
            batch.drop_column(col)
