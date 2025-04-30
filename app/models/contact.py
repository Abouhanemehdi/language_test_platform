from app import db
from datetime import datetime

class ContactRequest(db.Model):
    __tablename__ = 'contact_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Nullable car les visiteurs non connectés peuvent aussi envoyer des messages
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)  # Ajout du champ email
    phone = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(100), nullable=True)  # Ajout du champ sujet
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, contacted, completed
    source = db.Column(db.String(20), default='general')  # general, prospect
    
    # Relation avec User
    user = db.relationship('User', backref='contact_requests', lazy=True)

    def __repr__(self):
        return f'<ContactRequest {self.id} from {self.name}>' 