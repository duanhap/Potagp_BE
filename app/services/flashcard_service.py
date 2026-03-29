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

    def get_flashcards(self, uid, word_set_id, requested_mode, requested_filter='all', current_word_id=None, size=20):
        # 1. Verification
        user = self.user_repo.get_by_uid(uid)
        if not user:
            return None, 'user_not_found'
        
        word_set = self.word_set_repo.get_by_id(word_set_id)
        if not word_set:
            return None, 'word_set_not_found'
            
        if word_set.user_id != user.id and not word_set.is_public:
            return None, 'forbidden'
            
        # 2. Get/Create FlashcardGame
        game = self.game_repo.get_by_word_set_id(word_set_id)
        if not game:
            words = self.word_repo.get_all_by_word_set_id(word_set_id)
            if not words:
                return {"items": [], "total": 0, "page": 1, "size": size, "total_pages": 0}, None
            # If no game, create it
            game_id = self.game_repo.create(word_set_id, requested_mode, requested_filter)
            current_mode = requested_mode
            current_filter = requested_filter
        else:
            game_id = game.id
            current_mode = game.mode
            current_filter = game.filter

        # 3. Synchronize `Flashcard`s with `Word`s
        words = self.word_repo.get_all_by_word_set_id(word_set_id)
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

        # Mode or Filter changed check
        if current_mode != requested_mode or current_filter != requested_filter:
            self.game_repo.update_game_settings(game_id, requested_mode, requested_filter)
            current_mode = requested_mode
            current_filter = requested_filter
            needs_shuffle = True

        # Check if we have no active cards but words exist (to recover from buggy state)
        active_fcs = [fc for fc in existing_flashcards if fc.order > 0]
        if not needs_shuffle and not active_fcs and words:
            needs_shuffle = True

        # Re-calc orders if needed (triggered by mode/filter change OR zero flashcards)
        if needs_shuffle or (not existing_flashcards and words_to_add):
            all_word_ids = [fc.word_id for fc in existing_flashcards] + [w.id for w in words_to_add]
            all_word_ids.sort()
            
            matching_ids = []
            zero_ids = []
            for wid in all_word_ids:
                w = word_id_to_word.get(wid)
                if not w: continue
                is_match = False
                if current_filter.lower() == 'all': is_match = True
                elif current_filter.lower() == 'known' and w.status.lower() == 'known': is_match = True
                elif current_filter.lower() == 'unknown' and w.status.lower() == 'unknown': is_match = True
                
                if is_match: matching_ids.append(wid)
                else: zero_ids.append(wid)
            
            matching_ids.sort()
            orders = list(range(1, len(matching_ids) + 1))
            if current_mode == 'random':
                random.shuffle(orders)
            
            updates = []
            inserts = []
            word_id_to_fc_id = {fc.word_id: fc.id for fc in existing_flashcards}
            
            for wid, order in zip(matching_ids, orders):
                if wid in word_id_to_fc_id:
                    updates.append((order, word_id_to_fc_id[wid]))
                else:
                    inserts.append({'order': order, 'word_id': wid, 'game_id': game_id})
            
            for wid in zero_ids:
                if wid in word_id_to_fc_id:
                    updates.append((0, word_id_to_fc_id[wid]))
                else:
                    inserts.append({'order': 0, 'word_id': wid, 'game_id': game_id})
                    
            if updates: self.flashcard_repo.update_orders(updates)
            if inserts: self.flashcard_repo.create_many(inserts)
        else:
            # Incremental addition of new words
            if words_to_add:
                active_fcs = [fc for fc in existing_flashcards if fc.order > 0]
                inserts = []
                if current_mode == 'normal':
                    max_order = max([int(fc.order) for fc in active_fcs]) if active_fcs else 0
                    for w in words_to_add:
                        is_match = False
                        if current_filter.lower() == 'all': is_match = True
                        elif current_filter.lower() == 'known' and w.status.lower() == 'known': is_match = True
                        elif current_filter.lower() == 'unknown' and w.status.lower() == 'unknown': is_match = True
                        
                        if is_match:
                            max_order += 1
                            inserts.append({'order': max_order, 'word_id': w.id, 'game_id': game_id})
                        else:
                            inserts.append({'order': 0, 'word_id': w.id, 'game_id': game_id})
                    self.flashcard_repo.create_many(inserts)
                elif current_mode == 'random':
                    current_order = 0
                    if current_word_id:
                        for fc in existing_flashcards:
                            if fc.word_id == current_word_id:
                                current_order = fc.order
                                break
                    future_active_fcs = [fc for fc in active_fcs if fc.order > current_order]
                    matching_new = []
                    zero_new = []
                    for w in words_to_add:
                        is_match = False
                        if current_filter.lower() == 'all': is_match = True
                        elif current_filter.lower() == 'known' and w.status.lower() == 'known': is_match = True
                        elif current_filter.lower() == 'unknown' and w.status.lower() == 'unknown': is_match = True
                        if is_match: matching_new.append(w)
                        else: zero_new.append(w)
                    
                    future_ids = [fc.word_id for fc in future_active_fcs] + [w.id for w in matching_new]
                    future_ids.sort()
                    future_orders = list(range(current_order + 1, current_order + 1 + len(future_ids)))
                    random.shuffle(future_orders)
                    
                    updates = []
                    wid_to_fc_id = {fc.word_id: fc.id for fc in future_active_fcs}
                    for wid, order in zip(future_ids, future_orders):
                        if wid in wid_to_fc_id:
                            updates.append((order, wid_to_fc_id[wid]))
                        else:
                            inserts.append({'order': order, 'word_id': wid, 'game_id': game_id})
                    for w in zero_new:
                        inserts.append({'order': 0, 'word_id': w.id, 'game_id': game_id})
                    
                    if updates: self.flashcard_repo.update_orders(updates)
                    if inserts: self.flashcard_repo.create_many(inserts)

        # 4. Fetch the final list and prepare output
        final_flashcards = self.flashcard_repo.get_by_game_id(game_id)
        # Filter for active cards (order > 0)
        active_flashcards = [fc for fc in final_flashcards if fc.order > 0]
        
        result_items = []
        for fc in active_flashcards:
            w = word_id_to_word.get(fc.word_id)
            if w:
                w_dict = w.to_dict()
                w_dict['flashcard_order'] = fc.order
                result_items.append(w_dict)
                
        total = len(result_items)
        size = max(1, int(size or 20))
        
        start_idx = 0
        if current_word_id:
            for i, item in enumerate(result_items):
                if item['id'] == current_word_id:
                    start_idx = i
                    break
        
        paged_items = result_items[start_idx : start_idx + size]
        
        return {
            "items": paged_items,
            "total": total,
            "size": size,
            "total_pages": (total + size - 1) // size if size else 0
        }, None
