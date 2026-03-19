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
      - name: page_size
        in: query
        type: integer
        required: false
        description: Enable pagination when provided
      - name: page
        in: query
        type: integer
        required: false
        default: 1
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
    page_size = request.args.get('page_size', type=int)
    page = request.args.get('page', default=1, type=int)

    if not word_set_id:
        return jsonify({'success': False, 'message': 'word_set_id is required'}), 400

    words, total, error = word_service.get_words_by_word_set(uid, word_set_id, page=page, page_size=page_size)

    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'not_found':
        return jsonify({'success': False, 'message': 'Word set not found'}), 404
    if error == 'forbidden':
        return jsonify({'success': False, 'message': 'You do not have permission to access these words'}), 403

    response = {
        'success': True,
        'message': 'Words retrieved successfully',
        'data': [w.to_dict() for w in words]
    }
    if page_size is not None:
        total_pages = (total + page_size - 1) // page_size if page_size else 0
        response['pagination'] = {
            'page': page,
            'page_size': page_size,
            'total': total,
            'total_pages': total_pages
        }

    return jsonify(response), 200


@word_bp.route('/bulk', methods=['POST'])
@token_required
def create_words_bulk():
    """
    Create multiple words in a word set at once
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
            - words
          properties:
            word_set_id:
              type: integer
              example: 1
            words:
              type: array
              items:
                type: object
                required:
                  - term
                  - definition
                properties:
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
                    default: "unknown"
    responses:
      201:
        description: Words created successfully
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
    words = data.get('words')

    if not word_set_id:
        return jsonify({'success': False, 'message': 'word_set_id is required'}), 400
    if not words or not isinstance(words, list):
        return jsonify({'success': False, 'message': 'words must be a non-empty array'}), 400

    result, error = word_service.create_words(uid, word_set_id, words)

    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'not_found':
        return jsonify({'success': False, 'message': 'Word set not found'}), 404
    if error == 'forbidden':
        return jsonify({'success': False, 'message': 'You do not have permission to add words to this word set'}), 403

    if not result:
        return jsonify({
            'success': False,
            'message': 'No valid words to create (each word needs term and definition)'
        }), 400

    return jsonify({
        'success': True,
        'message': f'{len(result)} word(s) created successfully',
        'data': [w.to_dict() for w in result]
    }), 201


@word_bp.route('/by-id', methods=['GET'])
@token_required
def get_word():
    """
    Get a word by ID (query)
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
        in: query
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
    word_id = request.args.get('word_id', type=int)
    if not word_id:
        return jsonify({'success': False, 'message': 'word_id is required'}), 400
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
              default: "unknown"
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
    status = data.get('status', 'unknown')

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


@word_bp.route('', methods=['PUT'])
@token_required
def update_word():
    """
    Update a word (query)
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
        in: query
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
    word_id = request.args.get('word_id', type=int)
    if not word_id:
        return jsonify({'success': False, 'message': 'word_id is required'}), 400
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


@word_bp.route('', methods=['DELETE'])
@token_required
def delete_word():
    """
    Delete a word (query)
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
        in: query
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
    word_id = request.args.get('word_id', type=int)
    if not word_id:
        return jsonify({'success': False, 'message': 'word_id is required'}), 400
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
