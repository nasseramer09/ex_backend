from flask import request, jsonify, Blueprint
from app.services.task_services import Task_services
from app.models.tasks_model import Task
from flask_jwt_extended import jwt_required, get_jwt_identity

tasks_blueprint=Blueprint('tasks', __name__, url_prefix='/api/tasks')
tasks_services = Task_services()

@tasks_blueprint.route('/create_task', methods=['POST'])
def create_Task():
    try:
        task_data = request.get_json()

        if not task_data:
            return jsonify({"message": "Inga värde har motagits"}), 400
        
        required_fields = ['title', 'start_time', 'end_time', 'start_adress', 'destination_adress', 'car_ids', 'assigned_users']
        missing_fields = [field for field in required_fields if field not in task_data]
        
        if missing_fields:
            return jsonify({
                "message": f"Saknade obligatoriska fält: {', '.join(missing_fields)}"
            }), 400
        
        new_task_result, status_kod = tasks_services.create_task(task_data)

        if status_kod == 200:
            return jsonify(new_task_result), status_kod
        
        elif isinstance(new_task_result, dict) and 'message' in new_task_result:
            return jsonify(new_task_result), status_kod
        else:
            return jsonify({"message": "Kunde inte skapa uppgift"}), 500
            
    except Exception as e:
        return jsonify({"message": f"Ett fel uppstod vid skapandet av uppgiften: {str(e)}"}), 500
    

@tasks_blueprint.route('/<int:task_id>', methods=['GET'])
def get_task(task_id):

    task_result, status_kod = tasks_services.get_task_by_id(task_id)

    if status_kod==200:
        
        return jsonify(task_result), status_kod
    
    elif isinstance(task_result, dict) and 'message' in task_result:
        return jsonify(task_result), status_kod
    else:
        return jsonify({"message": f"Kunde inte hämta uppdraget med id: {task_id}"}), 500
    

@tasks_blueprint.route('/get_all_tasks', methods=['GET'])
def get_all_tasks():
    tasks_list, status_kod = tasks_services.get_all_tasks()
    if isinstance(tasks_list, list):
        return jsonify(tasks_list), status_kod
    
    else:
        return jsonify(tasks_list), status_kod

@tasks_blueprint.route('/<int:task_id>', methods=['PATCH'])
def update_task(task_id):
    task_data = request.get_json()

    if not task_data:
        return jsonify({"message": "Ingen uppdatering mottaget "}), 400
    
    uppdated_task_result, status_kod = tasks_services.update_task(task_id, task_data)
   
    if status_kod== 200:
        
        return jsonify(uppdated_task_result), status_kod
    
    elif isinstance(uppdated_task_result, dict) and 'message' in uppdated_task_result:
        return jsonify(uppdated_task_result), status_kod
    
    else:
        return jsonify({"message": f" Kunde inte uppdatera uppgiften med id {task_id}"}), 500
    

@tasks_blueprint.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    deletation_result, status_kod = tasks_services.delete_task(task_id)
    return jsonify(deletation_result), status_kod
    

@tasks_blueprint.route('/get_user_tasks/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_tasks(user_id):
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({"message": "Ingen inloggad användare"}), 401
            
        tasks_list, status_kod = tasks_services.get_user_tasks(user_id)
        
        if isinstance(tasks_list, list):
            return jsonify(tasks_list), status_kod
        else:
            return jsonify(tasks_list), status_kod
            
    except Exception as e:
        print(f"Error in get_user_tasks endpoint: {str(e)}")
        return jsonify({"message": f"Ett fel uppstod vid hämtning av användarens uppgifter: {str(e)}"}), 500
    
