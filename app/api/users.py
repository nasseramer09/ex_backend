from flask import Flask, jsonify, request, Blueprint
from app.services.user_services import User_Services
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required
from app.utils.decorators import role_required
from app.models.users_model import User
from app.models.tasks_model import Task

user_blueprint = Blueprint('users', __name__, url_prefix='/api/users')
user_services = User_Services()

@user_blueprint.route('/create', methods=['POST'])
@role_required(['admin'])
def createAccount():

    user_data = request.get_json()

    if not user_data:
        return jsonify({'message': 'Inga värde har motagits '}), 400
    if 'email' not in user_data or not user_data['email']:
        return jsonify({'message': 'E-postadress saknas '}), 400
    if 'password' not in user_data or not user_data['password']:
        return jsonify({'message': 'Lösenord saknas'}), 400
    
    new_user_result, status_kod = user_services.createAccount(user_data)

    if isinstance(new_user_result, User):
        return jsonify(new_user_result.user_to_dic()), status_kod
    
    elif isinstance(new_user_result, dict) and 'message' in new_user_result:
        return jsonify(new_user_result), status_kod
    
    else:
        return jsonify({"message": "Kunde inte skapa användare "}), 500
        
@user_blueprint.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def getAccount(user_id):
    user_result, status_kod = user_services.get_user_by_id(user_id)

    if isinstance(user_result, User):
        return jsonify(user_result.user_to_dic(include_tasks=True)), status_kod
    
    elif isinstance(user_result, dict) and 'message' in user_result:
        return jsonify(user_result), status_kod
    else:
        return jsonify({"message": f"kunde inte hämta användare med id: {user_id}"}), 500
    

@user_blueprint.route('/get_all_users', methods=['GET'])
@role_required(['admin', 'personal'])
def get_all_users():
    try:
        users_list, status_kod = user_services.get_all_users()
        if users_list:
            if status_kod != 200:
                return jsonify({"message": "Kunde inte hämta användare"}), status_kod
            
        if not users_list:
            return jsonify([]), 200
        
        users_dicts = []
        for user in users_list:
            if isinstance(user, User):
                users_dicts.append(user.user_to_dic(include_tasks=False))
            else:
                print(f"Varning: Icke-User objekt hittades i users_list: {user}")

        return jsonify(users_dicts), 200
    except Exception as e:
        print(f"Error in get_all_users endpoint: {e}")
        return jsonify({"message": "Ett fel uppstod vid hämtning av användare"}), 500
    
@user_blueprint.route('/<int:user_id>', methods=['PATCH'])
@role_required(['admin'])
def update_user(user_id):
    user_data = request.get_json()
    if not user_data:
        return jsonify({'message': 'Ingen uppdatering mottaget'}), 400
    
    update_user_result, status_kod = user_services.update_user(user_id, user_data)

    if isinstance(update_user_result, User):
        return jsonify(update_user_result.user_to_dic(include_tasks=True)), status_kod
    
    elif isinstance(update_user_result, dict) and 'message' in update_user_result:
        return jsonify(update_user_result), status_kod
    else:
        return jsonify({'message': f"Kunde inte uppdatera användaren med ID {user_id} "}), 500

@user_blueprint.route('/<int:user_id>', methods=['DELETE'])
@role_required(['admin'])
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
        access_token = create_access_token(identity = str(user.id))
        return jsonify({"access_token": access_token,
                         "user_id":user.id,
                         "user_role":user.role}), 200
    else:
        return jsonify({'message': "Inloggning misslyckades. Fel E-post eller lösenord "}), 401
    
@user_blueprint.route('/check_auth_status', methods=['GET'])
@jwt_required(optional=True)
def check_auth_status():
    current_user_id = get_jwt_identity()
    if current_user_id:
        claims = get_jwt()
        user_role = claims.get('role')
        return jsonify({
            "isLoggedIn": True,
            "user_id": int(current_user_id),
            "user_role": user_role
        }), 200
    return jsonify({"isLoggedIn": False}), 200