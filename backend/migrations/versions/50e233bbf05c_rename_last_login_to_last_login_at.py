"""rename_last_login_to_last_login_at

Revision ID: 50e233bbf05c
Revises: 00ec132e0f60
Create Date: 2026-08-12 10:59:37.354116

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50e233bbf05c'
down_revision: Union[str, Sequence[str], None] = '00ec132e0f60'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('users', 'last_login', new_column_name='last_login_at')


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('users', 'last_login_at', new_column_name='last_login')

