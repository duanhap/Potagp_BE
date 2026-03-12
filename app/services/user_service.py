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
