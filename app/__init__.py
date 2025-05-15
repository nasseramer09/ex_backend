from flask import Flask
from dotenv import load_dotenv
import os
from flask_jwt_extended import JWTManager
from flask_cors import CORS

def create_app():

    load_dotenv()
    
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')

    jwt = JWTManager(app)
    CORS(app, resources={r"/api/*":{"origins": "http://localhost:5173"}})

    from .api.users import user_blueprint 
    from .api.tasks import tasks_blueprint
    from .api.car import cars_blueprint

    app.register_blueprint(user_blueprint, url_prefix='/api/users')
    app.register_blueprint(tasks_blueprint, url_prefix='/api/tasks')
    app.register_blueprint(cars_blueprint, url_prefix='/api/cars')
    
    return app