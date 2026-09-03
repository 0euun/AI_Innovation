"""YouTube Data API v3의 허가된 공개 영상·댓글을 Mobius 이벤트로 정규화한다."""
import json
import os
import re
from datetime import UTC, datetime
from urllib.parse import urlencode
from urllib.request import urlopen

BASE_URL = "https://www.googleapis.com/youtube/v3"


def mask_text(value: str) -> str:
    value = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[EMAIL]", value)
    return re.sub(r"(?:\+82[- ]?)?0?1[0-9][ -]?\d{3,4}[ -]?\d{4}", "[PHONE]", value)


def status() -> dict:
    return {"provider": "youtube", "configured": bool(os.getenv("YOUTUBE_API_KEY")), "mode": "official_api", "scope": "public video search and published comments"}


def _get(path: str, **params) -> dict:
    key = os.getenv("YOUTUBE_API_KEY")
    if not key:
        raise RuntimeError("YOUTUBE_API_KEY가 설정되지 않았습니다.")
    params["key"] = key
    with urlopen(f"{BASE_URL}{path}?{urlencode(params)}", timeout=15) as response:
        return json.loads(response.read())


def collect(query: str, target_id: str, max_videos: int, max_comments: int) -> list[dict]:
    search = _get("/search", part="snippet", type="video", q=query, order="date", maxResults=max_videos)
    events = []
    for video in search.get("items", []):
        video_id = video.get("id", {}).get("videoId")
        if not video_id:
            continue
        try:
            threads = _get("/commentThreads", part="snippet", videoId=video_id, order="time", textFormat="plainText", maxResults=max_comments)
        except Exception:
            continue  # 댓글 비활성화 등 개별 영상 오류는 동기화 전체를 중단하지 않는다.
        for thread in threads.get("items", []):
            snippet = thread.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
            comment_id = thread.get("snippet", {}).get("topLevelComment", {}).get("id")
            if not comment_id or not snippet.get("textDisplay"):
                continue
            published = snippet.get("publishedAt") or datetime.now(UTC).isoformat()
            events.append({"event_id": f"youtube:{comment_id}", "occurred_at": published, "platform": "youtube", "author_ref": f"youtube:{snippet.get('authorChannelId', {}).get('value', 'masked')}", "target_ref": target_id, "text": mask_text(snippet["textDisplay"]), "hashtags": [], "likes": int(snippet.get("likeCount", 0)), "shares": 0, "comments": int(thread.get("snippet", {}).get("totalReplyCount", 0)), "source_url": f"https://www.youtube.com/watch?v={video_id}"})
    return events
