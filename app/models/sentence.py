class Sentence:
    def __init__(self, id=None, term=None, definition=None, created_at=None, 
                 status='unknown', mistakes=0, pattern_id=None, last_opened=None,
                 term_language_code=None, definition_language_code=None):
        self.id = id
        self.term = term
        self.definition = definition
        self.created_at = created_at
        self.status = status
        self.mistakes = mistakes
        self.pattern_id = pattern_id
        self.last_opened = last_opened
        self.term_language_code = term_language_code
        self.definition_language_code = definition_language_code

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
            pattern_id=data.get('SetencePatternId'),
            last_opened=str(data.get('LastOpened')) if data.get('LastOpened') else None,
            term_language_code=data.get('TermLanguageCode'),
            definition_language_code=data.get('DefinitionLanguageCode')
        )

    def to_dict(self):
        return {
            'id': self.id, 'term': self.term, 'definition': self.definition,
            'created_at': self.created_at, 'status': self.status,
            'number_of_mistakes': self.mistakes, 'sentence_pattern_id': self.pattern_id,
            'last_opened': self.last_opened,
            'term_language_code': self.term_language_code,
            'definition_language_code': self.definition_language_code
        }
