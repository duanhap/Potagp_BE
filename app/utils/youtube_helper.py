import re
import urllib.request
import urllib.parse
import json


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
