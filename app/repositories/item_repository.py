from app.utils.database import get_db_connection

class ItemRepository:
    def get_by_user_id(self, user_id):
        """Lấy thông tin vật phẩm của user theo UserId."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM Item WHERE UserId = %s"
                cursor.execute(sql, (user_id,))
                return cursor.fetchone()
        finally:
            connection.close()

    def decrement_water_streak(self, user_id):
        """Trừ 1 WaterStreak của user (nếu còn)."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # Chỉ trừ nếu WaterStreak > 0
                sql = "UPDATE Item SET WaterStreak = WaterStreak - 1 WHERE UserId = %s AND WaterStreak > 0"
                cursor.execute(sql, (user_id,))
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()
