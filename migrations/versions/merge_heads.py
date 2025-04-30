"""merge heads

Revision ID: merge_heads
Revises: add_phone_and_city_to_users, add_writing_fields
Create Date: 2024-03-08 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'merge_heads'
down_revision = ('add_phone_and_city_to_users', 'add_writing_fields')
branch_labels = None
depends_on = None


def upgrade():
    # This is a merge migration, no schema changes needed
    pass


def downgrade():
    # This is a merge migration, no schema changes needed
    pass 