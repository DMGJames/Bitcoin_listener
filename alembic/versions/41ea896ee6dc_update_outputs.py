"""Update outputs

Revision ID: 41ea896ee6dc
Revises: 2e32568b569b
Create Date: 2015-01-08 19:07:06.575246

"""

# revision identifiers, used by Alembic.
revision = '41ea896ee6dc'
down_revision = '2e32568b569b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_table('outputs')
    op.create_table('outputs',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('tx_id', sa.BigInteger(), nullable=True),
    sa.Column('dst_address', sa.String(length=36), nullable=True),
    sa.Column('value', sa.BigInteger(), nullable=True),
    sa.Column('offset', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('outputs')
    op.create_table('outputs',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('dstAddress', sa.String(length=36), nullable=True),
    sa.Column('value', sa.BigInteger(), nullable=True),
    sa.Column('txHash', sa.String(length=64), nullable=True),
    sa.Column('offset', sa.Integer(), nullable=True),
    sa.Column('pushed_from', sa.String(length=25), nullable=True, index=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('txHash_2', 'outputs', ['txHash', 'offset'], unique=False)
