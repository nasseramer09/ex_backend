from flask import Flask, request
from dotenv import load_dotenv
import os
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError, WrongTokenError

def create_app():
    load_dotenv()

    app = Flask(__name__)

    TEMP_TEST_JWT_SECRET_KEY = "EN_MYCKET_ENKEL_HEMLIGHET_FOR_TESTNING_123" 

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_flask_secret_if_not_set')
    app.config['JWT_SECRET_KEY'] = TEMP_TEST_JWT_SECRET_KEY 
    
    jwt = JWTManager(app)
    
    # Updated CORS configuration
    CORS(app, 
        resources={
            r"/api/*": {
                "origins": ["http://localhost:5173"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                "allow_headers": ["Content-Type", "Authorization", "Accept"],
                "expose_headers": ["Content-Type", "Authorization"],
                "supports_credentials": True,
                "max_age": 3600
            }
        },
        supports_credentials=True
    )

    @app.errorhandler(422)
    @app.errorhandler(401)
    def handle_auth_errors(e):
        if isinstance(e, (NoAuthorizationError, InvalidHeaderError, WrongTokenError)):
            return {"msg": str(e)}, 401 
        return {"msg": "Authentication failed or token invalid.", "details": str(e)}, 401
    
    @jwt.additional_claims_loader
    def add_claims_to_access_token(identity):
        from app.services.user_services import User_Services
        user_services = User_Services()
        user, status_kod = user_services.get_user_by_id(int(identity))

        print(f"DEBUG BACKEND: additional_claims_loader called for identity: {identity}")
        if user and status_kod == 200:
            print(f"DEBUG BACKEND: User {identity} found, assigning role: {user.role}")
            return {"role": user.role}
        print(f"DEBUG BACKEND: User {identity} not found or error (status: {status_kod}).")
        return {}

    from .api.users import user_blueprint
    from .api.tasks import tasks_blueprint
    from .api.car import cars_blueprint

    app.register_blueprint(user_blueprint, url_prefix='/api/users')
    app.register_blueprint(tasks_blueprint, url_prefix='/api/tasks')
    app.register_blueprint(cars_blueprint, url_prefix='/api/cars')
    return app