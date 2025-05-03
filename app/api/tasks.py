from flask import Flask, request, jsonify, Blueprint
from app.services.task_services import Task_services

tasks_blueprint=Blueprint('tasks', __name__, url_prefix='/api/tasks')
tasks_services = Task_services()

@tasks_blueprint.route('/create_task', methods=['POST'])
def create_Task():
    task_data = request.get_json()

    if not task_data:
        return jsonify({"message": "Inga värde har motagits "}), 400
    
    new_task, status_kod = tasks_services.create_task(task_data)

    if isinstance(new_task, dict) and len(new_task) == 2:
        task_obj, status = new_task
        return jsonify(task_obj.to_dic()), status
    elif isinstance(new_task, tuple) and 'message' in new_task:
        return jsonify(new_task.to_dic()), status_kod
    else:
        return jsonify({"message": "kunde inte skapa uppgift "}), 500
    

@tasks_blueprint.route('/<int:task_id>', methods=['GET'])
def get_task(task_id):

    task_result = tasks_services.get_task_by_id(task_id)

    if isinstance(task_result, tuple) and len(task_result)==2:
        task, status_kod = task_result
        return jsonify(task.to_dic()), status_kod
    elif isinstance(task_result, dict) and 'message' in task_result:
        return jsonify(task_result), 404
    else:
        return jsonify({"message": "Kunde inte hämta uppdraget med id: {task_id}"}), 500
    

@tasks_blueprint.route('/get_all_tasks', methods=['GET'])
def get_all_tasks():


    tasks, status_kod = tasks_services.get_all_tasks()
    if tasks:
        task_list = [task.to_dic() for task in tasks]
        return jsonify(task_list), status_kod
    else:
        return jsonify({"message": "Kunde inte hämta tasks"}), 400

@tasks_blueprint.route('/<int:task_id>', methods=['PATCH'])
def update_task(task_id):
    task_data = request.get_json()

    if not task_data:
        return jsonify({"message": "Ingen uppdatering mottaget "}), 400
    
    uppdated_task_result = tasks_services.update_task(task_id, task_data)
   
    if isinstance(uppdated_task_result, tuple) and len(uppdated_task_result) == 2:
        uppdated_task, status_kod = uppdated_task_result
        return jsonify(uppdated_task.to_dic()), status_kod
    
    elif isinstance(uppdated_task_result, dict) and 'message' in uppdated_task_result:
        return jsonify(uppdated_task_result), 404
    
    else:
        return jsonify({"message": f" Kunde inte uppdatera uppgiften med id {task_id}"}), 500
    

@tasks_blueprint.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    success_deletation= tasks_services.delete_task(task_id)

    if success_deletation:
        return '', 204
    else:
        return jsonify({"message": f"kunde inte hitta task med id: {task_id} för att ta bort "}), 404

    
