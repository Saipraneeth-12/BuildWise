from datetime import datetime

class Document:
    @staticmethod
    def create(data, user_id):
        return {
            'user_id': user_id,
            'project_id': data.get('project_id'),
            'name': data.get('name'),
            'type': data.get('type'),
            'url': data.get('url'),
            'size': data.get('size'),
            'created_at': datetime.utcnow()
        }
