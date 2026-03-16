from app.utils.database import get_db_connection
from app.models.video import Video
from datetime import datetime


class VideoRepository:

    # ─────────────────── READ ───────────────────

    def get_by_id(self, video_id):
        """Lấy 1 video theo Id."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM Video WHERE Id = %s", (video_id,))
                result = cursor.fetchone()
                return Video.from_dict(result) if result else None
        finally:
            connection.close()

    def get_all_public(self):
        """Lấy tất cả video chung (UserId IS NULL)."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM Video WHERE UserId IS NULL ORDER BY CreatedAt DESC"
                )
                results = cursor.fetchall()
                return [Video.from_dict(row) for row in results]
        finally:
            connection.close()

    def get_all_by_user_id(self, user_id):
        """Lấy tất cả video riêng của 1 user."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM Video WHERE UserId = %s ORDER BY LastOpened DESC, CreatedAt DESC",
                    (user_id,)
                )
                results = cursor.fetchall()
                return [Video.from_dict(row) for row in results]
        finally:
            connection.close()

    def get_user_copy_of_public(self, user_id, public_video_id):
        """Kiểm tra xem user đã có bản sao của video chung này chưa."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM Video WHERE UserId = %s AND PublicVideoId = %s LIMIT 1",
                    (user_id, public_video_id)
                )
                result = cursor.fetchone()
                return Video.from_dict(result) if result else None
        finally:
            connection.close()

    # ─────────────────── CREATE ───────────────────

    def create(self, title, thumbnail, source_url, type_video, user_id=None, public_video_id=None):
        """Tạo mới 1 video (dùng cho cả public lẫn private)."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO Video (Title, Thumbnail, SourceUrl, TypeVideo, CreatedAt, UserId, PublicVideoId)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    title, thumbnail, source_url, type_video,
                    datetime.now().date(), user_id, public_video_id
                ))
                new_id = cursor.lastrowid
            connection.commit()
            return new_id
        finally:
            connection.close()

    # ─────────────────── UPDATE ───────────────────

    def update(self, video_id, update_data):
        """
        Cập nhật video theo các field cho phép.
        update_data: dict với key là tên field Python (title, thumbnail, source_url, type_video)
        """
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                field_map = {
                    'title':      'Title',
                    'thumbnail':  'Thumbnail',
                    'source_url': 'SourceUrl',
                    'type_video': 'TypeVideo',
                }

                set_parts = []
                values = []
                for key, value in update_data.items():
                    col = field_map.get(key)
                    if col:
                        set_parts.append(f"`{col}` = %s")
                        values.append(value)

                if not set_parts:
                    return False

                sql = f"UPDATE Video SET {', '.join(set_parts)} WHERE Id = %s"
                values.append(video_id)
                cursor.execute(sql, tuple(values))
            connection.commit()
            return cursor.rowcount > 0
        finally:
            connection.close()

    def update_last_opened(self, video_id):
        """Cập nhật timestamp LastOpened."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE Video SET LastOpened = %s WHERE Id = %s",
                    (datetime.now(), video_id)
                )
            connection.commit()
        finally:
            connection.close()

    # ─────────────────── DELETE ───────────────────

    def delete(self, video_id):
        """Xóa video theo Id."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM Video WHERE Id = %s", (video_id,))
            connection.commit()
            return cursor.rowcount > 0
        finally:
            connection.close()
