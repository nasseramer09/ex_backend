from flask import Flask, jsonify, request, Blueprint
from app.services.user_services import User_Services

user_blueprint = Blueprint('users', __name__, url_prefix='api/users')
User_Services = User_Services()

@user_blueprint.route('/create', methods=['POST'])
def createAccount():

    user_data = request.get_json()

    if not user_data:
        return jsonify({'messafe': 'Inga värde har motagits '}), 400

    new_user, status_kod = User_Services.createAccount(user_data)

    if isinstance(new_user, dict) and 'message' in new_user:
        return jsonify(new_user), status_kod
    else:

        return jsonify(new_user.user_to_dic()), 201
        
@user_blueprint.route('/<int:user_id>', methods=['GET'])
def getAccount(user_id):

    user = User_Services.get_user_by_id(user_id)

    if user:
        return jsonify(user.user_to_dic()), 200
    else:
        return jsonify({"message": "kunde inte hämta användare med id: {user_id}"}), 404
    

@user_blueprint.route('/get_all_users', methods=['GET'])
def get_all_users():

    users = User_Services.get_all_users()

    if users:
        users_list = [user.user_to_dic() for user in users]
        return jsonify(users_list), 200
    else:
        return jsonify({"message": "kunde inte hämta användare med id: {user_id}"}), 404
    
@user_blueprint.route('/<int:user_id>', methods=['PATCH'])
def update_user(user_id):
    user_data = request.get_json()
    if not user_data:
        return jsonify({'message': 'Ingen uppdatering mottaget'}), 400
    
    update_user = User_Services.update_user(user_id, user_data)
    if update_user:
        return jsonify(update_user.user_to_dic()), 200
    else:
        return jsonify({'message': f"Kunde inte uppdatera användaren med ID {user_id} eller kunde inte hitta användaren"}), 400

@user_blueprint.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    success_deletation = User_Services.delete_user(user_id)

    if success_deletation:
        return '', 204
    else:
        return jsonify({"message": f"Kunde inte hitta användare med id {user_id} för att ta bort"}), 404
    