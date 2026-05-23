"""phase5 cart wishlist addresses and order checkout

Revision ID: 0003_phase5_commerce
Revises: 0002_auth_roles
Create Date: 2026-05-23
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_phase5_commerce"
down_revision = "0002_auth_roles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "customer_addresses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("label", sa.String(80), nullable=False, server_default="Home"),
        sa.Column("full_name", sa.String(160), nullable=False),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("line1", sa.String(240), nullable=False),
        sa.Column("line2", sa.String(240), nullable=True),
        sa.Column("city", sa.String(120), nullable=False),
        sa.Column("state", sa.String(120), nullable=True),
        sa.Column("postal_code", sa.String(40), nullable=False),
        sa.Column("country", sa.String(2), nullable=False, server_default="US"),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_customer_addresses_user_id", "customer_addresses", ["user_id"])

    op.create_table(
        "carts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_carts_user_id", "carts", ["user_id"])

    op.create_table(
        "cart_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("cart_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("carts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("cart_id", "product_id", name="uq_cart_item_product"),
    )
    op.create_index("ix_cart_items_cart_id", "cart_items", ["cart_id"])
    op.create_index("ix_cart_items_product_id", "cart_items", ["product_id"])

    op.create_table(
        "wishlist_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("user_id", "product_id", name="uq_wishlist_user_product"),
    )
    op.create_index("ix_wishlist_items_user_id", "wishlist_items", ["user_id"])
    op.create_index("ix_wishlist_items_product_id", "wishlist_items", ["product_id"])

    op.add_column("orders", sa.Column("payment_status", sa.String(32), nullable=False, server_default="unpaid"))
    op.add_column("orders", sa.Column("fulfillment_status", sa.String(32), nullable=False, server_default="unfulfilled"))
    op.add_column("orders", sa.Column("shipping_address_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customer_addresses.id"), nullable=True))
    op.add_column("orders", sa.Column("shipping_name", sa.String(160), nullable=True))
    op.add_column("orders", sa.Column("shipping_phone", sa.String(50), nullable=True))
    op.add_column("orders", sa.Column("shipping_line1", sa.String(240), nullable=True))
    op.add_column("orders", sa.Column("shipping_line2", sa.String(240), nullable=True))
    op.add_column("orders", sa.Column("shipping_city", sa.String(120), nullable=True))
    op.add_column("orders", sa.Column("shipping_state", sa.String(120), nullable=True))
    op.add_column("orders", sa.Column("shipping_postal_code", sa.String(40), nullable=True))
    op.add_column("orders", sa.Column("shipping_country", sa.String(2), nullable=True))
    op.add_column("orders", sa.Column("notes", sa.Text(), nullable=True))
    op.add_column("order_items", sa.Column("line_total", sa.Numeric(12, 2), nullable=False, server_default="0"))


def downgrade() -> None:
    op.drop_column("order_items", "line_total")
    for col in ["notes", "shipping_country", "shipping_postal_code", "shipping_state", "shipping_city", "shipping_line2", "shipping_line1", "shipping_phone", "shipping_name", "shipping_address_id", "fulfillment_status", "payment_status"]:
        op.drop_column("orders", col)
    op.drop_index("ix_wishlist_items_product_id", table_name="wishlist_items")
    op.drop_index("ix_wishlist_items_user_id", table_name="wishlist_items")
    op.drop_table("wishlist_items")
    op.drop_index("ix_cart_items_product_id", table_name="cart_items")
    op.drop_index("ix_cart_items_cart_id", table_name="cart_items")
    op.drop_table("cart_items")
    op.drop_index("ix_carts_user_id", table_name="carts")
    op.drop_table("carts")
    op.drop_index("ix_customer_addresses_user_id", table_name="customer_addresses")
    op.drop_table("customer_addresses")
