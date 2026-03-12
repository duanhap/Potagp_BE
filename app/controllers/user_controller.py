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
