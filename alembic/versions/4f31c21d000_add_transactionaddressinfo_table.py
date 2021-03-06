"""Add TransactionAddressInfo table

Revision ID: 4f31c21d000
Revises: 4a339e1591c4
Create Date: 2014-07-08 14:29:21.339031

"""

# revision identifiers, used by Alembic.
revision = '4f31c21d000'
down_revision = '4a339e1591c4'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('transaction_address_info',
    sa.Column('address', sa.String(length=250), nullable=False),
    sa.Column('in_value', sa.Numeric(precision=15, scale=8), nullable=True),
    sa.Column('out_value', sa.Numeric(precision=15, scale=8), nullable=True),
    sa.Column('in_count', sa.Integer(), nullable=True),
    sa.Column('out_count', sa.Integer(), nullable=True),
    sa.Column('coinbase', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('address')
    )
    op.create_index(op.f('ix_transaction_address_info_coinbase'), 'transaction_address_info', ['coinbase'], unique=False)
    op.create_index(op.f('ix_transaction_address_info_in_count'), 'transaction_address_info', ['in_count'], unique=False)
    op.create_index(op.f('ix_transaction_address_info_in_value'), 'transaction_address_info', ['in_value'], unique=False)
    op.create_index(op.f('ix_transaction_address_info_out_count'), 'transaction_address_info', ['out_count'], unique=False)
    op.create_index(op.f('ix_transaction_address_info_out_value'), 'transaction_address_info', ['out_value'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_transaction_address_info_out_value'), table_name='transaction_address_info')
    op.drop_index(op.f('ix_transaction_address_info_out_count'), table_name='transaction_address_info')
    op.drop_index(op.f('ix_transaction_address_info_in_value'), table_name='transaction_address_info')
    op.drop_index(op.f('ix_transaction_address_info_in_count'), table_name='transaction_address_info')
    op.drop_index(op.f('ix_transaction_address_info_coinbase'), table_name='transaction_address_info')
    op.drop_table('transaction_address_info')
    ### end Alembic commands ###
