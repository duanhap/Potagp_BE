from flask import Blueprint, request, jsonify
from app.services.sentence_pattern_service import SentencePatternService
from app.utils.firebase_auth import token_required

sentence_pattern_bp = Blueprint('sentence_pattern', __name__)
sentence_pattern_service = SentencePatternService()


@sentence_pattern_bp.route('', methods=['GET'])
@token_required
def get_sentence_patterns():
    uid = request.user['uid']
    patterns = sentence_pattern_service.get_sentence_patterns_by_user(uid)

    if patterns is None:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    return jsonify({
        'success': True,
        'message': 'Sentence patterns retrieved successfully',
        'data': [p.to_dict() for p in patterns]
    }), 200


@sentence_pattern_bp.route('/list', methods=['GET'])
@token_required
def get_sentence_patterns_with_recent():
    uid = request.user['uid']
    limit = request.args.get('limit', 10)
    try:
        limit = int(limit)
    except ValueError:
        limit = 10

    all_patterns, recent_patterns = sentence_pattern_service.get_sentence_patterns_with_recent(uid, limit)
    if all_patterns is None:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    return jsonify({
        'success': True,
        'message': 'Sentence patterns retrieved successfully',
        'data': {
            'recent': [p.to_dict() for p in recent_patterns],
            'all': [p.to_dict() for p in all_patterns]
        }
    }), 200


@sentence_pattern_bp.route('/recent', methods=['GET'])
@token_required
def get_recent_sentence_patterns():
    uid = request.user['uid']
    recent_patterns = sentence_pattern_service.get_recent_sentence_patterns(uid, limit=3)
    if recent_patterns is None:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    return jsonify({
        'success': True,
        'message': 'Recent sentence patterns retrieved successfully',
        'data': [p.to_dict() for p in recent_patterns]
    }), 200


@sentence_pattern_bp.route('/<int:sentence_pattern_id>', methods=['GET'])
@token_required
def get_sentence_pattern(sentence_pattern_id):
    uid = request.user['uid']
    pattern, error = sentence_pattern_service.get_sentence_pattern(sentence_pattern_id, uid)

    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'not_found':
        return jsonify({'success': False, 'message': 'Sentence pattern not found'}), 404
    if error == 'forbidden':
        return jsonify({'success': False, 'message': 'You do not have permission to access this sentence pattern'}), 403

    return jsonify({'success': True, 'message': 'Sentence pattern retrieved successfully', 'data': pattern.to_dict()}), 200


@sentence_pattern_bp.route('', methods=['POST'])
@token_required
def create_sentence_pattern():
    uid = request.user['uid']
    data = request.get_json() or {}

    name = data.get('name')
    description = data.get('description')
    term_lang_code = data.get('term_lang_code')
    def_lang_code = data.get('def_lang_code')

    if not name or not description or not term_lang_code or not def_lang_code:
        return jsonify({'success': False, 'message': 'name, description, term_lang_code and def_lang_code are required'}), 400

    is_public = data.get('is_public', False)
    pattern = sentence_pattern_service.create_sentence_pattern(uid, name, description, is_public, term_lang_code, def_lang_code)

    if not pattern:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    return jsonify({'success': True, 'message': 'Sentence pattern created successfully', 'data': pattern.to_dict()}), 201


@sentence_pattern_bp.route('/<int:sentence_pattern_id>', methods=['PUT'])
@token_required
def update_sentence_pattern(sentence_pattern_id):
    uid = request.user['uid']
    data = request.get_json() or {}

    name = data.get('name')
    description = data.get('description')
    term_lang_code = data.get('term_lang_code')
    def_lang_code = data.get('def_lang_code')

    if not name or not description or not term_lang_code or not def_lang_code:
        return jsonify({'success': False, 'message': 'name, description, term_lang_code and def_lang_code are required'}), 400

    is_public = data.get('is_public', False)
    pattern, error = sentence_pattern_service.update_sentence_pattern(sentence_pattern_id, uid, name, description, is_public, term_lang_code, def_lang_code)

    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'not_found':
        return jsonify({'success': False, 'message': 'Sentence pattern not found'}), 404
    if error == 'forbidden':
        return jsonify({'success': False, 'message': 'You do not have permission to update this sentence pattern'}), 403

    return jsonify({'success': True, 'message': 'Sentence pattern updated successfully', 'data': pattern.to_dict()}), 200


@sentence_pattern_bp.route('/<int:sentence_pattern_id>', methods=['DELETE'])
@token_required
def delete_sentence_pattern(sentence_pattern_id):
    uid = request.user['uid']
    error = sentence_pattern_service.delete_sentence_pattern(sentence_pattern_id, uid)

    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'not_found':
        return jsonify({'success': False, 'message': 'Sentence pattern not found'}), 404
    if error == 'forbidden':
        return jsonify({'success': False, 'message': 'You do not have permission to delete this sentence pattern'}), 403

    return jsonify({'success': True, 'message': 'Sentence pattern deleted successfully'}), 200
