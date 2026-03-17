from app.utils.database import get_db_connection
from app.models.subtitle import Subtitle

class SubtitleRepository:
    def get_by_video_id(self, video_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM Subtitle WHERE VideoId = %s ORDER BY StartTime ASC"
                cursor.execute(sql, (video_id,))
                results = cursor.fetchall()
                return [Subtitle.from_dict(row) for row in results]
        finally:
            connection.close()

    def delete_by_video_id(self, video_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "DELETE FROM Subtitle WHERE VideoId = %s"
                cursor.execute(sql, (video_id,))
            connection.commit()
            return cursor.rowcount
        finally:
            connection.close()

    def insert_many(self, subtitles, video_id):
        """
        subtitles: list of dict {'start_time', 'end_time', 'content', 'pronunciation', 'translation'}
        """
        if not subtitles:
            return 0
            
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO Subtitle (StartTime, EndTime, Content, Pronunciation, Translation, VideoId)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                values = [
                    (sub['start_time'], sub['end_time'], sub['content'], sub.get('pronunciation'), sub.get('translation'), video_id)
                    for sub in subtitles
                ]
                cursor.executemany(sql, values)
            connection.commit()
            return cursor.rowcount
        finally:
            connection.close()
