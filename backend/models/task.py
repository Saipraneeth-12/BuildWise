from datetime import datetime

class Task:
    @staticmethod
    def create(data, user_id):
        return {
            'user_id': user_id,
            'project_id': data.get('project_id'),
            'name': data.get('name'),
            'completed': data.get('completed', False),
            'time': data.get('time', '0 hours'),
            'category': data.get('category', 'general'),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
