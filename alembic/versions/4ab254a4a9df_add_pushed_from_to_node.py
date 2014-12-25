"""Add pushed_from to node

Revision ID: 4ab254a4a9df
Revises: 4211b886259d
Create Date: 2014-12-24 13:31:04.141556

"""

# revision identifiers, used by Alembic.
revision = '4ab254a4a9df'
down_revision = '4211b886259d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('node', sa.Column('pushed_from', sa.String(length=25), nullable=True))


def downgrade():
    op.drop_column('node', 'pushed_from')
