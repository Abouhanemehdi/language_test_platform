from flask import Blueprint, render_template, redirect, url_for, request, flash
from markupsafe import Markup
from flask_login import login_required, current_user
from app.models.test import Test, Question, Answer, TestSession, UserAnswer, WritingCriteria, WritingEvaluation, TestSection
from app.models.user import TestResult  # Ajout de l'import de TestResult
from app.models.contact import ContactRequest  # Ajout de l'import de ContactRequest
from app import db
from datetime import datetime
import random 

bp = Blueprint('test', __name__, url_prefix='/test')

@bp.app_template_filter('has_taken_test')
def has_taken_test(test, user):
    """Vérifie si un utilisateur a déjà passé un test spécifique"""
    return TestResult.query.filter_by(user_id=user.id, test_id=test.id).first() is not None

@bp.app_template_filter('nl2br')
def nl2br(value):
    """Convertit les retours à la ligne en balises <br>"""
    if not value:
        return value
    return Markup(value.replace('\n', '<br>'))

@bp.route('/take/<int:test_id>')
@login_required
def take_test(test_id):
    test = Test.query.get_or_404(test_id)
    
    # Vérification des autorisations avec la nouvelle méthode
    if not current_user.can_take_test(test):
        if current_user.role == 'prospect':
            flash("Vous avez déjà passé votre test gratuit. Devenez client pour accéder à plus de tests!")
            return redirect(url_for('test.upgrade_account'))
        else:
            flash("Vous n'avez pas accès à ce test.")
            return redirect(url_for('main.index'))

    # Construction des sections pour le template
    sections = []
    for section in sorted(test.sections, key=lambda s: s.order):
        if section.section_type == 'qcm':
            questions = []
            for question in section.questions:
                choices = [{"id": a.id, "text": a.answer_text} for a in question.answers]
                questions.append({
                    "id": question.id,
                    "text": question.question_text,
                    "choices": choices
                })
            sections.append({
                "id": section.id,
                "type": "qcm",
                "title": section.title,
                "questions": questions
            })
        elif section.section_type == 'writing':
            sections.append({
                "id": section.id,
                "type": "writing",
                "title": section.title,
                "instructions": section.content
            })
        elif section.section_type == 'reading':
            questions = []
            for question in section.questions:
                choices = [{"id": a.id, "text": a.answer_text} for a in question.answers]
                questions.append({
                    "id": question.id,
                    "text": question.question_text,
                    "choices": choices
                })
            sections.append({
                "id": section.id,
                "type": "reading",
                "title": section.title,
                "content": section.content,
                "questions": questions
            })
        # Ajoute d'autres types si besoin

    # Création d'une session de test
    test_session = TestSession(
        user_id=current_user.id,
        test_id=test.id,
        started_at=datetime.utcnow(),
        status='in_progress'
    )
    db.session.add(test_session)
    db.session.commit()

    return render_template(
        'test/take_test.html',
        test={
            "id": test.id,
            "title": test.title,
            "sections": sections,
            "duration": test.duration
        },
        session_id=test_session.id
    )


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
    # Utiliser la nouvelle méthode get_available_tests
    available_tests = current_user.get_available_tests()
    
    if not available_tests:
        if current_user.role == 'prospect':
            flash("Vous avez déjà passé votre test gratuit. Devenez client pour accéder à plus de tests!")
            return redirect(url_for('test.upgrade_account'))
        elif current_user.role == 'client':
            flash("Aucun test client n'est disponible pour le moment.")
            return redirect(url_for('main.index'))
        else:
            flash("Aucun test disponible pour le moment.")
            return redirect(url_for('main.index'))
    
    return render_template('test/available_tests.html', tests=available_tests)

@bp.route('/submit/<int:test_id>', methods=['POST'])
@login_required
def submit_test(test_id):
    test = Test.query.get_or_404(test_id)
    
    # Debug: Afficher tous les champs du formulaire
    print("DEBUG - Form data:", request.form)
    
    # Calcul du score initial (uniquement pour QCM et lecture)
    total_points = 0
    earned_points = 0
    has_writing = False
    
    # Créer le résultat du test
    test_result = TestResult(
        user_id=current_user.id,
        test_id=test_id,
        score=0,  # Temporaire
        level_achieved=test.level,
        completed_at=datetime.utcnow(),
        validated=False
    )
    db.session.add(test_result)
    db.session.flush()  # Pour obtenir l'ID
    
    # Traiter chaque section
    for section in sorted(test.sections, key=lambda s: s.order):
        print(f"DEBUG - Processing section: {section.id} ({section.section_type})")
        
        if section.section_type == 'writing':
            has_writing = True
            # Pour les sections d'écriture, sauvegarder directement la réponse
            field_name = f'writing_{section.id}'
            text_answer = request.form.get(field_name)
            
            print(f"DEBUG - Looking for field: {field_name}")
            print(f"DEBUG - Found answer: {text_answer}")
            
            # Créer une question si elle n'existe pas
            question = Question.query.filter_by(section_id=section.id).first()
            if not question:
                question = Question(
                    test_id=test.id,
                    section_id=section.id,
                    question_text=section.title,
                    question_type='writing',
                    points=10  # Points par défaut pour les questions d'écriture
                )
                db.session.add(question)
                db.session.flush()
            
            user_answer = UserAnswer(
                test_result_id=test_result.id,
                question_id=question.id,
                text_answer=text_answer,
                is_evaluated=False  # Important : marquer comme non évalué
            )
            db.session.add(user_answer)
            
        elif section.section_type in ['qcm', 'reading']:
            # Pour les sections QCM et lecture, traiter chaque question
            for question in section.questions:
                answer_id = request.form.get(f'q{question.id}')
                is_correct = False
                if answer_id:
                    answer = Answer.query.get(answer_id)
                    if answer and answer.is_correct:
                        earned_points += question.points
                        is_correct = True
                    user_answer = UserAnswer(
                        test_result_id=test_result.id,
                        question_id=question.id,
                        answer_id=int(answer_id),
                        is_correct=is_correct
                    )
                    db.session.add(user_answer)
                total_points += question.points
    
    # Mettre à jour le score initial
    if has_writing:
        # Si le test contient des sections d'écriture, le score initial est basé uniquement sur QCM/lecture
        if total_points > 0:
            initial_score = (earned_points / total_points) * 100
        else:
            initial_score = 0
        print(f"DEBUG - Score initial (sans écriture): {initial_score}%")
    else:
        # Si pas de section d'écriture, calculer le score normalement
        if total_points > 0:
            initial_score = (earned_points / total_points) * 100
        else:
            initial_score = 0
        print(f"DEBUG - Score final: {initial_score}%")
    
    test_result.score = initial_score
    db.session.commit()
    
    flash('Test soumis avec succès!')
    return redirect(url_for('test.show_result', result_id=test_result.id))

@bp.route('/result/<int:result_id>')
@login_required
def show_result(result_id):
    # Récupérer le résultat du test
    result = TestResult.query.get_or_404(result_id)
    print(f"\nDEBUG - Affichage du résultat {result_id}")
    print(f"DEBUG - Score actuel dans la base : {result.score}%")
    
    # Vérifier que l'utilisateur a le droit de voir ce résultat
    if result.user_id != current_user.id and current_user.role != 'admin':
        flash('Vous n\'avez pas accès à ce résultat.')
        return redirect(url_for('main.index'))
    
    # Récupérer le test et l'utilisateur
    user = current_user
    test = Test.query.get(result.test_id)
    
    # Récupérer toutes les réponses de l'utilisateur
    user_answers = UserAnswer.query.filter_by(test_result_id=result.id).all()
    print(f"DEBUG - Nombre total de réponses : {len(user_answers)}")
    
    # Organiser les réponses par section
    sections_results = {}
    section_scores = {}
    total_score = 0
    total_sections = 0
    
    for section in sorted(test.sections, key=lambda s: s.order):
        print(f"\nDEBUG - Traitement section : {section.title} ({section.section_type})")
        section_answers = []
        section_points = 0
        section_earned_points = 0
        
        # Trouver toutes les réponses pour cette section
        section_user_answers = [ua for ua in user_answers if Question.query.get(ua.question_id).section_id == section.id]
        print(f"DEBUG - Nombre de réponses pour cette section : {len(section_user_answers)}")
        
        if section.section_type == 'writing':
            # Pour les sections d'écriture
            writing_scores = []
            for user_answer in section_user_answers:
                if user_answer.is_evaluated and user_answer.writing_score is not None:
                    writing_scores.append(user_answer.writing_score)
                    print(f"DEBUG - Score d'écriture trouvé : {user_answer.writing_score}%")
                
                section_answers.append({
                    'question': Question.query.get(user_answer.question_id),
                    'text_answer': user_answer.text_answer,
                    'feedback': user_answer.feedback,
                    'is_evaluated': user_answer.is_evaluated,
                    'writing_score': user_answer.writing_score
                })
            
            # Calculer le score de la section d'écriture
            if writing_scores:
                section_score = sum(writing_scores) / len(writing_scores)
                print(f"DEBUG - Score moyen section écriture : {section_score}%")
                total_score += section_score
                total_sections += 1
            else:
                section_score = 0
                print("DEBUG - Section écriture non évaluée")
            
        else:
            # Pour les sections QCM et lecture
            total_questions = len(section.questions)
            correct_answers = 0
            
            for user_answer in section_user_answers:
                question = Question.query.get(user_answer.question_id)
                if user_answer.is_correct:
                    correct_answers += 1
                    print(f"DEBUG - Réponse correcte trouvée pour question {question.id}")
                
                section_answers.append({
                    'question': question,
                    'selected_answer': Answer.query.get(user_answer.answer_id) if user_answer.answer_id else None,
                    'correct_answer': Answer.query.filter_by(question_id=question.id, is_correct=True).first(),
                    'is_correct': user_answer.is_correct
                })
            
            # Calculer le score de la section QCM/lecture
            if total_questions > 0:
                section_score = (correct_answers / total_questions) * 100
                print(f"DEBUG - Score section {section.section_type} : {section_score}% ({correct_answers}/{total_questions})")
                total_score += section_score
                total_sections += 1
            else:
                section_score = 0
                print(f"DEBUG - Pas de questions dans la section {section.section_type}")
        
        # Ajouter les résultats de la section
        sections_results[section.id] = {
            'section': section,
            'answers': section_answers,
            'score': section_score,
            'is_evaluated': all(a.get('is_evaluated', True) for a in section_answers if 'is_evaluated' in a)
        }
        section_scores[section.id] = section_score
    
    # Mettre à jour le score global si toutes les sections sont évaluées
    if total_sections > 0:
        new_score = total_score / total_sections
        if abs(new_score - result.score) > 0.01:  # Si le score a changé
            print(f"DEBUG - Mise à jour du score global : {new_score}% (ancien : {result.score}%)")
            result.score = new_score
            db.session.commit()
        else:
            print(f"DEBUG - Score global inchangé : {result.score}%")
    
    return render_template('test/results.html',
                         result=result,
                         user=user,
                         test=test,
                         sections_results=sections_results,
                         section_scores=section_scores)

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

@bp.route('/contact-sales', methods=['POST'])
@login_required
def contact_sales():
    if current_user.role != 'prospect':
        flash("Cette fonctionnalité est réservée aux prospects.", "error")
        return redirect(url_for('main.index'))
        
    # Créer une nouvelle demande de contact
    contact_request = ContactRequest(
        user_id=current_user.id,
        name=current_user.username,
        email=current_user.email,  # Ajout de l'email de l'utilisateur
        phone=request.form.get('phone'),
        message=request.form.get('message'),
        source='prospect'  # Changé de 'general' à 'prospect'
    )
    
    db.session.add(contact_request)
    db.session.commit()
    
    flash("Votre demande a été envoyée. Notre équipe vous contactera bientôt.", "success")
    return redirect(url_for('main.index'))

def update_global_score(result_id):
    print(f"\nDEBUG - Mise à jour du score global pour le résultat {result_id}")
    result = TestResult.query.get(result_id)
    test = Test.query.get(result.test_id)
    
    # Récupérer toutes les sections du test
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
            test_result_id=result_id
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
        print(f"DEBUG - Nombre de sections évaluées : {len(section_scores)}")
        new_score = sum(section_scores) / len(section_scores)
        print(f"DEBUG - Nouveau score global : {new_score}% (moyenne de {len(section_scores)} sections évaluées)")
        
        # Mettre à jour le score dans la base de données
        result.score = new_score
        db.session.commit()
        print("DEBUG - Score global mis à jour dans la base de données")
    else:
        print("\nDEBUG - Aucun score de section disponible")

@bp.route('/evaluate_writing/<int:answer_id>', methods=['GET', 'POST'])
@login_required
def evaluate_writing(answer_id):
    if current_user.role != 'admin':
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('main.index'))
    
    user_answer = UserAnswer.query.get_or_404(answer_id)
    question = Question.query.get(user_answer.question_id)
    print(f"\nDEBUG - Évaluation de la réponse {answer_id}")
    
    if request.method == 'POST':
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
        
        return redirect(url_for('test.show_result', result_id=user_answer.test_result_id))
    
    return render_template(
        'test/evaluate_writing.html',
        answer=user_answer,
        question=question
    )