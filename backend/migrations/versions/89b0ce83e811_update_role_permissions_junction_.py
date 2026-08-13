"""update_role_permissions_junction_constraints

Revision ID: 89b0ce83e811
Revises: 00b0eb8a6bf4
Create Date: 2026-08-12 11:41:25.301160

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '89b0ce83e811'
down_revision: Union[str, Sequence[str], None] = '00b0eb8a6bf4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('role_permissions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))
        batch_op.drop_constraint(op.f('fk_role_permissions_role_id_roles'), type_='foreignkey')
        batch_op.drop_constraint(op.f('fk_role_permissions_permission_id_permissions'), type_='foreignkey')
        batch_op.create_foreign_key(op.f('fk_role_permissions_permission_id_permissions'), 'permissions', ['permission_id'], ['id'], ondelete='RESTRICT')
        batch_op.create_foreign_key(op.f('fk_role_permissions_role_id_roles'), 'roles', ['role_id'], ['id'], ondelete='RESTRICT')


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('role_permissions', schema=None) as batch_op:
        batch_op.drop_constraint(op.f('fk_role_permissions_role_id_roles'), type_='foreignkey')
        batch_op.drop_constraint(op.f('fk_role_permissions_permission_id_permissions'), type_='foreignkey')
        batch_op.create_foreign_key(op.f('fk_role_permissions_permission_id_permissions'), 'permissions', ['permission_id'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key(op.f('fk_role_permissions_role_id_roles'), 'roles', ['role_id'], ['id'], ondelete='CASCADE')
        batch_op.drop_column('created_at')
