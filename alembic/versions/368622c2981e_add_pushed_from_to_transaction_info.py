"""Add pushed_from to transaction_info

Revision ID: 368622c2981e
Revises: 430797e95650
Create Date: 2014-12-24 13:31:20.587923

"""

# revision identifiers, used by Alembic.
revision = '368622c2981e'
down_revision = '430797e95650'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('transaction_info', sa.Column('pushed_from', sa.String(length=25), nullable=True))


def downgrade():
    op.drop_column('transaction_info', 'pushed_from')
