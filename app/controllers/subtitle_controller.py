from flask import Blueprint, request, jsonify
from app.services.subtitle_service import SubtitleService
from app.utils.firebase_auth import token_required

subtitle_bp = Blueprint('subtitle', __name__)
subtitle_service = SubtitleService()

@subtitle_bp.route('/<int:video_id>', methods=['GET'])
@token_required
def get_subtitles(video_id):
    """
    Get all subtitles of a video
    ---
    tags:
      - Subtitle
    parameters:
      - name: video_id
        in: path
        type: integer
        required: true
        description: ID of the video
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
    responses:
      200:
        description: Subtitles retrieved successfully
      403:
        description: Forbidden (Not a public video and you don't own it)
      404:
        description: Video or User not found
      401:
        description: Unauthorized
    """
    uid = request.user['uid']
    subs, error = subtitle_service.get_subtitles(video_id, uid)
    
    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'not_found':
        return jsonify({'success': False, 'message': 'Video not found'}), 404
    if error == 'forbidden':
        return jsonify({'success': False, 'message': 'You do not have permission to view this video subtitles'}), 403
        
    return jsonify({
        'success': True,
        'message': 'Subtitles retrieved successfully',
        'data': [s.to_dict() for s in subs]
    }), 200

@subtitle_bp.route('/<int:video_id>/upload', methods=['POST'])
@token_required
def upload_subtitles(video_id):
    """
    Upload and parse SRT file for a video
    ---
    tags:
      - Subtitle
    consumes:
      - multipart/form-data
    parameters:
      - name: video_id
        in: path
        type: integer
        required: true
        description: ID of the video to add subtitles to
      - name: file
        in: formData
        type: file
        required: true
        description: Custom processed SRT file
      - name: Authorization
        in: header
        type: string
        required: true
        description: Firebase ID Token (Bearer <token>)
    responses:
      201:
        description: Subtitles added successfully
      400:
        description: No file / Invalid file / Invalid SRT format
      403:
        description: Forbidden (Admin required for public, Owner required for private)
      404:
        description: Video or User not found
      401:
        description: Unauthorized
    """
    uid = request.user['uid']
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part in the request'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400
        
    if not file.filename.endswith('.srt'):
        return jsonify({'success': False, 'message': 'Only .srt files are supported'}), 400
        
    srt_content = file.read().decode('utf-8')
    count, error = subtitle_service.upload_subtitles(video_id, uid, srt_content)
    
    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'not_found':
        return jsonify({'success': False, 'message': 'Video not found'}), 404
    if error == 'forbidden_admin_required':
        return jsonify({'success': False, 'message': 'Admin role required to add subtitles to public videos'}), 403
    if error == 'forbidden':
        return jsonify({'success': False, 'message': 'You do not own this video'}), 403
    if error == 'invalid_or_empty_srt':
        return jsonify({'success': False, 'message': 'Invalid or empty SRT content'}), 400
        
    return jsonify({
        'success': True,
        'message': f'Successfully parsed and added {count} subtitle chunks'
    }), 201

@subtitle_bp.route('/<int:video_id>/sync-job', methods=['POST'])
@token_required
def sync_job_status(video_id):
    """
    Check external YouTube subtitle job status and update DB if completed
    ---
    tags:
      - Subtitle
    parameters:
      - name: video_id
        in: path
        type: integer
        required: true
        description: ID of the video
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
            - job_id
          properties:
            job_id:
              type: string
              example: "5fbbddd7-19f3-45ab-a52a-10730ac65746"
              description: "The job_id returned during video creation"
    responses:
      200:
        description: Job status retrieved (and subtitles saved if completed)
      400:
        description: job_id is required
      403:
        description: Forbidden (Admin required for public, Owner required for private)
      404:
        description: Video or User not found
      401:
        description: Unauthorized
      500:
        description: Could not contact external tracking service
    """
    uid = request.user['uid']
    data = request.get_json(silent=True) or {}
    job_id = data.get('job_id')
    
    if not job_id:
        return jsonify({'success': False, 'message': 'job_id is required in the request body'}), 400
        
    job_info, error = subtitle_service.sync_youtube_job(video_id, uid, job_id)
    
    if error == 'user_not_found':
        return jsonify({'success': False, 'message': 'User not found'}), 404
    if error == 'not_found':
        return jsonify({'success': False, 'message': 'Video not found'}), 404
    if error == 'forbidden_admin_required':
        return jsonify({'success': False, 'message': 'Admin role required to add subtitles to public videos'}), 403
    if error == 'forbidden':
        return jsonify({'success': False, 'message': 'You do not own this video'}), 403
    if error == 'job_not_found_or_error':
        return jsonify({'success': False, 'message': 'Could not check job progress from external service'}), 500
        
    return jsonify({
        'success': True,
        'message': 'Job status retrieved successfully',
        'data': job_info
    }), 200
