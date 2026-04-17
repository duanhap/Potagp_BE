from flask import Blueprint, request, jsonify
from app.services.match_game_service import MatchGameService
from app.utils.firebase_auth import token_required

match_game_bp = Blueprint('match_game', __name__)
match_game_service = MatchGameService()


@match_game_bp.route('/start', methods=['POST'])
@token_required
def start_game():
    """
    Start a new match game — returns shuffled cards (term + definition pairs)
    ---
    tags:
      - MatchGame
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - word_set_id
          properties:
            word_set_id:
              type: integer
              example: 1
    responses:
      200:
        description: Game started successfully
      400:
        description: Not enough words (need at least 2)
      403:
        description: Forbidden
      404:
        description: Word set not found
      401:
        description: Unauthorized
    """
    uid = request.user['uid']
    data = request.get_json(silent=True) or {}
    word_set_id = data.get('word_set_id')

    if not word_set_id:
        return jsonify({'success': False, 'message': 'word_set_id is required'}), 400

    game_id, cards, error = match_game_service.start_game(uid, word_set_id)

    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'not_found':
        return jsonify({'success': False, 'message': 'Word set not found'}), 404
    if error == 'forbidden':
        return jsonify({'success': False, 'message': 'Forbidden'}), 403
    if error == 'not_enough_words':
        return jsonify({'success': False, 'message': 'Need at least 2 words to start a match game'}), 400

    return jsonify({
        'success': True,
        'message': 'Game started',
        'data': {
            'game_id': game_id,
            'cards': cards,
            'total_pairs': len(cards) // 2
        }
    }), 200


@match_game_bp.route('/submit', methods=['POST'])
@token_required
def submit_result():
    """
    Submit match game result and get best time
    ---
    tags:
      - MatchGame
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - game_id
            - word_set_id
            - completed_time
          properties:
            game_id:
              type: integer
              example: 1
            word_set_id:
              type: integer
              example: 1
            completed_time:
              type: number
              example: 30.5
              description: Time in seconds
    responses:
      200:
        description: Result submitted successfully
      400:
        description: Missing required fields
      401:
        description: Unauthorized
    """
    uid = request.user['uid']
    data = request.get_json(silent=True) or {}

    game_id = data.get('game_id')
    word_set_id = data.get('word_set_id')
    completed_time = data.get('completed_time')

    if not game_id or not word_set_id or completed_time is None:
        return jsonify({'success': False, 'message': 'game_id, word_set_id and completed_time are required'}), 400

    best, error = match_game_service.submit_result(uid, game_id, word_set_id, completed_time)

    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error in ('not_found', 'forbidden'):
        return jsonify({'success': False, 'message': error}), 403

    return jsonify({
        'success': True,
        'message': 'Result submitted',
        'data': {
            'completed_time': completed_time,
            'best_time': best
        }
    }), 200


@match_game_bp.route('/best', methods=['GET'])
@token_required
def get_best_time():
    """
    Get best time for a word set
    ---
    tags:
      - MatchGame
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
      - name: word_set_id
        in: query
        type: integer
        required: true
    responses:
      200:
        description: Best time retrieved
      401:
        description: Unauthorized
    """
    uid = request.user['uid']
    word_set_id = request.args.get('word_set_id', type=int)
    if not word_set_id:
        return jsonify({'success': False, 'message': 'word_set_id is required'}), 400

    best, error = match_game_service.get_best_time(uid, word_set_id)
    if error:
        return jsonify({'success': False, 'message': error}), 404

    return jsonify({
        'success': True,
        'data': best
    }), 200
