from app import db
from datetime import datetime

class Test(db.Model):
    __tablename__ = 'tests'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    level = db.Column(db.String(20), nullable=False)  # A1, A2, B1, B2, C1, C2
    user_role = db.Column(db.String(20), nullable=False)  # prospect, client
    duration = db.Column(db.Integer, nullable=False)  # en minutes
    test_type = db.Column(db.String(20), nullable=False, default='qcm')  # qcm, reading, writing, mixed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_free = db.Column(db.Boolean, default=False)  # Nouveau champ pour indiquer si le test est gratuit
    
    # Relations
    sections = db.relationship('TestSection', back_populates='test', lazy=True, cascade='all, delete-orphan')
    questions = db.relationship('Question', back_populates='test', lazy=True, cascade='all, delete-orphan')

class TestSection(db.Model):
    __tablename__ = 'test_sections'
    
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    section_type = db.Column(db.String(20), nullable=False)  # 'reading', 'qcm', 'writing'
    order = db.Column(db.Integer, nullable=False)
    
    # Relations
    test = db.relationship('Test', back_populates='sections')
    questions = db.relationship('Question', back_populates='section', cascade='all, delete-orphan')
    criteria = db.relationship('WritingCriteria', back_populates='section', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<TestSection {self.title}>'

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=True)  # Rendu nullable
    section_id = db.Column(db.Integer, db.ForeignKey('test_sections.id'), nullable=True)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), nullable=False)  # qcm, text, reference
    points = db.Column(db.Integer, nullable=False, default=1)
    reference_start = db.Column(db.Integer)  # Pour les questions faisant référence au texte
    reference_end = db.Column(db.Integer)
    
    # Relations
    answers = db.relationship('Answer', backref='question', lazy=True, cascade='all, delete-orphan')
    user_answers = db.relationship('UserAnswer', backref='question', lazy=True)
    section = db.relationship('TestSection', back_populates='questions')
    test = db.relationship('Test', back_populates='questions')

class Answer(db.Model):
    __tablename__ = 'answers'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    answer_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    explanation = db.Column(db.Text)  # Explication de la réponse

class TestSession(db.Model):
    __tablename__ = 'test_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    started_at = db.Column(db.DateTime, nullable=False)
    completed_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='in_progress')  # in_progress, completed, expired
    
def get_next_level(current_level):
    levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
    try:
        current_index = levels.index(current_level)
        if current_index < len(levels) - 1:
            return levels[current_index + 1]
    except ValueError:
        pass
    return current_level

class UserAnswer(db.Model):
    __tablename__ = 'user_answers'
    
    id = db.Column(db.Integer, primary_key=True)
    test_result_id = db.Column(db.Integer, db.ForeignKey('test_results.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    answer_id = db.Column(db.Integer, db.ForeignKey('answers.id'), nullable=True)  # Pour QCM
    text_answer = db.Column(db.Text)  # Pour les réponses textuelles (writing)
    is_correct = db.Column(db.Boolean)
    score = db.Column(db.Float)  # Pour les réponses textuelles notées
    feedback = db.Column(db.Text)  # Feedback du correcteur
    writing_score = db.Column(db.Float)  # Score spécifique pour les questions d'écriture
    is_evaluated = db.Column(db.Boolean, default=False)  # Indique si la réponse d'écriture a été évaluée

class WritingCriteria(db.Model):
    __tablename__ = 'writing_criteria'
    
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('test_sections.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    max_points = db.Column(db.Integer, nullable=False)
    
    # Relations
    section = db.relationship('TestSection', back_populates='criteria')
    performance_levels = db.relationship('WritingPerformanceLevel', back_populates='criteria', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<WritingCriteria {self.name}>'

class WritingEvaluation(db.Model):
    __tablename__ = 'writing_evaluations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_answer_id = db.Column(db.Integer, db.ForeignKey('user_answers.id'), nullable=False)
    criteria_id = db.Column(db.Integer, db.ForeignKey('writing_criteria.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)

class WritingPerformanceLevel(db.Model):
    __tablename__ = 'writing_performance_levels'
    
    id = db.Column(db.Integer, primary_key=True)
    criteria_id = db.Column(db.Integer, db.ForeignKey('writing_criteria.id'), nullable=False)
    level = db.Column(db.String(20), nullable=False)  # 'excellent', 'good', 'average', 'poor', 'very_poor'
    description = db.Column(db.Text, nullable=False)
    points = db.Column(db.Integer, nullable=False)
    
    # Relations
    criteria = db.relationship('WritingCriteria', back_populates='performance_levels')
    
    def __repr__(self):
        return f'<WritingPerformanceLevel {self.level}>'
    