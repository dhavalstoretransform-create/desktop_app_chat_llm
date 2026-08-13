"""make_user_role_dept_nullable

Revision ID: b885893e919c
Revises: c3a8f6d7e9b0
Create Date: 2026-08-13 17:13:05.894160

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b885893e919c'
down_revision: Union[str, Sequence[str], None] = 'c3a8f6d7e9b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('role_id',
                   existing_type=sa.UUID(),
                   nullable=True)
        batch_op.alter_column('department_id',
                   existing_type=sa.UUID(),
                   nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('department_id',
                   existing_type=sa.UUID(),
                   nullable=False)
        batch_op.alter_column('role_id',
                   existing_type=sa.UUID(),
                   nullable=False)
