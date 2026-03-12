class Setting:
    def __init__(self, id=None, notification=False, language=None, user_id=None):
        self.id = id
        self.notification = notification
        self.language = language
        self.user_id = user_id

    @staticmethod
    def from_dict(data):
        if not data: return None
        return Setting(
            id=data.get('Id'),
            notification=bool(data.get('Notification')),
            language=data.get('Language'),
            user_id=data.get('UserId')
        )

    def to_dict(self):
        return {
            'id': self.id, 'notification': self.notification,
            'language': self.language, 'user_id': self.user_id
        }
