"""Add transaction model

Revision ID: d6c05b083a7
Revises: 311088515769
Create Date: 2014-06-19 22:51:19.839229

"""

# revision identifiers, used by Alembic.
revision = 'd6c05b083a7'
down_revision = '311088515769'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('transaction',
    sa.Column('txid', sa.String(length=250), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('txid')
    )
    op.create_index(op.f('ix_transaction_created_at'), 'transaction', ['created_at'], unique=False)
    op.create_table('transaction_info',
    sa.Column('txid', sa.String(length=250), nullable=False),
    sa.Column('relayed_from', sa.String(length=250), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('json_string', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('txid', 'relayed_from')
    )
    op.create_index(op.f('ix_transaction_info_created_at'), 'transaction_info', ['created_at'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_transaction_info_created_at'), table_name='transaction_info')
    op.drop_table('transaction_info')
    op.drop_index(op.f('ix_transaction_created_at'), table_name='transaction')
    op.drop_table('transaction')
    ### end Alembic commands ###
