"""Remove global favorite columns from clients and projects.

Revision ID: 3d8e7b6c5a4f
Revises: fb7a10cd9df8
Create Date: 2026-11-04
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "3d8e7b6c5a4f"
down_revision: Union[str, Sequence[str], None] = "fb7a10cd9df8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("projects", "is_favorite")
    op.drop_column("clients", "is_favorite")


def downgrade() -> None:
    op.add_column(
        "clients",
        sa.Column("is_favorite", sa.Boolean(), server_default="0", nullable=False),
    )
    op.add_column(
        "projects",
        sa.Column("is_favorite", sa.Boolean(), server_default="0", nullable=False),
    )
