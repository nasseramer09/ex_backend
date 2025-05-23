from flask import request, jsonify, Blueprint
from app.services.task_services import Task_services
from app.models.tasks_model import Task

tasks_blueprint=Blueprint('tasks', __name__, url_prefix='/api/tasks')
tasks_services = Task_services()

@tasks_blueprint.route('/create_task', methods=['POST'])
def create_Task():
    task_data = request.get_json()

    if not task_data:
        return jsonify({"message": "Inga värde har motagits "}), 400
    
    new_task_result, status_kod = tasks_services.create_task(task_data)

    if isinstance(new_task_result, Task):
        return jsonify(new_task_result.to_dic()), status_kod
    
    elif isinstance(new_task_result, dict) and 'message' in new_task_result:
        return jsonify(new_task_result), status_kod
    else:
        return jsonify({"message": "kunde inte skapa uppgift "}), 500
    

@tasks_blueprint.route('/<int:task_id>', methods=['GET'])
def get_task(task_id):

    task_result, status_kod = tasks_services.get_task_by_id(task_id)

    if isinstance(task_result, Task):
        
        return jsonify(task_result.to_dic()), status_kod
    
    elif isinstance(task_result, dict) and 'message' in task_result:
        return jsonify(task_result), status_kod
    else:
        return jsonify({"message": f"Kunde inte hämta uppdraget med id: {task_id}"}), 500
    

@tasks_blueprint.route('/get_all_tasks', methods=['GET'])
def get_all_tasks():
    tasks_list, status_kod = tasks_services.get_all_tasks()
    if isinstance(tasks_list, list):
        task_dicts = [task.to_dic() for task in tasks_list if isinstance(task, Task)]
        return jsonify(task_dicts), status_kod
    
    else:
        return jsonify(tasks_list), status_kod

@tasks_blueprint.route('/<int:task_id>', methods=['PATCH'])
def update_task(task_id):
    task_data = request.get_json()

    if not task_data:
        return jsonify({"message": "Ingen uppdatering mottaget "}), 400
    
    uppdated_task_result, status_kod = tasks_services.update_task(task_id, task_data)
   
    if isinstance(uppdated_task_result, Task):
        
        return jsonify(uppdated_task_result.to_dic()), status_kod
    
    elif isinstance(uppdated_task_result, dict) and 'message' in uppdated_task_result:
        return jsonify(uppdated_task_result), 404
    
    else:
        return jsonify({"message": f" Kunde inte uppdatera uppgiften med id {task_id}"}), 500
    

@tasks_blueprint.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    deletation_result, status_kod = tasks_services.delete_task(task_id)

    
    return jsonify(deletation_result), status_kod
    
