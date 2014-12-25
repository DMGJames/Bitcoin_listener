"""Add index to blocks pushed_from

Revision ID: 56191088ff69
Revises: 368622c2981e
Create Date: 2014-12-24 13:45:13.950836

"""

# revision identifiers, used by Alembic.
revision = '56191088ff69'
down_revision = '368622c2981e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_index(op.f('ix_blocks_pushed_from'), 'blocks', ['pushed_from'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_blocks_pushed_from'), table_name='blocks')
