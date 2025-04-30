"""add is_free to tests

Revision ID: add_is_free_to_tests_v2
Revises: 697fd5dc6f6f
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_is_free_to_tests_v2'
down_revision = '697fd5dc6f6f'
branch_labels = None
depends_on = None


def upgrade():
    # Ajouter la colonne is_free avec une valeur par défaut False
    op.add_column('tests', sa.Column('is_free', sa.Boolean(), nullable=False, server_default='false'))
    
    # Mettre à jour les tests existants pour les prospects comme gratuits
    op.execute("""
        UPDATE tests 
        SET is_free = true 
        WHERE user_role = 'prospect'
    """)


def downgrade():
    op.drop_column('tests', 'is_free') 