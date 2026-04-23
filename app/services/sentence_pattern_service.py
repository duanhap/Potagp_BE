from app.repositories.sentence_pattern_repository import SentencePatternRepository
from app.repositories.user_repository import UserRepository


class SentencePatternService:
    def __init__(self):
        self.sentence_pattern_repository = SentencePatternRepository()
        self.user_repository = UserRepository()

    def get_sentence_patterns_by_user(self, uid):
        user = self.user_repository.get_by_uid(uid)
        if not user:
            return None
        return self.sentence_pattern_repository.get_all_by_user_id(user.id)

    def get_sentence_patterns_with_recent(self, uid, limit=10):
        user = self.user_repository.get_by_uid(uid)
        if not user:
            return None, None
        all_patterns = self.sentence_pattern_repository.get_all_by_user_id(user.id)
        recent_patterns = self.sentence_pattern_repository.get_recent_by_user_id(user.id, limit)
        return all_patterns, recent_patterns

    def get_recent_sentence_patterns(self, uid, limit=3):
        user = self.user_repository.get_by_uid(uid)
        if not user:
            return None
        return self.sentence_pattern_repository.get_recent_by_user_id(user.id, limit)

    def get_sentence_pattern(self, sentence_pattern_id, uid):
        user = self.user_repository.get_by_uid(uid)
        if not user:
            return None, 'user_not_found'

        sentence_pattern = self.sentence_pattern_repository.get_by_id(sentence_pattern_id)
        if not sentence_pattern:
            return None, 'not_found'

        if sentence_pattern.user_id != user.id and not sentence_pattern.is_public:
            return None, 'forbidden'

        # Update last_opened in DB when detail is fetched
        self.sentence_pattern_repository.update_last_opened(sentence_pattern_id)
        sentence_pattern = self.sentence_pattern_repository.get_by_id(sentence_pattern_id)

        return sentence_pattern, None

    def create_sentence_pattern(self, uid, name, description, is_public, term_lang_code, def_lang_code):
        user = self.user_repository.get_by_uid(uid)
        if not user:
            return None

        sentence_pattern_id = self.sentence_pattern_repository.create(
            name, description, is_public, term_lang_code, def_lang_code, user.id
        )
        return self.sentence_pattern_repository.get_by_id(sentence_pattern_id)

    def update_sentence_pattern(self, sentence_pattern_id, uid, name, description, is_public, term_lang_code, def_lang_code):
        user = self.user_repository.get_by_uid(uid)
        if not user:
            return None, 'user_not_found'

        sentence_pattern = self.sentence_pattern_repository.get_by_id(sentence_pattern_id)
        if not sentence_pattern:
            return None, 'not_found'
        if sentence_pattern.user_id != user.id:
            return None, 'forbidden'

        self.sentence_pattern_repository.update(sentence_pattern_id, name, description, is_public, term_lang_code, def_lang_code)
        return self.sentence_pattern_repository.get_by_id(sentence_pattern_id), None

    def delete_sentence_pattern(self, sentence_pattern_id, uid):
        user = self.user_repository.get_by_uid(uid)
        if not user:
            return 'user_not_found'

        sentence_pattern = self.sentence_pattern_repository.get_by_id(sentence_pattern_id)
        if not sentence_pattern:
            return 'not_found'
        if sentence_pattern.user_id != user.id:
            return 'forbidden'

        self.sentence_pattern_repository.delete(sentence_pattern_id)
        return None