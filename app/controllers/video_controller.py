from flask import Blueprint, request, jsonify
from app.services.video_service import VideoService
from app.utils.firebase_auth import token_required

video_bp = Blueprint('video', __name__)
video_service = VideoService()


# ═══════════════════════════════════════════════════════════
#  GET  /api/videos/public   – Lấy danh sách video chung
# ═══════════════════════════════════════════════════════════
@video_bp.route('/public', methods=['GET'])
@token_required
def get_public_videos():
    """
    Get all public (recommend) videos
    ---
    tags:
      - Video
    parameters:
      - name: term_lang_code
        in: query
        type: string
        required: false
        description: Filter by Term Language Code (e.g. en)
      - name: page
        in: query
        type: integer
        required: false
        description: Page number for pagination
      - name: size
        in: query
        type: integer
        required: false
        description: Number of items per page
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
    responses:
      200:
        description: Public videos retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            data:
              type: array
              items:
                $ref: '#/definitions/Video'
            total_count:
              type: integer
      401:
        description: Unauthorized
    """
    term_lang_code = request.args.get('term_lang_code')
    page = request.args.get('page', type=int)
    size = request.args.get('size', type=int)
    
    videos, total_count = video_service.get_public_videos(term_lang_code, page, size)
    
    return jsonify({
        'success': True,
        'message': 'Public videos retrieved successfully',
        'data': [v.to_dict() for v in videos],
        'total_count': total_count,
        'page': page,
        'size': size
    }), 200


# ═══════════════════════════════════════════════════════════
#  GET  /api/videos/my   – Lấy video riêng của user
# ═══════════════════════════════════════════════════════════
@video_bp.route('/my', methods=['GET'])
@token_required
def get_my_videos():
    """
    Get all private videos of the authenticated user
    ---
    tags:
      - Video
    parameters:
      - name: type_video
        in: query
        type: string
        required: false
        description: Filter by type of video (e.g. youtube, file...)
      - name: page
        in: query
        type: integer
        required: false
        description: Page number for pagination
      - name: size
        in: query
        type: integer
        required: false
        description: Number of items per page
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
    responses:
      200:
        description: My videos retrieved successfully
      404:
        description: User not found
      401:
        description: Unauthorized
    """
    uid = request.user['uid']
    type_video = request.args.get('type_video')
    page = request.args.get('page', type=int)
    size = request.args.get('size', type=int)
    
    res, error = video_service.get_my_videos(uid, type_video, page, size)

    if error:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    videos, total_count = res

    return jsonify({
        'success': True,
        'message': 'My videos retrieved successfully',
        'data': [v.to_dict() for v in videos],
        'total_count': total_count,
        'page': page,
        'size': size
    }), 200


# ═══════════════════════════════════════════════════════════
#  GET  /api/videos/recent   – Lấy video đã xem gần đây của user
# ═══════════════════════════════════════════════════════════
@video_bp.route('/recent', methods=['GET'])
@token_required
def get_recent_videos():
    """
    Get recent opened videos of the authenticated user
    ---
    tags:
      - Video
    parameters:
      - name: page
        in: query
        type: integer
        required: false
        description: Page number for pagination
      - name: size
        in: query
        type: integer
        required: false
        description: Number of items per page
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
    responses:
      200:
        description: Recent videos retrieved successfully
      404:
        description: User not found
      401:
        description: Unauthorized
    """
    uid = request.user['uid']
    page = request.args.get('page', type=int)
    size = request.args.get('size', type=int)
    
    res, error = video_service.get_recent_videos(uid, page, size)

    if error:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    videos, total_count = res

    return jsonify({
        'success': True,
        'message': 'Recent videos retrieved successfully',
        'data': [v.to_dict() for v in videos],
        'total_count': total_count,
        'page': page,
        'size': size
    }), 200

# ═══════════════════════════════════════════════════════════
#  GET  /api/videos/<id>   – Lấy chi tiết 1 video
# ═══════════════════════════════════════════════════════════
@video_bp.route('/<int:video_id>', methods=['GET'])
@token_required
def get_video(video_id):
    """
    Get detail of a specific video
    ---
    tags:
      - Video
    parameters:
      - name: video_id
        in: path
        type: integer
        required: true
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
    responses:
      200:
        description: Video retrieved successfully
      403:
        description: Forbidden – you do not own this video
      404:
        description: Video not found
      401:
        description: Unauthorized
    """
    uid = request.user['uid']
    video, error = video_service.get_video_detail(video_id, uid)

    if error == 'not_found':
        return jsonify({'success': False, 'message': 'Video not found'}), 404
    if error == 'forbidden':
        return jsonify({'success': False, 'message': 'You do not have permission to view this video'}), 403
    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404

    return jsonify({
        'success': True,
        'message': 'Video retrieved successfully',
        'data': video.to_dict()
    }), 200


# ═══════════════════════════════════════════════════════════
#  POST /api/videos/public   – Tạo video chung (Admin only)
# ═══════════════════════════════════════════════════════════
@video_bp.route('/public', methods=['POST'])
@token_required
def create_public_video():
    """
    Create a new public (recommend) video – Admin only
    ---
    tags:
      - Video
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
            - source_url
            - definition_lang_code
            - term_lang_code
          properties:
            title:
              type: string
              example: "Learn Python in 10 minutes"
            thumbnail:
              type: string
              example: "https://example.com/thumb.jpg"
            source_url:
              type: string
              example: "https://youtube.com/watch?v=abc123"
            type_video:
              type: string
              example: "youtube"
            definition_lang_code:
              type: string
              example: "vi"
              description: "Language code for definition (e.g. vi, en)"
            term_lang_code:
              type: string
              example: "en"
              description: "Language code for term (e.g. en, ja)"
    responses:
      201:
        description: Public video created successfully
      400:
        description: source_url or language codes are required
      403:
        description: Forbidden – Admin role required
      404:
        description: User not found
      401:
        description: Unauthorized
    """
    uid = request.user['uid']
    data = request.get_json(silent=True) or {}

    title               = data.get('title')
    thumbnail           = data.get('thumbnail')
    source_url          = data.get('source_url')
    type_video          = data.get('type_video')
    definition_lang_code = data.get('definition_lang_code')
    term_lang_code      = data.get('term_lang_code')

    video, error = video_service.create_public_video(
        uid, title, thumbnail, source_url, type_video,
        definition_lang_code, term_lang_code
    )

    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'forbidden':
        return jsonify({'success': False, 'message': 'Admin role required to create public videos'}), 403
    if error == 'source_url_required':
        return jsonify({'success': False, 'message': 'source_url is required'}), 400
    if error == 'lang_codes_required':
        return jsonify({'success': False, 'message': 'definition_lang_code and term_lang_code are required'}), 400
    if error == 'video_too_long':
        return jsonify({'success': False, 'message': 'Video is too long. The maximum allowed length is 30 minutes.'}), 400

    return jsonify({
        'success': True,
        'message': 'Public video created successfully',
        'data': video.to_dict()
    }), 201


# ═══════════════════════════════════════════════════════════
#  POST /api/videos/my   – Tạo video riêng
# ═══════════════════════════════════════════════════════════
@video_bp.route('/my', methods=['POST'])
@token_required
def create_my_video():
    """
    Create a new private video for the authenticated user
    ---
    tags:
      - Video
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
            - source_url
            - definition_lang_code
            - term_lang_code
          properties:
            title:
              type: string
              example: "My study video"
            thumbnail:
              type: string
              example: "https://example.com/thumb.jpg"
            source_url:
              type: string
              example: "https://youtube.com/watch?v=xyz999"
            type_video:
              type: string
              example: "youtube"
            definition_lang_code:
              type: string
              example: "vi"
              description: "Language code for definition (e.g. vi, en)"
            term_lang_code:
              type: string
              example: "en"
              description: "Language code for term (e.g. en, ja)"
    responses:
      201:
        description: Private video created successfully
      400:
        description: source_url or language codes are required
      404:
        description: User not found
      401:
        description: Unauthorized
    """
    uid = request.user['uid']
    data = request.get_json(silent=True) or {}

    title                = data.get('title')
    thumbnail            = data.get('thumbnail')
    source_url           = data.get('source_url')
    type_video           = data.get('type_video')
    definition_lang_code = data.get('definition_lang_code')
    term_lang_code       = data.get('term_lang_code')

    res, error = video_service.create_my_video(
        uid, title, thumbnail, source_url, type_video,
        definition_lang_code, term_lang_code
    )

    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'source_url_required':
        return jsonify({'success': False, 'message': 'source_url is required'}), 400
    if error == 'lang_codes_required':
        return jsonify({'success': False, 'message': 'definition_lang_code and term_lang_code are required'}), 400
    if error == 'video_too_long':
        return jsonify({'success': False, 'message': 'Video is too long. The maximum allowed length is 30 minutes.'}), 400

    video, job_id = res

    data_res = video.to_dict()
    data_res['job_id'] = job_id

    return jsonify({
        'success': True,
        'message': 'Private video created successfully',
        'data': data_res
    }), 201


# ═══════════════════════════════════════════════════════════
#  POST /api/videos/public/<id>/open  – Mở video chung (tạo bản sao)
# ═══════════════════════════════════════════════════════════
@video_bp.route('/public/<int:public_video_id>/open', methods=['POST'])
@token_required
def open_public_video(public_video_id):
    """
    Open a public video – creates a personal copy if not yet done, then returns it
    ---
    tags:
      - Video
    parameters:
      - name: public_video_id
        in: path
        type: integer
        required: true
        description: Id of the public video to open
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
    responses:
      200:
        description: Personal copy of public video returned (existing or newly created)
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            data:
              $ref: '#/definitions/Video'
      400:
        description: The target is not a public video
      404:
        description: Video or User not found
      401:
        description: Unauthorized
    """
    uid = request.user['uid']
    video, error = video_service.open_public_video(uid, public_video_id)

    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'not_found':
        return jsonify({'success': False, 'message': 'Public video not found'}), 404
    if error == 'not_a_public_video':
        return jsonify({'success': False, 'message': 'This video is not a public video'}), 400

    return jsonify({
        'success': True,
        'message': 'Video opened successfully',
        'data': video.to_dict()
    }), 200


# ═══════════════════════════════════════════════════════════
#  PUT  /api/videos/<id>   – Sửa video
# ═══════════════════════════════════════════════════════════
@video_bp.route('/<int:video_id>', methods=['PUT'])
@token_required
def update_video(video_id):
    """
    Update a video (Admin for public videos, owner for private videos)
    ---
    tags:
      - Video
    parameters:
      - name: video_id
        in: path
        type: integer
        required: true
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
          properties:
            title:
              type: string
              example: "Updated title"
            thumbnail:
              type: string
              example: "https://example.com/new-thumb.jpg"
            source_url:
              type: string
              example: "https://youtube.com/watch?v=newvid"
            type_video:
              type: string
              example: "youtube"
            definition_lang_code:
              type: string
              example: "vi"
            term_lang_code:
              type: string
              example: "en"
    responses:
      200:
        description: Video updated successfully
      400:
        description: No valid fields to update
      403:
        description: Forbidden
      404:
        description: Video or User not found
      401:
        description: Unauthorized
    """
    uid = request.user['uid']
    data = request.get_json(silent=True) or {}

    video, error = video_service.update_video(video_id, uid, data)

    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'not_found':
        return jsonify({'success': False, 'message': 'Video not found'}), 404
    if error == 'forbidden':
        return jsonify({'success': False, 'message': 'You do not have permission to update this video'}), 403
    if error == 'no_valid_fields':
        return jsonify({'success': False, 'message': 'No valid fields to update'}), 400

    return jsonify({
        'success': True,
        'message': 'Video updated successfully',
        'data': video.to_dict()
    }), 200


# ═══════════════════════════════════════════════════════════
#  DELETE /api/videos/<id>   – Xóa video
# ═══════════════════════════════════════════════════════════
@video_bp.route('/<int:video_id>', methods=['DELETE'])
@token_required
def delete_video(video_id):
    """
    Delete a video (Admin for public videos, owner for private videos)
    ---
    tags:
      - Video
    parameters:
      - name: video_id
        in: path
        type: integer
        required: true
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
    responses:
      200:
        description: Video deleted successfully
      403:
        description: Forbidden
      404:
        description: Video or User not found
      401:
        description: Unauthorized
    """
    uid = request.user['uid']
    error = video_service.delete_video(video_id, uid)

    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'not_found':
        return jsonify({'success': False, 'message': 'Video not found'}), 404
    if error == 'forbidden':
        return jsonify({'success': False, 'message': 'You do not have permission to delete this video'}), 403

    return jsonify({
        'success': True,
        'message': 'Video deleted successfully'
    }), 200
