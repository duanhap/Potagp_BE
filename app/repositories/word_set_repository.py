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
                sql = "SELECT * FROM WordSet WHERE UserId = %s ORDER BY CreatedAt DESC, UpdatedAt DESC"
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
                    SELECT * FROM WordSet 
                    WHERE UserId = %s 
                    ORDER BY LastOpened DESC 
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
                sql = "DELETE FROM WordSet WHERE Id = %s"
                cursor.execute(sql, (word_set_id,))
            connection.commit()
            return cursor.rowcount > 0
        finally:
            connection.close()
