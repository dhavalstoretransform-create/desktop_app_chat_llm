"""make_audit_log_user_id_nullable

Revision ID: ff356db00e3b
Revises: b885893e919c
Create Date: 2026-08-13 17:57:20.324273

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff356db00e3b'
down_revision: Union[str, Sequence[str], None] = 'b885893e919c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('audit_logs') as batch_op:
        batch_op.alter_column('user_id',
                   existing_type=sa.UUID(),
                   nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('audit_logs') as batch_op:
        batch_op.alter_column('user_id',
                   existing_type=sa.UUID(),
                   nullable=False)
