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

    def get_by_pattern_id(self, pattern_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM Setence WHERE SetencePatternId = %s ORDER BY CreatedAt DESC"
                cursor.execute(sql, (pattern_id,))
                results = cursor.fetchall()
                return [Sentence.from_dict(row) for row in results]
        finally:
            connection.close()

    def create(self, term, definition, status, mistakes, pattern_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO Setence (Term, Definition, CreatedAt, Status, NumberOfMistakes, SetencePatternId) VALUES (%s, %s, %s, %s, %s, %s)"
                now = datetime.now().date()
                cursor.execute(sql, (term, definition, now, status, mistakes, pattern_id))
                connection.commit()
                return cursor.lastrowid
        finally:
            connection.close()

    def create_bulk(self, sentences, pattern_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                now = datetime.now().date()
                sql = "INSERT INTO Setence (Term, Definition, CreatedAt, Status, NumberOfMistakes, SetencePatternId) VALUES (%s, %s, %s, %s, %s, %s)"
                values = []
                for sentence in sentences:
                    term = sentence.get('term')
                    definition = sentence.get('definition')
                    status = sentence.get('status', 'active')
                    mistakes = sentence.get('mistakes', 0)
                    values.append((term, definition, now, status, mistakes, pattern_id))

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