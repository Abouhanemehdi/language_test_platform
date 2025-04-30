"""update contact requests table

Revision ID: update_contact_requests_table
Revises: add_contact_requests_table
Create Date: 2024-03-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'update_contact_requests_table'
down_revision = 'add_contact_requests_table'
branch_labels = None
depends_on = None


def upgrade():
    # Ajouter les nouveaux champs
    op.add_column('contact_requests', sa.Column('email', sa.String(length=120), nullable=True))
    op.add_column('contact_requests', sa.Column('subject', sa.String(length=100), nullable=True))
    op.add_column('contact_requests', sa.Column('source', sa.String(length=20), server_default='general', nullable=True))
    
    # Rendre user_id nullable
    op.alter_column('contact_requests', 'user_id',
                    existing_type=sa.Integer(),
                    nullable=True)
    
    # Mettre à jour les enregistrements existants
    op.execute("""
        UPDATE contact_requests 
        SET email = 'non spécifié' 
        WHERE email IS NULL
    """)
    
    # Rendre email non nullable après la mise à jour
    op.alter_column('contact_requests', 'email',
                    existing_type=sa.String(length=120),
                    nullable=False)


def downgrade():
    # Supprimer les nouveaux champs
    op.drop_column('contact_requests', 'source')
    op.drop_column('contact_requests', 'subject')
    op.drop_column('contact_requests', 'email')
    
    # Rendre user_id non nullable
    op.alter_column('contact_requests', 'user_id',
                    existing_type=sa.Integer(),
                    nullable=False) 