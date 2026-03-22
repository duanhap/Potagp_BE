from flask import Blueprint, request, jsonify
from app.services.sentence_service import SentenceService
from app.utils.firebase_auth import token_required

sentence_bp = Blueprint('sentence', __name__)
sentence_service = SentenceService()


@sentence_bp.route('', methods=['GET'])
@token_required
def get_sentences():
    uid = request.user['uid']
    pattern_id = request.args.get('pattern_id')
    if not pattern_id:
        return jsonify({'success': False, 'message': 'pattern_id query parameter is required'}), 400

    try:
        pattern_id_int = int(pattern_id)
    except ValueError:
        return jsonify({'success': False, 'message': 'pattern_id must be an integer'}), 400

    page = request.args.get('page', '1')
    page_size = request.args.get('page_size', '20')

    try:
        page_int = int(page)
        page_size_int = int(page_size)
    except ValueError:
        return jsonify({'success': False, 'message': 'page and page_size must be integers'}), 400

    if page_int < 1 or page_size_int < 1:
        return jsonify({'success': False, 'message': 'page and page_size must be >= 1'}), 400

    # Check if status filter is provided
    status = request.args.get('status')
    
    if status:
        result, error = sentence_service.get_sentences_by_pattern_and_status(uid, pattern_id_int, status, page=page_int, page_size=page_size_int)
        if error == 'invalid_status':
            return jsonify({'success': False, 'message': 'status must be unknown or known'}), 400
    else:
        result, error = sentence_service.get_sentences_by_pattern(uid, pattern_id_int, page=page_int, page_size=page_size_int)
    
    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'pattern_not_found':
        return jsonify({'success': False, 'message': 'Sentence pattern not found'}), 404
    if error == 'forbidden':
        return jsonify({'success': False, 'message': 'You do not have permission to access this pattern'}), 403

    sentences = result['sentences']
    total = result['total']
    total_pages = (total + page_size_int - 1) // page_size_int if page_size_int > 0 else 0

    return jsonify({
        'success': True,
        'message': 'Sentences retrieved successfully',
        'data': [s.to_dict() for s in sentences],
        'pagination': {
            'page': page_int,
            'page_size': page_size_int,
            'total': total,
            'total_pages': total_pages
        }
    }), 200


@sentence_bp.route('/<int:sentence_id>', methods=['GET'])
@token_required
def get_sentence(sentence_id):
    uid = request.user['uid']
    sentence, error = sentence_service.get_sentence(sentence_id, uid)

    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'not_found':
        return jsonify({'success': False, 'message': 'Sentence not found'}), 404
    if error == 'pattern_not_found':
        return jsonify({'success': False, 'message': 'Sentence pattern not found'}), 404
    if error == 'forbidden':
        return jsonify({'success': False, 'message': 'You do not have permission to access this sentence'}), 403

    return jsonify({'success': True, 'message': 'Sentence retrieved successfully', 'data': sentence.to_dict()}), 200


@sentence_bp.route('/recent', methods=['GET'])
@token_required
def get_recent_sentences():
    uid = request.user['uid']
    recent_sentences = sentence_service.get_recent_sentences(uid, limit=3)
    if recent_sentences is None:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    return jsonify({
        'success': True,
        'message': 'Recent sentences retrieved successfully',
        'data': [s.to_dict() for s in recent_sentences]
    }), 200


@sentence_bp.route('', methods=['POST'])
@token_required
def create_sentences():
    uid = request.user['uid']
    data = request.get_json() or {}

    pattern_id = data.get('pattern_id')
    if not pattern_id:
        return jsonify({'success': False, 'message': 'pattern_id is required'}), 400

    try:
        pattern_id_int = int(pattern_id)
    except ValueError:
        return jsonify({'success': False, 'message': 'pattern_id must be integer'}), 400

    # Bulk request support
    if isinstance(data.get('sentences'), list):
        sentences_data = data.get('sentences')
        if not sentences_data:
            return jsonify({'success': False, 'message': 'sentences list cannot be empty'}), 400

        for s in sentences_data:
            if not s.get('term') or not s.get('definition'):
                return jsonify({'success': False, 'message': 'each sentence requires term and definition'}), 400
            status = s.get('status', 'unknown')
            if status not in ['unknown', 'known']:
                return jsonify({'success': False, 'message': 'each sentence status must be unknown or known'}), 400

        inserted, error = sentence_service.create_sentences_bulk(uid, pattern_id_int, sentences_data)
        if error == 'user_not_found':
            return jsonify({'success': False, 'message': 'User not found'}), 404
        if error == 'pattern_not_found':
            return jsonify({'success': False, 'message': 'Sentence pattern not found'}), 404
        if error == 'forbidden':
            return jsonify({'success': False, 'message': 'You do not have permission to add sentences to this pattern'}), 403

        return jsonify({'success': True, 'message': 'Sentences created successfully', 'data': [s.to_dict() for s in inserted]}), 201

    # Single sentence create
    term = data.get('term')
    definition = data.get('definition')
    if not term or not definition:
        return jsonify({'success': False, 'message': 'term and definition are required'}), 400

    status = data.get('status', 'unknown')
    mistakes = data.get('mistakes', 0)

    if status not in ['unknown', 'known']:
        return jsonify({'success': False, 'message': 'status must be unknown or known'}), 400

    sentence, error = sentence_service.create_sentence(uid, pattern_id_int, term, definition, status, mistakes)
    if error == 'invalid_status':
        return jsonify({'success': False, 'message': 'status must be unknown or known'}), 400
    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'pattern_not_found':
        return jsonify({'success': False, 'message': 'Sentence pattern not found'}), 404
    if error == 'forbidden':
        return jsonify({'success': False, 'message': 'You do not have permission to add sentences to this pattern'}), 403

    return jsonify({'success': True, 'message': 'Sentence created successfully', 'data': sentence.to_dict()}), 201


@sentence_bp.route('/<int:sentence_id>', methods=['PUT'])
@token_required
def update_sentence(sentence_id):
    uid = request.user['uid']
    data = request.get_json() or {}

    term = data.get('term')
    definition = data.get('definition')
    if not term or not definition:
        return jsonify({'success': False, 'message': 'term and definition are required'}), 400

    status = data.get('status', 'unknown')
    mistakes = data.get('mistakes', 0)

    if status not in ['unknown', 'known']:
        return jsonify({'success': False, 'message': 'status must be unknown or known'}), 400

    sentence, error = sentence_service.update_sentence(sentence_id, uid, term, definition, status, mistakes)
    if error == 'invalid_status':
        return jsonify({'success': False, 'message': 'status must be unknown or known'}), 400
    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'not_found':
        return jsonify({'success': False, 'message': 'Sentence not found'}), 404
    if error == 'pattern_not_found':
        return jsonify({'success': False, 'message': 'Sentence pattern not found'}), 404
    if error == 'forbidden':
        return jsonify({'success': False, 'message': 'You do not have permission to update this sentence'}), 403

    return jsonify({'success': True, 'message': 'Sentence updated successfully', 'data': sentence.to_dict()}), 200


@sentence_bp.route('/<int:sentence_id>', methods=['DELETE'])
@token_required
def delete_sentence(sentence_id):
    uid = request.user['uid']
    error = sentence_service.delete_sentence(sentence_id, uid)
    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'not_found':
        return jsonify({'success': False, 'message': 'Sentence not found'}), 404
    if error == 'pattern_not_found':
        return jsonify({'success': False, 'message': 'Sentence pattern not found'}), 404
    if error == 'forbidden':
        return jsonify({'success': False, 'message': 'You do not have permission to delete this sentence'}), 403
    if error == 'delete_failed':
        return jsonify({'success': False, 'message': 'Delete failed'}), 500

    return jsonify({'success': True, 'message': 'Sentence deleted successfully'}), 200


@sentence_bp.route('/list', methods=['GET'])
@token_required
def get_all_sentences():
    uid = request.user['uid']
    sentences = sentence_service.get_all_sentences(uid)
    if sentences is None:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    return jsonify({
        'success': True,
        'message': 'All sentences retrieved successfully',
        'data': [s.to_dict() for s in sentences]
    }), 200