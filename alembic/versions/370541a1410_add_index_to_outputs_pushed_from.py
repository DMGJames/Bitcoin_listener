"""Add index to outputs pushed_from

Revision ID: 370541a1410
Revises: 17da451caaf
Create Date: 2014-12-24 13:45:49.390927

"""

# revision identifiers, used by Alembic.
revision = '370541a1410'
down_revision = '17da451caaf'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_index(op.f('ix_outputs_pushed_from'), 'outputs', ['pushed_from'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_outputs_pushed_from'), table_name='outputs')
