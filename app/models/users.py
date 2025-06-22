import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    subscription_status = db.Column(db.String(50), nullable=False, default='inactive')

    def __repr__(self):
        return f'<User {self.email}>'

    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def user_to_dic(self):
        user_dict = {
            'id': self.id,
            'first_name': self.first_name,
            'last_name':self.last_name,
            'username':self.username,
            'role': self.role,
            'phone_number' : self.phone_number,
            'email' : self.email,
            'created_at':self.created_at.isoformat() if self.created_at else None,
        }
        return user_dict

