from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from urllib.parse import urlparse
from werkzeug.security import generate_password_hash
from datetime import datetime
from app.models.user import User  # Changé l'import pour pointer directement vers user.py


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        username = request.form.get('username')
        
        if User.query.filter_by(email=email).first():
            flash("Cet email est déjà utilisé")
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(username=username).first():
            flash("Ce nom d'utilisateur est déjà utilisé")
            return redirect(url_for('auth.register'))
            
        user = User(
            email=email,
            username=username,
            role='prospect'
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash("Inscription réussie !")
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me')
        
        user = User.query.filter_by(email=email).first()
        
         # Vérifier si l'utilisateur existe, si le mot de passe est correct ET si le compte est actif
        if user is None or not user.check_password(password):
            flash("Email ou mot de passe incorrect")
            return redirect(url_for('auth.login'))
        
        # Vérification supplémentaire pour voir si le compte est actif
        if not user.is_active:
            flash("Ce compte a été désactivé. Veuillez contacter l'administrateur.")
            return redirect(url_for('auth.login'))
            
        login_user(user, remember=bool(remember_me))
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
        
        return redirect(next_page)
        
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))