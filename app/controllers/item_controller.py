from flask import Blueprint, request, jsonify
from app.services.item_service import ItemService
from app.utils.firebase_auth import token_required

item_bp = Blueprint('item', __name__)
item_service = ItemService()


@item_bp.route('', methods=['GET'])
@token_required
def get_items():
    """
    Get current user's items
    ---
    tags:
      - Item
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
    responses:
      200:
        description: Items retrieved successfully
      404:
        description: User not found
      401:
        description: Unauthorized
    """
    uid = request.user['uid']
    item, error = item_service.get_items(uid)
    if error:
        return jsonify({'success': False, 'message': error}), 404

    return jsonify({
        'success': True,
        'message': 'Items retrieved successfully',
        'data': item.to_dict()
    }), 200


@item_bp.route('/purchase', methods=['POST'])
@token_required
def purchase():
    """
    Purchase an item using diamonds
    ---
    tags:
      - Item
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - item_type
            - quantity
          properties:
            item_type:
              type: string
              enum: [water_streak, super_xp, hack_xp]
              example: "water_streak"
            quantity:
              type: integer
              enum: [1, 3, 5]
              example: 1
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
    responses:
      200:
        description: Purchase successful
      400:
        description: Invalid request or not enough diamonds
      404:
        description: User not found
      401:
        description: Unauthorized
    """
    uid = request.user['uid']
    data = request.get_json(silent=True) or {}

    item_type = data.get('item_type')
    quantity = data.get('quantity')

    if not item_type or quantity is None:
        return jsonify({'success': False, 'message': 'item_type and quantity are required'}), 400

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'quantity must be an integer'}), 400

    item, diamond_remaining, error = item_service.purchase(uid, item_type, quantity)
    if error:
        status = 404 if error == 'User not found' else 400
        return jsonify({'success': False, 'message': error}), status

    return jsonify({
        'success': True,
        'message': 'Purchase successful',
        'data': {
            'items': item.to_dict(),
            'diamond_remaining': diamond_remaining
        }
    }), 200


@item_bp.route('/use', methods=['POST'])
@token_required
def use_item():
    """
    Use one item of the given type
    ---
    tags:
      - Item
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - item_type
          properties:
            item_type:
              type: string
              enum: [water_streak, super_xp, hack_xp]
              example: "super_xp"
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
    responses:
      200:
        description: Item used successfully
      400:
        description: Invalid request or no items available
      404:
        description: User not found
      401:
        description: Unauthorized
    """
    uid = request.user['uid']
    data = request.get_json(silent=True) or {}

    item_type = data.get('item_type')
    if not item_type:
        return jsonify({'success': False, 'message': 'item_type is required'}), 400

    item, error = item_service.use_item(uid, item_type)
    if error:
        status = 404 if error == 'User not found' else 400
        return jsonify({'success': False, 'message': error}), status

    return jsonify({
        'success': True,
        'message': 'Item used successfully',
        'data': item.to_dict()
    }), 200
