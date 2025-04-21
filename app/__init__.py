from flask import Flask
from flask_sqlalchemy import SQLALCHEMY
from flask_session import Session 
from .config import Config


db= SQLALCHEMY()
session = Session()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    session.init_app(app)

    


