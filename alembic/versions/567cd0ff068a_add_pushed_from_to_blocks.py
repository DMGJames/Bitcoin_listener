"""Add pushed_from to blocks

Revision ID: 567cd0ff068a
Revises: 4eb83a33e8f1
Create Date: 2014-12-24 13:29:57.604579

"""

# revision identifiers, used by Alembic.
revision = '567cd0ff068a'
down_revision = '4eb83a33e8f1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('blocks', sa.Column('pushed_from', sa.String(length=25), nullable=True))


def downgrade():
    op.drop_column('blocks', 'pushed_from')
