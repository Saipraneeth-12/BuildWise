from flask import Blueprint, request, jsonify
from middleware.auth import jwt_required_custom
from services.material_estimator import MaterialEstimator

materials_bp = Blueprint('materials', __name__)

@materials_bp.route('/estimate', methods=['POST'])
@jwt_required_custom
def estimate_materials():
    try:
        data = request.get_json()
        
        built_up_area = float(data.get('built_up_area', 0))
        floors = int(data.get('floors', 1))
        structure_type = data.get('structure_type', 'RCC')
        
        estimate = MaterialEstimator.estimate(built_up_area, floors, structure_type)
        
        return jsonify({'estimate': estimate}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
