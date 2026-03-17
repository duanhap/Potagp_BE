from app.utils.database import get_db_connection
from datetime import datetime
from app.models.user import User
from app.models.setting import Setting

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
                user_id = cursor.lastrowid

                sql_default_setting = """
                    INSERT INTO Setting (Notification, Language, ExperienceGoal, UserId)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql_default_setting, (0, 'en', 15, user_id))

            connection.commit()
            return user_id
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

    def update_profile(self, uid, update_data):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                field_map = {
                    'name': 'Name',
                    'avatar': 'Avatar',
                    'token_fcm': 'TokenFCM'
                }

                set_parts = []
                values = []
                for key, value in update_data.items():
                    column_name = field_map.get(key)
                    if column_name:
                        set_parts.append(f"`{column_name}` = %s")
                        values.append(value)

                if not set_parts:
                    return False

                sql = f"UPDATE `User` SET {', '.join(set_parts)} WHERE Uid = %s"
                values.append(uid)
                cursor.execute(sql, tuple(values))
            connection.commit()
            return cursor.rowcount > 0
        finally:
            connection.close()

    def save_user_setting(self, uid, notification, language, experience_goal):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql_get_user = "SELECT Id FROM `User` WHERE Uid = %s"
                cursor.execute(sql_get_user, (uid,))
                user_row = cursor.fetchone()
                if not user_row:
                    return None

                user_id = user_row.get('Id')

                sql_get_setting = "SELECT Id FROM Setting WHERE UserId = %s LIMIT 1"
                cursor.execute(sql_get_setting, (user_id,))
                setting_row = cursor.fetchone()

                if setting_row:
                    sql_update = """
                        UPDATE Setting
                        SET Notification = %s, Language = %s, ExperienceGoal = %s
                        WHERE Id = %s
                    """
                    cursor.execute(sql_update, (notification, language, experience_goal, setting_row.get('Id')))
                else:
                    sql_insert = """
                        INSERT INTO Setting (Notification, Language, ExperienceGoal, UserId)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(sql_insert, (notification, language, experience_goal, user_id))

                sql_get_saved = "SELECT * FROM Setting WHERE UserId = %s LIMIT 1"
                cursor.execute(sql_get_saved, (user_id,))
                saved_setting = cursor.fetchone()

            connection.commit()
            return Setting.from_dict(saved_setting) if saved_setting else None
        finally:
            connection.close()

    def get_user_setting(self, uid):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql_get_user = "SELECT Id FROM `User` WHERE Uid = %s"
                cursor.execute(sql_get_user, (uid,))
                user_row = cursor.fetchone()
                if not user_row:
                    return None

                user_id = user_row.get('Id')
                sql_get_setting = "SELECT * FROM Setting WHERE UserId = %s LIMIT 1"
                cursor.execute(sql_get_setting, (user_id,))
                setting_row = cursor.fetchone()
                return Setting.from_dict(setting_row) if setting_row else Setting(
                    notification=False,
                    language='en',
                    user_id=user_id,
                    experience_goal=15
                )
        finally:
            connection.close()
