class Subtitle:
    def __init__(self, id=None, source_url=None, video_id=None):
        self.id = id
        self.source_url = source_url
        self.video_id = video_id

    @staticmethod
    def from_dict(data):
        if not data: return None
        return Subtitle(
            id=data.get('Id'),
            source_url=data.get('SourceUrl'),
            video_id=data.get('VideoId')
        )

    def to_dict(self):
        return {
            'id': self.id, 'source_url': self.source_url, 'video_id': self.video_id
        }
