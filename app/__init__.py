from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

from .api.users import user_blueprint 

app.register_blueprint(user_blueprint, url_prefix='/api/users')

if __name__=='__main__':
    app.run(debug=True) 