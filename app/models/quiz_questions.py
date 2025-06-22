from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import JSON

db = SQLAlchemy()

class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON, nullable=False)
    correct_answer = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(50))

    def __repr__(self):
        return f'<QuizQuestion {self.id}>'
