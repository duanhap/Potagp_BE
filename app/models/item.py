class Item:
    def __init__(self, id=None, water_streak=0, super_xp=0, hack_xp=0, user_id=None):
        self.id = id
        self.water_streak = water_streak
        self.super_xp = super_xp
        self.hack_xp = hack_xp
        self.user_id = user_id

    @staticmethod
    def from_dict(data):
        if not data: return None
        return Item(
            id=data.get('Id'),
            water_streak=data.get('WaterStreak', 0),
            super_xp=data.get('SuperExperience', 0),
            hack_xp=data.get('HackExperience', 0),
            user_id=data.get('UserId')
        )

    def to_dict(self):
        return {
            'id': self.id, 'water_streak': self.water_streak,
            'super_xp': self.super_xp, 'hack_xp': self.hack_xp, 'user_id': self.user_id
        }
