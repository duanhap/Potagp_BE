from app.utils.database import get_db_connection
from app.models.flashcard_game import FlashcardGame

class FlashcardGameRepository:
    def get_by_word_set_id(self, word_set_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM FlashcardGame WHERE WordSetId = %s LIMIT 1"
                cursor.execute(sql, (word_set_id,))
                result = cursor.fetchone()
                return FlashcardGame.from_dict(result) if result else None
        finally:
            connection.close()

    def create(self, word_set_id, mode):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                from datetime import datetime
                sql = "INSERT INTO FlashcardGame (`Mode`, UpdatedAt, WordSetId) VALUES (%s, %s, %s)"
                cursor.execute(sql, (mode, datetime.now().date(), word_set_id))
            connection.commit()
            return cursor.lastrowid
        finally:
            connection.close()

    def update_mode(self, game_id, mode):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "UPDATE FlashcardGame SET `Mode` = %s WHERE Id = %s"
                cursor.execute(sql, (mode, game_id))
            connection.commit()
            return cursor.rowcount > 0
        finally:
            connection.close()
