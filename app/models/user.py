from datetime import datetime

class User:
    def __init__(self, id=None, uid=None, email=None, name=None, experience_points=0, 
                 diamond=0, role='User', created_at=None, last_login=None, 
                 avatar=None, token_fcm=None):
        self.id = id
        self.uid = uid
        self.email = email
        self.name = name
        self.experience_points = experience_points
        self.diamond = diamond
        self.role = role
        self.created_at = created_at or datetime.now().date()
        self.last_login = last_login
        self.avatar = avatar
        self.token_fcm = token_fcm

    @staticmethod
    def from_dict(data):
        if not data:
            return None
        return User(
            id=data.get('Id'),
            uid=data.get('Uid'),
            email=data.get('Email'),
            name=data.get('Name'),
            experience_points=data.get('ExperiencePoints', 0),
            diamond=data.get('Diamond', 0),
            role=data.get('Role', 'User'),
            created_at=data.get('CreatedAt'),
            last_login=data.get('LastLogin'),
            avatar=data.get('Avatar'),
            token_fcm=data.get('TokenFCM')
        )

    def to_dict(self):
        return {
            'id': self.id,
            'uid': self.uid,
            'email': self.email,
            'name': self.name,
            'experience_points': self.experience_points,
            'diamond': self.diamond,
            'role': self.role,
            'created_at': str(self.created_at) if self.created_at else None,
            'last_login': str(self.last_login) if self.last_login else None,
            'avatar': self.avatar,
            'token_fcm': self.token_fcm
        }
