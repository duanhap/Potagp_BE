from flask import Blueprint, request, jsonify
from app.services.reward_service import RewardService
from app.utils.firebase_auth import token_required

reward_bp = Blueprint('reward', __name__)
reward_service = RewardService()


@reward_bp.route('/claim', methods=['POST'])
@token_required
def claim_reward():
    uid = request.user['uid']
    data = request.get_json() or {}

    action = data.get('action')
    if not action:
        return jsonify({'success': False, 'message': 'action is required'}), 400

    hack_experience = bool(data.get('hackExperience', False))
    super_experience = bool(data.get('superExperience', False))

    result, error = reward_service.claim_reward(
        uid,
        action,
        hack_experience=hack_experience,
        super_experience=super_experience,
    )

    if error == 'invalid_action':
        return jsonify({'success': False, 'message': f"Unknown action: '{action}'"}), 400
    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'update_failed':
        return jsonify({'success': False, 'message': 'Failed to update reward'}), 500

    return jsonify({
        'success': True,
        'message': 'Reward claimed successfully',
        'data': result
    }), 200
