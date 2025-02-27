from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.user import TestResult  # Import depuis user.py
from app.models.test import Test        # Import depuis test.py
from datetime import datetime

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/')
@login_required
def index():
    # Récupérer tous les résultats de tests de l'utilisateur
    test_results = TestResult.query.filter_by(user_id=current_user.id)\
        .order_by(TestResult.completed_at.desc()).all()
    
    # Statistiques de base
    total_tests = len(test_results)
    average_score = sum(result.score for result in test_results) / total_tests if total_tests > 0 else 0
    
    # Redirection selon le rôle de l'utilisateur
    template_map = {
        'admin': 'dashboard/admin.html',
        'client': 'dashboard/client.html',
        'prospect': 'dashboard/prospect.html'
    }
    
    context = {
        'test_results': test_results,
        'total_tests': total_tests,
        'average_score': average_score
    }
    
    if current_user.role == 'admin':
        # Ajouter des données spécifiques pour l'admin
        context.update({
            'recent_tests': Test.query.order_by(Test.created_at.desc()).limit(5).all(),
            'pending_results': TestResult.query.filter_by(validated=False).count()
        })
    
    return render_template(template_map.get(current_user.role, 'dashboard/prospect.html'), **context)

@bp.route('/')
@login_required
def user_dashboard():
    # Récupérer tous les résultats de tests de l'utilisateur
    test_results = TestResult.query.filter_by(user_id=current_user.id)\
        .order_by(TestResult.completed_at.desc()).all()
    
    # Calculer les statistiques
    total_tests = len(test_results)
    average_score = sum(result.score for result in test_results) / total_tests if total_tests > 0 else 0
    
    return render_template('dashboard/user_dashboard.html',
                         test_results=test_results,
                         total_tests=total_tests,
                         average_score=average_score)