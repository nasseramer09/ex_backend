from flask import Flask
from flask_sqlalchemy import SQLALCHEMY
from flask_session import Session 
from config import Config
import os


db= SQLALCHEMY()
session = Session()

def create_app():
    app = Flask(__name__)

    basedir= os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '../database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
    app.config.from_object(Config)

    session.init_app(app)
    db.init_app(app)
    
    from models.user import User
    from models.schedule import Shedual
    from models.route import Route

    with app.app_context():
        db.create_all()

    return app 

    


