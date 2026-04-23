from flask import Blueprint, request, jsonify
from app.services.flashcard_service import FlashcardService
from app.utils.firebase_auth import token_required

flashcard_bp = Blueprint('flashcard', __name__)
flashcard_service = FlashcardService()

@flashcard_bp.route('', methods=['GET'])
@token_required
def get_flashcards():
    """
    Get flashcards for a specific WordSet with sync and shuffle logic
    ---
    tags:
      - Flashcard
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
      - name: word_set_id
        in: query
        type: integer
        required: true
      - name: mode
        in: query
        type: string
        required: true
        description: Mode for learning, normal or random
        enum: [normal, random]
      - name: current_word_id
        in: query
        type: integer
        required: false
        description: The ID of the word the user is currently learning
      - name: size
        in: query
        type: integer
        required: false
        default: 20
      - name: filter
        in: query
        type: string
        required: false
        default: all
        description: Filter by word status (all, known, unknown)
        enum: [all, known, unknown]
    responses:
      200:
        description: Flashcards retrieved successfully
      400:
        description: Missing required params
      403:
        description: Forbidden
      404:
        description: Not found
    """
    uid = request.user['uid']
    word_set_id = request.args.get('word_set_id', type=int)
    mode = request.args.get('mode', type=str)
    current_word_id = request.args.get('current_word_id', type=int)
    size = request.args.get('size', default=20, type=int)
    filter_val = request.args.get('filter', default='all', type=str)

    if not filter_val: filter_val = 'all'

    if not word_set_id or not mode:
        return jsonify({'success': False, 'message': 'word_set_id and mode are required'}), 400

    if mode not in ['normal', 'random']:
        return jsonify({'success': False, 'message': 'mode must be normal or random'}), 400

    if filter_val.lower() not in ['all', 'known', 'unknown']:
        return jsonify({'success': False, 'message': 'filter must be All, known or unknown'}), 400

    data, error = flashcard_service.get_flashcards(
        uid, word_set_id, mode, filter_val, current_word_id, size
    )

    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'word_set_not_found':
        return jsonify({'success': False, 'message': 'Word set not found'}), 404
    if error == 'game_not_found':
        return jsonify({'success': False, 'message': 'Flashcard Game not found'}), 404
    if error == 'forbidden':
        return jsonify({'success': False, 'message': 'You do not have permission to access this word set'}), 403

    return jsonify({
        'success': True,
        'message': 'Flashcards retrieved successfully',
        'data': data['items'],
        'pagination': {
            'size': data['size'],
            'total': data['total'],
            'total_pages': data['total_pages']
        }
    }), 200
