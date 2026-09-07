"""RBAC User-Bidder Linkage

Revision ID: 003_rbac_user_bidder_link
Revises: 002_phase5_models
Create Date: 2026-09-07 11:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '003_rbac_user_bidder_link'
down_revision: Union[str, None] = '002_phase5_models'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add bidder_id column to users table
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('bidder_id', sa.String(length=36), nullable=True))
        batch_op.create_index('ix_users_bidder_id', ['bidder_id'])

    # Add user_id column to bidders table
    with op.batch_alter_table('bidders') as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.String(length=36), nullable=True))
        batch_op.create_index('ix_bidders_user_id', ['user_id'])


def downgrade() -> None:
    with op.batch_alter_table('bidders') as batch_op:
        batch_op.drop_index('ix_bidders_user_id')
        batch_op.drop_column('user_id')

    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_index('ix_users_bidder_id')
        batch_op.drop_column('bidder_id')
