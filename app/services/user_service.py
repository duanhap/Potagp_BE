from app.repositories.user_repository import UserRepository

class UserService:
    def __init__(self):
        self.user_repository = UserRepository()

    def get_user_profile(self, uid):
        user = self.user_repository.get_by_uid(uid)
        if user:
            self.user_repository.update_last_login(uid)
        return user

    def register_user(self, uid, email, name):
        existing_user = self.user_repository.get_by_uid(uid)
        if existing_user:
            return existing_user, False # Already exists
        
        user_id = self.user_repository.create(uid, email, name)
        return self.user_repository.get_by_uid(uid), True

    def update_user_profile(self, uid, data):
        allowed_profile_fields = {'name', 'avatar', 'token_fcm'}

        if not isinstance(data, dict):
            return None, 'Invalid request body'

        update_data = {
            key: value
            for key, value in data.items()
            if key in allowed_profile_fields and value is not None
        }

        if not update_data:
            return None, 'No valid fields to update'

        existing_user = self.user_repository.get_by_uid(uid)
        if not existing_user:
            return None, 'User not found'

        updated = self.user_repository.update_profile(uid, update_data)
        if not updated:
            # No changed fields in DB (same payload), still treat as success.
            return existing_user, None

        return self.user_repository.get_by_uid(uid), None

    def save_user_setting(self, uid, data):
        if not isinstance(data, dict):
            return None, 'Invalid request body'

        notification = data.get('notification')
        language = data.get('language')
        experience_goal = data.get('experiencegoal', data.get('experience_goal', 15))

        if notification not in (0, 1, True, False):
            return None, 'notification must be 0 or 1'

        if language not in ('en', 'vi'):
            return None, 'language must be en or vi'

        try:
            experience_goal = int(experience_goal)
        except (TypeError, ValueError):
            return None, 'experiencegoal must be an integer'

        if experience_goal <= 0:
            return None, 'experiencegoal must be greater than 0'

        setting = self.user_repository.save_user_setting(
            uid=uid,
            notification=int(bool(notification)),
            language=language,
            experience_goal=experience_goal
        )

        if not setting:
            return None, 'User not found'

        return setting, None

    def get_user_setting(self, uid):
        setting = self.user_repository.get_user_setting(uid)
        if not setting:
            return None, 'User not found'
        return setting, None

    def get_top_users(self, limit=1000):
        return self.user_repository.get_top_users(limit)

    def get_user_rank(self, uid):
        user = self.user_repository.get_by_uid(uid)
        if not user:
            return None
        return self.user_repository.get_user_rank(uid)
