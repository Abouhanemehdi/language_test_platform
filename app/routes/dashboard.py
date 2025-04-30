from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.user import TestResult  # Import depuis user.py
from app.models.test import Test        # Import depuis test.py
from datetime import datetime

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/')
@login_required
def index():
    # Redirect administrators to the admin dashboard
    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    
    # Get all test results for the user
    test_results = TestResult.query.filter_by(user_id=current_user.id)\
        .order_by(TestResult.completed_at.desc()).all()
    
    # Calculate statistics
    total_tests = len(test_results)
    average_score = sum(result.score for result in test_results) / total_tests if total_tests > 0 else 0
    
    if current_user.role == 'client':
        # Get scheduled tests and certified results for clients
        scheduled_tests = Test.query.filter_by(is_active=True).all()
        certified_results = [result for result in test_results if result.validated]
        return render_template('dashboard/client.html',
                            test_results=test_results,
                            total_tests=total_tests,
                            average_score=average_score,
                            scheduled_tests=scheduled_tests,
                            certified_results=certified_results)
    else:  # prospect
        return render_template('dashboard/prospect.html',
                            test_results=test_results,
                            total_tests=total_tests,
                            average_score=average_score)