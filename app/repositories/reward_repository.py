from app.utils.database import get_db_connection


class RewardRepository:
    def add_experience_and_diamond(self, uid, experience, diamond):
        """Cộng thêm experience và diamond vào user, trả về (new_exp, new_diamond) hoặc None nếu không tìm thấy."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql_update = """
                    UPDATE `User`
                    SET ExperiencePoints = ExperiencePoints + %s,
                        Diamond = Diamond + %s
                    WHERE Uid = %s
                """
                cursor.execute(sql_update, (experience, diamond, uid))
                if cursor.rowcount == 0:
                    return None

                sql_select = "SELECT ExperiencePoints, Diamond FROM `User` WHERE Uid = %s"
                cursor.execute(sql_select, (uid,))
                row = cursor.fetchone()

            connection.commit()
            if not row:
                return None
            return row['ExperiencePoints'], row['Diamond']
        finally:
            connection.close()
