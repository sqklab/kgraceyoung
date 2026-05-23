"""initial grace young schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-23
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('email', sa.String(320), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=True),
        sa.Column('full_name', sa.String(160), nullable=True),
        sa.Column('locale', sa.String(8), nullable=False, server_default='en'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_table('brands',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('slug', sa.String(140), nullable=False, unique=True, index=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('country', sa.String(80), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_table('categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('categories.id'), nullable=True),
        sa.Column('slug', sa.String(140), nullable=False, unique=True, index=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
    )

    op.create_table('products',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('brand_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('brands.id'), nullable=True),
        sa.Column('slug', sa.String(180), nullable=False, unique=True, index=True),
        sa.Column('name', sa.String(240), nullable=False),
        sa.Column('short_description', sa.Text(), nullable=True),
        sa.Column('price', sa.Numeric(12, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='USD'),
        sa.Column('status', sa.String(32), nullable=False, server_default='draft'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_table('product_translations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('locale', sa.String(8), nullable=False),
        sa.Column('name', sa.String(240), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.UniqueConstraint('product_id', 'locale', name='uq_product_translation_locale')
    )

    op.create_table('product_images',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('alt_text', sa.String(240), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
    )

    op.create_table('product_categories',
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True),
    )

    op.create_table('orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('email', sa.String(320), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='pending'),
        sa.Column('subtotal', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('shipping_total', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('tax_total', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('grand_total', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('currency', sa.String(3), nullable=False, server_default='USD'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_table('order_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id'), nullable=True),
        sa.Column('product_name', sa.String(240), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(12, 2), nullable=False),
    )

    op.create_table('reels',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('title', sa.String(240), nullable=False),
        sa.Column('video_url', sa.Text(), nullable=False),
        sa.Column('thumbnail_url', sa.Text(), nullable=True),
        sa.Column('locale', sa.String(8), nullable=False, server_default='en'),
        sa.Column('status', sa.String(32), nullable=False, server_default='draft'),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('like_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    op.create_table('reel_products',
        sa.Column('reel_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('reels.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('start_second', sa.Integer(), nullable=True),
        sa.Column('end_second', sa.Integer(), nullable=True),
        sa.Column('caption', sa.String(240), nullable=True),
    )

    op.create_table('membership_tiers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('code', sa.String(40), nullable=False, unique=True),
        sa.Column('name', sa.String(120), nullable=False),
        sa.Column('annual_spend_min', sa.Numeric(12,2), nullable=False, server_default='0'),
        sa.Column('point_rate', sa.Numeric(5,2), nullable=False, server_default='0'),
    )


def downgrade() -> None:
    op.drop_table('membership_tiers')
    op.drop_table('reel_products')
    op.drop_table('reels')
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('product_categories')
    op.drop_table('product_images')
    op.drop_table('product_translations')
    op.drop_table('products')
    op.drop_table('categories')
    op.drop_table('brands')
    op.drop_table('users')
