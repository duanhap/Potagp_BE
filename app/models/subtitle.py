class Subtitle:
    def __init__(self, id=None, start_time=None, end_time=None, content=None, 
                 pronunciation=None, translation=None, video_id=None):
        self.id = id
        self.start_time = start_time
        self.end_time = end_time
        self.content = content
        self.pronunciation = pronunciation
        self.translation = translation
        self.video_id = video_id

    @staticmethod
    def from_dict(data):
        if not data: return None
        return Subtitle(
            id=data.get('Id'),
            start_time=data.get('StartTime'),
            end_time=data.get('EndTime'),
            content=data.get('Content'),
            pronunciation=data.get('Pronunciation'),
            translation=data.get('Translation'),
            video_id=data.get('VideoId')
        )

    def to_dict(self):
        return {
            'id': self.id, 
            'start_time': self.start_time, 
            'end_time': self.end_time,
            'content': self.content,
            'pronunciation': self.pronunciation,
            'translation': self.translation,
            'video_id': self.video_id
        }
