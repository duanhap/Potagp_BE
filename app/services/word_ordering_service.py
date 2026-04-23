from app.repositories.sentence_repository import SentenceRepository
from app.repositories.sentence_pattern_repository import SentencePatternRepository
from app.repositories.user_repository import UserRepository
from app.services.reward_service import RewardService
from app.utils.database import get_db_connection
from datetime import datetime

GAME_SIZE = 5


class WordOrderingService:

    def __init__(self):
        self.sentence_repo = SentenceRepository()
        self.pattern_repo = SentencePatternRepository()
        self.user_repo = UserRepository()
        self.reward_service = RewardService()

    def _check_access(self, uid, pattern_id):
        user = self.user_repo.get_by_uid(uid)
        if not user:
            return None, None, 'user_not_found'
        pattern = self.pattern_repo.get_by_id(pattern_id)
        if not pattern:
            return None, None, 'not_found'
        if pattern.user_id != user.id and not pattern.is_public:
            return None, None, 'forbidden'
        return user, pattern, None

    def start_game(self, uid, pattern_id):
        """Lấy random GAME_SIZE câu, tạo WritingGame session, trả về game_id + sentences."""
        user, pattern, error = self._check_access(uid, pattern_id)
        if error:
            return None, None, error

        sentences = self.sentence_repo.get_random_by_pattern_id(pattern_id, limit=GAME_SIZE)
        if len(sentences) < 2:
            return None, None, 'not_enough_sentences'

        game_id = self._create_writing_game(pattern_id)
        self.pattern_repo.update_last_opened(pattern_id)

        return game_id, sentences, None

    def submit_result(self, uid, game_id, pattern_id, correct_sentence_ids, wrong_sentence_ids,
                      hack_experience=False, super_experience=False):
        """
        Lưu kết quả game:
        - Tăng NumberOfMistakes cho câu sai
        - Cập nhật LastOpened cho tất cả câu đã làm
        - Gọi RewardService để cộng XP + Diamond + xử lý streak
        - Cập nhật WritingGame
        """
        user, _, error = self._check_access(uid, pattern_id)
        if error:
            return None, error

        all_sentence_ids = correct_sentence_ids + wrong_sentence_ids

        # Tăng mistakes cho câu sai
        for sid in wrong_sentence_ids:
            self.sentence_repo.increment_mistakes(sid)

        # Cập nhật LastOpened cho tất cả câu đã làm
        for sid in all_sentence_ids:
            self.sentence_repo.update_last_opened(sid)

        correct_count = len(correct_sentence_ids)
        total_count = correct_count + len(wrong_sentence_ids)

        # Cập nhật WritingGame
        self._complete_writing_game(game_id)

        # Claim reward qua RewardService (nhất quán với MatchGame)
        reward_result, reward_error = self.reward_service.claim_reward(
            uid=uid,
            action='playing-word-ordering',
            hack_experience=hack_experience,
            super_experience=super_experience
        )
        if reward_error:
            return None, reward_error

        return {
            'correct_count': correct_count,
            'total_count': total_count,
            **reward_result   # experience_earned, diamond_earned, new_experience, new_diamond, streak
        }, None

    # ── DB helpers ────────────────────────────────────────────────────────────

    def _create_writing_game(self, pattern_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO WritingGame (CreatedAt, SetencePatternId) VALUES (%s, %s)",
                    (datetime.now(), pattern_id)
                )
            connection.commit()
            return cursor.lastrowid
        finally:
            connection.close()

    def _complete_writing_game(self, game_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE WritingGame SET CompletedTime = %s WHERE Id = %s",
                    (datetime.now(), game_id)
                )
            connection.commit()
        finally:
            connection.close()
