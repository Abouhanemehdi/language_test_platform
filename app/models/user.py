from app import db  # Import directement depuis app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime



class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'prospect', 'client', 'admin'
    phone = db.Column(db.String(20), nullable=True)  # Nouveau champ
    city = db.Column(db.String(100), nullable=True)  # Nouveau champ
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    active = db.Column(db.Boolean, default=True)
    subscription_date = db.Column(db.DateTime)  # Date de souscription pour les clients
    
    # Surcharge de la propriété is_active de UserMixin
    @property
    def is_active(self):
        return self.active
        
    @is_active.setter
    def is_active(self, value):
        self.active = value

    # Relations
    scheduled_tests = db.relationship('ScheduledTest', backref='user', lazy=True, cascade="all, delete-orphan")
    test_sessions = db.relationship('TestSession', backref='user', lazy=True, cascade="all, delete-orphan")
    # La relation test_results est définie dans le modèle TestResult

    def get_tests_taken(self):
        """Retourne le nombre de tests passés"""
        return TestResult.query.filter_by(user_id=self.id).count()

    def can_take_test(self, test):
        """Vérifie si l'utilisateur peut passer un test spécifique"""
        # Vérifier si l'utilisateur a déjà passé ce test spécifique
        if TestResult.query.filter_by(user_id=self.id, test_id=test.id).first():
            return False
            
        # Les admins peuvent toujours passer les tests
        if self.role == 'admin':
            return True
            
        # Les clients peuvent passer les tests clients une seule fois
        if self.role == 'client':
            return test.user_role == 'client'
            
        # Les prospects peuvent passer les tests gratuits et un seul test de placement
        if self.role == 'prospect':
            if test.is_free:  # Si le test est marqué comme gratuit
                return True
            # Pour les tests non gratuits, vérifier si c'est leur premier test
            return test.user_role == 'prospect' and self.get_tests_taken() == 0
            
        return False

    def get_available_tests(self):
        """Retourne les tests disponibles pour l'utilisateur"""
        from app.models.test import Test
        
        if self.role == 'admin':
            return Test.query.filter_by(is_active=True).all()
        elif self.role == 'client':
            return Test.query.filter_by(user_role='client', is_active=True).all()
        elif self.role == 'prospect':
            # Tests gratuits
            free_tests = Test.query.filter_by(is_free=True, is_active=True).all()
            # Un seul test de placement si l'utilisateur n'a pas encore passé de test
            if self.get_tests_taken() == 0:
                placement_test = Test.query.filter_by(user_role='prospect', is_active=True).first()
                if placement_test and placement_test not in free_tests:
                    free_tests.append(placement_test)
            return free_tests
        return []

    def upgrade_to_client(self):
        """Met à jour le rôle de l'utilisateur de prospect à client"""
        if self.role == 'prospect':
            self.role = 'client'
            self.subscription_date = datetime.utcnow()
            db.session.commit()
            return True
        return False

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def is_valid_role(role):
        return role in ['prospect', 'client', 'admin']

    def __repr__(self):
        return f'<User {self.username}>'

class TestResult(db.Model):
    __tablename__ = 'test_results'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    level_achieved = db.Column(db.String(10))  # A1, A2, B1, etc.
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    validated = db.Column(db.Boolean, default=False)  # Pour les clients
    
    # Relation avec Test
    test = db.relationship('Test', backref='results', lazy=True)
    # Relation avec User
    user = db.relationship('User', backref='test_results', lazy=True)

    def __repr__(self):
        return f'<TestResult {self.user_id} {self.test_id} {self.score}>'

class ScheduledTest(db.Model):
    __tablename__ = 'scheduled_tests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    scheduled_for = db.Column(db.DateTime, nullable=False)
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<ScheduledTest {self.user_id} {self.test_id} {self.scheduled_for}>'