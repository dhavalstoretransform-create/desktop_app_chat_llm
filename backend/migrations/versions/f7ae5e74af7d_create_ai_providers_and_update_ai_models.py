"""create_ai_providers_and_update_ai_models

Revision ID: f7ae5e74af7d
Revises: 89b0ce83e811
Create Date: 2026-08-12 18:03:18.128814

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7ae5e74af7d'
down_revision: Union[str, Sequence[str], None] = '89b0ce83e811'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('ai_providers',
    sa.Column('code', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_ai_providers'))
    )
    op.create_index(op.f('ix_ai_providers_code'), 'ai_providers', ['code'], unique=True)
    op.create_index(op.f('ix_ai_providers_id'), 'ai_providers', ['id'], unique=False)
    op.create_index(op.f('ix_ai_providers_is_active'), 'ai_providers', ['is_active'], unique=False)
    op.create_index(op.f('ix_ai_providers_name'), 'ai_providers', ['name'], unique=False)

    with op.batch_alter_table('ai_models', schema=None) as batch_op:
        batch_op.add_column(sa.Column('provider_id', sa.UUID(), nullable=False))
        batch_op.add_column(sa.Column('code', sa.String(length=50), nullable=False))
        batch_op.add_column(sa.Column('name', sa.String(length=100), nullable=False))
        batch_op.add_column(sa.Column('description', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('input_token_price', sa.Numeric(precision=10, scale=4), nullable=False))
        batch_op.add_column(sa.Column('output_token_price', sa.Numeric(precision=10, scale=4), nullable=False))
        batch_op.add_column(sa.Column('max_output_tokens', sa.Integer(), nullable=False))
        batch_op.drop_index(op.f('ix_ai_models_model_name'))
        batch_op.create_index(op.f('ix_ai_models_code'), ['code'], unique=False)
        batch_op.create_index(op.f('ix_ai_models_is_active'), ['is_active'], unique=False)
        batch_op.create_index(op.f('ix_ai_models_name'), ['name'], unique=False)
        batch_op.create_index(op.f('ix_ai_models_provider_id'), ['provider_id'], unique=False)
        batch_op.create_unique_constraint('uq_ai_models_provider_id_code', ['provider_id', 'code'])
        batch_op.create_foreign_key(op.f('fk_ai_models_provider_id_ai_providers'), 'ai_providers', ['provider_id'], ['id'], ondelete='RESTRICT')
        batch_op.create_check_constraint('ck_ai_models_check_input_token_price_non_negative', 'input_token_price >= 0')
        batch_op.create_check_constraint('ck_ai_models_check_max_context_tokens_positive', 'max_context_tokens > 0')
        batch_op.create_check_constraint('ck_ai_models_check_max_output_tokens_positive', 'max_output_tokens > 0')
        batch_op.create_check_constraint('ck_ai_models_check_output_token_price_non_negative', 'output_token_price >= 0')
        batch_op.drop_column('provider')
        batch_op.drop_column('model_version')
        batch_op.drop_column('model_name')
        batch_op.drop_column('output_cost_per_million')
        batch_op.drop_column('created_by')
        batch_op.drop_column('model_type')
        batch_op.drop_column('input_cost_per_million')


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('ai_models', schema=None) as batch_op:
        batch_op.add_column(sa.Column('input_cost_per_million', sa.NUMERIC(precision=10, scale=4), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('model_type', sa.VARCHAR(length=50), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('created_by', sa.UUID(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('output_cost_per_million', sa.NUMERIC(precision=10, scale=4), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('model_name', sa.VARCHAR(length=100), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('model_version', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('provider', sa.VARCHAR(length=100), autoincrement=False, nullable=False))
        batch_op.drop_constraint('ck_ai_models_check_output_token_price_non_negative', type_='check')
        batch_op.drop_constraint('ck_ai_models_check_max_output_tokens_positive', type_='check')
        batch_op.drop_constraint('ck_ai_models_check_max_context_tokens_positive', type_='check')
        batch_op.drop_constraint('ck_ai_models_check_input_token_price_non_negative', type_='check')
        batch_op.drop_constraint(op.f('fk_ai_models_provider_id_ai_providers'), type_='foreignkey')
        batch_op.drop_constraint('uq_ai_models_provider_id_code', type_='unique')
        batch_op.drop_index(op.f('ix_ai_models_provider_id'))
        batch_op.drop_index(op.f('ix_ai_models_name'))
        batch_op.drop_index(op.f('ix_ai_models_is_active'))
        batch_op.drop_index(op.f('ix_ai_models_code'))
        batch_op.create_index(op.f('ix_ai_models_model_name'), ['model_name'], unique=True)
        batch_op.drop_column('max_output_tokens')
        batch_op.drop_column('output_token_price')
        batch_op.drop_column('input_token_price')
        batch_op.drop_column('description')
        batch_op.drop_column('name')
        batch_op.drop_column('code')
        batch_op.drop_column('provider_id')

    op.drop_index(op.f('ix_ai_providers_name'), table_name='ai_providers')
    op.drop_index(op.f('ix_ai_providers_is_active'), table_name='ai_providers')
    op.drop_index(op.f('ix_ai_providers_id'), table_name='ai_providers')
    op.drop_index(op.f('ix_ai_providers_code'), table_name='ai_providers')
    op.drop_table('ai_providers')
