from app.utils.database import get_db_connection
from app.models.streak import Streak
from app.models.streak_date import StreakDate
from datetime import date


class StreakRepository:

    # ── StreakDate ─────────────────────────────────────────────

    def get_streak_date_today(self, user_id):
        """Trả về dict row của StreakDate hôm nay, hoặc None."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM StreakDate WHERE UserId = %s AND `Date` = %s LIMIT 1"
                cursor.execute(sql, (user_id, date.today()))
                return cursor.fetchone()
        finally:
            connection.close()

    def create_streak_date(self, user_id, exp_earned, protected, protected_by, streak_id=None):
        """Tạo mới StreakDate hôm nay, trả về id."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO StreakDate (`Date`, ProtectedDate, ProtectedBy, ExperiencePointsEarned, StreakId, UserId)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (date.today(), protected, protected_by, exp_earned, streak_id, user_id))
                connection.commit()
                return cursor.lastrowid
        finally:
            connection.close()

    def update_streak_date_exp(self, streak_date_id, new_total_exp, protected, protected_by):
        """Cập nhật điểm kinh nghiệm và trạng thái bảo vệ của StreakDate."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    UPDATE StreakDate
                    SET ExperiencePointsEarned = %s, ProtectedDate = %s, ProtectedBy = %s
                    WHERE Id = %s
                """
                cursor.execute(sql, (new_total_exp, protected, protected_by, streak_date_id))
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()

    def update_streak_id(self, streak_date_id, streak_id):
        """Gán StreakId cho StreakDate sau khi tạo/cập nhật Streak."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "UPDATE StreakDate SET StreakId = %s WHERE Id = %s"
                cursor.execute(sql, (streak_id, streak_date_id))
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()

    # ── Streak ────────────────────────────────────────────────

    def get_current_streak(self, user_id):
        """Trả về dict row của Streak đang active (CurentStreak = true), hoặc None."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM Streak WHERE UserId = %s AND CurentStreak = TRUE LIMIT 1"
                cursor.execute(sql, (user_id,))
                return cursor.fetchone()
        finally:
            connection.close()

    def get_streak_by_id(self, streak_id):
        """Lấy Streak theo Id."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM Streak WHERE Id = %s"
                cursor.execute(sql, (streak_id,))
                return cursor.fetchone()
        finally:
            connection.close()

    def create_streak(self, user_id, start_date_int):
        """Tạo Streak mới với LenghtStreak = 1, trả về id."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO Streak (LenghtStreak, StartDate, CurentStreak, UserId)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql, (1, start_date_int, 1, user_id))
                connection.commit()
                return cursor.lastrowid
        finally:
            connection.close()

    def increment_streak_length(self, streak_id):
        """Tăng LenghtStreak thêm 1."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "UPDATE Streak SET LenghtStreak = LenghtStreak + 1 WHERE Id = %s"
                cursor.execute(sql, (streak_id,))
                connection.commit()
                return cursor.rowcount > 0
        finally:
            connection.close()

    # ── Setting ───────────────────────────────────────────────

    def get_experience_goal(self, user_id):
        """Lấy ExperienceGoal từ bảng Setting, mặc định 15 nếu chưa có."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT ExperienceGoal FROM Setting WHERE UserId = %s LIMIT 1"
                cursor.execute(sql, (user_id,))
                row = cursor.fetchone()
                return row['ExperienceGoal'] if row else 15
        finally:
            connection.close()

    # ── API-facing methods (trả về model objects) ─────────────

    def get_current_streak_model(self, user_id):
        """Trả về Streak model đang active, hoặc None."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM Streak WHERE UserId = %s AND CurentStreak = TRUE LIMIT 1"
                cursor.execute(sql, (user_id,))
                return Streak.from_dict(cursor.fetchone())
        finally:
            connection.close()

    def get_streak_date_today_model(self, user_id):
        """Trả về StreakDate model của hôm nay, hoặc None."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM StreakDate WHERE UserId = %s AND `Date` = %s LIMIT 1"
                cursor.execute(sql, (user_id, date.today()))
                return StreakDate.from_dict(cursor.fetchone())
        finally:
            connection.close()
