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

    def get_all_public(self, term_lang_code=None, limit=None, offset=None):
        """Lấy tất cả video chung (UserId IS NULL) có tùy chọn phân trang và theo term language."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                base_query = "FROM Video WHERE UserId IS NULL"
                params = []
                
                if term_lang_code:
                    base_query += " AND TermLanguageCode = %s"
                    params.append(term_lang_code)
                    
                # Mặc định lấy tổng số dòng thỏa mãn (để phân trang)
                cursor.execute(f"SELECT COUNT(*) as total {base_query}", tuple(params))
                count_result = cursor.fetchone()
                # Kiểm tra dạng trả về là dict (['total']) hay tuple ([0])
                total_count = count_result['total'] if isinstance(count_result, dict) else count_result[0]
                
                query = f"SELECT * {base_query} ORDER BY CreatedAt DESC"
                if limit is not None and offset is not None:
                    query += " LIMIT %s OFFSET %s"
                    params.extend([limit, offset])
                    
                cursor.execute(query, tuple(params))
                results = cursor.fetchall()
                videos = [Video.from_dict(row) for row in results]
                
                return videos, total_count
        finally:
            connection.close()

    def get_all_by_user_id(self, user_id, type_video=None, limit=None, offset=None):
        """Lấy tất cả video riêng của 1 user có tùy chọn phân trang và type."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                base_query = "FROM Video WHERE UserId = %s"
                params = [user_id]
                
                if type_video:
                    base_query += " AND TypeVideo = %s"
                    params.append(type_video)
                    
                # Mặc định lấy tổng số dòng thỏa mãn (để phân trang)
                cursor.execute(f"SELECT COUNT(*) as total {base_query}", tuple(params))
                count_result = cursor.fetchone()
                total_count = count_result['total'] if isinstance(count_result, dict) else count_result[0]
                
                query = f"SELECT * {base_query} ORDER BY LastOpened DESC, CreatedAt DESC"
                if limit is not None and offset is not None:
                    query += " LIMIT %s OFFSET %s"
                    params.extend([limit, offset])

                cursor.execute(query, tuple(params))
                results = cursor.fetchall()
                videos = [Video.from_dict(row) for row in results]
                
                return videos, total_count
        finally:
            connection.close()

    def get_recent_by_user_id(self, user_id, limit=None, offset=None):
        """Lấy danh sách video xem gần đây (LastOpened IS NOT NULL) của user."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                base_query = "FROM Video WHERE UserId = %s AND LastOpened IS NOT NULL"
                params = [user_id]
                
                # Mặc định lấy tổng số dòng thỏa mãn (để phân trang)
                cursor.execute(f"SELECT COUNT(*) as total {base_query}", tuple(params))
                count_result = cursor.fetchone()
                total_count = count_result['total'] if isinstance(count_result, dict) else count_result[0]
                
                query = f"SELECT * {base_query} ORDER BY LastOpened DESC"
                if limit is not None and offset is not None:
                    query += " LIMIT %s OFFSET %s"
                    params.extend([limit, offset])

                cursor.execute(query, tuple(params))
                results = cursor.fetchall()
                videos = [Video.from_dict(row) for row in results]
                
                return videos, total_count
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

    def get_public_by_source_url(self, source_url):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM Video WHERE SourceUrl = %s AND UserId IS NULL LIMIT 1"
                cursor.execute(sql, (source_url,))
                result = cursor.fetchone()
                return Video.from_dict(result) if result else None
        finally:
            connection.close()

    def check_user_duplicate_video(self, user_id, source_url, definition_lang_code, term_lang_code):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """SELECT Id FROM Video 
                         WHERE UserId = %s AND SourceUrl = %s 
                               AND DefinitionLanguageCode = %s AND TermLanguageCode = %s 
                         LIMIT 1"""
                cursor.execute(sql, (user_id, source_url, definition_lang_code, term_lang_code))
                result = cursor.fetchone()
                return result is not None
        finally:
            connection.close()

    # ─────────────────── CREATE ───────────────────

    def create(self, title, thumbnail, source_url, type_video,
                definition_lang_code, term_lang_code,
                user_id=None, public_video_id=None, server_source_url=None):
        """Tạo mới 1 video (dùng cho cả public lẫn private)."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO Video (
                        Title, Thumbnail, SourceUrl, TypeVideo, CreatedAt,
                        UserId, PublicVideoId,
                        DefinitionLanguageCode, TermLanguageCode, ServerSourceUrl
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    title, thumbnail, source_url, type_video,
                    datetime.now().date(), user_id, public_video_id,
                    definition_lang_code, term_lang_code, server_source_url
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
        update_data: dict với key là tên field Python
        """
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                field_map = {
                    'title':                'Title',
                    'thumbnail':            'Thumbnail',
                    'source_url':           'SourceUrl',
                    'type_video':           'TypeVideo',
                    'definition_lang_code': 'DefinitionLanguageCode',
                    'term_lang_code':       'TermLanguageCode',
                    'server_source_url':    'ServerSourceUrl',
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
        """Xóa video theo Id và các data liên quan."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # 1. Tháo liên kết các video bản sao (tránh lỗi khóa ngoại FK_Video_Public nếu đây là Public Video)
                cursor.execute("UPDATE Video SET PublicVideoId = NULL WHERE PublicVideoId = %s", (video_id,))
                
                # 2. Xóa toàn bộ subtitle của video này
                cursor.execute("DELETE FROM Subtitle WHERE VideoId = %s", (video_id,))
                
                # 3. Cuối cùng mới xóa video
                cursor.execute("DELETE FROM Video WHERE Id = %s", (video_id,))
            connection.commit()
            return cursor.rowcount > 0
        finally:
            connection.close()
