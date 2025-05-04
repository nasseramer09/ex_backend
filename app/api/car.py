from flask import request, jsonify, Blueprint
from app.services.car_services import Car_services

cars_blueprint=Blueprint('cars', __name__, url_prefix='/api/cars')
car_services = Car_services()

@cars_blueprint.route('create_car', methods=['POST'])
def create_car():
    car_data = request.get_json()

    if not car_data:
        return jsonify({"message": f"Inga värde har motagits "}), 400
    
    new_car, status_kod = car_services.insert_car(car_data)

    if isinstance(new_car, dict) and len(new_car) == 2:
        car_obj, status_kod = new_car

        return jsonify(car_obj.to_dic()), status_kod
    
    elif isinstance(new_car, tuple) and 'message' in new_car:
        return jsonify(new_car.to_dic()), status_kod
    
    else:
        return jsonify({"message": " Kunde inte skapa car"}), 500

@cars_blueprint.route('/<int:car_id>', methods=['GET'])
def get_car_by_id(car_id):
    car_result =  car_services.get_car_by_id(car_id)
    if isinstance(car_result, tuple) and len(car_result) == 2:
        car, status_kod = car_result
        return jsonify(car.to_dic()), status_kod
    elif isinstance(car_result, dict) and 'message' in car_result:
        return jsonify(car_result), 404
    
    else:
        return jsonify({"message": " Kunde inte hämta fordonet med id: {car_id}"}), 500

@cars_blueprint.route('/get_all_cars', methods=['GET'])
def get_all_cars():
    cars, status_kod = car_services.get_all_cars()
    if cars:
        car_list = [car.to_dic() for car in cars]
        return jsonify(car_list), status_kod
    else:
        return jsonify({"message": "Kunde ite hämta fordon "}), 400
    

@cars_blueprint.route('/<int:car_id>', methods=['PATCH'])
def update_car(car_id):
    car_data = request.get_json()

    if not car_data:
        return jsonify({"message": "Ingen uppdatering mottaget "}), 400
    
    update_car_result = car_services.update_car(car_id, car_data)
    print(f"error 1 {update_car_result}")
    if isinstance(update_car_result, tuple) and len(update_car_result) == 2:
        update_car, status_kod = update_car_result
        print(f"error 2 {update_car}")
        return jsonify(update_car.to_dic()), status_kod
    
    elif isinstance(update_car_result, dict) and 'message' in update_car_result:
        return jsonify(update_car_result), 404
    
    else:
        return jsonify({"message": f" Kunde inte uppdatera car med id {car_id}"}), 500
    

@cars_blueprint.route('/<int:car_id>', methods = ['DELETE'])
def delete_car(car_id):
    success_deletation= car_services.delete_car(car_id)

    if success_deletation:
        return '', 204
    else:
        return jsonify({"message": f"kunde inte hitta car med id: {car_id} för att ta bort "}), 404
