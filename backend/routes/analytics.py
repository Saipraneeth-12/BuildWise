from flask import Blueprint, request, jsonify
from middleware.auth import jwt_required_custom, get_current_user
from utils.db import get_db
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics/dashboard', methods=['GET'])
@jwt_required_custom
def get_dashboard_analytics():
    try:
        user_id = get_current_user()
        db = get_db()
        
        # Get real data from database
        projects = list(db.projects.find({'user_id': user_id}))
        expenses = list(db.expenses.find({'user_id': user_id}))
        tasks = list(db.tasks.find({'user_id': user_id}))
        budget = db.budgets.find_one({'user_id': user_id})
        
        # Calculate real metrics
        total_projects = len(projects)
        active_projects = len([p for p in projects if p.get('status') == 'active'])
        completed_projects = len([p for p in projects if p.get('status') == 'completed'])
        
        # Ensure amounts are numeric
        total_spent = sum(float(exp.get('amount', 0)) for exp in expenses)
        total_budget = float(budget.get('total_budget', 0)) if budget else 0.0
        budget_remaining = total_budget - total_spent
        
        completed_tasks = len([t for t in tasks if t.get('completed')])
        total_tasks = len(tasks)
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Monthly expense trend (last 6 months)
        monthly_expenses = {}
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        current_month = datetime.utcnow().month
        for i in range(6):
            month_idx = (current_month - i - 1) % 12
            month_key = months[month_idx]
            monthly_expenses[month_key] = 0
        
        for expense in expenses:
            exp_date = expense.get('created_at', datetime.utcnow())
            if isinstance(exp_date, str):
                try:
                    exp_date = datetime.fromisoformat(exp_date.replace('Z', '+00:00'))
                except:
                    exp_date = datetime.utcnow()
            month_key = months[exp_date.month - 1]
            if month_key in monthly_expenses:
                monthly_expenses[month_key] += float(expense.get('amount', 0))
        
        # Category-wise expenses
        category_expenses = {}
        if expenses:
            for expense in expenses:
                category = expense.get('category', 'other')
                category_expenses[category] = category_expenses.get(category, 0) + float(expense.get('amount', 0))
        else:
            # Default categories if no expenses
            category_expenses = {'materials': 0, 'labour': 0, 'equipment': 0, 'other': 0}
        
        analytics = {
            'overview': {
                'total_projects': total_projects,
                'active_projects': active_projects,
                'completed_projects': completed_projects,
                'total_budget': total_budget,
                'total_spent': total_spent,
                'budget_remaining': budget_remaining,
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'completion_rate': round(completion_rate, 2)
            },
            'monthly_trend': [
                {'month': month, 'amount': monthly_expenses[month]}
                for month in list(monthly_expenses.keys())[::-1]
            ],
            'category_breakdown': [
                {'category': cat, 'amount': amt}
                for cat, amt in category_expenses.items()
            ]
        }
        
        return jsonify({'analytics': analytics}), 200
    except Exception as e:
        print(f"Dashboard analytics error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/analytics/reports', methods=['GET'])
@jwt_required_custom
def get_reports():
    try:
        user_id = get_current_user()
        db = get_db()
        
        # Generate comprehensive reports
        projects = list(db.projects.find({'user_id': user_id}))
        expenses = list(db.expenses.find({'user_id': user_id}))
        
        # Default project if none exist
        project_performance = []
        if projects:
            project_performance = [
                {
                    'name': p.get('name', 'Unnamed Project'),
                    'progress': p.get('progress', 0),
                    'budget': p.get('budget', 0),
                    'spent': p.get('spent', 0),
                    'status': p.get('status', 'planning')
                }
                for p in projects
            ]
        else:
            # Sample data if no projects
            project_performance = [
                {
                    'name': 'Sample Project',
                    'progress': 0,
                    'budget': 0,
                    'spent': 0,
                    'status': 'planning'
                }
            ]
        
        reports = {
            'project_performance': project_performance,
            'expense_summary': {
                'total': sum(float(e.get('amount', 0)) for e in expenses),
                'average': sum(float(e.get('amount', 0)) for e in expenses) / len(expenses) if expenses else 0,
                'highest': max((float(e.get('amount', 0)) for e in expenses), default=0),
                'count': len(expenses)
            }
        }
        
        return jsonify({'reports': reports}), 200
    except Exception as e:
        print(f"Reports error: {str(e)}")
        return jsonify({'error': str(e)}), 500
