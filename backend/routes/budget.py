from flask import Blueprint, request, jsonify
from middleware.auth import jwt_required_custom, get_current_user
from utils.db import get_db
from datetime import datetime

budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/budget', methods=['GET'])
@jwt_required_custom
def get_budget():
    try:
        user_id = get_current_user()
        db = get_db()
        
        budget = db.budgets.find_one({'user_id': user_id})
        
        if not budget:
            # Create default budget
            budget = {
                'user_id': user_id,
                'total_budget': 0,
                'allocated': 0,
                'spent': 0,
                'remaining': 0,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            result = db.budgets.insert_one(budget)
            budget['_id'] = result.inserted_id
        
        budget['_id'] = str(budget['_id'])
        budget['created_at'] = budget['created_at'].isoformat()
        budget['updated_at'] = budget['updated_at'].isoformat()
        
        return jsonify({'budget': budget}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@budget_bp.route('/budget', methods=['PUT'])
@jwt_required_custom
def update_budget():
    try:
        data = request.get_json()
        user_id = get_current_user()
        db = get_db()
        
        total_budget = float(data.get('total_budget', 0))
        
        update_data = {
            'total_budget': total_budget,
            'updated_at': datetime.utcnow()
        }
        
        # Calculate remaining based on expenses
        expenses = list(db.expenses.find({'user_id': user_id}))
        total_spent = sum(float(exp.get('amount', 0)) for exp in expenses)
        
        update_data['spent'] = total_spent
        update_data['remaining'] = total_budget - total_spent
        
        db.budgets.update_one(
            {'user_id': user_id},
            {'$set': update_data},
            upsert=True
        )
        
        # Convert datetime for JSON response
        response_data = update_data.copy()
        response_data['updated_at'] = response_data['updated_at'].isoformat()
        
        return jsonify({'message': 'Budget updated', 'budget': response_data}), 200
    except Exception as e:
        print(f"Budget update error: {str(e)}")
        return jsonify({'error': str(e)}), 500
