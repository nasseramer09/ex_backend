from app import app, db
from models.user import User
from models.schedule import Shedual
from models.route import Route

with app.app_context():
    db.create_all()
    print("Tabeler har skapats ")