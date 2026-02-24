from flask import Blueprint, request, jsonify
from middleware.auth import jwt_required_custom, get_current_user
from utils.db import get_db
from services.advanced_scrum_master import AdvancedScrumMaster
from datetime import datetime

scrum_bp = Blueprint('scrum', __name__)
scrum_service = AdvancedScrumMaster()

@scrum_bp.route('/scrum/generate', methods=['POST'])
@jwt_required_custom
def generate_scrum_schedule():
    try:
        data = request.get_json()
        user_id = get_current_user()
        
        prompt = data.get('prompt', 'Generate construction schedule')
        floors = data.get('floors', 'G+1')
        season = data.get('season', 'summer')
        
        # Generate realistic schedule with Granite LLM
        schedule = scrum_service.generate_realistic_schedule(prompt, floors, season)
        
        # Save to database
        db = get_db()
        schedule_doc = {
            'user_id': user_id,
            'prompt': prompt,
            'floors': floors,
            'season': season,
            'schedule': schedule,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = db.scrum_schedules.insert_one(schedule_doc)
        schedule_doc['_id'] = str(result.inserted_id)
        schedule_doc['created_at'] = schedule_doc['created_at'].isoformat()
        schedule_doc['updated_at'] = schedule_doc['updated_at'].isoformat()
        
        return jsonify({
            'message': 'Realistic Scrum schedule generated successfully',
            'schedule': schedule_doc
        }), 201
        
    except Exception as e:
        print(f"Generate schedule error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@scrum_bp.route('/scrum/delay', methods=['POST'])
@jwt_required_custom
def handle_delay():
    try:
        data = request.get_json()
        user_id = get_current_user()
        db = get_db()
        
        schedule_id = data.get('schedule_id')
        task_name = data.get('task_name')
        delay_days = data.get('delay_days', 0)
        
        # Get existing schedule
        from bson import ObjectId
        schedule_doc = db.scrum_schedules.find_one({
            '_id': ObjectId(schedule_id),
            'user_id': user_id
        })
        
        if not schedule_doc:
            return jsonify({'error': 'Schedule not found'}), 404
        
        # Handle delay
        updated_schedule = scrum_service.handle_delay(
            schedule_doc['schedule'],
            {'task_name': task_name, 'delay_days': delay_days}
        )
        
        # Update database
        db.scrum_schedules.update_one(
            {'_id': ObjectId(schedule_id)},
            {'$set': {
                'schedule': updated_schedule,
                'updated_at': datetime.utcnow()
            }}
        )
        
        # Get updated document
        updated_doc = db.scrum_schedules.find_one({'_id': ObjectId(schedule_id)})
        updated_doc['_id'] = str(updated_doc['_id'])
        updated_doc['created_at'] = updated_doc['created_at'].isoformat()
        updated_doc['updated_at'] = updated_doc['updated_at'].isoformat()
        
        return jsonify({
            'message': 'Delay handled successfully',
            'schedule': updated_doc
        }), 200
        
    except Exception as e:
        print(f"Handle delay error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@scrum_bp.route('/scrum/checklist', methods=['POST'])
@jwt_required_custom
def update_checklist():
    try:
        data = request.get_json()
        user_id = get_current_user()
        db = get_db()
        
        schedule_id = data.get('schedule_id')
        task_name = data.get('task_name')
        checklist_item = data.get('checklist_item')
        completed = data.get('completed', False)
        
        # Get existing schedule
        from bson import ObjectId
        schedule_doc = db.scrum_schedules.find_one({
            '_id': ObjectId(schedule_id),
            'user_id': user_id
        })
        
        if not schedule_doc:
            return jsonify({'error': 'Schedule not found'}), 404
        
        # Update checklist
        updated_schedule = scrum_service.update_checklist(
            schedule_doc['schedule'],
            task_name,
            checklist_item,
            completed
        )
        
        # Update database
        db.scrum_schedules.update_one(
            {'_id': ObjectId(schedule_id)},
            {'$set': {
                'schedule': updated_schedule,
                'updated_at': datetime.utcnow()
            }}
        )
        
        # Get updated document
        updated_doc = db.scrum_schedules.find_one({'_id': ObjectId(schedule_id)})
        updated_doc['_id'] = str(updated_doc['_id'])
        updated_doc['created_at'] = updated_doc['created_at'].isoformat()
        updated_doc['updated_at'] = updated_doc['updated_at'].isoformat()
        
        return jsonify({
            'message': 'Checklist updated successfully',
            'schedule': updated_doc
        }), 200
        
    except Exception as e:
        print(f"Update checklist error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@scrum_bp.route('/scrum/schedules', methods=['GET'])
@jwt_required_custom
def get_schedules():
    try:
        user_id = get_current_user()
        db = get_db()
        
        schedules = list(db.scrum_schedules.find({'user_id': user_id}))
        
        for schedule in schedules:
            schedule['_id'] = str(schedule['_id'])
            schedule['created_at'] = schedule['created_at'].isoformat()
            schedule['updated_at'] = schedule['updated_at'].isoformat()
        
        return jsonify({'schedules': schedules}), 200
        
    except Exception as e:
        print(f"Get schedules error: {str(e)}")
        return jsonify({'error': str(e)}), 500
