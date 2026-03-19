from app.repositories.word_repository import WordRepository
from app.repositories.word_set_repository import WordSetRepository
from app.repositories.user_repository import UserRepository


class WordService:

    def __init__(self):
        self.word_repository = WordRepository()
        self.word_set_repository = WordSetRepository()
        self.user_repository = UserRepository()

    def _check_word_set_access(self, uid, word_set_id, require_owner=True):
        user = self.user_repository.get_by_uid(uid)
        if not user:
            return None, 'user_not_found'

        word_set = self.word_set_repository.get_by_id(word_set_id)
        if not word_set:
            return None, 'not_found'
        if require_owner and word_set.user_id != user.id:
            return None, 'forbidden'

        return user, None

    def get_words_by_word_set(self, uid, word_set_id, page=1, page_size=None):
        user, error = self._check_word_set_access(uid, word_set_id, require_owner=False)
        if error:
            return None, None, error
        if not user:
            return None, None, 'user_not_found'

        word_set = self.word_set_repository.get_by_id(word_set_id)
        if word_set.user_id != user.id and not word_set.is_public:
            return None, None, 'forbidden'

        if page_size is None:
            return self.word_repository.get_all_by_word_set_id(word_set_id), None, None

        total = self.word_repository.count_by_word_set_id(word_set_id)
        words = self.word_repository.get_page_by_word_set_id(word_set_id, page=page, page_size=page_size)
        return words, total, None

    def get_word(self, uid, word_id):
        user = self.user_repository.get_by_uid(uid)
        if not user:
            return None, 'user_not_found'

        word = self.word_repository.get_by_id(word_id)
        if not word:
            return None, 'not_found'

        word_set = self.word_set_repository.get_by_id(word.word_set_id)
        if not word_set:
            return None, 'not_found'
        if word_set.user_id != user.id and not word_set.is_public:
            return None, 'forbidden'

        return word, None

    def create_word(self, uid, word_set_id, term, definition, description=None, status='unknown'):
        user, error = self._check_word_set_access(uid, word_set_id)
        if error:
            return None, error

        word_id = self.word_repository.create(term, definition, word_set_id, description, status)
        return self.word_repository.get_by_id(word_id), None

    def create_words(self, uid, word_set_id, words):
        """Create multiple words at once. words: list of dict with term, definition, description?, status?"""
        user, error = self._check_word_set_access(uid, word_set_id)
        if error:
            return None, error

        valid_words = [w for w in words if w.get('term') and w.get('definition')]
        if not valid_words:
            return [], None

        created_ids = self.word_repository.create_many(word_set_id, valid_words)
        result = [self.word_repository.get_by_id(wid) for wid in created_ids]
        return result, None

    def update_word(self, uid, word_id, term=None, definition=None, description=None, status=None):
        user = self.user_repository.get_by_uid(uid)
        if not user:
            return None, 'user_not_found'

        word = self.word_repository.get_by_id(word_id)
        if not word:
            return None, 'not_found'

        word_set = self.word_set_repository.get_by_id(word.word_set_id)
        if not word_set or word_set.user_id != user.id:
            return None, 'forbidden'

        self.word_repository.update(word_id, term, definition, description, status)
        return self.word_repository.get_by_id(word_id), None

    def delete_word(self, uid, word_id):
        user = self.user_repository.get_by_uid(uid)
        if not user:
            return 'user_not_found'

        word = self.word_repository.get_by_id(word_id)
        if not word:
            return 'not_found'

        word_set = self.word_set_repository.get_by_id(word.word_set_id)
        if not word_set or word_set.user_id != user.id:
            return 'forbidden'

        self.word_repository.delete(word_id)
        return None
