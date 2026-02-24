from flask import Blueprint, request, jsonify
from middleware.auth import jwt_required_custom
from services.cost_planner import CostPlanner

cost_bp = Blueprint('cost', __name__)

@cost_bp.route('/calculate', methods=['POST'])
@jwt_required_custom
def calculate_cost():
    try:
        data = request.get_json()
        
        materials = data.get('materials', {})
        prices = data.get('prices', {})
        
        cost_breakdown = CostPlanner.calculate(materials, prices)
        
        return jsonify({'cost': cost_breakdown}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
