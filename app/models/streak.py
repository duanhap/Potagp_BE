class Streak:
    def __init__(self, id=None, length_streak=0, start_date=0, current_streak=False, user_id=None):
        self.id = id
        self.length_streak = length_streak
        self.start_date = start_date
        self.current_streak = current_streak
        self.user_id = user_id

    @staticmethod
    def from_dict(data):
        if not data: return None
        raw = data.get('CurentStreak')
        current = (raw != b'\x00') if isinstance(raw, bytes) else bool(raw)
        return Streak(
            id=data.get('Id'),
            length_streak=data.get('LenghtStreak', 0),
            start_date=data.get('StartDate', 0),
            current_streak=current,
            user_id=data.get('UserId')
        )

    def to_dict(self):
        return {
            'id': self.id,
            'length_streak': self.length_streak,
            'start_date': self.start_date,
            'current_streak': self.current_streak,
            'user_id': self.user_id
        }
