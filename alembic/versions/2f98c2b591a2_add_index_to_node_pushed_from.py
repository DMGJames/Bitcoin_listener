"""Add index to node pushed_from

Revision ID: 2f98c2b591a2
Revises: 370541a1410
Create Date: 2014-12-24 13:45:54.270030

"""

# revision identifiers, used by Alembic.
revision = '2f98c2b591a2'
down_revision = '370541a1410'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_index(op.f('ix_node_pushed_from'), 'node', ['pushed_from'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_node_pushed_from'), table_name='node')
