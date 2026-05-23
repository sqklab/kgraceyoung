"""add auth roles and admin seed

Revision ID: 0002_auth_roles
Revises: 0001_initial_schema
Create Date: 2026-05-23
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_auth_roles"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(32), nullable=False, server_default="customer"))
    op.create_index("ix_users_role", "users", ["role"])


def downgrade() -> None:
    op.drop_index("ix_users_role", table_name="users")
    op.drop_column("users", "role")
