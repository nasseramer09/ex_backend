from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Lesson(db.Model):
    __tablename__ = 'lessons'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    image_url = db.Column(db.String(255))
    order_index = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f'<Lesson {self.title}>'
