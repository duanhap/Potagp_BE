from flask import Blueprint, request, jsonify
from app.services.word_ordering_service import WordOrderingService
from app.utils.firebase_auth import token_required

word_ordering_bp = Blueprint('word_ordering', __name__)
word_ordering_service = WordOrderingService()


@word_ordering_bp.route('/start', methods=['POST'])
@token_required
def start_game():
    """
    Start a word ordering game for a sentence pattern
    ---
    tags:
      - WordOrdering
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
            - pattern_id
          properties:
            pattern_id:
              type: integer
              example: 1
    responses:
      200:
        description: Game started, returns game_id and list of sentences
      400:
        description: Not enough sentences (need at least 2)
      403:
        description: Forbidden
      404:
        description: Pattern not found
    """
    uid = request.user['uid']
    data = request.get_json(silent=True) or {}
    pattern_id = data.get('pattern_id')

    if not pattern_id:
        return jsonify({'success': False, 'message': 'pattern_id is required'}), 400

    game_id, sentences, error = word_ordering_service.start_game(uid, pattern_id)

    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'not_found':
        return jsonify({'success': False, 'message': 'Sentence pattern not found'}), 404
    if error == 'forbidden':
        return jsonify({'success': False, 'message': 'Forbidden'}), 403
    if error == 'not_enough_sentences':
        return jsonify({'success': False, 'message': 'Need at least 2 sentences to start'}), 400

    return jsonify({
        'success': True,
        'message': 'Game started',
        'data': {
            'game_id': game_id,
            'sentences': [s.to_dict() for s in sentences],
            'total': len(sentences)
        }
    }), 200


@word_ordering_bp.route('/submit', methods=['POST'])
@token_required
def submit_result():
    """
    Submit word ordering game result
    ---
    tags:
      - WordOrdering
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
            - pattern_id
            - correct_sentence_ids
            - wrong_sentence_ids
          properties:
            game_id:
              type: integer
              example: 5
            pattern_id:
              type: integer
              example: 1
            correct_sentence_ids:
              type: array
              items:
                type: integer
              example: [1, 2, 3]
            wrong_sentence_ids:
              type: array
              items:
                type: integer
              example: [4, 5]
            hackExperience:
              type: boolean
              example: false
            superExperience:
              type: boolean
              example: false
    responses:
      200:
        description: Result submitted, returns xp_earned, diamond_earned, streak info
      400:
        description: Missing required fields
      404:
        description: User or pattern not found
    """
    uid = request.user['uid']
    data = request.get_json(silent=True) or {}

    game_id = data.get('game_id')
    pattern_id = data.get('pattern_id')
    correct_ids = data.get('correct_sentence_ids', [])
    wrong_ids = data.get('wrong_sentence_ids', [])
    hack_experience = bool(data.get('hackExperience', False))
    super_experience = bool(data.get('superExperience', False))

    if not game_id or not pattern_id:
        return jsonify({'success': False, 'message': 'game_id and pattern_id are required'}), 400

    result, error = word_ordering_service.submit_result(
        uid, game_id, pattern_id, correct_ids, wrong_ids,
        hack_experience=hack_experience,
        super_experience=super_experience
    )

    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error in ('not_found', 'forbidden'):
        return jsonify({'success': False, 'message': error}), 403
    if error:
        return jsonify({'success': False, 'message': error}), 500

    return jsonify({
        'success': True,
        'message': 'Result submitted',
        'data': result
    }), 200
