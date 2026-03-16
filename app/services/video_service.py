from app.repositories.video_repository import VideoRepository
from app.repositories.user_repository import UserRepository
from app.utils.youtube_helper import fetch_youtube_info


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

    def get_public_videos(self):
        """Lấy danh sách video chung (recommend) – ai cũng xem được."""
        return self.video_repo.get_all_public()

    def get_my_videos(self, uid):
        """Lấy danh sách video riêng của user đang đăng nhập."""
        user = self.user_repo.get_by_uid(uid)
        if not user:
            return None, 'user_not_found'
        videos = self.video_repo.get_all_by_user_id(user.id)
        return videos, None

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

    def create_public_video(self, uid, title, thumbnail, source_url, type_video):
        """
        Tạo video chung (recommend).
        Chỉ Admin mới có quyền.
        Nếu type_video='youtube' và title/thumbnail chưa đủ → tự động fetch.
        """
        user = self.user_repo.get_by_uid(uid)
        if not user:
            return None, 'user_not_found'

        if user.role != 'Admin':
            return None, 'forbidden'

        if not source_url:
            return None, 'source_url_required'

        # Auto-fetch YouTube metadata nếu cần
        if type_video == 'youtube':
            title, thumbnail = self._enrich_youtube_meta(source_url, title, thumbnail)

        new_id = self.video_repo.create(
            title=title,
            thumbnail=thumbnail,
            source_url=source_url,
            type_video=type_video,
            user_id=None,           # video chung: không thuộc user nào
            public_video_id=None
        )
        return self.video_repo.get_by_id(new_id), None

    def create_my_video(self, uid, title, thumbnail, source_url, type_video):
        """
        Tạo video riêng của user.
        Nếu type_video='youtube' và title/thumbnail chưa đủ → tự động fetch.
        """
        user = self.user_repo.get_by_uid(uid)
        if not user:
            return None, 'user_not_found'

        if not source_url:
            return None, 'source_url_required'

        # Auto-fetch YouTube metadata nếu cần
        if type_video == 'youtube':
            title, thumbnail = self._enrich_youtube_meta(source_url, title, thumbnail)

        new_id = self.video_repo.create(
            title=title,
            thumbnail=thumbnail,
            source_url=source_url,
            type_video=type_video,
            user_id=user.id,
            public_video_id=None
        )
        return self.video_repo.get_by_id(new_id), None

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

        # Tạo bản sao mới
        new_id = self.video_repo.create(
            title=public_video.title,
            thumbnail=public_video.thumbnail,
            source_url=public_video.source_url,
            type_video=public_video.type_video,
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

        allowed_fields = {'title', 'thumbnail', 'source_url', 'type_video'}
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
