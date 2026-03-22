from app.utils.database import get_db_connection
from app.models.sentence import Sentence
from datetime import datetime


class SentenceRepository:
    def get_by_id(self, sentence_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM Setence WHERE Id = %s"
                cursor.execute(sql, (sentence_id,))
                result = cursor.fetchone()
                return Sentence.from_dict(result) if result else None
        finally:
            connection.close()

    def get_by_pattern_id(self, pattern_id, page=1, page_size=20):
        offset = (page - 1) * page_size
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM Setence WHERE SetencePatternId = %s ORDER BY CreatedAt DESC LIMIT %s OFFSET %s"
                cursor.execute(sql, (pattern_id, page_size, offset))
                results = cursor.fetchall()
                return [Sentence.from_dict(row) for row in results]
        finally:
            connection.close()

    def count_by_pattern_id(self, pattern_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT COUNT(*) AS total FROM Setence WHERE SetencePatternId = %s"
                cursor.execute(sql, (pattern_id,))
                result = cursor.fetchone()
                return result['total'] if result else 0
        finally:
            connection.close()

    def get_all_by_user_id(self, user_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    SELECT s.* FROM Setence s
                    JOIN SetencePattern sp ON s.SetencePatternId = sp.Id
                    WHERE sp.UserId = %s
                    ORDER BY s.CreatedAt DESC
                """
                cursor.execute(sql, (user_id,))
                results = cursor.fetchall()
                return [Sentence.from_dict(row) for row in results]
        finally:
            connection.close()

    def create(self, term, definition, status, mistakes, pattern_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO Setence (Term, Definition, CreatedAt, Status, NumberOfMistakes, SetencePatternId, LastOpened) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                now = datetime.now().date()
                status = status if status in ['unknown', 'known'] else 'unknown'
                cursor.execute(sql, (term, definition, now, status, mistakes, pattern_id, None))
                connection.commit()
                return cursor.lastrowid
        finally:
            connection.close()

    def create_bulk(self, sentences, pattern_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                now = datetime.now().date()
                sql = "INSERT INTO Setence (Term, Definition, CreatedAt, Status, NumberOfMistakes, SetencePatternId, LastOpened) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                values = []
                for sentence in sentences:
                    term = sentence.get('term')
                    definition = sentence.get('definition')
                    status = sentence.get('status', 'unknown')
                    if status not in ['unknown', 'known']:
                        status = 'unknown'
                    mistakes = sentence.get('mistakes', 0)
                    values.append((term, definition, now, status, mistakes, pattern_id, None))

                if not values:
                    return []

                cursor.executemany(sql, values)
                connection.commit()
                # cursors may not return lastrowid for executemany; fetch inserted records by pattern
            return self.get_by_pattern_id(pattern_id)
        finally:
            connection.close()

    def update(self, sentence_id, term, definition, status, mistakes):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "UPDATE Setence SET Term = %s, Definition = %s, Status = %s, NumberOfMistakes = %s WHERE Id = %s"
                cursor.execute(sql, (term, definition, status, mistakes, sentence_id))
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()

    def update_last_opened(self, sentence_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "UPDATE Setence SET LastOpened = %s WHERE Id = %s"
                now = datetime.now()
                cursor.execute(sql, (now, sentence_id))
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()

    def get_recent_sentences_by_user_id(self, user_id, limit=3):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    SELECT s.* FROM Setence s
                    JOIN SetencePattern sp ON s.SetencePatternId = sp.Id
                    WHERE sp.UserId = %s
                    ORDER BY s.LastOpened DESC, s.CreatedAt DESC
                    LIMIT %s
                """
                cursor.execute(sql, (user_id, limit))
                results = cursor.fetchall()
                return [Sentence.from_dict(row) for row in results]
        finally:
            connection.close()

    def delete(self, sentence_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "DELETE FROM Setence WHERE Id = %s"
                cursor.execute(sql, (sentence_id,))
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()