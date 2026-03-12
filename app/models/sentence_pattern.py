class SentencePattern:
    def __init__(self, id=None, name=None, description=None, created_at=None, 
                 is_public=False, term_lang_code=None, def_lang_code=None, 
                 updated_at=None, last_opened=None, user_id=None):
        self.id = id
        self.name = name
        self.description = description
        self.created_at = created_at
        self.is_public = is_public
        self.term_lang_code = term_lang_code
        self.def_lang_code = def_lang_code
        self.updated_at = updated_at
        self.last_opened = last_opened
        self.user_id = user_id

    @staticmethod
    def from_dict(data):
        if not data: return None
        return SentencePattern(
            id=data.get('Id'),
            name=data.get('Name'),
            description=data.get('Description'),
            created_at=str(data.get('CreatedAt')) if data.get('CreatedAt') else None,
            is_public=bool(data.get('IsPublic')),
            term_lang_code=data.get('TermLanguageCode'),
            def_lang_code=data.get('DefinitionLanguageCode'),
            updated_at=str(data.get('UpdateAt')) if data.get('UpdateAt') else None,
            last_opened=str(data.get('LastOpened')) if data.get('LastOpened') else None,
            user_id=data.get('UserId')
        )

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'description': self.description,
            'created_at': self.created_at, 'is_public': self.is_public,
            'term_lang_code': self.term_lang_code, 'def_lang_code': self.def_lang_code,
            'updated_at': self.updated_at, 'last_opened': self.last_opened,
            'user_id': self.user_id
        }
