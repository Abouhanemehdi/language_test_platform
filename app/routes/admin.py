from flask import Blueprint, render_template, redirect, url_for, request, flash, make_response, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User, TestResult 
from app.models.test import Test, Question, Answer, UserAnswer, TestSection, WritingCriteria, WritingPerformanceLevel, TestSession
from app.models.contact import ContactRequest
from datetime import datetime
from functools import wraps
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from flask import current_app
import csv
from io import StringIO

bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.role == 'admin':
            flash('Accès réservé aux administrateurs.')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@admin_required
def dashboard():
    tests = Test.query.order_by(Test.created_at.desc()).all()
    active_tests_count = Test.query.filter_by(is_active=True).count()
    pending_results_count = TestResult.query.filter_by(validated=False).count()
    users_count = User.query.count()
    contact_requests = ContactRequest.query.order_by(ContactRequest.created_at.desc()).all()
    
    return render_template('admin/dashboard.html',
                         tests=tests,
                         active_tests_count=active_tests_count,
                         pending_results_count=pending_results_count,
                         users_count=users_count,
                         contact_requests=contact_requests)

@bp.route('/test/create', methods=['GET', 'POST'])
@admin_required
def create_test():
    """Ancienne route de création de test - à supprimer"""
    flash('Cette route n\'est plus utilisée. Veuillez utiliser les nouvelles routes de création de test.', 'warning')
    return redirect(url_for('admin.select_test_type'))

@bp.route('/test/<int:test_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_test(test_id):
    test = Test.query.get_or_404(test_id)
    
    if request.method == 'POST':
        test.title = request.form.get('title')
        test.level = request.form.get('level')
        test.is_active = 'is_active' in request.form
        test.is_free = 'is_free' in request.form
        test.user_role = request.form.get('user_role')
        
        db.session.commit()
        flash('Test mis à jour avec succès')
        
    return render_template('admin/edit_test.html', test=test)

@bp.route('/test/<int:test_id>/delete')
@admin_required
def delete_test(test_id):
    """Suppression d'un test et de toutes ses données associées."""
    try:
        test = Test.query.get_or_404(test_id)

        # Supprimer d'abord les sessions de test associées
        TestSession.query.filter_by(test_id=test.id).delete()
        db.session.commit()
        
        # Supprimer d'abord les sections et leurs données associées
        for section in test.sections:
            # Supprimer les critères d'écriture et leurs niveaux de performance
            if section.section_type == 'writing':
                for criterion in section.criteria:
                    # Supprimer les niveaux de performance
                    WritingPerformanceLevel.query.filter_by(criteria_id=criterion.id).delete()
                    # Supprimer le critère
                    db.session.delete(criterion)
            
            # Supprimer les questions et leurs réponses
            for question in section.questions:
                # Supprimer les UserAnswer associés à chaque réponse
                for answer in question.answers:
                    UserAnswer.query.filter_by(answer_id=answer.id).delete()
                # Supprimer les réponses
                Answer.query.filter_by(question_id=question.id).delete()
                # Supprimer la question
                db.session.delete(question)
            
            # Supprimer la section
            db.session.delete(section)
        
        # Supprimer tous les UserAnswer associés aux TestResult du test
        test_result_ids = [tr.id for tr in TestResult.query.filter_by(test_id=test.id).all()]
        if test_result_ids:
            UserAnswer.query.filter(UserAnswer.test_result_id.in_(test_result_ids)).delete(synchronize_session=False)
            db.session.commit()
        
        # Supprimer les résultats de test associés
        TestResult.query.filter_by(test_id=test.id).delete()
        
        # Supprimer le test
        db.session.delete(test)
        db.session.commit()
        
        flash('Test supprimé avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erreur lors de la suppression du test: {str(e)}')
        flash('Une erreur est survenue lors de la suppression du test', 'error')
    
    return redirect(url_for('admin.manage_tests'))

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

@bp.route('/users/export')
@admin_required
def export_users():
    # Créer un buffer pour le CSV
    si = StringIO()
    cw = csv.writer(si)
    
    # Écrire l'en-tête
    headers = [
        'ID', 'Nom d\'utilisateur', 'Email', 'Rôle', 'Statut', 
        'Téléphone', 'Ville', 'Date d\'inscription',
        'Nombre de tests complétés', 'Score moyen',
        'Dernier test complété'
    ]
    cw.writerow(headers)
    
    # Récupérer tous les utilisateurs avec leurs résultats
    users = User.query.all()
    
    for user in users:
        # Récupérer les résultats de test de l'utilisateur
        test_results = TestResult.query.filter_by(user_id=user.id).all()
        
        # Calculer les statistiques
        completed_tests = len(test_results)
        avg_score = sum(r.score for r in test_results) / len(test_results) if test_results else 0
        last_test = max(r.completed_at for r in test_results) if test_results else None
        
        # Écrire les données de l'utilisateur
        row = [
            user.id,
            user.username,
            user.email,
            user.role,
            'Actif' if user.is_active else 'Inactif',
            user.phone or 'Non renseigné',
            user.city or 'Non renseignée',
            user.created_at.strftime('%d/%m/%Y %H:%M'),
            completed_tests,
            f"{avg_score:.1f}%" if test_results else "0%",
            last_test.strftime('%d/%m/%Y %H:%M') if last_test else 'Aucun test'
        ]
        cw.writerow(row)
    
    # Préparer la réponse
    output = si.getvalue()
    si.close()
    
    # Créer la réponse avec le fichier CSV
    response = make_response(output)
    response.headers['Content-Disposition'] = f'attachment; filename=users_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    response.headers['Content-type'] = 'text/csv'
    
    return response

@bp.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'change_role':
            new_role = request.form.get('role')
            if new_role in ['prospect', 'client']:
                user.role = new_role
                db.session.commit()
                flash(f'Rôle de {user.username} mis à jour en {new_role}.')
        
        elif action == 'deactivate':
            user.is_active = False
            db.session.commit()
            flash(f'Utilisateur {user.username} désactivé.')
        
        elif action == 'activate':
            user.is_active = True
            db.session.commit()
            flash(f'Utilisateur {user.username} activé.')

        return redirect(url_for('admin.manage_users'))
        
    return render_template('admin/edit_user.html', user=user)

@bp.route('/user/<int:user_id>/delete')
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash('Impossible de supprimer un administrateur.', 'error')
        return redirect(url_for('admin.manage_users'))
        
    db.session.delete(user)
    db.session.commit()
    flash('Utilisateur supprimé avec succès.', 'success')
    return redirect(url_for('admin.manage_users'))

@bp.route('/user/<int:user_id>/results')
@admin_required
def view_user_results(user_id):
    user = User.query.get_or_404(user_id)
    results = TestResult.query.filter_by(user_id=user.id).order_by(TestResult.completed_at.desc()).all()
    return render_template('admin/user_results.html', user=user, results=results)

@bp.route('/result/<int:result_id>/reject', methods=['GET', 'POST'])
@admin_required
def reject_result(result_id):
    result = TestResult.query.get_or_404(result_id)
    
    if request.method == 'POST':
        reason = request.form.get('reason', '')
        result.validated = False
        result.rejected = True
        result.rejection_reason = reason
        db.session.commit()
        flash('Résultat rejeté avec succès.', 'success')
        return redirect(url_for('admin.pending_results'))
    
    # Pour la méthode GET, on affiche une page de confirmation
    return render_template('admin/reject_result.html', result=result)

@bp.route('/results/pending')
@admin_required
def pending_results():
    # Récupérer les résultats en attente
    pending_results = TestResult.query.filter_by(validated=False)\
        .order_by(TestResult.completed_at.desc()).all()
    
    # Calculer les statistiques
    pending_count = len(pending_results)
    unique_tests = len(set(result.test_id for result in pending_results))
    
    # Calculer le temps moyen d'attente
    current_time = datetime.utcnow()
    wait_times = [(current_time - result.completed_at).total_seconds() / 3600 for result in pending_results]
    avg_wait_time = round(sum(wait_times) / len(wait_times)) if wait_times else 0
    
    # Récupérer tous les tests pour le filtre
    tests = Test.query.all()
    
    return render_template('admin/pending_results.html',
                         pending_results=pending_results,
                         pending_count=pending_count,
                         unique_tests=unique_tests,
                         avg_wait_time=avg_wait_time,
                         tests=tests,
                         now=current_time)

@bp.route('/result/<int:result_id>/validate', methods=['GET', 'POST'])
@admin_required
def validate_result(result_id):
    result = TestResult.query.get_or_404(result_id)
    
    if request.method == 'POST':
        result.validated = True
        db.session.commit()
        flash('Résultat validé avec succès', 'success')
        return redirect(url_for('admin.pending_results'))
    
    # Pour la méthode GET, on affiche une page de confirmation
    return render_template('admin/validate_result.html', result=result)

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
    
    # Calculer les statistiques
    total_tests = len(prospect_tests) + len(client_tests)
    active_tests = sum(1 for t in prospect_tests + client_tests if t.is_active)
    total_questions = sum(len(t.questions) for t in prospect_tests + client_tests)
    
    return render_template('admin/tests.html', 
                         client_tests=client_tests, 
                         prospect_tests=prospect_tests,
                         total_tests=total_tests,
                         active_tests=active_tests,
                         total_questions=total_questions)

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

@bp.route('/result/<int:result_id>/detail')
@login_required
@admin_required
def result_detail(result_id):
    result = TestResult.query.get_or_404(result_id)
    test = Test.query.get(result.test_id)
    user = User.query.get(result.user_id)
    
    # Récupérer toutes les réponses de l'utilisateur
    user_answers = UserAnswer.query.filter_by(test_result_id=result.id).all()
    
    # Organiser les réponses par section
    sections_results = {}
    section_scores = {}
    
    for section in sorted(test.sections, key=lambda s: s.order):
        section_answers = []
        section_points = 0
        section_earned_points = 0
        
        for user_answer in user_answers:
            question = Question.query.get(user_answer.question_id)
            if question and question.section_id == section.id:
                answer_data = {
                    'id': user_answer.id,
                    'question': question,
                    'text_answer': user_answer.text_answer,
                    'selected_answer': Answer.query.get(user_answer.answer_id) if user_answer.answer_id else None,
                    'is_correct': user_answer.is_correct,
                    'feedback': user_answer.feedback,
                    'writing_score': user_answer.writing_score,
                    'is_evaluated': user_answer.is_evaluated
                }
                
                if question.question_type != 'writing':
                    correct_answer = Answer.query.filter_by(question_id=question.id, is_correct=True).first()
                    answer_data['correct_answer'] = correct_answer
                    
                    if user_answer.is_correct:
                        section_earned_points += question.points
                    section_points += question.points
                
                section_answers.append(answer_data)
        
        # Calculer le score de la section
        section_score = 0
        if section_points > 0:
            section_score = (section_earned_points / section_points) * 100
        
        sections_results[section.id] = {
            'section': section,
            'answers': section_answers,
            'score': section_score
        }
        section_scores[section.id] = section_score
    
    return render_template(
        'admin/result_detail.html',
        result=result,
        test=test,
        user=user,
        sections_results=sections_results,
        section_scores=section_scores
    )

@bp.route('/evaluate_writing/<int:answer_id>', methods=['POST'])
@login_required
@admin_required
def evaluate_writing(answer_id):
    user_answer = UserAnswer.query.get_or_404(answer_id)
    print(f"\nDEBUG - Évaluation de la réponse {answer_id}")
    
    # Récupérer les données du formulaire
    score = float(request.form.get('score', 0))
    feedback = request.form.get('feedback', '')
    print(f"DEBUG - Score attribué : {score}%")
    print(f"DEBUG - Feedback fourni : {feedback[:50]}...")
    
    # Mettre à jour la réponse
    user_answer.writing_score = score
    user_answer.feedback = feedback
    user_answer.is_evaluated = True
    
    try:
        db.session.commit()
        print("DEBUG - Évaluation enregistrée avec succès")
        print(f"DEBUG - Score enregistré : {user_answer.writing_score}%")
        
        # Recalculer le score global
        result = TestResult.query.get(user_answer.test_result_id)
        old_score = result.score
        print(f"DEBUG - Ancien score global : {old_score}%")
        
        # Récupérer toutes les sections du test
        test = Test.query.get(result.test_id)
        sections = TestSection.query.filter_by(test_id=test.id).all()
        section_scores = []
        
        for section in sections:
            print(f"\nDEBUG - Calcul du score pour la section {section.id} ({section.section_type})")
            
            # Récupérer toutes les questions de la section
            questions = Question.query.filter_by(section_id=section.id).all()
            if not questions:
                print("DEBUG - Aucune question dans cette section")
                continue
                
            # Récupérer les réponses de l'utilisateur pour cette section
            user_answers = UserAnswer.query.filter_by(
                test_result_id=result.id
            ).join(Question).filter(
                Question.section_id == section.id
            ).all()
            
            if section.section_type == 'writing':
                # Pour les sections d'écriture
                evaluated_answers = [a for a in user_answers if a.is_evaluated]
                if evaluated_answers:
                    writing_scores = [a.writing_score for a in evaluated_answers]
                    print(f"DEBUG - Scores d'écriture trouvés : {writing_scores}")
                    section_score = sum(writing_scores) / len(writing_scores)
                    print(f"DEBUG - Score section écriture : {section_score}% ({len(evaluated_answers)} réponses évaluées)")
                    section_scores.append(section_score)
                else:
                    print("DEBUG - Aucune réponse d'écriture évaluée")
            else:
                # Pour les sections QCM/lecture
                if user_answers:
                    correct_answers = sum(1 for a in user_answers if a.is_correct)
                    total_questions = len(questions)
                    print(f"DEBUG - QCM : {correct_answers} réponses correctes sur {total_questions} questions")
                    section_score = (correct_answers / total_questions) * 100
                    print(f"DEBUG - Score section QCM/lecture : {section_score}%")
                    section_scores.append(section_score)
                else:
                    print("DEBUG - Aucune réponse pour cette section")
        
        # Calculer le score global comme moyenne des scores des sections évaluées
        if section_scores:
            print(f"\nDEBUG - Scores des sections évaluées : {section_scores}")
            new_score = sum(section_scores) / len(section_scores)
            print(f"DEBUG - Nouveau score global : {new_score}% (moyenne de {len(section_scores)} sections évaluées)")
            
            # Mettre à jour le score dans la base de données
            result.score = new_score
            db.session.commit()
            print("DEBUG - Score global mis à jour dans la base de données")
        else:
            print("\nDEBUG - Aucun score de section disponible")
        
        flash('Évaluation enregistrée avec succès!', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"DEBUG - Erreur lors de l'enregistrement : {str(e)}")
        flash('Erreur lors de l\'enregistrement de l\'évaluation.', 'error')
    
    return redirect(url_for('admin.result_detail', result_id=user_answer.test_result_id))

@bp.route('/results/validated')
@admin_required
def validated_results():
    results = TestResult.query.filter_by(validated=True)\
        .order_by(TestResult.completed_at.desc()).all()
    return render_template('admin/validated_results.html', results=results)

@bp.route('/user/create', methods=['GET', 'POST'])
@admin_required
def create_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'user')
        
        if User.query.filter_by(email=email).first():
            flash('Cet email est déjà utilisé.', 'error')
            return redirect(url_for('admin.create_user'))
            
        if User.query.filter_by(username=username).first():
            flash('Ce nom d\'utilisateur est déjà utilisé.', 'error')
            return redirect(url_for('admin.create_user'))
            
        user = User(
            username=username,
            email=email,
            role=role,
            is_active=True,
            created_at=datetime.utcnow()
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Utilisateur créé avec succès.', 'success')
        return redirect(url_for('admin.manage_users'))
        
    return render_template('admin/create_user.html')

@bp.route('/tests/select-type')
@login_required
@admin_required
def select_test_type():
    """Page de sélection du type de test à créer."""
    return render_template('admin/select_test_type.html')

@bp.route('/tests/create/qcm', methods=['GET', 'POST'])
@login_required
@admin_required
def create_qcm_test():
    """Création d'un test QCM."""
    if request.method == 'POST':
        try:
            # Créer le test
            test = Test(
                title=request.form.get('title'),
                description=request.form.get('description'),
                level=request.form.get('level'),
                user_role=request.form.get('user_role'),
                duration=int(request.form.get('duration')),
                test_type='qcm',
                is_active=True
            )
            db.session.add(test)
            db.session.flush()

            # Créer la section QCM automatiquement
            from app.models.test import TestSection
            section = TestSection(
                test_id=test.id,
                title='Questions à choix multiples',
                content='',  # Pas de texte de consigne spécifique
                section_type='qcm',
                order=0
            )
            db.session.add(section)
            db.session.flush()

            # Récupérer le nombre de questions
            question_count = 0
            while f'questions[{question_count}][text]' in request.form:
                question_count += 1

            # Créer les questions et les lier à la section
            for i in range(question_count):
                question = Question(
                    test_id=test.id,
                    section_id=section.id,
                    question_text=request.form.get(f'questions[{i}][text]'),
                    question_type='qcm',
                    points=int(request.form.get(f'questions[{i}][points]'))
                )
                db.session.add(question)
                db.session.flush()

                # Récupérer le nombre de réponses pour cette question
                answer_count = 0
                while f'questions[{i}][answers][{answer_count}][text]' in request.form:
                    answer_count += 1

                # Récupérer l'index de la réponse correcte
                correct_answer_index = int(request.form.get(f'questions[{i}][correct_answer]'))

                # Créer les réponses
                for j in range(answer_count):
                    answer = Answer(
                        question_id=question.id,
                        answer_text=request.form.get(f'questions[{i}][answers][{j}][text]'),
                        is_correct=(j == correct_answer_index)
                    )
                    db.session.add(answer)

            db.session.commit()
            flash('Test QCM créé avec succès', 'success')
            return redirect(url_for('admin.manage_tests'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la création du test: {str(e)}', 'error')
            return redirect(url_for('admin.create_qcm_test'))

    return render_template('admin/create_qcm_test.html')

@bp.route('/tests/create/mixed', methods=['GET', 'POST'])
@login_required
@admin_required
def create_mixed_test():
    """Création d'un test mixte."""
    if request.method == 'POST':
        try:
            # Log des données du formulaire
            current_app.logger.info("Données du formulaire reçues:")
            current_app.logger.info(f"Form data: {request.form}")
            
            # Validation des données de base
            required_fields = ['title', 'description', 'level', 'user_role', 'duration']
            for field in required_fields:
                if not request.form.get(field):
                    raise ValueError(f'Le champ {field} est requis')

            # Validation des sections
            sections_data = []
            i = 0
            while f'sections[{i}][title]' in request.form:
                sections_data.append({
                    'title': request.form.get(f'sections[{i}][title]'),
                    'content': request.form.get(f'sections[{i}][content]'),
                    'type': request.form.get(f'sections[{i}][type]')
                })
                i += 1

            current_app.logger.info(f"Sections data: {sections_data}")
            
            if not sections_data:
                raise ValueError('Au moins une section est requise')

            # Créer le test
            test = Test(
                title=request.form.get('title'),
                description=request.form.get('description'),
                level=request.form.get('level'),
                user_role=request.form.get('user_role'),
                duration=int(request.form.get('duration')),
                test_type='mixed',
                is_active=True
            )
            db.session.add(test)
            db.session.flush()

            current_app.logger.info(f'Test mixte créé: {test.id} - {test.title}')

            # Créer les sections
            for i, section_data in enumerate(sections_data):
                if not section_data['title'] or not section_data['content'] or not section_data['type']:
                    raise ValueError(f'Données manquantes pour la section {i + 1}')

                if section_data['type'] not in ['reading', 'qcm', 'writing']:
                    raise ValueError(f'Type de section invalide: {section_data["type"]}')

                section = TestSection(
                    test_id=test.id,
                    title=section_data['title'],
                    content=section_data['content'],
                    section_type=section_data['type'],
                    order=i
                )
                db.session.add(section)
                db.session.flush()

                current_app.logger.info(f'Section créée: {section.id} - {section.title} ({section.section_type})')

                if section_data['type'] in ['reading', 'qcm']:
                    # Validation des questions
                    questions_data = []
                    j = 0
                    while f'sections[{i}][questions][{j}][text]' in request.form:
                        questions_data.append({
                            'text': request.form.get(f'sections[{i}][questions][{j}][text]'),
                            'points': request.form.get(f'sections[{i}][questions][{j}][points]'),
                            'correct_answer': request.form.get(f'sections[{i}][questions][{j}][correct_answer]')
                        })
                        j += 1

                    current_app.logger.info(f"Questions pour la section {i}: {questions_data}")

                    if not questions_data:
                        raise ValueError(f'Au moins une question est requise pour la section {section.title}')

                    for j, question_data in enumerate(questions_data):
                        if not question_data['text'] or not question_data['points']:
                            raise ValueError(f'Données manquantes pour la question {j + 1} de la section {section.title}')

                        try:
                            points_value = int(question_data['points'])
                            if points_value <= 0:
                                raise ValueError
                        except ValueError:
                            raise ValueError(f'Points invalides pour la question {j + 1} de la section {section.title}')

                        question = Question(
                            test_id=test.id,
                            section_id=section.id,
                            question_text=question_data['text'],
                            question_type='qcm',
                            points=points_value
                        )
                        db.session.add(question)
                        db.session.flush()

                        current_app.logger.info(f'Question créée: {question.id} - Section {section.id}')

                        # Validation et création des réponses
                        answers_data = []
                        k = 0
                        while f'sections[{i}][questions][{j}][answers][{k}][text]' in request.form:
                            answers_data.append(request.form.get(f'sections[{i}][questions][{j}][answers][{k}][text]'))
                            k += 1

                        current_app.logger.info(f"Réponses pour la question {j}: {answers_data}")
                        
                        if len(answers_data) < 2:
                            raise ValueError(f'Au moins deux réponses sont requises pour la question {j + 1}')

                        try:
                            correct_answer_index = int(question_data['correct_answer'])
                            if correct_answer_index < 0 or correct_answer_index >= len(answers_data):
                                raise ValueError
                        except ValueError:
                            raise ValueError(f'Index de réponse correcte invalide pour la question {j + 1}')

                        for k, answer_text in enumerate(answers_data):
                            if not answer_text:
                                raise ValueError(f'Texte de réponse manquant pour la question {j + 1}')

                            answer = Answer(
                                question_id=question.id,
                                answer_text=answer_text,
                                is_correct=(k == correct_answer_index)
                            )
                            db.session.add(answer)

                elif section_data['type'] == 'writing':
                    # Créer une question de type writing pour la section
                    question = Question(
                        test_id=test.id,
                        section_id=section.id,
                        question_text=section_data['content'] or section_data['title'],
                        question_type='writing',
                        points=10  # barème par défaut, à ajuster si besoin
                    )
                    db.session.add(question)
                    db.session.flush()

                    # Validation des critères d'évaluation
                    criteria_data = []
                    j = 0
                    while f'sections[{i}][criteria][{j}][name]' in request.form:
                        criteria_data.append({
                            'name': request.form.get(f'sections[{i}][criteria][{j}][name]'),
                            'description': request.form.get(f'sections[{i}][criteria][{j}][description]'),
                            'max_points': request.form.get(f'sections[{i}][criteria][{j}][max_points]')
                        })
                        j += 1

                    current_app.logger.info(f"Critères pour la section {i}: {criteria_data}")

                    if not criteria_data:
                        raise ValueError(f'Au moins un critère est requis pour la section d\'écriture {section.title}')

                    for j, criterion_data in enumerate(criteria_data):
                        if not criterion_data['name'] or not criterion_data['description']:
                            raise ValueError(f'Données manquantes pour le critère {j + 1}')

                        try:
                            points_value = int(criterion_data['max_points'])
                            if points_value <= 0:
                                raise ValueError
                        except ValueError:
                            raise ValueError(f'Points invalides pour le critère {j + 1}')

                        criterion = WritingCriteria(
                            section_id=section.id,
                            name=criterion_data['name'],
                            description=criterion_data['description'],
                            max_points=points_value
                        )
                        db.session.add(criterion)
                        current_app.logger.info(f'Critère créé: {criterion_data["name"]} - Section {section.id}')

            db.session.commit()
            current_app.logger.info(f'Test mixte {test.id} créé avec succès')
            flash('Test mixte créé avec succès', 'success')
            return redirect(url_for('admin.manage_tests'))

        except ValueError as e:
            db.session.rollback()
            current_app.logger.error(f'Erreur de validation lors de la création du test mixte: {str(e)}')
            flash(str(e), 'error')
            return redirect(url_for('admin.create_mixed_test'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Erreur inattendue lors de la création du test mixte: {str(e)}')
            flash('Une erreur est survenue lors de la création du test', 'error')
            return redirect(url_for('admin.create_mixed_test'))

    return render_template('admin/create_mixed_test.html')

@bp.route('/tests/create/writing', methods=['GET', 'POST'])
@login_required
@admin_required
def create_writing_test():
    """Création d'un test d'écriture."""
    if request.method == 'POST':
        try:
            # Validation des données de base
            required_fields = ['title', 'description', 'level', 'user_role', 'duration']
            for field in required_fields:
                if not request.form.get(field):
                    raise ValueError(f'Le champ {field} est requis')

            # Créer le test
            test = Test(
                title=request.form.get('title'),
                description=request.form.get('description'),
                level=request.form.get('level'),
                user_role=request.form.get('user_role'),
                duration=int(request.form.get('duration')),
                test_type='writing',
                is_active=True
            )
            db.session.add(test)
            db.session.flush()

            current_app.logger.info(f'Test d\'écriture créé: {test.id} - {test.title}')

            # Créer la section d'écriture
            section = TestSection(
                test_id=test.id,
                title='Expression écrite',
                content=request.form.get('prompt'),
                section_type='writing',
                order=1
            )
            db.session.add(section)
            db.session.flush()

            current_app.logger.info(f'Section d\'écriture créée: {section.id}')

            # Créer les critères d'évaluation
            criteria_data = []
            i = 0
            while f'criteria[{i}][name]' in request.form:
                criteria_data.append({
                    'name': request.form.get(f'criteria[{i}][name]'),
                    'description': request.form.get(f'criteria[{i}][description]'),
                    'max_points': request.form.get(f'criteria[{i}][max_points]')
                })
                i += 1

            current_app.logger.info(f"Critères d'évaluation: {criteria_data}")

            if not criteria_data:
                raise ValueError('Au moins un critère d\'évaluation est requis')

            for i, criterion_data in enumerate(criteria_data):
                if not criterion_data['name'] or not criterion_data['description']:
                    raise ValueError(f'Données manquantes pour le critère {i + 1}')

                try:
                    points_value = int(criterion_data['max_points'])
                    if points_value <= 0:
                        raise ValueError
                except ValueError:
                    raise ValueError(f'Points invalides pour le critère {i + 1}')

                criterion = WritingCriteria(
                    section_id=section.id,
                    name=criterion_data['name'],
                    description=criterion_data['description'],
                    max_points=points_value
                )
                db.session.add(criterion)
                db.session.flush()

                current_app.logger.info(f'Critère créé: {criterion_data["name"]} - Section {section.id}')

                # Créer les niveaux de performance pour chaque critère
                levels = ['excellent', 'good', 'average', 'poor', 'very_poor']
                points = [5, 4, 3, 2, 1]
                for level, point in zip(levels, points):
                    description = request.form.get(f'criteria[{i}][levels][{level}]')
                    if not description:
                        raise ValueError(f'Description manquante pour le niveau {level} du critère {i + 1}')

                    performance_level = WritingPerformanceLevel(
                        criteria_id=criterion.id,
                        level=level,
                        description=description,
                        points=point
                    )
                    db.session.add(performance_level)
                    current_app.logger.info(f'Niveau de performance créé: {level} - Critère {criterion.id}')

            db.session.commit()
            current_app.logger.info(f'Test d\'écriture {test.id} créé avec succès')
            flash('Test d\'écriture créé avec succès', 'success')
            return redirect(url_for('admin.manage_tests'))

        except ValueError as e:
            db.session.rollback()
            current_app.logger.error(f'Erreur de validation lors de la création du test d\'écriture: {str(e)}')
            flash(str(e), 'error')
            return redirect(url_for('admin.create_writing_test'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Erreur inattendue lors de la création du test d\'écriture: {str(e)}')
            flash('Une erreur est survenue lors de la création du test', 'error')
            return redirect(url_for('admin.create_writing_test'))

    return render_template('admin/create_writing_test.html')

@bp.route('/contact-request/<int:request_id>/status', methods=['POST'])
@admin_required
def update_contact_request_status(request_id):
    request_data = request.get_json()
    new_status = request_data.get('status')
    
    if new_status not in ['pending', 'contacted', 'completed']:
        return jsonify({'success': False, 'error': 'Statut invalide'})
    
    contact_request = ContactRequest.query.get_or_404(request_id)
    contact_request.status = new_status
    db.session.commit()
    
    return jsonify({'success': True})

@bp.route('/contact-request/<int:request_id>')
@admin_required
def get_contact_request_details(request_id):
    contact_request = ContactRequest.query.get_or_404(request_id)
    return jsonify({
        'id': contact_request.id,
        'name': contact_request.name,
        'email': contact_request.email,
        'phone': contact_request.phone,
        'message': contact_request.message,
        'created_at': contact_request.created_at.strftime('%d/%m/%Y %H:%M'),
        'status': contact_request.status,
        'subject': contact_request.subject,
        'source': contact_request.source
    })

@bp.route('/user/<int:user_id>/details')
@admin_required
def user_details(user_id):
    user = User.query.get_or_404(user_id)
    # Récupérer les résultats de test de l'utilisateur
    test_results = TestResult.query.filter_by(user_id=user.id).order_by(TestResult.completed_at.desc()).all()
    
    return render_template('admin/user_details.html', 
                         user=user,
                         test_results=test_results)