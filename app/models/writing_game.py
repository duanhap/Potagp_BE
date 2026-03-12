class WritingGame:
    def __init__(self, id=None, created_at=None, completed_time=None, pattern_id=None):
        self.id = id
        self.created_at = created_at
        self.completed_time = completed_time
        self.pattern_id = pattern_id

    @staticmethod
    def from_dict(data):
        if not data: return None
        return WritingGame(
            id=data.get('Id'),
            created_at=str(data.get('CreatedAt')) if data.get('CreatedAt') else None,
            completed_time=str(data.get('CompletedTime')) if data.get('CompletedTime') else None,
            pattern_id=data.get('SetencePatternId')
        )

    def to_dict(self):
        return {
            'id': self.id, 'created_at': self.created_at,
            'completed_time': self.completed_time, 'pattern_id': self.pattern_id
        }
