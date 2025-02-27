import click
from flask.cli import with_appcontext
from app import db
from app.models.user import User
from sqlalchemy.exc import IntegrityError

def init_app(app):
    app.cli.add_command(create_admin)

@click.command('create-admin')
@click.argument('email')
@click.argument('password')
@with_appcontext
def create_admin(email, password):
    """Créer un utilisateur administrateur."""
    # Vérifier si l'admin existe déjà
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        if existing_user.role == 'admin':
            click.echo(f'Un admin avec cet email existe déjà: {email}')
            return
        else:
            # Mettre à jour le rôle en admin si l'utilisateur existe mais n'est pas admin
            existing_user.role = 'admin'
            db.session.commit()
            click.echo(f'Utilisateur existant promu en admin: {email}')
            return

    try:
        user = User(
            email=email,
            username='admin',
            role='admin'
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f'Admin créé avec succès: {email}')
    except IntegrityError:
        db.session.rollback()
        click.echo('Erreur: Impossible de créer l\'admin.')