"""Add index to transactions pushed_from

Revision ID: 690688b405
Revises: 56191088ff69
Create Date: 2014-12-24 13:45:38.649952

"""

# revision identifiers, used by Alembic.
revision = '690688b405'
down_revision = '56191088ff69'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_index(op.f('ix_transactions_pushed_from'), 'transactions', ['pushed_from'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_transactions_pushed_from'), table_name='transactions')
