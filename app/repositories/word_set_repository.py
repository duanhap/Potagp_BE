from app.utils.database import get_db_connection
from app.models.word_set import WordSet
from datetime import datetime


class WordSetRepository:

    def get_by_id(self, word_set_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM WordSet WHERE Id = %s"
                cursor.execute(sql, (word_set_id,))
                result = cursor.fetchone()
                return WordSet.from_dict(result) if result else None
        finally:
            connection.close()

    def get_all_by_user_id(self, user_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    SELECT ws.*,
                           (SELECT COUNT(*) FROM Word WHERE WordSetId = ws.Id) AS amount_of_words
                    FROM WordSet ws
                    WHERE ws.UserId = %s
                    ORDER BY ws.CreatedAt DESC, ws.UpdatedAt DESC
                """
                cursor.execute(sql, (user_id,))
                results = cursor.fetchall()
                return [WordSet.from_dict(row) for row in results]
        finally:
            connection.close()

    def get_recent_by_user_id(self, user_id, limit=3):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    SELECT ws.*,
                           (SELECT COUNT(*) FROM Word WHERE WordSetId = ws.Id) AS amount_of_words
                    FROM WordSet ws
                    WHERE ws.UserId = %s
                    ORDER BY ws.LastOpened DESC
                    LIMIT %s
                """
                cursor.execute(sql, (user_id, limit))
                results = cursor.fetchall()
                return [WordSet.from_dict(row) for row in results]
        finally:
            connection.close()

    def create(self, name, description, is_public, def_lang_code, term_lang_code, user_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO WordSet (Name, Description, CreatedAt, IsPublic, DefinitionLanguageCode, TermLanguageCode, UpdatedAt, LastOpened, UserId)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                now = datetime.now()
                cursor.execute(sql, (name, description, now.date(), is_public, def_lang_code, term_lang_code, now.date(), now, user_id))
            connection.commit()
            return cursor.lastrowid
        finally:
            connection.close()

    def update(self, word_set_id, name, description, is_public, def_lang_code, term_lang_code):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    UPDATE WordSet
                    SET Name = %s, Description = %s, IsPublic = %s,
                        DefinitionLanguageCode = %s, TermLanguageCode = %s, UpdatedAt = %s
                    WHERE Id = %s
                """
                cursor.execute(sql, (name, description, is_public, def_lang_code, term_lang_code, datetime.now().date(), word_set_id))
            connection.commit()
            return cursor.rowcount > 0
        finally:
            connection.close()

    def delete(self, word_set_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE fc FROM Flashcard fc
                    INNER JOIN FlashcardGame fcg ON fc.FlashcardGameId = fcg.Id
                    WHERE fcg.WordSetId = %s
                    """,
                    (word_set_id,),
                )
                cursor.execute("DELETE FROM Word WHERE WordSetId = %s", (word_set_id,))
                cursor.execute("DELETE FROM FlashcardGame WHERE WordSetId = %s", (word_set_id,))
                cursor.execute("DELETE FROM MatchGame WHERE WordSetId = %s", (word_set_id,))
                cursor.execute("DELETE FROM WordSet WHERE Id = %s", (word_set_id,))
                deleted = cursor.rowcount > 0
            connection.commit()
            return deleted
        finally:
            connection.close()

    def update_last_opened(self, word_set_id, last_opened=None):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "UPDATE WordSet SET LastOpened = %s WHERE Id = %s"
                cursor.execute(sql, (last_opened or datetime.now(), word_set_id))
            connection.commit()
            return cursor.rowcount > 0
        finally:
            connection.close()
