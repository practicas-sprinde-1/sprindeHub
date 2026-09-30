"""rename environment type column

Revision ID: 9abe4273da70
Revises: a1efed4f891d
Create Date: 2026-09-30 16:33:08.278050

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9abe4273da70'
down_revision: Union[str, Sequence[str], None] = 'a1efed4f891d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
