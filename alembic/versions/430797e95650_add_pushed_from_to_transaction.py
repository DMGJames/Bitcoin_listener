"""Add pushed_from to transaction

Revision ID: 430797e95650
Revises: 126f347bc599
Create Date: 2014-12-24 13:31:18.060173

"""

# revision identifiers, used by Alembic.
revision = '430797e95650'
down_revision = '126f347bc599'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('transaction', sa.Column('pushed_from', sa.String(length=25), nullable=True))


def downgrade():
    op.drop_column('transaction', 'pushed_from')
