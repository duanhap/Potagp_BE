from datetime import date, timedelta
from app.repositories.streak_repository import StreakRepository
from app.repositories.item_repository import ItemRepository

def run_midnight_streak_check():
    """
    Hàm thực hiện kiểm tra streak của toàn bộ user vào lúc 0h.
    Nếu hôm qua họ không học bài:
      - Nếu có WaterStreak: Trừ 1 và bảo vệ chuỗi (tăng LenghtStreak + 1).
      - Nếu không có: Reset CurentStreak về False.
    """
    print(">>> [STREAK TASK] Starting midnight check...")
    streak_repo = StreakRepository()
    item_repo = ItemRepository()
    
    # Ngày cần kiểm tra là ngày hôm qua (vì bây giờ là 0h)
    yesterday = date.today() - timedelta(days=1)
    
    # 1. Lấy toàn bộ user đang có chuỗi active
    active_streaks = streak_repo.get_all_active_streaks()
    
    for streak in active_streaks:
        user_id = streak['UserId']
        streak_id = streak['Id']
        
        # 2. Kiểm tra xem hôm qua họ đã đạt mục tiêu chưa
        streak_date = streak_repo.get_streak_date_by_date(user_id, yesterday)
        
        # StreakDate.ProtectedDate lưu dưới dạng bit trong MySQL/PyMySQL
        # Cần kiểm tra xem nó có giá trị True (hoặc 1) không
        is_already_protected = False
        if streak_date:
            val = streak_date.get('ProtectedDate')
            if isinstance(val, bytes):
                is_already_protected = val != b'\x00'
            else:
                is_already_protected = bool(val)

        if is_already_protected:
            # Họ đã tự học bài rồi, không cần can thiệp
            continue
            
        # 3. Nếu chưa học -> Thử dùng Item
        user_items = item_repo.get_by_user_id(user_id)
        if user_items and user_items.get('WaterStreak', 0) > 0:
            # Trừ bình nước
            if item_repo.decrement_water_streak(user_id):
                # Bảo vệ ngày hôm qua
                if streak_date:
                    streak_repo.update_streak_date_exp(
                        streak_date['Id'], 
                        streak_date['ExperiencePointsEarned'], 
                        True, 
                        'item'
                    )
                else:
                    streak_repo.create_protected_streak_date(user_id, yesterday, 'item', streak_id)
                
                # Nối dài streak thêm 1 ngày
                streak_repo.increment_streak_length(streak_id)
                print(f"[STREAK TASK] User {user_id}: Managed to save streak using WaterStreak.")
        else:
            # Không có item -> Đứt chuỗi
            streak_repo.set_streak_inactive(streak_id)
            print(f"[STREAK TASK] User {user_id}: Streak broken (no item available).")

    print(">>> [STREAK TASK] Midnight check completed.")
