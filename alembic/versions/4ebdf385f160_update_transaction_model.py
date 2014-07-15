"""Update transaction model

Revision ID: 4ebdf385f160
Revises: 107ed5cddfa
Create Date: 2014-07-09 15:11:42.201341

"""

# revision identifiers, used by Alembic.
revision = '4ebdf385f160'
down_revision = '107ed5cddfa'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('transaction_vout',
    sa.Column('txid', sa.String(length=250), nullable=False),
    sa.Column('offset', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('address', sa.String(length=250), nullable=True),
    sa.Column('block_hash', sa.String(length=250), nullable=True),
    sa.Column('block_height', sa.Integer(), nullable=True),
    sa.Column('value', sa.Numeric(precision=15, scale=8), nullable=True),
    sa.Column('is_from_coinbase', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('txid', 'offset')
    )
    op.create_index(op.f('ix_transaction_vout_address'), 'transaction_vout', ['address'], unique=False)
    op.create_index(op.f('ix_transaction_vout_block_hash'), 'transaction_vout', ['block_hash'], unique=False)
    op.create_index(op.f('ix_transaction_vout_block_height'), 'transaction_vout', ['block_height'], unique=False)
    op.create_index(op.f('ix_transaction_vout_is_from_coinbase'), 'transaction_vout', ['is_from_coinbase'], unique=False)
    op.create_index(op.f('ix_transaction_vout_offset'), 'transaction_vout', ['offset'], unique=False)
    op.create_index(op.f('ix_transaction_vout_txid'), 'transaction_vout', ['txid'], unique=False)
    op.create_index(op.f('ix_transaction_vout_value'), 'transaction_vout', ['value'], unique=False)
    op.create_table('transaction_vin',
    sa.Column('txid', sa.String(length=250), nullable=False),
    sa.Column('offset', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('output_txid', sa.String(length=250), nullable=True),
    sa.Column('vout_offset', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('txid', 'offset')
    )
    op.create_index('ix_transaction_input_output_txid_and_vout_index', 'transaction_vin', ['output_txid', 'vout_offset'], unique=False)
    op.create_index(op.f('ix_transaction_vin_offset'), 'transaction_vin', ['offset'], unique=False)
    op.create_index(op.f('ix_transaction_vin_output_txid'), 'transaction_vin', ['output_txid'], unique=False)
    op.create_index(op.f('ix_transaction_vin_txid'), 'transaction_vin', ['txid'], unique=False)
    op.create_index(op.f('ix_transaction_vin_vout_offset'), 'transaction_vin', ['vout_offset'], unique=False)
    op.drop_table('transaction_address')
    op.drop_table('transaction_spending')
    op.create_index(op.f('ix_node_address'), 'node', ['address'], unique=False)
    op.create_index(op.f('ix_node_activity_id'), 'node_activity', ['id'], unique=False)
    op.add_column('transaction', sa.Column('block_hash', sa.String(length=250), nullable=True))
    op.create_index(op.f('ix_transaction_block_hash'), 'transaction', ['block_hash'], unique=False)
    op.create_index(op.f('ix_transaction_txid'), 'transaction', ['txid'], unique=False)
    op.create_index(op.f('ix_transaction_info_relayed_from'), 'transaction_info', ['relayed_from'], unique=False)
    op.create_index(op.f('ix_transaction_info_txid'), 'transaction_info', ['txid'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_transaction_info_txid'), table_name='transaction_info')
    op.drop_index(op.f('ix_transaction_info_relayed_from'), table_name='transaction_info')
    op.drop_index(op.f('ix_transaction_txid'), table_name='transaction')
    op.drop_index(op.f('ix_transaction_block_hash'), table_name='transaction')
    op.drop_column('transaction', 'block_hash')
    op.drop_index(op.f('ix_node_activity_id'), table_name='node_activity')
    op.drop_index(op.f('ix_node_address'), table_name='node')
    op.create_table('transaction_spending',
    sa.Column('txid', mysql.VARCHAR(collation=u'utf8_unicode_ci', length=250), nullable=False),
    sa.Column('input_txid', mysql.VARCHAR(collation=u'utf8_unicode_ci', length=250), nullable=False),
    sa.Column('vout_index', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('txid', 'input_txid', 'vout_index'),
    mysql_collate=u'utf8_unicode_ci',
    mysql_default_charset=u'utf8',
    mysql_engine=u'InnoDB'
    )
    op.create_table('transaction_address',
    sa.Column('txid', mysql.VARCHAR(collation=u'utf8_unicode_ci', length=250), nullable=False),
    sa.Column('address', mysql.VARCHAR(collation=u'utf8_unicode_ci', length=250), nullable=False),
    sa.Column('vout_index', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('block_hash', mysql.VARCHAR(collation=u'utf8_unicode_ci', length=250), nullable=True),
    sa.Column('block_height', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('value', mysql.DECIMAL(precision=15, scale=8), nullable=True),
    sa.Column('is_from_coinbase', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('txid', 'address', 'vout_index'),
    mysql_collate=u'utf8_unicode_ci',
    mysql_default_charset=u'utf8',
    mysql_engine=u'InnoDB'
    )
    op.drop_index(op.f('ix_transaction_vin_vout_offset'), table_name='transaction_vin')
    op.drop_index(op.f('ix_transaction_vin_txid'), table_name='transaction_vin')
    op.drop_index(op.f('ix_transaction_vin_output_txid'), table_name='transaction_vin')
    op.drop_index(op.f('ix_transaction_vin_offset'), table_name='transaction_vin')
    op.drop_index('ix_transaction_input_output_txid_and_vout_index', table_name='transaction_vin')
    op.drop_table('transaction_vin')
    op.drop_index(op.f('ix_transaction_vout_value'), table_name='transaction_vout')
    op.drop_index(op.f('ix_transaction_vout_txid'), table_name='transaction_vout')
    op.drop_index(op.f('ix_transaction_vout_offset'), table_name='transaction_vout')
    op.drop_index(op.f('ix_transaction_vout_is_from_coinbase'), table_name='transaction_vout')
    op.drop_index(op.f('ix_transaction_vout_block_height'), table_name='transaction_vout')
    op.drop_index(op.f('ix_transaction_vout_block_hash'), table_name='transaction_vout')
    op.drop_index(op.f('ix_transaction_vout_address'), table_name='transaction_vout')
    op.drop_table('transaction_vout')
    ### end Alembic commands ###
