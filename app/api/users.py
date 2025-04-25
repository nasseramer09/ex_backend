from flask import Falsk, jsonify, request, Blueprint
from app.services.user_services import User_Services

user_blueprint = Blueprint('users', __name__, url_prefix='api/users')
User_Services = User_Services()

@user_blueprint.route('/create', methods=['POST'])
def createAcount():

    user_data = request.get_json()

    if not user_data:
        return jsonify({'messafe': 'Inga värde har motagits '}), 400

    new_user = User_Services.createAcount(user_data)

    if new_user:
        return jsonify(new_user.to_dict()), 201
    else:

        return jsonify({"message": "kunde inte skapa användare"}), 500
        