class Sentence:
    def __init__(self, id=None, term=None, definition=None, created_at=None, 
                 status=None, mistakes=0, pattern_id=None):
        self.id = id
        self.term = term
        self.definition = definition
        self.created_at = created_at
        self.status = status
        self.mistakes = mistakes
        self.pattern_id = pattern_id

    @staticmethod
    def from_dict(data):
        if not data: return None
        return Sentence(
            id=data.get('Id'),
            term=data.get('Term'),
            definition=data.get('Definition'),
            created_at=str(data.get('CreatedAt')) if data.get('CreatedAt') else None,
            status=data.get('Status'),
            mistakes=data.get('NumberOfMistakes', 0),
            pattern_id=data.get('SetencePatternId')
        )

    def to_dict(self):
        return {
            'id': self.id, 'term': self.term, 'definition': self.definition,
            'created_at': self.created_at, 'status': self.status,
            'mistakes': self.mistakes, 'pattern_id': self.pattern_id
        }
