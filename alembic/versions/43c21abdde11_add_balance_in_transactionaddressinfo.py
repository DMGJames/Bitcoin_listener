"""Add balance in TransactionAddressInfo

Revision ID: 43c21abdde11
Revises: 2b4163692c62
Create Date: 2014-07-08 18:05:52.610369

"""

# revision identifiers, used by Alembic.
revision = '43c21abdde11'
down_revision = '2b4163692c62'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('transaction_address_info', sa.Column('balance', sa.Numeric(precision=15, scale=8), nullable=True))
    op.create_index(op.f('ix_transaction_address_info_balance'), 'transaction_address_info', ['balance'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_transaction_address_info_balance'), table_name='transaction_address_info')
    op.drop_column('transaction_address_info', 'balance')
    ### end Alembic commands ###
