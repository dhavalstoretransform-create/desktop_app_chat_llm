"""create_user_refresh_tokens_table

Revision ID: c3a8f6d7e9b0
Revises: f7ae5e74af7d
Create Date: 2026-08-13 10:24:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3a8f6d7e9b0'
down_revision: Union[str, Sequence[str], None] = 'f7ae5e74af7d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'user_refresh_tokens',
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_user_refresh_tokens_user_id_users'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_user_refresh_tokens'))
    )
    op.create_index(op.f('ix_user_refresh_tokens_id'), 'user_refresh_tokens', ['id'], unique=False)
    op.create_index(op.f('ix_user_refresh_tokens_token'), 'user_refresh_tokens', ['token'], unique=True)
    op.create_index(op.f('ix_user_refresh_tokens_user_id'), 'user_refresh_tokens', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_user_refresh_tokens_user_id'), table_name='user_refresh_tokens')
    op.drop_index(op.f('ix_user_refresh_tokens_token'), table_name='user_refresh_tokens')
    op.drop_index(op.f('ix_user_refresh_tokens_id'), table_name='user_refresh_tokens')
    op.drop_table('user_refresh_tokens')
