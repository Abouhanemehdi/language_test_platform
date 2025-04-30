from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

# Initialiser les extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Configuration de Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    # Enregistrer les blueprints
    from app.routes import main, auth, test, admin, dashboard, user, subscription
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(test.bp, url_prefix='/test')
    app.register_blueprint(admin.bp, url_prefix='/admin')
    app.register_blueprint(dashboard.bp, url_prefix='/dashboard')
    app.register_blueprint(user.bp, url_prefix='/user')
    app.register_blueprint(subscription.bp, url_prefix='/subscription')

    # Enregistrer les commandes CLI
    from . import commands
    commands.init_app(app)

    return app