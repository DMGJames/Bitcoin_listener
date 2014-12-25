"""Add pushed_from to node_activity

Revision ID: 126f347bc599
Revises: 4ab254a4a9df
Create Date: 2014-12-24 13:31:10.638048

"""

# revision identifiers, used by Alembic.
revision = '126f347bc599'
down_revision = '4ab254a4a9df'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('node_activity', sa.Column('pushed_from', sa.String(length=25), nullable=True))


def downgrade():
    op.drop_column('node_activity', 'pushed_from')
