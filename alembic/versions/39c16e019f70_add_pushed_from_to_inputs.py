"""Add pushed_from to inputs

Revision ID: 39c16e019f70
Revises: 4c04dffdd007
Create Date: 2014-12-24 13:30:53.805929

"""

# revision identifiers, used by Alembic.
revision = '39c16e019f70'
down_revision = '4c04dffdd007'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('inputs', sa.Column('pushed_from', sa.String(length=25), nullable=True))


def downgrade():
    op.drop_column('inputs', 'pushed_from')
