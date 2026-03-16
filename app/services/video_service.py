from app.repositories.video_repository import VideoRepository
from app.repositories.user_repository import UserRepository
from app.utils.youtube_helper import fetch_youtube_info, start_youtube_subtitle_job


class VideoService:

    def __init__(self):
        self.video_repo = VideoRepository()
        self.user_repo = UserRepository()

    # ─────────────────────────────────────────────
    #  INTERNAL HELPERS
    # ─────────────────────────────────────────────

    def _enrich_youtube_meta(self, source_url: str, title, thumbnail):
        """
        Nếu type_video là 'youtube' và title/thumbnail chưa được cung cấp,
        tự động fetch từ YouTube oEmbed + img.youtube.com.

        Trả về (title, thumbnail) đã được điền đầy đủ (hoặc giữ nguyên
        giá trị user truyền vào nếu đã có).
        """
        info = fetch_youtube_info(source_url)

        # Chỉ dùng giá trị fetch được khi user KHÔNG tự truyền
        resolved_title     = title     if title     else info.get('title')
        resolved_thumbnail = thumbnail if thumbnail else info.get('thumbnail')

        return resolved_title, resolved_thumbnail

    # ─────────────────────────────────────────────
    #  READ
    # ─────────────────────────────────────────────

    def get_public_videos(self, term_lang_code=None, page=None, size=None):
        """Lấy danh sách video chung (recommend) kèm tổng số để phân trang."""
        limit = None
        offset = None
        if page is not None and size is not None:
            limit = size
            offset = (page - 1) * size
            
        return self.video_repo.get_all_public(term_lang_code, limit, offset)

    def get_my_videos(self, uid, type_video=None, page=None, size=None):
        """Lấy danh sách video riêng của user đang đăng nhập."""
        user = self.user_repo.get_by_uid(uid)
        if not user:
            return None, 'user_not_found'
            
        limit = None
        offset = None
        if page is not None and size is not None:
            limit = size
            offset = (page - 1) * size
            
        videos, total_count = self.video_repo.get_all_by_user_id(user.id, type_video, limit, offset)
        return (videos, total_count), None

    def get_video_detail(self, video_id, uid):
        """
        Lấy chi tiết 1 video.
        - Video chung: ai cũng được xem.
        - Video riêng: chỉ chủ sở hữu.
        """
        user = self.user_repo.get_by_uid(uid)
        if not user:
            return None, 'user_not_found'

        video = self.video_repo.get_by_id(video_id)
        if not video:
            return None, 'not_found'

        # Video chung (không có owner) → ai cũng xem được
        if video.user_id is None:
            return video, None

        # Video riêng → chỉ chủ
        if video.user_id != user.id:
            return None, 'forbidden'

        return video, None

    # ─────────────────────────────────────────────
    #  CREATE
    # ─────────────────────────────────────────────

    def create_public_video(self, uid, title, thumbnail, source_url, type_video,
                             definition_lang_code, term_lang_code):
        """
        Tạo video chung (recommend). Chỉ Admin mới có quyền.
        Nếu type_video='youtube' và title/thumbnail chưa đủ → tự động fetch.
        """
        user = self.user_repo.get_by_uid(uid)
        if not user:
            return None, 'user_not_found'

        if user.role != 'Admin':
            return None, 'forbidden'

        if not source_url:
            return None, 'source_url_required'

        if not definition_lang_code or not term_lang_code:
            return None, 'lang_codes_required'

        # Auto-fetch YouTube metadata nếu cần
        if type_video == 'youtube':
            title, thumbnail = self._enrich_youtube_meta(source_url, title, thumbnail)

        new_id = self.video_repo.create(
            title=title,
            thumbnail=thumbnail,
            source_url=source_url,
            type_video=type_video,
            definition_lang_code=definition_lang_code,
            term_lang_code=term_lang_code,
            user_id=None,           # video chung: không thuộc user nào
            public_video_id=None
        )

        return self.video_repo.get_by_id(new_id), None

    def create_my_video(self, uid, title, thumbnail, source_url, type_video,
                        definition_lang_code, term_lang_code):
        """
        Tạo video riêng của user.
        Nếu type_video='youtube' và title/thumbnail chưa đủ → tự động fetch.
        """
        user = self.user_repo.get_by_uid(uid)
        if not user:
            return None, 'user_not_found'

        if not source_url:
            return None, 'source_url_required'

        if not definition_lang_code or not term_lang_code:
            return None, 'lang_codes_required'

        # Check trùng public video by source_url nếu là youtube
        if type_video == 'youtube':
            public_vid = self.video_repo.get_public_by_source_url(source_url)
            if public_vid:
                # Nếu đã có public video chung URL, thì mở sang dạng bản sao (không call API phụ đề ngoại nữa)
                copied_vid, err = self.open_public_video(uid, public_vid.id)
                if err:
                    return None, err
                return (copied_vid, None), None

        # Auto-fetch YouTube metadata nếu cần
        if type_video == 'youtube':
            title, thumbnail = self._enrich_youtube_meta(source_url, title, thumbnail)

        new_id = self.video_repo.create(
            title=title,
            thumbnail=thumbnail,
            source_url=source_url,
            type_video=type_video,
            definition_lang_code=definition_lang_code,
            term_lang_code=term_lang_code,
            user_id=user.id,
            public_video_id=None
        )

        job_id = None
        if type_video == 'youtube':
            job_id = start_youtube_subtitle_job(source_url, term_lang_code, definition_lang_code)

        return (self.video_repo.get_by_id(new_id), job_id), None

    def open_public_video(self, uid, public_video_id):
        """
        User nhấn xem một video chung.
        - Nếu đã có bản sao → cập nhật LastOpened và trả về bản sao đó.
        - Nếu chưa có    → tạo bản sao mới (copy title, thumbnail, source_url, type_video)
                           rồi gán UserId và PublicVideoId.
        """
        user = self.user_repo.get_by_uid(uid)
        if not user:
            return None, 'user_not_found'

        public_video = self.video_repo.get_by_id(public_video_id)
        if not public_video:
            return None, 'not_found'

        # Chỉ clone video chung (UserId IS NULL)
        if public_video.user_id is not None:
            return None, 'not_a_public_video'

        # Kiểm tra xem đã có bản sao chưa
        existing_copy = self.video_repo.get_user_copy_of_public(user.id, public_video_id)
        if existing_copy:
            self.video_repo.update_last_opened(existing_copy.id)
            return self.video_repo.get_by_id(existing_copy.id), None

        # Tạo bản sao mới (copy toàn bộ nội dung từ video gốc, kể cả language codes)
        new_id = self.video_repo.create(
            title=public_video.title,
            thumbnail=public_video.thumbnail,
            source_url=public_video.source_url,
            type_video=public_video.type_video,
            definition_lang_code=public_video.definition_lang_code,
            term_lang_code=public_video.term_lang_code,
            user_id=user.id,
            public_video_id=public_video_id
        )
        self.video_repo.update_last_opened(new_id)
        return self.video_repo.get_by_id(new_id), None

    # ─────────────────────────────────────────────
    #  UPDATE
    # ─────────────────────────────────────────────

    def update_video(self, video_id, uid, data):
        """
        Cập nhật video.
        - Video chung (UserId NULL): chỉ Admin.
        - Video riêng: chỉ chủ sở hữu.
        """
        user = self.user_repo.get_by_uid(uid)
        if not user:
            return None, 'user_not_found'

        video = self.video_repo.get_by_id(video_id)
        if not video:
            return None, 'not_found'

        if video.user_id is None:
            # Video chung → cần Admin
            if user.role != 'Admin':
                return None, 'forbidden'
        else:
            # Video riêng → cần là chủ
            if video.user_id != user.id:
                return None, 'forbidden'

        allowed_fields = {
            'title', 'thumbnail', 'source_url', 'type_video',
            'definition_lang_code', 'term_lang_code'
        }
        update_data = {k: v for k, v in data.items() if k in allowed_fields and v is not None}

        if not update_data:
            return None, 'no_valid_fields'

        self.video_repo.update(video_id, update_data)
        return self.video_repo.get_by_id(video_id), None

    # ─────────────────────────────────────────────
    #  DELETE
    # ─────────────────────────────────────────────

    def delete_video(self, video_id, uid):
        """
        Xóa video.
        - Video chung (UserId NULL): chỉ Admin.
        - Video riêng: chỉ chủ sở hữu.
        """
        user = self.user_repo.get_by_uid(uid)
        if not user:
            return 'user_not_found'

        video = self.video_repo.get_by_id(video_id)
        if not video:
            return 'not_found'

        if video.user_id is None:
            if user.role != 'Admin':
                return 'forbidden'
        else:
            if video.user_id != user.id:
                return 'forbidden'

        self.video_repo.delete(video_id)
        return None
