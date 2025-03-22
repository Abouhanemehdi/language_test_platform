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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    active = db.Column(db.Boolean, default=True)  # Ajoutez cette ligne
    
    # Surcharge de la propriété is_active de UserMixin
    @property
    def is_active(self):
        return self.active
        
    @is_active.setter
    def is_active(self, value):
        self.active = value

    test_results = db.relationship('TestResult', backref='user', lazy=True)

    def get_tests_taken(self):
        """Retourne le nombre de tests passés"""
        return TestResult.query.filter_by(user_id=self.id).count()

    def can_take_test(self):
        """Vérifie si l'utilisateur peut passer un test"""
        if self.role == 'client':
            return True
        return self.get_tests_taken() == 0

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
    
    # Ajout de la relation avec Test
    test = db.relationship('Test', backref='results', lazy=True)

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