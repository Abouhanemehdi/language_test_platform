"""add contact requests table

Revision ID: add_contact_requests_table
Revises: add_is_free_to_tests_v2
Create Date: 2024-03-19 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_contact_requests_table'
down_revision = 'add_is_free_to_tests_v2'
branch_labels = None
depends_on = None


def upgrade():
    # Créer la table contact_requests
    op.create_table('contact_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Supprimer la table contact_requests
    op.drop_table('contact_requests') 