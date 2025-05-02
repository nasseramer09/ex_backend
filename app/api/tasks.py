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

    task = tasks_services.get_task_by_id(task_id)

    if task:
        return jsonify(task.to_dic()), 200
    else:
        return jsonify({"message": "Kunde inte hämta uppdraget med id: {task_id}"}), 404
    

@tasks_blueprint.route('/get_all_tasks', methods=['GET'])
def get_all_tasks():


    tasks, status_kod = tasks_services.get_all_tasks()
    if tasks:
        task_list = [task.to_dic() for task in tasks]
        return jsonify(task_list), status_kod
    else:
        return jsonify({"message": "Kunde inte hämta tasks"}), 400
