"""Add transaction address and transaction spending

Revision ID: 4a339e1591c4
Revises: 274183f65b9b
Create Date: 2014-07-03 21:45:30.518396

"""

# revision identifiers, used by Alembic.
revision = '4a339e1591c4'
down_revision = '274183f65b9b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('transaction_address',
    sa.Column('txid', sa.String(length=250), nullable=False),
    sa.Column('address', sa.String(length=250), nullable=False),
    sa.Column('vout_index', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('block_hash', sa.String(length=250), nullable=True),
    sa.Column('block_height', sa.Integer(), nullable=True),
    sa.Column('value', sa.Numeric(precision=15, scale=8), nullable=True),
    sa.Column('is_from_coinbase', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('txid', 'address', 'vout_index')
    )
    op.create_index(op.f('ix_transaction_address_block_hash'), 'transaction_address', ['block_hash'], unique=False)
    op.create_index(op.f('ix_transaction_address_block_height'), 'transaction_address', ['block_height'], unique=False)
    op.create_index(op.f('ix_transaction_address_is_from_coinbase'), 'transaction_address', ['is_from_coinbase'], unique=False)
    op.create_index(op.f('ix_transaction_address_value'), 'transaction_address', ['value'], unique=False)
    op.create_table('transaction_spending',
    sa.Column('txid', sa.String(length=250), nullable=False),
    sa.Column('input_txid', sa.String(length=250), nullable=False),
    sa.Column('vout_index', sa.Integer(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('txid', 'input_txid', 'vout_index')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transaction_spending')
    op.drop_index(op.f('ix_transaction_address_value'), table_name='transaction_address')
    op.drop_index(op.f('ix_transaction_address_is_from_coinbase'), table_name='transaction_address')
    op.drop_index(op.f('ix_transaction_address_block_height'), table_name='transaction_address')
    op.drop_index(op.f('ix_transaction_address_block_hash'), table_name='transaction_address')
    op.drop_table('transaction_address')
    ### end Alembic commands ###
