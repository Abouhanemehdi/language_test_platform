from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

bp = Blueprint('subscription', __name__)

@bp.route('/subscribe')
@login_required
def subscribe():
    """Page d'abonnement Premium."""
    return render_template('subscription/subscribe.html')

@bp.route('/process-payment', methods=['POST'])
@login_required
def process_payment():
    """Traitement du paiement pour l'abonnement Premium."""
    # TODO: Intégrer le système de paiement
    flash('Fonctionnalité de paiement en cours de développement.', 'info')
    return redirect(url_for('subscription.subscribe')) 