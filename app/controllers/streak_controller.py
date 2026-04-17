from flask import Blueprint, request, jsonify
from app.services.streak_service import StreakService
from app.repositories.user_repository import UserRepository
from app.utils.firebase_auth import token_required

streak_bp = Blueprint('streak', __name__)
streak_service = StreakService()
user_repository = UserRepository()


@streak_bp.route('/current', methods=['GET'])
@token_required
def get_current_streak():
    """Lấy chuỗi Streak đang active (CurentStreak = true) của user."""
    uid = request.user['uid']

    user = user_repository.get_by_uid(uid)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    streak, _ = streak_service.get_current_streak(uid, user.id)
    if not streak:
        return jsonify({
            'success': True,
            'message': 'No active streak found',
            'data': None
        }), 200

    return jsonify({
        'success': True,
        'message': 'Current streak retrieved successfully',
        'data': streak.to_dict()
    }), 200


@streak_bp.route('/today', methods=['GET'])
@token_required
def get_streak_date_today():
    """Lấy StreakDate của ngày hôm nay của user."""
    uid = request.user['uid']

    user = user_repository.get_by_uid(uid)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    streak_date, _ = streak_service.get_streak_date_today(uid, user.id)
    if not streak_date:
        return jsonify({
            'success': True,
            'message': 'No streak activity today',
            'data': None
        }), 200

    return jsonify({
        'success': True,
        'message': 'Today streak date retrieved successfully',
        'data': streak_date.to_dict()
    }), 200
