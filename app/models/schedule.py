from app import db
from datetime import datetime

class Schedule(db.Model):
    __tablename__='schedules'

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.string(250), nullable = False)
    date = db.Column(db.DateTime, nullable = False, default = datetime.now(datetime.timezone.utc))
    description=db.Column(db.Text, nullable=True)
    startTime = db.Column(db.DateTime, nullable=True)
    endTime = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Boolean, default=False)

    tasks = db.relationship('Task', backref = 'schedule', lazy = True)

    def __repr__(self):
        return f'<Schedule {self.title}>'