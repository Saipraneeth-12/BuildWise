from flask import Blueprint, request, jsonify
from bson import ObjectId
from middleware.auth import jwt_required_custom, get_current_user
from utils.db import get_db
from models.expense import Expense

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route('/expenses', methods=['GET'])
@jwt_required_custom
def get_expenses():
    try:
        user_id = get_current_user()
        db = get_db()
        
        expenses = list(db.expenses.find({'user_id': user_id}))
        
        for expense in expenses:
            expense['_id'] = str(expense['_id'])
            expense['created_at'] = expense['created_at'].isoformat()
        
        return jsonify({'expenses': expenses}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@expenses_bp.route('/expenses', methods=['POST'])
@jwt_required_custom
def create_expense():
    try:
        data = request.get_json()
        user_id = get_current_user()
        db = get_db()
        
        expense_data = Expense.create(data, user_id)
        result = db.expenses.insert_one(expense_data)
        
        expense_data['_id'] = str(result.inserted_id)
        expense_data['created_at'] = expense_data['created_at'].isoformat()
        
        return jsonify({'expense': expense_data}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
