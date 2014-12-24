"""Add index to node_activity pushed_from

Revision ID: 1a14366af1dd
Revises: 2f98c2b591a2
Create Date: 2014-12-24 13:46:01.440637

"""

# revision identifiers, used by Alembic.
revision = '1a14366af1dd'
down_revision = '2f98c2b591a2'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_index(op.f('ix_node_activity_pushed_from'), 'node_activity', ['pushed_from'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_node_activity_pushed_from'), table_name='node_activity')
