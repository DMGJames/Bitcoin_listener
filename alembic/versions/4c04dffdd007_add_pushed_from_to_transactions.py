"""Add pushed_from to transactions

Revision ID: 4c04dffdd007
Revises: 567cd0ff068a
Create Date: 2014-12-24 13:30:49.189214

"""

# revision identifiers, used by Alembic.
revision = '4c04dffdd007'
down_revision = '567cd0ff068a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('transactions', sa.Column('pushed_from', sa.String(length=25), nullable=True))


def downgrade():
    op.drop_column('transactions', 'pushed_from')
