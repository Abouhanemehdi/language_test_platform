from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/profile')
@login_required
def profile():
    return render_template('user/profile.html')

@bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    username = request.form.get('username')
    phone = request.form.get('phone')
    city = request.form.get('city')
    
    # Vérifier si le nom d'utilisateur est déjà pris
    if username != current_user.username:
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Ce nom d\'utilisateur est déjà utilisé.', 'error')
            return redirect(url_for('user.profile'))
    
    # Mettre à jour les informations
    current_user.username = username
    current_user.phone = phone
    current_user.city = city
    
    db.session.commit()
    flash('Votre profil a été mis à jour avec succès.', 'success')
    return redirect(url_for('user.profile'))

@bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Vérifier le mot de passe actuel
    if not current_user.check_password(current_password):
        flash('Le mot de passe actuel est incorrect.', 'error')
        return redirect(url_for('user.profile'))
    
    # Vérifier que les nouveaux mots de passe correspondent
    if new_password != confirm_password:
        flash('Les nouveaux mots de passe ne correspondent pas.', 'error')
        return redirect(url_for('user.profile'))
    
    # Changer le mot de passe
    current_user.set_password(new_password)
    db.session.commit()
    
    flash('Votre mot de passe a été changé avec succès.', 'success')
    return redirect(url_for('user.profile')) 