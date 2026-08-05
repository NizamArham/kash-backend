"""Merge POS and soft delete migrations

Revision ID: 3e75c1f78459
Revises: 2fb7b1395898, 8b792739b8b7
Create Date: 2026-07-15 15:25:44.155097

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3e75c1f78459'
down_revision = ('2fb7b1395898', '8b792739b8b7')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
