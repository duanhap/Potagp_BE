class FlashcardGame:
    def __init__(self, id=None, mode=None, updated_at=None, word_set_id=None):
        self.id = id
        self.mode = mode
        self.updated_at = updated_at
        self.word_set_id = word_set_id

    @staticmethod
    def from_dict(data):
        if not data: return None
        return FlashcardGame(
            id=data.get('Id'),
            mode=data.get('Mode'),
            updated_at=str(data.get('UpdatedAt')) if data.get('UpdatedAt') else None,
            word_set_id=data.get('WordSetId')
        )

    def to_dict(self):
        return {
            'id': self.id, 'mode': self.mode, 
            'updated_at': self.updated_at, 'word_set_id': self.word_set_id
        }
