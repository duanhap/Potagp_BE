from datetime import date
from app.repositories.streak_repository import StreakRepository


def _bit_to_bool(value):
    """
    Chuyển bit(1) từ PyMySQL sang bool đúng.
    PyMySQL trả bit(1) dưới dạng bytes: b'\\x00' = False, b'\\x01' = True.
    Dùng bool() trực tiếp sẽ sai vì bool(b'\\x00') = True (bytes object không rỗng).
    """
    if isinstance(value, bytes):
        return value != b'\x00'
    return bool(value)


class StreakService:
    def __init__(self):
        self.streak_repo = StreakRepository()

    def get_current_streak(self, uid, user_id):
        """Lấy Streak đang active của user. Trả về (streak_model, error)."""
        streak = self.streak_repo.get_current_streak_model(user_id)
        return streak, None

    def get_streak_date_today(self, uid, user_id):
        """Lấy StreakDate hôm nay của user. Trả về (streak_date_model, error)."""
        streak_date = self.streak_repo.get_streak_date_today_model(user_id)
        return streak_date, None

    def process_streak(self, user_id, experience_earned):
        """
        Xử lý StreakDate và Streak sau khi user nhận thưởng.

        Trả về dict chứa thông tin streak:
          status:
            'not_reached'    – chưa đủ ExperienceGoal hôm nay
            'already_counted'– đã đủ goal và đã được tính streak trước đó trong ngày
            'extended'       – streak hiện tại được nối thêm 1 ngày
            'created'        – streak mới được tạo
          current_length  : int hoặc None
          experience_today: tổng XP kiếm được hôm nay
          experience_goal : mục tiêu XP mỗi ngày
        """
        experience_goal = self.streak_repo.get_experience_goal(user_id)
        today = date.today()
        today_int = int(today.strftime('%Y%m%d'))  # vì StartDate lưu kiểu int

        # ── Bước 1: Tìm / tạo StreakDate hôm nay ─────────────
        existing = self.streak_repo.get_streak_date_today(user_id)

        if existing:
            was_protected_before = _bit_to_bool(existing.get('ProtectedDate'))
            streak_date_id = existing.get('Id')
            new_total_exp = (existing.get('ExperiencePointsEarned') or 0) + experience_earned
        else:
            was_protected_before = False
            streak_date_id = None
            new_total_exp = experience_earned

        # ── Bước 2: Kiểm tra có đủ goal không ────────────────
        now_protected = new_total_exp >= experience_goal
        protected_by = 'user' if now_protected else None

        if existing:
            self.streak_repo.update_streak_date_exp(streak_date_id, new_total_exp, now_protected, protected_by)
        else:
            streak_date_id = self.streak_repo.create_streak_date(
                user_id, new_total_exp, now_protected, protected_by
            )

        # ── Chưa đủ goal → dừng ──────────────────────────────
        if not now_protected:
            return {
                'status': 'not_reached',
                'current_length': None,
                'experience_today': new_total_exp,
                'experience_goal': experience_goal,
            }

        # ── Đã đủ goal nhưng đã tính streak rồi trong ngày ───
        if was_protected_before:
            # Ưu tiên lấy streak qua StreakId lưu trong StreakDate (đáng tin hơn)
            streak_id = existing.get('StreakId') if existing else None
            current_length = None
            if streak_id:
                streak = self.streak_repo.get_streak_by_id(streak_id)
                current_length = streak.get('LenghtStreak') if streak else None
            if current_length is None:
                # Fallback: tìm streak đang active của user
                current_streak = self.streak_repo.get_current_streak(user_id)
                current_length = current_streak.get('LenghtStreak') if current_streak else None
            return {
                'status': 'already_counted',
                'current_length': current_length,
                'experience_today': new_total_exp,
                'experience_goal': experience_goal,
            }

        # ── Lần đầu đủ goal hôm nay → tạo/nối Streak ─────────
        current_streak = self.streak_repo.get_current_streak(user_id)

        if current_streak:
            streak_id = current_streak.get('Id')
            self.streak_repo.increment_streak_length(streak_id)
            self.streak_repo.update_streak_id(streak_date_id, streak_id)
            new_length = current_streak.get('LenghtStreak', 0) + 1
            status = 'extended'
        else:
            streak_id = self.streak_repo.create_streak(user_id, today_int)
            self.streak_repo.update_streak_id(streak_date_id, streak_id)
            new_length = 1
            status = 'created'

        return {
            'status': status,
            'current_length': new_length,
            'experience_today': new_total_exp,
            'experience_goal': experience_goal,
        }
