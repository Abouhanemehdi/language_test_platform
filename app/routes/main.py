from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app import db
from app.models.contact import ContactRequest

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('main/index.html')

@bp.route('/cours')
def cours():
    return render_template('main/cours.html')

@bp.route('/tests')
def tests():
    """Page d'information sur les tests de langue."""
    return render_template('main/about_tests.html')

@bp.route('/about')
def about():
    return render_template('main/about.html')

@bp.route('/pricing')
def pricing():
    return render_template('main/pricing.html')

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Créer une nouvelle demande de contact
        contact_request = ContactRequest(
            user_id=current_user.id if current_user.is_authenticated else None,
            name=request.form.get('name'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            subject=request.form.get('subject'),
            message=request.form.get('message'),
            source='general'
        )
        
        db.session.add(contact_request)
        db.session.commit()
        
        flash("Votre message a été envoyé. Nous vous répondrons dans les plus brefs délais.", "success")
        return redirect(url_for('main.contact'))
        
    return render_template('main/contact.html')