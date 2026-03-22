from app.utils.database import get_db_connection
from app.models.sentence_pattern import SentencePattern
from datetime import datetime


class SentencePatternRepository:
    def get_by_id(self, sentence_pattern_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM SetencePattern WHERE Id = %s"
                cursor.execute(sql, (sentence_pattern_id,))
                result = cursor.fetchone()
                return SentencePattern.from_dict(result) if result else None
        finally:
            connection.close()

    def get_all_by_user_id(self, user_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM SetencePattern WHERE UserId = %s ORDER BY UpdateAt DESC, CreatedAt DESC"
                cursor.execute(sql, (user_id,))
                results = cursor.fetchall()
                return [SentencePattern.from_dict(row) for row in results]
        finally:
            connection.close()

    def get_recent_by_user_id(self, user_id, limit=10):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM SetencePattern WHERE UserId = %s ORDER BY LastOpened DESC, UpdateAt DESC, CreatedAt DESC LIMIT %s"
                cursor.execute(sql, (user_id, limit))
                results = cursor.fetchall()
                return [SentencePattern.from_dict(row) for row in results]
        finally:
            connection.close()

    def create(self, name, description, is_public, term_lang_code, def_lang_code, user_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO SetencePattern (Name, Description, CreatedAt, IsPublic, TermLanguageCode, DefinitionLanguageCode, UpdateAt, LastOpened, UserId)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                now = datetime.now().date()
                cursor.execute(sql, (name, description, now, is_public, term_lang_code, def_lang_code, now, None, user_id))
            connection.commit()
            return cursor.lastrowid
        finally:
            connection.close()

    def update(self, sentence_pattern_id, name, description, is_public, term_lang_code, def_lang_code):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    UPDATE SetencePattern
                    SET Name = %s, Description = %s, IsPublic = %s,
                        TermLanguageCode = %s, DefinitionLanguageCode = %s, UpdateAt = %s
                    WHERE Id = %s
                """
                cursor.execute(sql, (name, description, is_public, term_lang_code, def_lang_code, datetime.now().date(), sentence_pattern_id))
            connection.commit()
            return cursor.rowcount > 0
        finally:
            connection.close()

    def delete(self, sentence_pattern_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "DELETE FROM SetencePattern WHERE Id = %s"
                cursor.execute(sql, (sentence_pattern_id,))
            connection.commit()
            return cursor.rowcount > 0
        finally:
            connection.close()

    def update_last_opened(self, sentence_pattern_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "UPDATE SetencePattern SET LastOpened = %s WHERE Id = %s"
                now = datetime.now()
                cursor.execute(sql, (now, sentence_pattern_id))
            connection.commit()
            return cursor.rowcount > 0
        finally:
            connection.close()
