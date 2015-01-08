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


def upgrade():
    op.drop_table('blocks')
    op.create_table('blocks',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('height', sa.BigInteger(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('hash', sa.String(length=64), nullable=True),
    sa.Column('time', sa.BigInteger(), nullable=True),
    sa.Column('pushed_from', sa.String(length=25), nullable=True),
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
