from flask import Blueprint, request, jsonify
from app.services.word_service import WordService
from app.utils.firebase_auth import token_required

word_bp = Blueprint('word', __name__)
word_service = WordService()


@word_bp.route('', methods=['GET'])
@token_required
def get_words():
    """
    Get all words in a word set
    ---
    tags:
      - Word
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
    responses:
      200:
        description: Words retrieved successfully
      403:
        description: Forbidden
      404:
        description: User or word set not found
      401:
        description: Unauthorized
    """
    uid = request.user['uid']
    word_set_id = request.args.get('word_set_id', type=int)

    if not word_set_id:
        return jsonify({'success': False, 'message': 'word_set_id is required'}), 400

    words, error = word_service.get_words_by_word_set(uid, word_set_id)

    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'not_found':
        return jsonify({'success': False, 'message': 'Word set not found'}), 404
    if error == 'forbidden':
        return jsonify({'success': False, 'message': 'You do not have permission to access these words'}), 403

    return jsonify({
        'success': True,
        'message': 'Words retrieved successfully',
        'data': [w.to_dict() for w in words]
    }), 200


@word_bp.route('/<int:word_id>', methods=['GET'])
@token_required
def get_word(word_id):
    """
    Get a word by ID
    ---
    tags:
      - Word
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
      - name: word_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Word retrieved successfully
      403:
        description: Forbidden
      404:
        description: Word not found
      401:
        description: Unauthorized
    """
    uid = request.user['uid']
    word, error = word_service.get_word(uid, word_id)

    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'not_found':
        return jsonify({'success': False, 'message': 'Word not found'}), 404
    if error == 'forbidden':
        return jsonify({'success': False, 'message': 'You do not have permission to access this word'}), 403

    return jsonify({
        'success': True,
        'message': 'Word retrieved successfully',
        'data': word.to_dict()
    }), 200


@word_bp.route('', methods=['POST'])
@token_required
def create_word():
    """
    Create a new word in a word set
    ---
    tags:
      - Word
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
            - term
            - definition
          properties:
            word_set_id:
              type: integer
              example: 1
            term:
              type: string
              example: "Hello"
            definition:
              type: string
              example: "Xin chào"
            description:
              type: string
            status:
              type: string
              default: "new"
    responses:
      201:
        description: Word created successfully
      400:
        description: Missing required fields
      403:
        description: Forbidden
      404:
        description: User or word set not found
      401:
        description: Unauthorized
    """
    uid = request.user['uid']
    data = request.get_json()

    word_set_id = data.get('word_set_id')
    term = data.get('term')
    definition = data.get('definition')

    if not word_set_id or not term or not definition:
        return jsonify({'success': False, 'message': 'word_set_id, term and definition are required'}), 400

    description = data.get('description')
    status = data.get('status', 'new')

    word, error = word_service.create_word(uid, word_set_id, term, definition, description, status)

    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'not_found':
        return jsonify({'success': False, 'message': 'Word set not found'}), 404
    if error == 'forbidden':
        return jsonify({'success': False, 'message': 'You do not have permission to add words to this word set'}), 403

    return jsonify({
        'success': True,
        'message': 'Word created successfully',
        'data': word.to_dict()
    }), 201


@word_bp.route('/<int:word_id>', methods=['PUT'])
@token_required
def update_word(word_id):
    """
    Update a word
    ---
    tags:
      - Word
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
      - name: word_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        schema:
          type: object
          properties:
            term:
              type: string
            definition:
              type: string
            description:
              type: string
            status:
              type: string
    responses:
      200:
        description: Word updated successfully
      403:
        description: Forbidden
      404:
        description: Word not found
      401:
        description: Unauthorized
    """
    uid = request.user['uid']
    data = request.get_json() or {}

    term = data.get('term')
    definition = data.get('definition')
    description = data.get('description')
    status = data.get('status')

    if not any([term is not None, definition is not None, description is not None, status is not None]):
        return jsonify({'success': False, 'message': 'At least one field (term, definition, description, status) is required'}), 400

    word, error = word_service.update_word(uid, word_id, term, definition, description, status)

    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'not_found':
        return jsonify({'success': False, 'message': 'Word not found'}), 404
    if error == 'forbidden':
        return jsonify({'success': False, 'message': 'You do not have permission to update this word'}), 403

    return jsonify({
        'success': True,
        'message': 'Word updated successfully',
        'data': word.to_dict()
    }), 200


@word_bp.route('/<int:word_id>', methods=['DELETE'])
@token_required
def delete_word(word_id):
    """
    Delete a word
    ---
    tags:
      - Word
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
      - name: word_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Word deleted successfully
      403:
        description: Forbidden
      404:
        description: Word not found
      401:
        description: Unauthorized
    """
    uid = request.user['uid']
    error = word_service.delete_word(uid, word_id)

    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'not_found':
        return jsonify({'success': False, 'message': 'Word not found'}), 404
    if error == 'forbidden':
        return jsonify({'success': False, 'message': 'You do not have permission to delete this word'}), 403

    return jsonify({
        'success': True,
        'message': 'Word deleted successfully'
    }), 200
