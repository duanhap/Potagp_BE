from app.repositories.reward_repository import RewardRepository
from app.repositories.user_repository import UserRepository
from app.services.streak_service import StreakService

# Bảng cấu hình phần thưởng theo action
REWARD_CONFIG = {
    'learning-video': {
        'base_experience': 15,
        'diamond': 20,
    }
}


class RewardService:
    def __init__(self):
        self.reward_repository = RewardRepository()
        self.user_repository = UserRepository()
        self.streak_service = StreakService()

    def claim_reward(self, uid, action, hack_experience=False, super_experience=False):
        """
        Tính và cộng phần thưởng cho user, sau đó xử lý streak hàng ngày.

        Multiplier XP:
          - hackExperience = True  → x2
          - superExperience = True → x3
          - Mặc định              → x1

        Returns:
          (result_dict, error_string)
          result_dict gồm: experience_earned, diamond_earned, new_experience, new_diamond, streak
        """
        config = REWARD_CONFIG.get(action)
        if config is None:
            return None, 'invalid_action'

        user = self.user_repository.get_by_uid(uid)
        if not user:
            return None, 'user_not_found'

        base_exp = config['base_experience']
        diamond = config['diamond']

        if super_experience:
            multiplier = 3
        elif hack_experience:
            multiplier = 2
        else:
            multiplier = 1

        experience_earned = base_exp * multiplier

        result = self.reward_repository.add_experience_and_diamond(uid, experience_earned, diamond)
        if result is None:
            return None, 'update_failed'

        new_experience, new_diamond = result

        # Xử lý streak sau khi cộng XP thành công
        streak_result = self.streak_service.process_streak(user.id, experience_earned)

        return {
            'experience_earned': experience_earned,
            'diamond_earned': diamond,
            'new_experience': new_experience,
            'new_diamond': new_diamond,
            'streak': streak_result,
        }, None
