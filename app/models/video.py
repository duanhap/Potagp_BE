class Video:
    def __init__(self, id=None, title=None, thumbnail=None, source_url=None, 
                 last_opened=None, type_video=None, created_at=None, user_id=None):
        self.id = id
        self.title = title
        self.thumbnail = thumbnail
        self.source_url = source_url
        self.last_opened = last_opened
        self.type_video = type_video
        self.created_at = created_at
        self.user_id = user_id

    @staticmethod
    def from_dict(data):
        if not data: return None
        return Video(
            id=data.get('Id'),
            title=data.get('Title'),
            thumbnail=data.get('Thumbnail'),
            source_url=data.get('SourceUrl'),
            last_opened=str(data.get('LastOpened')) if data.get('LastOpened') else None,
            type_video=data.get('TypeVideo'),
            created_at=str(data.get('CreatedAt')) if data.get('CreatedAt') else None,
            user_id=data.get('UserId')
        )

    def to_dict(self):
        return {
            'id': self.id, 'title': self.title, 'thumbnail': self.thumbnail,
            'source_url': self.source_url, 'last_opened': self.last_opened,
            'type_video': self.type_video, 'created_at': self.created_at,
            'user_id': self.user_id
        }
