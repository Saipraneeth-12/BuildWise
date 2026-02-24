from datetime import datetime

class Expense:
    @staticmethod
    def create(data, user_id):
        return {
            'user_id': user_id,
            'project_id': data.get('project_id'),
            'category': data.get('category'),
            'amount': float(data.get('amount', 0)),  # Convert to float
            'description': data.get('description'),
            'date': data.get('date', datetime.utcnow()),
            'created_at': datetime.utcnow()
        }
