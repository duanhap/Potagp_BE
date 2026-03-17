import re
from app.repositories.video_repository import VideoRepository
from app.repositories.user_repository import UserRepository
from app.repositories.subtitle_repository import SubtitleRepository
from app.utils.youtube_helper import check_youtube_subtitle_job, cancel_youtube_subtitle_job

def parse_srt_content(file_content: str):
    """
    Parse content from SRT file.
    Expects format per block:
    [Index]
    [StartTime] --> [EndTime]
    [Content line 1]
    ...
    [Pronunciation] (second to last line)
    [Translation] (last line)
    """
    file_content = file_content.replace('\r\n', '\n')
    blocks = re.split(r'\n\s*\n', file_content.strip())
    
    subtitles = []
    time_pattern = re.compile(
        r'(\d{2}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,.]\d{3})'
    )
    
    def time_to_ms(time_str):
        # Support both comma and dot as ms separator
        time_str = time_str.replace('.', ',')
        parts = time_str.split(':')
        if len(parts) != 3:
            return 0
        h, m, s_ms = parts
        try:
            s, ms = s_ms.split(',')
            return int(h) * 3600000 + int(m) * 60000 + int(s) * 1000 + int(ms)
        except:
            return 0

    for block in blocks:
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        if len(lines) < 3:
            continue
            
        time_match = time_pattern.search(lines[1])
        text_lines = []
        if time_match:
            text_lines = lines[2:]
        else:
            # Fallback in case index line is missing
            time_match = time_pattern.search(lines[0])
            if time_match:
                text_lines = lines[1:]
                
        if not time_match or not text_lines:
            continue
            
        start_str, end_str = time_match.groups()
        start_ms = time_to_ms(start_str)
        end_ms = time_to_ms(end_str)
        
        content = ""
        pronunciation = ""
        translation = ""
        
        if len(text_lines) >= 3:
            translation = text_lines[-1]
            pronunciation = text_lines[-2]
            content = "\n".join(text_lines[:-2])
        elif len(text_lines) == 2:
            content = text_lines[0]
            pronunciation = text_lines[1]
        else:
            content = text_lines[0]
            
        subtitles.append({
            'start_time': start_ms,
            'end_time': end_ms,
            'content': content,
            'pronunciation': pronunciation,
            'translation': translation
        })
        
    return subtitles

class SubtitleService:
    def __init__(self):
        self.video_repo = VideoRepository()
        self.user_repo = UserRepository()
        self.subtitle_repo = SubtitleRepository()

    def get_subtitles(self, video_id, uid):
        # Ai cũng có thể xem subtitle nếu video là public hoặc là của họ
        user = self.user_repo.get_by_uid(uid)
        if not user:
            return None, 'user_not_found'
            
        video = self.video_repo.get_by_id(video_id)
        if not video:
            return None, 'not_found'
            
        # Nếu video ko phải public và không phải do user sở hữu -> Cấm
        if video.user_id is not None and video.user_id != user.id:
            return None, 'forbidden'
            
        # Cập nhật thuật tính LastOpened khi mở coi sub
        self.video_repo.update_last_opened(video_id)
            
        subs = self.subtitle_repo.get_by_video_id(video_id)
        
        # Nếu không có subtitle trực tiếp, mà video này là bản copy (có PublicVideoId)
        # -> Thử lấy subtitle của video gốc public
        if not subs and video.public_video_id is not None:
            subs = self.subtitle_repo.get_by_video_id(video.public_video_id)
            
        return subs, None

    def upload_subtitles(self, video_id, uid, srt_content):
        user = self.user_repo.get_by_uid(uid)
        if not user:
            return None, 'user_not_found'
            
        video = self.video_repo.get_by_id(video_id)
        if not video:
            return None, 'not_found'
            
        # Kiểm tra quyền:
        if video.user_id is None:
            # Video Public -> Chỉ Admin được thêm sub
            if user.role != 'Admin':
                return None, 'forbidden_admin_required'
        else:
            # Video Private -> Chủ sở hữu mới được thêm/sửa
            if video.user_id != user.id:
                return None, 'forbidden'

        subs = parse_srt_content(srt_content)
        if not subs:
            return None, 'invalid_or_empty_srt'
            
        # Xóa hết subtitle cũ của video này và insert toàn bộ
        self.subtitle_repo.delete_by_video_id(video_id)
        count = self.subtitle_repo.insert_many(subs, video_id)
        
        return count, None

    def sync_youtube_job(self, video_id, uid, job_id):
        # Kiểm tra quyền:
        user = self.user_repo.get_by_uid(uid)
        if not user:
            return None, 'user_not_found'
            
        video = self.video_repo.get_by_id(video_id)
        if not video:
            return None, 'not_found'
            
        if video.user_id is None:
            if user.role != 'Admin':
                return None, 'forbidden_admin_required'
        else:
            if video.user_id != user.id:
                return None, 'forbidden'

        # Gọi external API
        job_res = check_youtube_subtitle_job(job_id)
        if not job_res:
            return None, 'job_not_found_or_error'
            
        # Nếu đã completed, tiến hành insert vào Database
        if job_res.get('status') == 'completed':
            raw_subs = job_res.get('data', [])
            
            def parse_time_to_ms(t_str):
                # format: HH:MM:SS,mmm
                try:
                    parts = t_str.replace('.', ',').split(':')
                    if len(parts) == 3:
                        h, m, s_ms = parts
                        s, ms = s_ms.split(',')
                        return int(h) * 3600000 + int(m) * 60000 + int(s) * 1000 + int(ms)
                except:
                    return 0
                return 0
            
            format_subs = []
            for item in raw_subs:
                format_subs.append({
                    'start_time': parse_time_to_ms(item.get('starttime', '00:00:00,000')),
                    'end_time': parse_time_to_ms(item.get('endtime', '00:00:00,000')),
                    'content': item.get('content', ''),
                    'pronunciation': item.get('pronunciation', ''),
                    'translation': item.get('translation', '')
                })
            
            if format_subs:
                self.subtitle_repo.delete_by_video_id(video_id)
                self.subtitle_repo.insert_many(format_subs, video_id)
                
        return job_res, None

    def cancel_youtube_job(self, video_id, uid, job_id):
        user = self.user_repo.get_by_uid(uid)
        if not user:
            return None, 'user_not_found'
            
        video = self.video_repo.get_by_id(video_id)
        if not video:
            return None, 'not_found'
            
        if video.user_id is None:
            if user.role != 'Admin':
                return None, 'forbidden_admin_required'
        else:
            if video.user_id != user.id:
                return None, 'forbidden'

        cancel_res = cancel_youtube_subtitle_job(job_id)
        
        # Nếu gửi yêu cầu hủy thành công (tức External API trả về {success: True}),
        # Xóa video khỏi CSDL (theo logic: MK làm API gọi đến và nếu thành công thì xóa video đó đi luôn).
        if cancel_res and cancel_res.get('success'):
            self.video_repo.delete(video_id)
            
        return cancel_res, None
