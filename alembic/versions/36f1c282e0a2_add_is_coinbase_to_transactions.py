"""Add is_coinbase to transactions

Revision ID: 36f1c282e0a2
Revises: 14fbd693ba5b
Create Date: 2014-12-10 15:58:43.715020

"""

# revision identifiers, used by Alembic.
revision = '36f1c282e0a2'
down_revision = '14fbd693ba5b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('transactions', sa.Column('is_coinbase', sa.Boolean(), nullable=True))
    op.create_index(op.f('ix_transactions_is_coinbase'), 'transactions', ['is_coinbase'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_transactions_is_coinbase'), table_name='transactions')
    op.drop_column('transactions', 'is_coinbase')
    ### end Alembic commands ###