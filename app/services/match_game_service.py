import random
from app.repositories.match_game_repository import MatchGameRepository
from app.repositories.word_set_repository import WordSetRepository
from app.repositories.user_repository import UserRepository

MAX_PAIRS = 6  # tối đa 6 cặp = 12 thẻ


class MatchGameService:

    def __init__(self):
        self.match_repo = MatchGameRepository()
        self.word_set_repo = WordSetRepository()
        self.user_repo = UserRepository()

    def _check_access(self, uid, word_set_id):
        user = self.user_repo.get_by_uid(uid)
        if not user:
            return None, None, 'user_not_found'
        word_set = self.word_set_repo.get_by_id(word_set_id)
        if not word_set:
            return None, None, 'not_found'
        if word_set.user_id != user.id and not word_set.is_public:
            return None, None, 'forbidden'
        return user, word_set, None

    def start_game(self, uid, word_set_id):
        """
        Lấy random tối đa 6 từ, tạo 12 thẻ (term + definition), shuffle.
        Trả về game_id và danh sách thẻ.
        """
        user, word_set, error = self._check_access(uid, word_set_id)
        if error:
            return None, None, error

        words = self.match_repo.get_random_words(word_set_id, limit=MAX_PAIRS)
        if len(words) < 2:
            return None, None, 'not_enough_words'

        # Tạo 2 thẻ cho mỗi từ: 1 term + 1 definition
        cards = []
        for word in words:
            cards.append({
                'card_id': f'term_{word.id}',
                'pair_id': word.id,
                'content': word.term,
                'type': 'term'
            })
            cards.append({
                'card_id': f'def_{word.id}',
                'pair_id': word.id,
                'content': word.definition,
                'type': 'definition'
            })

        random.shuffle(cards)

        game_id = self.match_repo.create_game(word_set_id)
        return game_id, cards, None

    def submit_result(self, uid, game_id, word_set_id, completed_time):
        """Lưu thời gian hoàn thành, trả về best time."""
        user, _, error = self._check_access(uid, word_set_id)
        if error:
            return None, error

        self.match_repo.submit_result(game_id, completed_time)
        best = self.match_repo.get_best_time(word_set_id)
        return best, None

    def get_best_time(self, uid, word_set_id):
        user, _, error = self._check_access(uid, word_set_id)
        if error:
            return None, error
        return self.match_repo.get_best_time(word_set_id), None
