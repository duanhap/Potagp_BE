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

        updated = self.user_repository.update_profile(uid, update_data)
        if not updated:
            return None, 'User not found'

        return self.user_repository.get_by_uid(uid), None
