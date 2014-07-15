"""Add Block table

Revision ID: 107ed5cddfa
Revises: 14149dc0102f
Create Date: 2014-07-09 10:12:06.394050

"""

# revision identifiers, used by Alembic.
revision = '107ed5cddfa'
down_revision = '14149dc0102f'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('block',
    sa.Column('block_hash', sa.String(length=250), nullable=False),
    sa.Column('block_height', sa.Integer(), nullable=True),
    sa.Column('is_orphaned', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('block_hash')
    )
    op.create_index(op.f('ix_block_block_hash'), 'block', ['block_hash'], unique=False)
    op.create_index(op.f('ix_block_block_height'), 'block', ['block_height'], unique=False)
    op.create_index(op.f('ix_block_is_orphaned'), 'block', ['is_orphaned'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_block_is_orphaned'), table_name='block')
    op.drop_index(op.f('ix_block_block_height'), table_name='block')
    op.drop_index(op.f('ix_block_block_hash'), table_name='block')
    op.drop_table('block')
    ### end Alembic commands ###
