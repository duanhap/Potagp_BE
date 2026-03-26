class Flashcard:
    def __init__(self, id=None, order=None, word_id=None, flashcard_game_id=None):
        self.id = id
        self.order = order
        self.word_id = word_id
        self.flashcard_game_id = flashcard_game_id

    @staticmethod
    def from_dict(data):
        if not data: return None
        return Flashcard(
            id=data.get('Id'),
            order=data.get('Order'),
            word_id=data.get('WordId'),
            flashcard_game_id=data.get('FlashcardGameId')
        )

    def to_dict(self):
        return {
            'id': self.id, 
            'order': self.order, 
            'word_id': self.word_id, 
            'flashcard_game_id': self.flashcard_game_id
        }
