import re
import urllib.request
import urllib.parse
import json
import os

YOUTUBE_SUB_API_URL = os.getenv('YOUTUBE_SUB_API_URL', 'https://simple-emu-vocal.ngrok-free.app')



def extract_youtube_video_id(url: str) -> str | None:
    """
    Trích xuất YouTube Video ID từ nhiều dạng URL khác nhau.

    Hỗ trợ:
      - https://www.youtube.com/watch?v=VIDEO_ID
      - https://youtu.be/VIDEO_ID
      - https://www.youtube.com/embed/VIDEO_ID
      - https://www.youtube.com/shorts/VIDEO_ID
    """
    if not url:
        return None

    patterns = [
        r'(?:youtube\.com/watch\?.*v=)([a-zA-Z0-9_-]{11})',
        r'(?:youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com/shorts/)([a-zA-Z0-9_-]{11})',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def get_youtube_thumbnail_url(video_id: str) -> str:
    """
    Trả về URL thumbnail chất lượng cao nhất còn khả dụng.
    Thứ tự ưu tiên: maxresdefault → sddefault → hqdefault
    """
    resolutions = ['maxresdefault', 'sddefault', 'hqdefault']
    for res in resolutions:
        url = f"https://img.youtube.com/vi/{video_id}/{res}.jpg"
        try:
            req = urllib.request.Request(url, method='HEAD')
            with urllib.request.urlopen(req, timeout=5) as resp:
                # YouTube trả về ảnh placeholder 120x90 cho video không tồn tại
                content_length = resp.headers.get('Content-Length', '0')
                if int(content_length) > 2000:   # ảnh thật lớn hơn 2KB
                    return url
        except Exception:
            continue

    # fallback mặc định
    return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"


def fetch_youtube_info(source_url: str) -> dict:
    """
    Lấy title và thumbnail của video YouTube từ source_url.

    Trả về dict:
      {
        'title':     str | None,
        'thumbnail': str | None,
        'video_id':  str | None,
        'error':     str | None   # None nếu thành công
      }
    """
    video_id = extract_youtube_video_id(source_url)
    if not video_id:
        return {
            'title': None,
            'thumbnail': None,
            'video_id': None,
            'error': 'Cannot extract YouTube video ID from URL'
        }

    # ── Lấy title từ oEmbed API ─────────────────────────────────────
    title = None
    try:
        oembed_url = (
            "https://www.youtube.com/oembed?"
            + urllib.parse.urlencode({'url': source_url, 'format': 'json'})
        )
        req = urllib.request.Request(oembed_url)
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            title = data.get('title')
    except Exception as e:
        # Không lấy được title — vẫn tiếp tục để lấy thumbnail
        print(f"[YouTube] oEmbed fetch failed: {e}")

    # ── Lấy thumbnail từ img.youtube.com ────────────────────────────
    thumbnail = get_youtube_thumbnail_url(video_id)

    return {
        'title':     title,
        'thumbnail': thumbnail,
        'video_id':  video_id,
        'error':     None
    }


def start_youtube_subtitle_job(source_url: str, term_lang_code: str, definition_lang_code: str) -> str | None:
    """
    Gọi External API để start job tạo subtitle.
    Trả về job_id nếu thành công, None nếu thất bại.
    """
    url = f"{YOUTUBE_SUB_API_URL}/youtube"
    payload = {
        "sourceurl": source_url,
        "termlanguagecode": term_lang_code,
        "definitionlanguagecode": definition_lang_code
    }
    data = json.dumps(payload).encode('utf-8')
    headers = {
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'true'
    }
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp_data = json.loads(resp.read().decode('utf-8'))
            if resp_data.get('success'):
                return resp_data.get('data', {}).get('job_id')
    except Exception as e:
        print(f"[YouTube Job] Failed to start job: {e}")
    return None


def check_youtube_subtitle_job(job_id: str) -> dict | None:
    """
    Kiểm tra tiến trình job từ External API.
    Trả về nguyên response dict từ external API hoặc None nếu lỗi.
    """
    url = f"{YOUTUBE_SUB_API_URL}/progress/{job_id}"
    headers = {
        'ngrok-skip-browser-warning': 'true'
    }
    req = urllib.request.Request(url, headers=headers, method='GET')
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"[YouTube Job] Failed to check job progress {job_id}: {e}")
    return None
