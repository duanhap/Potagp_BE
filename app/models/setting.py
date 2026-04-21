class Setting:
    def __init__(self, id=None, notification=False, language=None, user_id=None, experience_goal=15):
        self.id = id
        self.notification = notification
        self.language = language
        self.user_id = user_id
        self.experience_goal = experience_goal

    @staticmethod
    def from_dict(data):
        if not data: return None
        raw_notification = data.get('Notification')
        # MySQL bit(1) trả về bytes b'\x01' hoặc b'\x00'
        if isinstance(raw_notification, (bytes, bytearray)):
            notification = raw_notification != b'\x00'
        elif isinstance(raw_notification, int):
            notification = bool(raw_notification)
        else:
            notification = bool(raw_notification)
        return Setting(
            id=data.get('Id'),
            notification=notification,
            experience_goal=data.get('ExperienceGoal', 15),
            language=data.get('Language'),
            user_id=data.get('UserId')
        )

    def to_dict(self):
        return {
            'id': self.id, 'notification': self.notification,
            'language': self.language, 'user_id': self.user_id,
            'experience_goal': self.experience_goal
        }
