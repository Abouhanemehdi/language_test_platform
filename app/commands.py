import click
from flask.cli import with_appcontext
from app import db
from app.models.user import User
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from app.models.test import Test, Question, Answer, TestSection
from datetime import datetime

def init_app(app):
    app.cli.add_command(create_admin)
    app.cli.add_command(reset_migrations_command)
    app.cli.add_command(init_db_command)

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

@click.command('reset-migrations')
@with_appcontext
def reset_migrations_command():
    """Réinitialise la table alembic_version."""
    with db.engine.connect() as conn:
        conn.execute(text('DROP TABLE IF EXISTS alembic_version'))
        conn.commit()
    click.echo('Table alembic_version supprimée.')

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialise la base de données avec les données de base."""
    # Créer un utilisateur admin
    admin = User(
        email='admin@example.com',
        username='admin',
        role='admin',
        active=True
    )
    admin.set_password('admin123')
    db.session.add(admin)

    # Créer un test de niveau A1
    test_a1 = Test(
        title='Test de niveau A1',
        description='Test de niveau débutant (A1) pour évaluer les compétences de base.',
        level='A1',
        user_role='prospect',
        duration=30,
        test_type='qcm',
        is_active=True
    )
    db.session.add(test_a1)
    db.session.flush()  # Pour obtenir l'ID du test

    # Créer des questions pour le test A1
    questions_a1 = [
        {
            'text': 'What is your name?',
            'type': 'qcm',
            'points': 1,
            'answers': [
                {'text': 'My name is John', 'is_correct': True},
                {'text': 'I am 25 years old', 'is_correct': False},
                {'text': 'I live in Paris', 'is_correct': False},
                {'text': 'I am a student', 'is_correct': False}
            ]
        },
        {
            'text': 'How old are you?',
            'type': 'qcm',
            'points': 1,
            'answers': [
                {'text': 'I am 25 years old', 'is_correct': True},
                {'text': 'My name is John', 'is_correct': False},
                {'text': 'I live in Paris', 'is_correct': False},
                {'text': 'I am a student', 'is_correct': False}
            ]
        }
    ]

    for q_data in questions_a1:
        question = Question(
            test_id=test_a1.id,
            question_text=q_data['text'],
            question_type=q_data['type'],
            points=q_data['points']
        )
        db.session.add(question)
        db.session.flush()

        for a_data in q_data['answers']:
            answer = Answer(
                question_id=question.id,
                answer_text=a_data['text'],
                is_correct=a_data['is_correct']
            )
            db.session.add(answer)

    # Créer un test de niveau B1
    test_b1 = Test(
        title='Test de niveau B1',
        description='Test de niveau intermédiaire (B1) pour évaluer les compétences avancées.',
        level='B1',
        user_role='client',
        duration=45,
        test_type='mixed',
        is_active=True
    )
    db.session.add(test_b1)
    db.session.flush()

    # Créer une section de lecture pour le test B1
    reading_section = TestSection(
        test_id=test_b1.id,
        title='Compréhension écrite',
        content='Read the following text and answer the questions...',
        section_type='reading',
        order=1
    )
    db.session.add(reading_section)
    db.session.flush()

    # Créer des questions pour la section de lecture
    reading_questions = [
        {
            'text': 'What is the main idea of the text?',
            'type': 'qcm',
            'points': 2,
            'answers': [
                {'text': 'The importance of education', 'is_correct': True},
                {'text': 'The history of technology', 'is_correct': False},
                {'text': 'The benefits of exercise', 'is_correct': False},
                {'text': 'The impact of climate change', 'is_correct': False}
            ]
        }
    ]

    for q_data in reading_questions:
        question = Question(
            test_id=test_b1.id,
            section_id=reading_section.id,
            question_text=q_data['text'],
            question_type=q_data['type'],
            points=q_data['points']
        )
        db.session.add(question)
        db.session.flush()

        for a_data in q_data['answers']:
            answer = Answer(
                question_id=question.id,
                answer_text=a_data['text'],
                is_correct=a_data['is_correct']
            )
            db.session.add(answer)

    db.session.commit()
    click.echo('Base de données initialisée avec succès.')