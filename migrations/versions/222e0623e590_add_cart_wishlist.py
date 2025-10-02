"""add cart & wishlist

Revision ID: 222e0623e590
Revises: cab00a13d2bb
Create Date: 2025-10-02 14:14:02.745552

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '222e0623e590'
down_revision: Union[str, Sequence[str], None] = 'cab00a13d2bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
