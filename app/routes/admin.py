from flask import Blueprint, render_template, redirect, url_for, request, flash, make_response
from flask_login import login_required, current_user
from app import db
from app.models.user import User, TestResult 
from app.models.test import Test, Question, Answer
from datetime import datetime
from functools import wraps
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.role == 'admin':
            flash('Accès réservé aux administrateurs.')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@admin_required
def dashboard():
    tests = Test.query.order_by(Test.created_at.desc()).all()
    active_tests_count = Test.query.filter_by(is_active=True).count()
    pending_results_count = TestResult.query.filter_by(validated=False).count()
    users_count = User.query.count()
    
    return render_template('admin/dashboard.html',
                         tests=tests,
                         active_tests_count=active_tests_count,
                         pending_results_count=pending_results_count,
                         users_count=users_count)

@bp.route('/test/create', methods=['GET', 'POST'])
@admin_required
def create_test():
    if request.method == 'POST':
        user_role = request.form.get('user_role')
        test = Test(
            title=request.form.get('title'),
            level=request.form.get('level'),
            description=request.form.get('description'),
            user_role=user_role,
            duration=int(request.form.get('duration')),
            is_active='is_active' in request.form,
            created_at=datetime.utcnow()
        )
        
        try:
            db.session.add(test)
            db.session.commit()
            flash('Test créé avec succès', 'success')
            return redirect(url_for('admin.edit_test', test_id=test.id))
        except Exception as e:
            db.session.rollback()
            flash('Erreur lors de la création du test', 'error')
            return redirect(url_for('admin.create_test'))
            
    return render_template('admin/create_test.html')

@bp.route('/test/<int:test_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_test(test_id):
    test = Test.query.get_or_404(test_id)
    
    if request.method == 'POST':
        test.title = request.form.get('title')
        test.level = request.form.get('level')
        test.is_active = 'is_active' in request.form
        test.user_role = request.form.get('user_role')
        
        db.session.commit()
        flash('Test mis à jour avec succès')
        
    return render_template('admin/edit_test.html', test=test)

@bp.route('/test/<int:test_id>/delete')
@admin_required
def delete_test(test_id):
    test = Test.query.get_or_404(test_id)
    db.session.delete(test)
    db.session.commit()
    flash('Test supprimé avec succès')
    return redirect(url_for('admin.dashboard'))

@bp.route('/test/<int:test_id>/questions/add', methods=['POST'])
@admin_required
def add_question(test_id):
    test = Test.query.get_or_404(test_id)
    
    question_text = request.form.get('question_text')
    question_type = request.form.get('question_type')
    points = request.form.get('points', type=int)
    
    if not all([question_text, question_type, points]):
        flash('Tous les champs sont requis')
        return redirect(url_for('admin.edit_test', test_id=test_id))
    
    question = Question(
        test_id=test.id,
        question_text=question_text,
        question_type=question_type,
        points=points
    )
    
    db.session.add(question)
    db.session.commit()
    
    # Si c'est une question à choix multiples, on redirige vers l'ajout de réponses
    if question_type == 'qcm':
        return redirect(url_for('admin.edit_question', question_id=question.id))
    
    return redirect(url_for('admin.edit_test', test_id=test_id))

@bp.route('/question/<int:question_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    
    if request.method == 'POST':
        question.question_text = request.form.get('question_text')
        question.points = request.form.get('points', type=int)
        
        db.session.commit()
        flash('Question mise à jour avec succès')
        
    return render_template('admin/edit_question.html', question=question)

@bp.route('/question/<int:question_id>/delete')
@admin_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    test_id = question.test_id
    db.session.delete(question)
    db.session.commit()
    
    flash('Question supprimée avec succès')
    return redirect(url_for('admin.edit_test', test_id=test_id))

@bp.route('/question/<int:question_id>/answers/add', methods=['POST'])
@admin_required
def add_answer(question_id):
    question = Question.query.get_or_404(question_id)
    
    answer_text = request.form.get('answer_text')
    is_correct = 'is_correct' in request.form
    
    if not answer_text:
        flash('Le texte de la réponse est requis')
        return redirect(url_for('admin.edit_question', question_id=question_id))
    
    answer = Answer(
        question_id=question.id,
        answer_text=answer_text,
        is_correct=is_correct
    )
    
    db.session.add(answer)
    db.session.commit()
    
    return redirect(url_for('admin.edit_question', question_id=question_id))

@bp.route('/answer/<int:answer_id>/edit', methods=['POST'])
@admin_required
def edit_answer(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    
    answer.answer_text = request.form.get('answer_text')
    answer.is_correct = 'is_correct' in request.form
    
    db.session.commit()
    flash('Réponse mise à jour avec succès')
    
    return redirect(url_for('admin.edit_question', question_id=answer.question_id))

@bp.route('/answer/<int:answer_id>/delete')
@admin_required
def delete_answer(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    question_id = answer.question_id
    
    db.session.delete(answer)
    db.session.commit()
    
    flash('Réponse supprimée avec succès')
    return redirect(url_for('admin.edit_question', question_id=question_id))

@bp.route('/users')
@admin_required
def manage_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@bp.route('/user/<int:user_id>/edit', methods=['POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    action = request.form.get('action')
    
    if action == 'change_role':
        new_role = request.form.get('role')
        if new_role in ['prospect', 'client', 'admin']:
            user.role = new_role
            db.session.commit()
            flash(f'Rôle de {user.username} mis à jour.')
    
    elif action == 'deactivate':
        user.is_active = False
        db.session.commit()
        flash(f'Utilisateur {user.username} désactivé.')
    
    elif action == 'activate':
        user.is_active = True
        db.session.commit()
        flash(f'Utilisateur {user.username} activé.')

    return redirect(url_for('admin.manage_users'))


@bp.route('/results/pending')
@admin_required
def pending_results():
    results = TestResult.query.filter_by(validated=False)\
        .order_by(TestResult.completed_at.desc()).all()
    return render_template('admin/pending_results.html', results=results)

@bp.route('/result/<int:result_id>/validate', methods=['POST'])
@admin_required
def validate_result(result_id):
    result = TestResult.query.get_or_404(result_id)
    result.validated = True
    db.session.commit()
    flash('Résultat validé avec succès')
    return redirect(url_for('admin.pending_results'))

from flask import make_response
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

@bp.route('/generate_certificate/<int:result_id>')
@admin_required
def generate_certificate(result_id):
    result = TestResult.query.get_or_404(result_id)
    user = result.user
    test = result.test

    # Générer le certificat PDF
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    
    # Ajouter le contenu du certificat
    pdf.drawString(100, 700, f"Certificat de réussite - {test.title}")
    pdf.drawString(100, 650, f"Attribué à : {user.username}")
    pdf.drawString(100, 600, f"Score obtenu : {result.score}")
    pdf.drawString(100, 550, f"Date de complétion : {result.completed_at.strftime('%d/%m/%Y')}")
    
    pdf.showPage()
    pdf.save()

    # Renvoyer le fichier PDF en réponse
    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=certificat_{result.id}.pdf'
    response.mimetype = 'application/pdf'
    return response


def send_certificate_email(result):
    # Code pour envoyer un email avec le certificat
    pass


@bp.route('/tests')
@admin_required
def manage_tests():
    prospect_tests = Test.query.filter_by(user_role='prospect').order_by(Test.created_at.desc()).all()
    client_tests = Test.query.filter_by(user_role='client').order_by(Test.created_at.desc()).all()
    
    print("Prospect tests:", [{"id": t.id, "title": t.title, "role": t.user_role} for t in prospect_tests])
    print("Client tests:", [{"id": t.id, "title": t.title, "role": t.user_role} for t in client_tests])
    
    return render_template('admin/manage_tests.html', 
                         client_tests=client_tests, 
                         prospect_tests=prospect_tests)

@bp.route('/results')
@admin_required
def manage_results():
    results = TestResult.query.filter_by(validated=False).order_by(TestResult.completed_at.desc()).all()
    return render_template('admin/manage_results.html', results=results)

@bp.route('/test/activate/<int:test_id>', methods=['POST'])
@admin_required
def activate_test(test_id):
    test = Test.query.get_or_404(test_id)
    test.is_active = True
    db.session.commit()
    flash('Test activé avec succès.')
    return redirect(url_for('admin.manage_tests'))

@bp.route('/test/deactivate/<int:test_id>', methods=['POST'])
@admin_required
def deactivate_test(test_id):
    test = Test.query.get_or_404(test_id)
    test.is_active = False
    db.session.commit()
    flash('Test désactivé avec succès.')
    return redirect(url_for('admin.manage_tests'))

@bp.route('/test/<int:test_id>/view')
@admin_required
def view_test(test_id):
    test = Test.query.get_or_404(test_id)
    return render_template('admin/view_test.html', test=test)

@bp.route('/result/<int:result_id>')
@admin_required
def view_result(result_id):
    result = TestResult.query.get_or_404(result_id)
    test = result.test
    user = result.user
    return render_template('admin/view_result.html', result=result, test=test, user=user)