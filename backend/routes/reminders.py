from flask import Blueprint, request, jsonify
from bson import ObjectId
from middleware.auth import jwt_required_custom, get_current_user
from utils.db import get_db
from models.reminder import Reminder

reminders_bp = Blueprint('reminders', __name__)

@reminders_bp.route('/reminders', methods=['GET'])
@jwt_required_custom
def get_reminders():
    try:
        user_id = get_current_user()
        db = get_db()
        
        reminders = list(db.reminders.find({'user_id': user_id}))
        
        for reminder in reminders:
            reminder['_id'] = str(reminder['_id'])
            reminder['created_at'] = reminder['created_at'].isoformat()
        
        return jsonify({'reminders': reminders}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reminders_bp.route('/reminders', methods=['POST'])
@jwt_required_custom
def create_reminder():
    try:
        data = request.get_json()
        user_id = get_current_user()
        db = get_db()
        
        reminder_data = Reminder.create(data, user_id)
        result = db.reminders.insert_one(reminder_data)
        
        reminder_data['_id'] = str(result.inserted_id)
        reminder_data['created_at'] = reminder_data['created_at'].isoformat()
        
        return jsonify({'reminder': reminder_data}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
