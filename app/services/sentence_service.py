from app.repositories.sentence_repository import SentenceRepository
from app.repositories.sentence_pattern_repository import SentencePatternRepository
from app.repositories.user_repository import UserRepository


class SentenceService:
    def __init__(self):
        self.sentence_repository = SentenceRepository()
        self.sentence_pattern_repository = SentencePatternRepository()
        self.user_repository = UserRepository()

    def get_sentences_by_pattern(self, uid, pattern_id, page=1, page_size=20):
        user = self.user_repository.get_by_uid(uid)
        if not user:
            return None, 'user_not_found'

        pattern = self.sentence_pattern_repository.get_by_id(pattern_id)
        if not pattern:
            return None, 'pattern_not_found'
        if pattern.user_id != user.id and not pattern.is_public:
            return None, 'forbidden'

        sentences = self.sentence_repository.get_by_pattern_id(pattern_id, page, page_size)
        total = self.sentence_repository.count_by_pattern_id(pattern_id)
        return {'sentences': sentences, 'total': total}, None

    def create_sentences_bulk(self, uid, pattern_id, sentences):
        user = self.user_repository.get_by_uid(uid)
        if not user:
            return None, 'user_not_found'

        pattern = self.sentence_pattern_repository.get_by_id(pattern_id)
        if not pattern:
            return None, 'pattern_not_found'
        if pattern.user_id != user.id:
            return None, 'forbidden'

        inserted = self.sentence_repository.create_bulk(sentences, pattern_id)
        return inserted, None

    def create_sentence(self, uid, pattern_id, term, definition, status='unknown', mistakes=0):
        if status not in ['unknown', 'known']:
            return None, 'invalid_status'
        user = self.user_repository.get_by_uid(uid)
        if not user:
            return None, 'user_not_found'

        pattern = self.sentence_pattern_repository.get_by_id(pattern_id)
        if not pattern:
            return None, 'pattern_not_found'
        if pattern.user_id != user.id:
            return None, 'forbidden'

        sentence_id = self.sentence_repository.create(term, definition, status, mistakes, pattern_id)
        return self.sentence_repository.get_by_id(sentence_id), None

    def update_sentence(self, sentence_id, uid, term, definition, status='unknown', mistakes=0):
        if status not in ['unknown', 'known']:
            return None, 'invalid_status'
        user = self.user_repository.get_by_uid(uid)
        if not user:
            return None, 'user_not_found'

        sentence = self.sentence_repository.get_by_id(sentence_id)
        if not sentence:
            return None, 'not_found'

        pattern = self.sentence_pattern_repository.get_by_id(sentence.pattern_id)
        if not pattern:
            return None, 'pattern_not_found'
        if pattern.user_id != user.id:
            return None, 'forbidden'

        updated = self.sentence_repository.update(sentence_id, term, definition, status, mistakes)
        if not updated:
            return None, 'update_failed'

        return self.sentence_repository.get_by_id(sentence_id), None

    def delete_sentence(self, sentence_id, uid):
        user = self.user_repository.get_by_uid(uid)
        if not user:
            return 'user_not_found'

        sentence = self.sentence_repository.get_by_id(sentence_id)
        if not sentence:
            return 'not_found'

        pattern = self.sentence_pattern_repository.get_by_id(sentence.pattern_id)
        if not pattern:
            return 'pattern_not_found'
        if pattern.user_id != user.id:
            return 'forbidden'

        deleted = self.sentence_repository.delete(sentence_id)
        if not deleted:
            return 'delete_failed'
        return None