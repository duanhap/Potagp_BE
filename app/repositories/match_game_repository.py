import random
from app.utils.database import get_db_connection
from app.models.word import Word
from datetime import datetime


class MatchGameRepository:

    def get_random_words(self, word_set_id, limit=6):
        """Lấy random tối đa `limit` từ từ word set."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM Word WHERE WordSetId = %s ORDER BY RAND() LIMIT %s",
                    (word_set_id, limit)
                )
                results = cursor.fetchall()
                return [Word.from_dict(row) for row in results]
        finally:
            connection.close()

    def create_game(self, word_set_id):
        """Tạo mới một MatchGame, trả về game_id."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO MatchGame (CreatedAt, WordSetId) VALUES (%s, %s)",
                    (datetime.now(), word_set_id)
                )
            connection.commit()
            return cursor.lastrowid
        finally:
            connection.close()

    def submit_result(self, game_id, completed_time):
        """Lưu thời gian hoàn thành vào MatchGame."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE MatchGame SET CompletedTime = %s WHERE Id = %s",
                    (completed_time, game_id)
                )
            connection.commit()
            return cursor.rowcount > 0
        finally:
            connection.close()

    def get_best_time(self, word_set_id):
        """Lấy thời gian tốt nhất (nhỏ nhất) của word set."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT CompletedTime AS best_time, CreatedAt
                    FROM MatchGame
                    WHERE WordSetId = %s AND CompletedTime IS NOT NULL
                    ORDER BY CompletedTime ASC
                    LIMIT 1
                    """,
                    (word_set_id,)
                )
                row = cursor.fetchone()
                if row and row.get('best_time') is not None:
                    return {'best_time': float(row['best_time']), 'date': str(row['CreatedAt'])}
                return None
        finally:
            connection.close()
