class UserAchievement:
    def __init__(self, id=None, name=None, description=None, earned_at=None, image=None, user_id=None):
        self.id = id
        self.name = name
        self.description = description
        self.earned_at = earned_at
        self.image = image
        self.user_id = user_id

    @staticmethod
    def from_dict(data):
        if not data: return None
        return UserAchievement(
            id=data.get('Id'),
            name=data.get('Name'),
            description=data.get('Description'),
            earned_at=str(data.get('EarnedAt')) if data.get('EarnedAt') else None,
            image=data.get('Image'),
            user_id=data.get('UserId')
        )

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'description': self.description,
            'earned_at': self.earned_at, 'image': self.image, 'user_id': self.user_id
        }
