class MatchGame:
    def __init__(self, id=None, created_at=None, completed_time=None, word_set_id=None):
        self.id = id
        self.created_at = created_at
        self.completed_time = completed_time
        self.word_set_id = word_set_id

    @staticmethod
    def from_dict(data):
        if not data: return None
        return MatchGame(
            id=data.get('Id'),
            created_at=str(data.get('CreatedAt')) if data.get('CreatedAt') else None,
            completed_time=data.get('CompletedTime'),
            word_set_id=data.get('WordSetId')
        )

    def to_dict(self):
        return {
            'id': self.id, 'created_at': self.created_at,
            'completed_time': self.completed_time, 'word_set_id': self.word_set_id
        }
