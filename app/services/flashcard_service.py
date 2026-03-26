import random
from app.repositories.flashcard_repository import FlashcardRepository
from app.repositories.flashcard_game_repository import FlashcardGameRepository
from app.repositories.word_repository import WordRepository
from app.repositories.word_set_repository import WordSetRepository
from app.repositories.user_repository import UserRepository

class FlashcardService:
    def __init__(self):
        self.flashcard_repo = FlashcardRepository()
        self.game_repo = FlashcardGameRepository()
        self.word_repo = WordRepository()
        self.word_set_repo = WordSetRepository()
        self.user_repo = UserRepository()

    def get_flashcards(self, uid, word_set_id, requested_mode, current_word_id=None, size=20):
        # 1. Verification
        user = self.user_repo.get_by_uid(uid)
        if not user:
            return None, 'user_not_found'
        
        word_set = self.word_set_repo.get_by_id(word_set_id)
        if not word_set:
            return None, 'word_set_not_found'
            
        if word_set.user_id != user.id and not word_set.is_public:
            return None, 'forbidden'
            
        # 2. Get FlashcardGame
        game = self.game_repo.get_by_word_set_id(word_set_id)
        if not game:
            words = self.word_repo.get_all_by_word_set_id(word_set_id)
            if not words:
                return {"items": [], "total": 0, "page": 1, "size": size, "total_pages": 0}, None
            # If no game, create it
            game_id = self.game_repo.create(word_set_id, requested_mode)
            current_mode = requested_mode
        else:
            game_id = game.id
            current_mode = game.mode

        # 3. Synchronize `Flashcard`s with `Word`s
        words = self.word_repo.get_all_by_word_set_id(word_set_id)
        # Sort words by id ASC so they match the original addition order
        words.sort(key=lambda w: w.id)
        
        existing_flashcards = self.flashcard_repo.get_by_game_id(game_id)
        
        word_id_to_word = {w.id: w for w in words}
        fc_word_ids = {fc.word_id for fc in existing_flashcards}
        
        words_to_add = [w for w in words if w.id not in fc_word_ids]
        flashcards_to_remove = [fc for fc in existing_flashcards if fc.word_id not in word_id_to_word]
        
        needs_shuffle = False

        if flashcards_to_remove:
            self.flashcard_repo.delete_by_ids([fc.id for fc in flashcards_to_remove])
            existing_flashcards = [fc for fc in existing_flashcards if fc.word_id in word_id_to_word]

        # Mode changed check
        if current_mode != requested_mode:
            self.game_repo.update_mode(game_id, requested_mode)
            current_mode = requested_mode
            needs_shuffle = True

        # Handle Initial / Complete Shuffle
        if needs_shuffle or (not existing_flashcards and words_to_add):
            all_word_ids = [fc.word_id for fc in existing_flashcards] + [w.id for w in words_to_add]
            # Ensure word IDs are perfectly sorted chronologically
            all_word_ids.sort()
            
            orders = list(range(1, len(all_word_ids) + 1))
            if current_mode == 'random':
                random.shuffle(orders)
            
            updates = []
            inserts = []
            word_id_to_fc_id = {fc.word_id: fc.id for fc in existing_flashcards}
            
            for wid, order in zip(all_word_ids, orders):
                if wid in word_id_to_fc_id:
                    updates.append((order, word_id_to_fc_id[wid]))
                else:
                    inserts.append({'order': order, 'word_id': wid, 'game_id': game_id})
                    
            if updates:
                self.flashcard_repo.update_orders(updates)
            if inserts:
                self.flashcard_repo.create_many(inserts)
                
        else:
            # Add New Words Handling
            if words_to_add:
                if current_mode == 'normal':
                    max_order = max([int(fc.order) for fc in existing_flashcards]) if existing_flashcards else 0
                    max_order = int(max_order)
                    inserts = []
                    for i, w in enumerate(words_to_add):
                        inserts.append({'order': max_order + i + 1, 'word_id': w.id, 'game_id': game_id})
                    self.flashcard_repo.create_many(inserts)
                elif current_mode == 'random':
                    current_order = 0
                    if current_word_id:
                        for fc in existing_flashcards:
                            if fc.word_id == current_word_id:
                                current_order = fc.order
                                break
                    
                    past_fcs = [fc for fc in existing_flashcards if fc.order <= current_order]
                    future_fcs = [fc for fc in existing_flashcards if fc.order > current_order]
                    
                    future_word_ids = [fc.word_id for fc in future_fcs] + [w.id for w in words_to_add]
                    future_word_ids.sort()
                    
                    future_orders = list(range(current_order + 1, current_order + 1 + len(future_word_ids)))
                    random.shuffle(future_orders)
                    
                    updates = []
                    inserts = []
                    word_id_to_fc_id = {fc.word_id: fc.id for fc in future_fcs}
                    
                    for wid, order in zip(future_word_ids, future_orders):
                        if wid in word_id_to_fc_id:
                            updates.append((order, word_id_to_fc_id[wid]))
                        else:
                            inserts.append({'order': order, 'word_id': wid, 'game_id': game_id})
                    
                    if updates:
                        self.flashcard_repo.update_orders(updates)
                    if inserts:
                        self.flashcard_repo.create_many(inserts)

        # 4. Fetch the final ordered list from DB and close gaps
        final_flashcards = self.flashcard_repo.get_by_game_id(game_id)
        
        needs_gap_close = False
        for i, fc in enumerate(final_flashcards):
            expected_order = i + 1
            if fc.order != expected_order:
                needs_gap_close = True
                break
                
        if needs_gap_close:
            updates = []
            for i, fc in enumerate(final_flashcards):
                new_order = i + 1
                updates.append((new_order, fc.id))
                fc.order = new_order
            self.flashcard_repo.update_orders(updates)

        # 5. Pagination
        total = len(final_flashcards)
        size = max(1, int(size or 20))
        
        start_idx = 0
        if current_word_id:
            for i, fc in enumerate(final_flashcards):
                if fc.word_id == current_word_id:
                    start_idx = i
                    break
        
        end_idx = start_idx + size
        paged_flashcards = final_flashcards[start_idx:end_idx]
        
        # Mapping properties
        result_items = []
        for fc in paged_flashcards:
            w = word_id_to_word.get(fc.word_id)
            if w:
                w_dict = w.to_dict()
                w_dict['flashcard_order'] = fc.order
                result_items.append(w_dict)
                
        return {
            "items": result_items,
            "total": total,
            "size": size,
            "total_pages": (total + size - 1) // size if size else 0
        }, None
