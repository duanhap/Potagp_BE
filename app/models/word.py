class Word:
    def __init__(self, id=None, term=None, definition=None, description=None, 
                 created_at=None, status=None, word_set_id=None, 
                 flashcard_game_id=None, match_game_id=None):
        self.id = id
        self.term = term
        self.definition = definition
        self.description = description
        self.created_at = created_at
        self.status = status
        self.word_set_id = word_set_id
        self.flashcard_game_id = flashcard_game_id
        self.match_game_id = match_game_id

    @staticmethod
    def from_dict(data):
        if not data: return None
        return Word(
            id=data.get('Id'),
            term=data.get('Term'),
            definition=data.get('Definition'),
            description=data.get('Description'),
            created_at=str(data.get('CreatedAt')) if data.get('CreatedAt') else None,
            status=data.get('Status'),
            word_set_id=data.get('WordSetId'),
            flashcard_game_id=data.get('FlashcardGameId'),
            match_game_id=data.get('MatchGameId')
        )

    def to_dict(self):
        return {
            'id': self.id, 'term': self.term, 'definition': self.definition,
            'description': self.description, 'created_at': self.created_at,
            'status': self.status, 'word_set_id': self.word_set_id,
            'flashcard_game_id': self.flashcard_game_id, 'match_game_id': self.match_game_id
        }
