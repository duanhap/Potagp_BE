from app.repositories.word_set_repository import WordSetRepository
from app.repositories.user_repository import UserRepository


class WordSetService:

    def __init__(self):
        self.word_set_repository = WordSetRepository()
        self.user_repository = UserRepository()

    def get_word_sets_by_user(self, uid):
        user = self.user_repository.get_by_uid(uid)
        if not user:
            return None
        return self.word_set_repository.get_all_by_user_id(user.id)

    def get_recent_word_sets(self, uid, limit=3):
        user = self.user_repository.get_by_uid(uid)
        if not user:
            return None
        return self.word_set_repository.get_recent_by_user_id(user.id, limit)

    def get_word_set(self, word_set_id, uid):
        user = self.user_repository.get_by_uid(uid)
        if not user:
            return None, 'user_not_found'

        word_set = self.word_set_repository.get_by_id(word_set_id)
        if not word_set:
            return None, 'not_found'
        if word_set.user_id != user.id and not word_set.is_public:
            return None, 'forbidden'

        self.word_set_repository.update_last_opened(word_set_id)
        return self.word_set_repository.get_by_id(word_set_id), None

    def create_word_set(self, uid, name, description, is_public, def_lang_code, term_lang_code):
        user = self.user_repository.get_by_uid(uid)
        if not user:
            return None

        word_set_id = self.word_set_repository.create(
            name, description, is_public, def_lang_code, term_lang_code, user.id
        )
        return self.word_set_repository.get_by_id(word_set_id)

    def update_word_set(self, word_set_id, uid, name, description, is_public, def_lang_code, term_lang_code):
        user = self.user_repository.get_by_uid(uid)
        if not user:
            return None, 'user_not_found'

        word_set = self.word_set_repository.get_by_id(word_set_id)
        if not word_set:
            return None, 'not_found'
        if word_set.user_id != user.id:
            return None, 'forbidden'

        self.word_set_repository.update(word_set_id, name, description, is_public, def_lang_code, term_lang_code)
        return self.word_set_repository.get_by_id(word_set_id), None

    def delete_word_set(self, word_set_id, uid):
        user = self.user_repository.get_by_uid(uid)
        if not user:
            return 'user_not_found'

        word_set = self.word_set_repository.get_by_id(word_set_id)
        if not word_set:
            return 'not_found'
        if word_set.user_id != user.id:
            return 'forbidden'

        self.word_set_repository.delete(word_set_id)
        return None
