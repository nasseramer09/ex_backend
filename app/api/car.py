from flask import request, jsonify, Blueprint
from app.services.car_services import Car_services
from app.models.car_model import Car

cars_blueprint=Blueprint('cars', __name__, url_prefix='/api/cars')
car_services = Car_services()

@cars_blueprint.route('/create_car', methods=['POST'])
def create_car():
    car_data = request.get_json()

    if not car_data:
        return jsonify({"message": "Inga värde har motagits "}), 400
    
    new_car_results, status_kod = car_services.insert_car(car_data)

    if isinstance(new_car_results, Car):
        return jsonify(new_car_results.to_dic()), status_kod
    
    elif isinstance(new_car_results, dict) and 'message' in new_car_results:
        return jsonify(new_car_results), status_kod
    
    else:
        return jsonify({"message": " Kunde inte skapa fordon"}), 500

@cars_blueprint.route('/<int:car_id>', methods=['GET'])
def get_car_by_id(car_id):

    car_result, status_kod =  car_services.get_car_by_id(car_id)

    if isinstance(car_result, Car):
        return jsonify(car_result.to_dic()), status_kod
    
    elif isinstance(car_result, dict) and 'message' in car_result:
        return jsonify(car_result), status_kod
    
    else:
        return jsonify({"message": f" Kunde inte hämta fordonet med id: {car_id}"}), 500

@cars_blueprint.route('/get_all_cars', methods=['GET'])
def get_all_cars():
    cars_list, status_kod = car_services.get_all_cars()
    if isinstance(cars_list, list):
        car_dicts = [car.to_dic() for car in cars_list if isinstance(car, Car)]
        return jsonify(car_dicts), status_kod
    else:
        return jsonify(cars_list), status_kod
    

@cars_blueprint.route('/<int:car_id>', methods=['PATCH'])
def update_car(car_id):
    car_data = request.get_json()

    if not car_data:
        return jsonify({"message": "Ingen uppdatering mottaget "}), 400
    
    update_car_result, status_kod = car_services.update_car(car_id, car_data)

    if isinstance(update_car_result, Car):
        return jsonify(update_car_result.to_dic()), status_kod
    
    elif isinstance(update_car_result, dict) and 'message' in update_car_result:
        return jsonify(update_car_result), status_kod
    
    else:
        return jsonify({"message": f" Kunde inte uppdatera car med id {car_id}"}), 500
    

@cars_blueprint.route('/<int:car_id>', methods = ['DELETE'])
def delete_car(car_id):
    deletation_result, status_kod = car_services.delete_car(car_id)
    
    return jsonify(deletation_result), status_kod
