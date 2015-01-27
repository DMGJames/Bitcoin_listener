"""Update blocks

Revision ID: bbe8a259072
Revises: 41ea896ee6dc
Create Date: 2015-01-09 11:08:26.363107

"""

# revision identifiers, used by Alembic.
revision = 'bbe8a259072'
down_revision = '54808a569644'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    op.drop_table('blocks')
    op.create_table('blocks',
    sa.Column('id', mysql.BIGINT, nullable=False),
    sa.Column('hash', mysql.BINARY(32), nullable=True),
    sa.Column('time', mysql.BIGINT, nullable=True),
    sa.Column('received_time', mysql.BIGINT, nullable=True),
    sa.Column('relayed_by', mysql.VARBINARY(16), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('blocks')
    op.create_table('blocks',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('hash', sa.String(length=64), nullable=True, index=True),
    sa.Column('time', sa.BigInteger(), nullable=True),
    sa.Column('pushed_from', sa.String(length=25), nullable=True, index=True),
    sa.PrimaryKeyConstraint('id')
    )
