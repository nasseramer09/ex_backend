from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import JSON
from datetime import datetime

db = SQLAlchemy()

class QuizResult(db.Model):
    __tablename__ = 'quiz_results'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    questions = db.Column(db.JSON, nullable=False)  # lista av fråge-id
    answers = db.Column(db.JSON, nullable=False)    # användarens svar
    score = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(100))
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('quiz_results', lazy=True))

    def __repr__(self):
        return f'<QuizResult {self.id}>'
