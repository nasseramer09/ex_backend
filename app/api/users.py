from flask import Flask, jsonify, request, Blueprint
from app.services.user_services import User_Services
from flask_jwt_extended import create_access_token, JWTManager

from app.models.users_model import User

user_blueprint = Blueprint('users', __name__, url_prefix='/api/users')
user_services = User_Services()

@user_blueprint.route('/create', methods=['POST'])
def createAccount():

    user_data = request.get_json()

    if not user_data:
        return jsonify({'message': 'Inga värde har motagits '}), 400

    if 'email' not in user_data or not user_data['email']:
        return jsonify({'message': 'E-postadress saknas '}), 400
    if 'password_hash' not in user_data or not user_data['password']:
        return jsonify({'message': 'Lösenord saknas'}), 400
    
    new_user_result, status_kod = user_services.createAccount(user_data)

    if isinstance(new_user_result, User):
        return jsonify(new_user_result.user_to_dic()), status_kod
    
    elif isinstance(new_user_result, dict) and 'message' in new_user_result:
        return jsonify(new_user_result), status_kod
    
    else:
        return jsonify({"message": "Kunde inte skapa användare "}), 500
        
@user_blueprint.route('/<int:user_id>', methods=['GET'])
def getAccount(user_id):

    user_result, status_kod = user_services.get_user_by_id(user_id)

    if isinstance(user_result, User):
        return jsonify(user_result.user_to_dic()), status_kod
    
    elif isinstance(user_result, dict) and 'message' in user_result:
        return jsonify(user_result), status_kod
    else:
        return jsonify({"message": f"kunde inte hämta användare med id: {user_id}"}), 500
    

@user_blueprint.route('/get_all_users', methods=['GET'])
def get_all_users():

    users_list, status_kod = user_services.get_all_users()

    if users_list:
        users_dicts = [user.user_to_dic() for user in users_list if isinstance(user, User)]
        return jsonify(users_dicts), status_kod
    else:
        
        return jsonify(users_list), status_kod
    
@user_blueprint.route('/<int:user_id>', methods=['PATCH'])
def update_user(user_id):
    user_data = request.get_json()
    if not user_data:
        return jsonify({'message': 'Ingen uppdatering mottaget'}), 400
    
    update_user_result, status_kod = User_Services.update_user(user_id, user_data)

    if isinstance(update_user_result, User):
        return jsonify(update_user_result.user_to_dic()), status_kod
    
    elif isinstance(update_user_result, dict) and 'message' in update_user_result:
        return jsonify(update_user_result), status_kod
    else:
        return jsonify({'message': f"Kunde inte uppdatera användaren med ID {user_id} "}), 500

@user_blueprint.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    deletation_result, status_kod = user_services.delete_user(user_id)
    return jsonify(deletation_result), status_kod

@user_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'E-post och lösenord krävs '}), 400
    
    email = data['email']
    password = data['password']

    user, status_kod = user_services.get_user_by_email(email)

    if user and isinstance(user, User) and user_services.verify_password(user, password):
        access_token = create_access_token(identity = user.id)
        return jsonify({"access_token": access_token, "user":user.user_to_dic()}), 200
    else:
        return jsonify({'message': "Inloggning misslyckades. Fel E-post eller lösenord "}), 401