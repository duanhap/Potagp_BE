from flask import Blueprint, request, jsonify
from app.services.word_set_service import WordSetService
from app.utils.firebase_auth import token_required

word_set_bp = Blueprint('word_set', __name__)
word_set_service = WordSetService()


@word_set_bp.route('', methods=['GET'])
@token_required
def get_word_sets():
    """
    Get all word sets of the current user
    ---
    tags:
      - WordSet
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
    responses:
      200:
        description: Word sets retrieved successfully
      404:
        description: User not found
      401:
        description: Unauthorized
    """
    uid = request.user['uid']
    word_sets = word_set_service.get_word_sets_by_user(uid)

    if word_sets is None:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    return jsonify({
        'success': True,
        'message': 'Word sets retrieved successfully',
        'data': [ws.to_dict() for ws in word_sets]
    }), 200


@word_set_bp.route('/recent', methods=['GET'])
@token_required
def get_recent_word_sets():
    """
    Get 3 most recently created word sets of the current user
    ---
    tags:
      - WordSet
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
      - name: limit
        in: query
        type: integer
        default: 3
        description: Number of recent word sets to return (max 10)
    responses:
      200:
        description: Recent word sets retrieved successfully
      404:
        description: User not found
      401:
        description: Unauthorized
    """
    uid = request.user['uid']
    try:
        limit = min(max(1, int(request.args.get('limit', 3))), 10)
    except (ValueError, TypeError):
        limit = 3
    word_sets = word_set_service.get_recent_word_sets(uid, limit)

    if word_sets is None:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    return jsonify({
        'success': True,
        'message': 'Recent word sets retrieved successfully',
        'data': [ws.to_dict() for ws in word_sets]
    }), 200


@word_set_bp.route('/<int:word_set_id>', methods=['GET'])
@token_required
def get_word_set(word_set_id):
    """
    Get a word set by ID
    ---
    tags:
      - WordSet
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
      - name: word_set_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Word set retrieved successfully
      403:
        description: Forbidden
      404:
        description: Word set not found
      401:
        description: Unauthorized
    """
    uid = request.user['uid']
    word_set, error = word_set_service.get_word_set(word_set_id, uid)

    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'not_found':
        return jsonify({'success': False, 'message': 'Word set not found'}), 404
    if error == 'forbidden':
        return jsonify({'success': False, 'message': 'You do not have permission to access this word set'}), 403

    return jsonify({
        'success': True,
        'message': 'Word set retrieved successfully',
        'data': word_set.to_dict()
    }), 200


@word_set_bp.route('', methods=['POST'])
@token_required
def create_word_set():
    """
    Create a new word set
    ---
    tags:
      - WordSet
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
            - name
            - def_lang_code
            - term_lang_code
          properties:
            name:
              type: string
              example: "English Vocabulary"
            description:
              type: string
              example: "Basic English words"
            is_public:
              type: boolean
              example: false
            def_lang_code:
              type: string
              example: "vi"
            term_lang_code:
              type: string
              example: "en"
    responses:
      201:
        description: Word set created successfully
      400:
        description: Missing required fields
      404:
        description: User not found
      401:
        description: Unauthorized
    """
    uid = request.user['uid']
    data = request.get_json()

    name = data.get('name')
    def_lang_code = data.get('def_lang_code')
    term_lang_code = data.get('term_lang_code')

    if not name or not def_lang_code or not term_lang_code:
        return jsonify({'success': False, 'message': 'name, def_lang_code and term_lang_code are required'}), 400

    description = data.get('description')
    is_public = data.get('is_public', False)

    word_set = word_set_service.create_word_set(uid, name, description, is_public, def_lang_code, term_lang_code)

    if not word_set:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    return jsonify({
        'success': True,
        'message': 'Word set created successfully',
        'data': word_set.to_dict()
    }), 201


@word_set_bp.route('/<int:word_set_id>', methods=['PUT'])
@token_required
def update_word_set(word_set_id):
    """
    Update a word set
    ---
    tags:
      - WordSet
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
      - name: word_set_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
            - def_lang_code
            - term_lang_code
          properties:
            name:
              type: string
              example: "Updated Vocabulary"
            description:
              type: string
              example: "Updated description"
            is_public:
              type: boolean
              example: true
            def_lang_code:
              type: string
              example: "vi"
            term_lang_code:
              type: string
              example: "en"
    responses:
      200:
        description: Word set updated successfully
      400:
        description: Missing required fields
      403:
        description: Forbidden
      404:
        description: Word set not found
      401:
        description: Unauthorized
    """
    uid = request.user['uid']
    data = request.get_json()

    name = data.get('name')
    def_lang_code = data.get('def_lang_code')
    term_lang_code = data.get('term_lang_code')

    if not name or not def_lang_code or not term_lang_code:
        return jsonify({'success': False, 'message': 'name, def_lang_code and term_lang_code are required'}), 400

    description = data.get('description')
    is_public = data.get('is_public', False)

    word_set, error = word_set_service.update_word_set(
        word_set_id, uid, name, description, is_public, def_lang_code, term_lang_code
    )

    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'not_found':
        return jsonify({'success': False, 'message': 'Word set not found'}), 404
    if error == 'forbidden':
        return jsonify({'success': False, 'message': 'You do not have permission to update this word set'}), 403

    return jsonify({
        'success': True,
        'message': 'Word set updated successfully',
        'data': word_set.to_dict()
    }), 200


@word_set_bp.route('/<int:word_set_id>', methods=['DELETE'])
@token_required
def delete_word_set(word_set_id):
    """
    Delete a word set
    ---
    tags:
      - WordSet
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
      - name: word_set_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Word set deleted successfully
      403:
        description: Forbidden
      404:
        description: Word set not found
      401:
        description: Unauthorized
    """
    uid = request.user['uid']
    error = word_set_service.delete_word_set(word_set_id, uid)

    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'not_found':
        return jsonify({'success': False, 'message': 'Word set not found'}), 404
    if error == 'forbidden':
        return jsonify({'success': False, 'message': 'You do not have permission to delete this word set'}), 403

    return jsonify({
        'success': True,
        'message': 'Word set deleted successfully'
    }), 200
