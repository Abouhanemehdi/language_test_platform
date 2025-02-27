from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models.test import Test, Question, Answer, TestSession
from app.models.user import TestResult  # Ajout de l'import de TestResult
from app import db
from datetime import datetime
import random 

bp = Blueprint('test', __name__, url_prefix='/test')

@bp.route('/take/<int:test_id>')
@login_required

def take_test(test_id):
    test = Test.query.get_or_404(test_id)
    
    # Vérification des autorisations
    if current_user.role != 'admin' and test.user_role != current_user.role:
        flash("Vous n'avez pas accès à ce test.")
        return redirect(url_for('main.index'))
    
    # Vérification pour les prospects
    if current_user.role == 'prospect':
        if not current_user.can_take_test():
            flash("Vous avez déjà passé votre test gratuit.")
            return redirect(url_for('test.upgrade_account'))
    
    # Récupération des questions avec leurs réponses
    questions = Question.query.filter_by(test_id=test.id).all()
    
    # Pour chaque question, récupérer et mélanger les réponses
    for question in questions:
        answers = Answer.query.filter_by(question_id=question.id).all()
        random.shuffle(answers)
        question.answers = answers
    
    # Mélanger les questions
    random.shuffle(questions)
    
    # Création d'une session de test
    test_session = TestSession(
        user_id=current_user.id,
        test_id=test.id,
        started_at=datetime.utcnow(),
        status='in_progress'
    )
    db.session.add(test_session)
    db.session.commit()
    
    return render_template('test/take_test.html', 
                         test=test, 
                         questions=questions,
                         session_id=test_session.id)


@bp.route('/upgrade')
@login_required
def upgrade_account():
    """Page pour devenir client"""
    return render_template('test/upgrade.html')

@bp.route('/results/<int:test_id>')
@login_required
def show_results(test_id):
    return render_template('test/results.html')

@bp.route('/available')
@login_required
def available_tests():
    print(f"DEBUG - Rôle utilisateur actuel : {current_user.role}")  # Log pour debug

    # Vérifier les droits du prospect
    if current_user.role == 'prospect' and not current_user.can_take_test():
        flash("Vous avez déjà passé votre test gratuit. Devenez client pour accéder à plus de tests!")
        return redirect(url_for('main.index'))

    # Récupérer uniquement les tests correspondant au rôle de l'utilisateur
    tests = Test.query.filter_by(
        is_active=True,
        user_role=current_user.role
    ).all()

    print(f"DEBUG - Tests trouvés : {[(t.title, t.user_role) for t in tests]}")  # Log pour debug

    return render_template('test/available_tests.html', tests=tests)

@bp.route('/submit/<int:test_id>', methods=['POST'])
@login_required
def submit_test(test_id):
    test = Test.query.get_or_404(test_id)
    questions = Question.query.filter_by(test_id=test.id).all()
    
    # Calcul du score
    total_points = 0
    earned_points = 0
    
    for question in questions:
        answer_id = request.form.get(f'q{question.id}')
        if answer_id:
            answer = Answer.query.get(answer_id)
            if answer and answer.is_correct:
                earned_points += question.points
        total_points += question.points
    
    # Calcul du pourcentage
    score_percentage = (earned_points / total_points * 100) if total_points > 0 else 0
    
    # Détermination du niveau atteint
    level_achieved = test.level
    if score_percentage >= 80:
        level_achieved = get_next_level(test.level)
    
    # Enregistrement du résultat
    test_result = TestResult(
        user_id=current_user.id,
        test_id=test_id,
        score=score_percentage,
        level_achieved=level_achieved,
        completed_at=datetime.utcnow()
    )
    db.session.add(test_result)
    
    # Mise à jour de la session de test
    test_session = TestSession.query.filter_by(
        user_id=current_user.id,
        test_id=test_id,
        status='in_progress'
    ).first()
    if test_session:
        test_session.status = 'completed'
        test_session.completed_at = datetime.utcnow()
    
    db.session.commit()
    
    flash(f'Test terminé! Score obtenu : {score_percentage:.1f}%')
    return redirect(url_for('test.show_result', result_id=test_result.id))


@bp.route('/result/<int:result_id>')
@login_required
def show_result(result_id):
    # Récupérer le résultat du test
    test_result = TestResult.query.get_or_404(result_id)
    
    # Vérifier que l'utilisateur a le droit de voir ce résultat
    if test_result.user_id != current_user.id and current_user.role != 'admin':
        flash('Vous n\'avez pas accès à ce résultat.')
        return redirect(url_for('main.index'))
    
    return render_template('test/results.html', result=test_result)

@bp.route('/schedule/<int:test_id>', methods=['GET', 'POST'])
@login_required
def schedule_test(test_id):
    if current_user.role != 'client':
        flash("Seuls les clients peuvent réserver des tests.")
        return redirect(url_for('main.index'))
    
    test = Test.query.get_or_404(test_id)
    
    if request.method == 'POST':
        scheduled_date = datetime.strptime(request.form.get('test_date'), '%Y-%m-%d %H:%M')
        
        scheduled_test = ScheduledTest(
            user_id=current_user.id,
            test_id=test_id,
            scheduled_for=scheduled_date
        )
        
        db.session.add(scheduled_test)
        db.session.commit()
        
        flash("Test programmé avec succès!")
        return redirect(url_for('dashboard.index'))
        
    return render_template('test/schedule.html', test=test)


def notify_upcoming_test():
    """Notifier les clients de leurs tests à venir"""
    tomorrow = datetime.utcnow() + timedelta(days=1)
    scheduled_tests = ScheduledTest.query.filter(
        ScheduledTest.scheduled_for <= tomorrow,
        ScheduledTest.completed == False
    ).all()
    
    for scheduled_test in scheduled_tests:
        send_reminder_email(scheduled_test)

def send_reminder_email(scheduled_test):
    # Code pour envoyer un email de rappel
    pass