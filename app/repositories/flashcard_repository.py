from app.utils.database import get_db_connection
from app.models.flashcard import Flashcard

class FlashcardRepository:

    def get_by_game_id(self, game_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM Flashcard WHERE FlashcardGameId = %s ORDER BY `Order` ASC"
                cursor.execute(sql, (game_id,))
                results = cursor.fetchall()
                return [Flashcard.from_dict(row) for row in results]
        finally:
            connection.close()

    def create_many(self, flashcards_data):
        # flashcards_data is list of dict: {'order': ..., 'word_id': ..., 'game_id': ...}
        if not flashcards_data: return True
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO Flashcard (`Order`, WordId, FlashcardGameId) VALUES (%s, %s, %s)"
                data_tuples = [(d['order'], d['word_id'], d['game_id']) for d in flashcards_data]
                cursor.executemany(sql, data_tuples)
                connection.commit()
                return True
        finally:
            connection.close()

    def delete_by_ids(self, ids):
        if not ids: return False
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                format_strings = ','.join(['%s'] * len(ids))
                sql = f"DELETE FROM Flashcard WHERE Id IN ({format_strings})"
                cursor.execute(sql, tuple(ids))
                connection.commit()
                return True
        finally:
            connection.close()

    def update_orders(self, order_updates):
        # order_updates is list of tuples: (new_order, flashcard_id)
        if not order_updates: return False
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "UPDATE Flashcard SET `Order` = %s WHERE Id = %s"
                cursor.executemany(sql, order_updates)
                connection.commit()
                return True
        finally:
            connection.close()
