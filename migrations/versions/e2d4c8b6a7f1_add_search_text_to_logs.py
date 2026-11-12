"""add search text to logs

Revision ID: e2d4c8b6a7f1
Revises: 9f343894c5b9
Create Date: 2026-10-27 16:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "e2d4c8b6a7f1"
down_revision: Union[str, Sequence[str], None] = "9f343894c5b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "logs",
        sa.Column(
            "search_text",
            sa.String(length=1024),
            server_default="",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("logs", "search_text")
