from flask import Blueprint, request, jsonify
from bson import ObjectId
from middleware.auth import jwt_required_custom, get_current_user
from utils.db import get_db
from models.task import Task

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/tasks', methods=['GET'])
@jwt_required_custom
def get_tasks():
    try:
        user_id = get_current_user()
        db = get_db()
        
        project_id = request.args.get('project_id')
        query = {'user_id': user_id}
        if project_id:
            query['project_id'] = project_id
        
        tasks = list(db.tasks.find(query))
        
        for task in tasks:
            task['_id'] = str(task['_id'])
            task['created_at'] = task['created_at'].isoformat()
            task['updated_at'] = task['updated_at'].isoformat()
        
        return jsonify({'tasks': tasks}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/tasks', methods=['POST'])
@jwt_required_custom
def create_task():
    try:
        data = request.get_json()
        user_id = get_current_user()
        db = get_db()
        
        task_data = Task.create(data, user_id)
        result = db.tasks.insert_one(task_data)
        
        task_data['_id'] = str(result.inserted_id)
        task_data['created_at'] = task_data['created_at'].isoformat()
        task_data['updated_at'] = task_data['updated_at'].isoformat()
        
        return jsonify({'task': task_data}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/tasks/<task_id>', methods=['PUT'])
@jwt_required_custom
def update_task(task_id):
    try:
        data = request.get_json()
        user_id = get_current_user()
        db = get_db()
        
        from datetime import datetime
        data['updated_at'] = datetime.utcnow()
        
        db.tasks.update_one(
            {'_id': ObjectId(task_id), 'user_id': user_id},
            {'$set': data}
        )
        
        return jsonify({'message': 'Task updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/tasks/<task_id>', methods=['DELETE'])
@jwt_required_custom
def delete_task(task_id):
    try:
        user_id = get_current_user()
        db = get_db()
        
        db.tasks.delete_one({'_id': ObjectId(task_id), 'user_id': user_id})
        
        return jsonify({'message': 'Task deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/tasks/generate', methods=['POST'])
@jwt_required_custom
def generate_tasks():
    try:
        data = request.get_json()
        user_id = get_current_user()
        db = get_db()
        
        prompt = data.get('prompt', '')
        project_id = data.get('project_id')
        
        # Placeholder for RAG - will be replaced with actual AI generation
        ai_response = {
            'message': 'AI-generated tracker will be created here. RAG integration pending.',
            'suggested_tasks': [
                {
                    'name': 'AI Suggested: Site Preparation',
                    'time': '8 hours',
                    'category': 'preparation',
                    'completed': False
                },
                {
                    'name': 'AI Suggested: Foundation Work',
                    'time': '16 hours',
                    'category': 'foundation',
                    'completed': False
                },
                {
                    'name': 'AI Suggested: Structure Building',
                    'time': '40 hours',
                    'category': 'construction',
                    'completed': False
                }
            ]
        }
        
        # Auto-create suggested tasks if requested
        if data.get('auto_create', False):
            created_tasks = []
            for suggested_task in ai_response['suggested_tasks']:
                task_data = Task.create({
                    'project_id': project_id,
                    'name': suggested_task['name'],
                    'time': suggested_task['time'],
                    'category': suggested_task['category'],
                    'completed': suggested_task['completed']
                }, user_id)
                result = db.tasks.insert_one(task_data)
                task_data['_id'] = str(result.inserted_id)
                task_data['created_at'] = task_data['created_at'].isoformat()
                task_data['updated_at'] = task_data['updated_at'].isoformat()
                created_tasks.append(task_data)
            
            return jsonify({
                'message': ai_response['message'],
                'tasks': created_tasks
            }), 201
        
        return jsonify(ai_response), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
