from datetime import datetime

class Project:
    @staticmethod
    def create(data, user_id):
        return {
            'user_id': user_id,
            'name': data.get('name'),
            'description': data.get('description'),
            'budget': data.get('budget', 0),
            'spent': data.get('spent', 0),
            'progress': data.get('progress', 0),
            'status': data.get('status', 'planning'),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
