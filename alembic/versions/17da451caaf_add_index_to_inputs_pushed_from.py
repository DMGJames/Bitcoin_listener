"""Add index to inputs pushed_from

Revision ID: 17da451caaf
Revises: 690688b405
Create Date: 2014-12-24 13:45:44.332640

"""

# revision identifiers, used by Alembic.
revision = '17da451caaf'
down_revision = '690688b405'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_index(op.f('ix_inputs_pushed_from'), 'inputs', ['pushed_from'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_inputs_pushed_from'), table_name='inputs')
