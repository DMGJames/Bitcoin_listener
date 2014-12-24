"""Add index to transaction_info pushed_from

Revision ID: 54808a569644
Revises: 182e37fa94bb
Create Date: 2014-12-24 13:46:12.032640

"""

# revision identifiers, used by Alembic.
revision = '54808a569644'
down_revision = '182e37fa94bb'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_index(op.f('ix_transaction_info_pushed_from'), 'transaction_info', ['pushed_from'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_transaction_info_pushed_from'), table_name='transaction_info')
