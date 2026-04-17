class StreakDate:
    def __init__(self, id=None, date=None, protected_date=False, protected_by=None, 
                 xp_earned=0, streak_id=None, user_id=None):
        self.id = id
        self.date = date
        self.protected_date = protected_date
        self.protected_by = protected_by
        self.xp_earned = xp_earned
        self.streak_id = streak_id
        self.user_id = user_id

    @staticmethod
    def from_dict(data):
        if not data: return None
        raw = data.get('ProtectedDate')
        protected = (raw != b'\x00') if isinstance(raw, bytes) else bool(raw)
        return StreakDate(
            id=data.get('Id'),
            date=str(data.get('Date')) if data.get('Date') else None,
            protected_date=protected,
            protected_by=data.get('ProtectedBy'),
            xp_earned=data.get('ExperiencePointsEarned', 0),
            streak_id=data.get('StreakId'),
            user_id=data.get('UserId')
        )

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date,
            'protected_date': self.protected_date,
            'protected_by': self.protected_by,
            'xp_earned': self.xp_earned,
            'streak_id': self.streak_id,
            'user_id': self.user_id
        }
