from app.utils.database import get_db_connection
from datetime import datetime
from app.models.user import User

class UserRepository:
    def get_by_uid(self, uid):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM `User` WHERE Uid = %s"
                cursor.execute(sql, (uid,))
                result = cursor.fetchone()
                return User.from_dict(result) if result else None
        finally:
            connection.close()

    def create(self, uid, email, name):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO `User` (Uid, Email, Name, ExperiencePoints, Diamond, Password, Role, CreatedAt, LastLogin)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (uid, email, name, 0, 0, 0, 'User', datetime.now().date(), datetime.now()))
            connection.commit()
            return cursor.lastrowid
        finally:
            connection.close()

    def update_last_login(self, uid):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "UPDATE `User` SET LastLogin = %s WHERE Uid = %s"
                cursor.execute(sql, (datetime.now(), uid))
            connection.commit()
        finally:
            connection.close()
