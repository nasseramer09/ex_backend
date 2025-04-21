from flask import Blueprint, Flask, jsonify 

user_blue_print = Blueprint('user', __name__)

@user_blue_print.route('/users', methods=['GET'])
def get_users():
    return jsonify({"message": "Här kommer alla användare"}), 200