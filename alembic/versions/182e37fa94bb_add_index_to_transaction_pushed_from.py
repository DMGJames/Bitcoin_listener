"""Add index to transaction pushed_from

Revision ID: 182e37fa94bb
Revises: 1a14366af1dd
Create Date: 2014-12-24 13:46:08.288520

"""

# revision identifiers, used by Alembic.
revision = '182e37fa94bb'
down_revision = '1a14366af1dd'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_index(op.f('ix_transaction_pushed_from'), 'transaction', ['pushed_from'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_transaction_pushed_from'), table_name='transaction')
