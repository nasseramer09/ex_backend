from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserProgress(db.Model):
    __tablename__ = 'user_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lessons_completed = db.Column(db.Integer, default=0, nullable=False)
    quiz_accuracy = db.Column(db.Float, default=0.0, nullable=False)
    study_streak = db.Column(db.Integer, default=0, nullable=False)
    total_study_time = db.Column(db.Integer, default=0, nullable=False)  # i minuter eller sekunder

    user = db.relationship('User', backref=db.backref('progress', lazy=True))

    def __repr__(self):
        return f'<UserProgress user_id={self.user_id}>'
