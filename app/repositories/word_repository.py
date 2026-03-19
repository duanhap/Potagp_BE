from app.utils.database import get_db_connection
from app.models.word import Word
from datetime import datetime


class WordRepository:

    def get_by_id(self, word_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM Word WHERE Id = %s"
                cursor.execute(sql, (word_id,))
                result = cursor.fetchone()
                return Word.from_dict(result) if result else None
        finally:
            connection.close()

    def get_all_by_word_set_id(self, word_set_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM Word WHERE WordSetId = %s ORDER BY CreatedAt DESC"
                cursor.execute(sql, (word_set_id,))
                results = cursor.fetchall()
                return [Word.from_dict(row) for row in results]
        finally:
            connection.close()

    def count_by_word_set_id(self, word_set_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT COUNT(*) AS Total FROM Word WHERE WordSetId = %s"
                cursor.execute(sql, (word_set_id,))
                row = cursor.fetchone()
                return int(row['Total']) if row and row.get('Total') is not None else 0
        finally:
            connection.close()

    def get_page_by_word_set_id(self, word_set_id, page=1, page_size=20):
        page = max(1, int(page or 1))
        page_size = max(1, int(page_size or 20))
        offset = (page - 1) * page_size

        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    SELECT * FROM Word
                    WHERE WordSetId = %s
                    ORDER BY CreatedAt DESC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(sql, (word_set_id, page_size, offset))
                results = cursor.fetchall()
                return [Word.from_dict(row) for row in results]
        finally:
            connection.close()

    def _get_or_create_flashcard_game(self, connection, word_set_id):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT Id FROM FlashcardGame WHERE WordSetId = %s LIMIT 1",
                (word_set_id,)
            )
            row = cursor.fetchone()
            if row:
                return row['Id']

            cursor.execute(
                "INSERT INTO FlashcardGame (Mode, UpdatedAt, WordSetId) VALUES (%s, %s, %s)",
                ('default', datetime.now().date(), word_set_id)
            )
            connection.commit()
            return cursor.lastrowid

    def _get_or_create_match_game(self, connection, word_set_id):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT Id FROM MatchGame WHERE WordSetId = %s LIMIT 1",
                (word_set_id,)
            )
            row = cursor.fetchone()
            if row:
                return row['Id']

            cursor.execute(
                "INSERT INTO MatchGame (CreatedAt, WordSetId) VALUES (%s, %s)",
                (datetime.now(), word_set_id)
            )
            connection.commit()
            return cursor.lastrowid

    def create(self, term, definition, word_set_id, description=None, status='unknown'):
        connection = get_db_connection()
        try:
            flashcard_game_id = self._get_or_create_flashcard_game(connection, word_set_id)
            match_game_id = self._get_or_create_match_game(connection, word_set_id)

            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO Word (Term, Definition, Description, CreatedAt, Status, WordSetId, FlashcardGameId, MatchGameId)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    term, definition, description,
                    datetime.now().date(), status,
                    word_set_id, flashcard_game_id, match_game_id
                ))
            connection.commit()
            return cursor.lastrowid
        finally:
            connection.close()

    def create_many(self, word_set_id, words):
        """Create multiple words for the same word set. words: list of dict with term, definition, description?, status?"""
        if not words:
            return []

        connection = get_db_connection()
        try:
            flashcard_game_id = self._get_or_create_flashcard_game(connection, word_set_id)
            match_game_id = self._get_or_create_match_game(connection, word_set_id)
            now = datetime.now().date()

            created_ids = []
            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO Word (Term, Definition, Description, CreatedAt, Status, WordSetId, FlashcardGameId, MatchGameId)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                for w in words:
                    term = w.get('term')
                    definition = w.get('definition')
                    if not term or not definition:
                        continue
                    cursor.execute(sql, (
                        term, definition, w.get('description'),
                        now, w.get('status', 'unknown'),
                        word_set_id, flashcard_game_id, match_game_id
                    ))
                    created_ids.append(cursor.lastrowid)
            connection.commit()
            return created_ids
        finally:
            connection.close()

    def update(self, word_id, term, definition, description=None, status=None):
        connection = get_db_connection()
        try:
            updates = []
            params = []

            if term is not None:
                updates.append("Term = %s")
                params.append(term)
            if definition is not None:
                updates.append("Definition = %s")
                params.append(definition)
            if description is not None:
                updates.append("Description = %s")
                params.append(description)
            if status is not None:
                updates.append("Status = %s")
                params.append(status)

            if not updates:
                return False

            params.append(word_id)
            sql = f"UPDATE Word SET {', '.join(updates)} WHERE Id = %s"
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                updated = cursor.rowcount
            connection.commit()
            return updated > 0
        finally:
            connection.close()

    def delete(self, word_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "DELETE FROM Word WHERE Id = %s"
                cursor.execute(sql, (word_id,))
            connection.commit()
            return cursor.rowcount > 0
        finally:
            connection.close()
