"""Rename legacy tag table and add optional unique MAC and IP.

Revision ID: a3b7d92c6f10
Revises: 8109e2dfaec4
"""
from alembic import op
import sqlalchemy as sa


revision = "a3b7d92c6f10"
down_revision = "8109e2dfaec4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table("client_tags", "tags")
    op.add_column("tags", sa.Column("mac", sa.String(255), nullable=True))
    op.add_column("tags", sa.Column("ip", sa.String(255), nullable=True))
    op.create_unique_constraint("uq_tags_mac", "tags", ["mac"])
    op.create_unique_constraint("uq_tags_ip", "tags", ["ip"])


def downgrade() -> None:
    op.drop_constraint("uq_tags_ip", "tags", type_="unique")
    op.drop_constraint("uq_tags_mac", "tags", type_="unique")
    op.drop_column("tags", "ip")
    op.drop_column("tags", "mac")
    op.rename_table("tags", "client_tags")
