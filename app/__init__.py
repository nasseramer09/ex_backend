from flask import Flask
from dotenv import load_dotenv
import os

def create_app():

    load_dotenv()
    
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

    from .api.users import user_blueprint 
    from .api.tasks import tasks_blueprint

    app.register_blueprint(user_blueprint, url_prefix='/api/users')
    app.register_blueprint(tasks_blueprint, url_prefix='/api/tasks')
   
    return app