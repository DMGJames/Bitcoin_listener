"""Alter column order of inputs

Revision ID: 4eb83a33e8f1
Revises: 4455210b7c7
Create Date: 2014-12-10 16:27:42.776127

"""

# revision identifiers, used by Alembic.
revision = '4eb83a33e8f1'
down_revision = '4455210b7c7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute("ALTER TABLE inputs MODIFY script_sig VARCHAR(500) AFTER outputN")


def downgrade():
    op.execute("ALTER TABLE inputs MODIFY script_sig VARCHAR(500) AFTER offset")
