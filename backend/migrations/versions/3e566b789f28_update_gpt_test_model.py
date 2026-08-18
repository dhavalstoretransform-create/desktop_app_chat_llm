"""update_gpt_test_model

Revision ID: 3e566b789f28
Revises: f070b507c09b
Create Date: 2026-08-18 16:20:39.326435

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e566b789f28'
down_revision: Union[str, Sequence[str], None] = 'f070b507c09b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("UPDATE ai_models SET code = 'gpt-3.5-turbo', name = 'GPT-3.5 Turbo' WHERE code = 'gpt-test'")


def downgrade() -> None:
    """Downgrade schema."""
    pass
