"""Add pushed_from to outputs

Revision ID: 4211b886259d
Revises: 39c16e019f70
Create Date: 2014-12-24 13:30:57.411010

"""

# revision identifiers, used by Alembic.
revision = '4211b886259d'
down_revision = '39c16e019f70'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('outputs', sa.Column('pushed_from', sa.String(length=25), nullable=True))


def downgrade():
    op.drop_column('outputs', 'pushed_from')
