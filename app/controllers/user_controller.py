from flask import Blueprint, request, jsonify
from app.services.user_service import UserService
from app.utils.firebase_auth import token_required

user_bp = Blueprint('user', __name__)
user_service = UserService()

@user_bp.route('/register', methods=['POST'])
@token_required
def register():
    """
    Register a new user
    ---
    tags:
      - User
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: "John Doe"
            email:
              type: string
              example: "john@example.com"
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
    responses:
      201:
        description: User registered successfully
      200:
        description: User already exists
      400:
        description: Name and Email are required
      401:
        description: Unauthorized (Invalid or missing token)
    """
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    
    # UID is retrieved from the verified token in the decorator
    uid = request.user['uid']
    
    if not name or not email:
        return jsonify({'success': False,'message': 'Name and Email are required'}), 400
    
    user, created = user_service.register_user(uid, email, name)
    
    if created:
        return jsonify({'success': True,'message': 'User registered successfully', 'data': user.to_dict()}), 201
    else:
        return jsonify({'success': True,'message': 'User already exists', 'data': user.to_dict()}), 200

@user_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """
    Get user profile information
    ---
    tags:
      - User
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
    responses:
      200:
        description: User profile retrieved successfully
      404:
        description: User not found
      401:
        description: Unauthorized (Invalid or missing token)
    """
    uid = request.user['uid']
    user = user_service.get_user_profile(uid)
    
    if not user:
        return jsonify({'success': False,'message': 'User not found'}), 404
        
    return jsonify({'success': True,'message': 'User profile retrieved successfully', 'data': user.to_dict()}), 200

@user_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile():
    """
    Update user profile information
    ---
    tags:
      - User
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: "John Doe"
            avatar:
              type: string
              example: "https://example.com/avatar.jpg"
            token_fcm:
              type: string
              example: "fcm_token_value"
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
    responses:
      200:
        description: User profile updated successfully
      400:
        description: Invalid request body or no valid fields to update
      404:
        description: User not found
      401:
        description: Unauthorized (Invalid or missing token)
    """
    uid = request.user['uid']
    data = request.get_json(silent=True) or {}

    user, error = user_service.update_user_profile(uid, data)
    if error:
        status_code = 404 if error == 'User not found' else 400
        return jsonify({'success': False, 'message': error}), status_code

    return jsonify({
        'success': True,
        'message': 'User profile updated successfully',
        'data': user.to_dict()
    }), 200

@user_bp.route('/settings', methods=['PUT'])
@token_required
def save_user_settings():
    """
    Save user settings
    ---
    tags:
      - User
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            notification:
              type: integer
              example: 1
              description: 0 or 1
            language:
              type: string
              example: "en"
              description: "en or vi"
            experiencegoal:
              type: integer
              example: 15
              description: Defaults to 15 if not provided
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
    responses:
      200:
        description: User settings saved successfully
      400:
        description: Invalid request body
      404:
        description: User not found
      401:
        description: Unauthorized (Invalid or missing token)
    """
    uid = request.user['uid']
    data = request.get_json(silent=True) or {}

    setting, error = user_service.save_user_setting(uid, data)
    if error:
        status_code = 404 if error == 'User not found' else 400
        return jsonify({'success': False, 'message': error}), status_code

    return jsonify({
        'success': True,
        'message': 'User settings saved successfully',
        'data': setting.to_dict()
    }), 200

@user_bp.route('/settings', methods=['GET'])
@token_required
def get_user_settings():
    """
    Get user settings
    ---
    tags:
      - User
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
    responses:
      200:
        description: User settings retrieved successfully
      404:
        description: User not found
      401:
        description: Unauthorized (Invalid or missing token)
    """
    uid = request.user['uid']
    setting, error = user_service.get_user_setting(uid)
    if error:
        return jsonify({'success': False, 'message': error}), 404

    return jsonify({
        'success': True,
        'message': 'User settings retrieved successfully',
        'data': setting.to_dict()
    }), 200

@user_bp.route('/ranking/top', methods=['GET'])
@token_required
def get_top_users():
    """
    Get top 1000 users by experience points
    ---
    tags:
      - User
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
    responses:
      200:
        description: Top users retrieved successfully
      401:
        description: Unauthorized (Invalid or missing token)
    """
    top_users = user_service.get_top_users(limit=1000)
    return jsonify({
        'success': True,
        'message': 'Top users retrieved successfully',
        'data': [user.to_dict() for user in top_users]
    }), 200

@user_bp.route('/ranking/me', methods=['GET'])
@token_required
def get_user_rank():
    """
    Get current user's rank
    ---
    tags:
      - User
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
    responses:
      200:
        description: User rank retrieved successfully
      404:
        description: User not found
      401:
        description: Unauthorized (Invalid or missing token)
    """
    uid = request.user['uid']
    rank = user_service.get_user_rank(uid)
    if rank is None:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    return jsonify({
        'success': True,
        'message': 'User rank retrieved successfully',
        'data': {'rank': rank}
    }), 200
