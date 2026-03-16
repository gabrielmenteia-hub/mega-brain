"""YouTube Data API v3 collector for Pain Radar.

Collects pain signals from YouTube search results with persistent quota management.
Quota guard prevents exceeding 10,000 daily units even across process restarts.
Daily quota resets at 07:00 UTC (midnight PT).
"""
import asyncio
import hashlib
import json
import os
from datetime import datetime, timedelta, timezone

import sqlite_utils
import structlog

from googleapiclient.discovery import build

log = structlog.get_logger()


# ---------------------------------------------------------------------------
# Quota management
# ---------------------------------------------------------------------------

def get_quota_used_today(db_path: str, reset_hour_utc: int = 7) -> int:
    """Sum units used since today's daily reset (07:00 UTC = midnight PT).

    Args:
        db_path: Path to the SQLite database file.
        reset_hour_utc: Hour (UTC) at which daily quota resets. Default 7 (midnight PT).

    Returns:
        Total units consumed since the last reset.
    """
    db = sqlite_utils.Database(db_path)

    # Guard: table may not exist yet
    if "youtube_quota_log" not in db.table_names():
        return 0

    today = datetime.now(timezone.utc)
    reset_dt = today.replace(hour=reset_hour_utc, minute=0, second=0, microsecond=0)
    if today.hour < reset_hour_utc:
        # Reset hasn't happened yet today — use yesterday's reset as the cutoff
        reset_dt -= timedelta(days=1)

    rows = list(db["youtube_quota_log"].rows_where(
        "logged_at > ?", [reset_dt.isoformat()]
    ))
    return sum(r["units"] for r in rows)


def log_quota_usage(db_path: str, units: int, operation: str) -> None:
    """Persist quota usage to youtube_quota_log table.

    Args:
        db_path: Path to the SQLite database file.
        units: Number of API units consumed.
        operation: Human-readable operation label (e.g. 'search.list').
    """
    db = sqlite_utils.Database(db_path)
    db["youtube_quota_log"].insert({
        "units": units,
        "operation": operation,
        "logged_at": datetime.now(timezone.utc).isoformat(),
    })


# ---------------------------------------------------------------------------
# Synchronous YouTube API calls (run inside executor to stay async-friendly)
# ---------------------------------------------------------------------------

def _sync_collect_youtube(keyword: str, lang: str, api_key: str) -> tuple:
    """Collect signals from YouTube for a single keyword.

    Runs synchronously; call via loop.run_in_executor() from async context.

    Returns:
        Tuple of (signals: list[dict], units_used: int).
        Never propagates exceptions — returns ([], 0) on error.
    """
    try:
        youtube = build("youtube", "v3", developerKey=api_key)

        # search.list = 100 units
        search_resp = youtube.search().list(
            q=keyword,
            part="snippet",
            maxResults=10,
            relevanceLanguage=lang,
            type="video",
        ).execute()
        units_used = 100

        videos = search_resp.get("items", [])[:5]
        if not videos:
            return [], units_used

        # videos.list statistics = 1 unit for multiple IDs in one request
        video_ids = [v["id"]["videoId"] for v in videos]
        stats_resp = youtube.videos().list(
            id=",".join(video_ids),
            part="statistics",
        ).execute()
        units_used += 1

        stats_map = {
            s["id"]: s.get("statistics", {})
            for s in stats_resp.get("items", [])
        }

        signals = []
        for video in videos:
            vid_id = video["id"]["videoId"]
            title = video["snippet"]["title"]
            stats = stats_map.get(vid_id, {})
            view_count = int(stats.get("viewCount", 0))
            like_count = int(stats.get("likeCount", 0))

            # commentThreads.list = 1 unit per video
            try:
                comments_resp = youtube.commentThreads().list(
                    videoId=vid_id,
                    part="snippet",
                    maxResults=10,
                    order="relevance",
                ).execute()
                top_comments = [
                    c["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                    for c in comments_resp.get("items", [])
                ]
                units_used += 1
            except Exception:
                top_comments = []

            signals.append({
                "url": f"https://youtube.com/watch?v={vid_id}",
                "title": title,
                "source": "youtube",
                "score": view_count,
                "extra_json": json.dumps({
                    "top_comments": top_comments,
                    "like_count": like_count,
                }),
                "collected_at": datetime.now(timezone.utc).isoformat(),
            })

        return signals, units_used

    except Exception as exc:
        log.error(
            "radar.youtube.failed",
            keyword=keyword,
            error=str(exc),
            alert="radar_collector_failed",
        )
        return [], 0


# ---------------------------------------------------------------------------
# Async entry point
# ---------------------------------------------------------------------------

async def collect_youtube_signals(niche: dict, db_path: str, config: dict) -> list:
    """Collect YouTube pain signals for a niche with persistent quota guard.

    Checks quota before each keyword. Stops early when daily limit reached.
    Upserts signals into pain_signals table via url_hash UNIQUE constraint.

    Args:
        niche: Niche dict with slug, keywords, and radar sub-dict.
        db_path: Path to the SQLite database file.
        config: Config dict; reads config['settings']['youtube_quota_daily_limit'].

    Returns:
        List of signal dicts collected in this run (may be empty if quota exhausted).
    """
    api_key = os.environ.get("YOUTUBE_DATA_API_KEY", "")
    if not api_key:
        log.warning("radar.youtube.no_api_key", alert="radar_collector_failed")
        return []

    quota_limit = config.get("settings", {}).get("youtube_quota_daily_limit", 9000)
    quota_used = get_quota_used_today(db_path)
    if quota_used >= quota_limit:
        log.warning(
            "radar.youtube.quota_exhausted",
            quota_used=quota_used,
            alert="youtube_quota_exhausted",
        )
        return []

    lang = niche.get("radar", {}).get("relevance_language", "pt")
    all_signals = []
    loop = asyncio.get_event_loop()
    db = sqlite_utils.Database(db_path)

    for keyword in niche.get("keywords", []):
        # Re-check quota before each keyword to stop mid-niche if needed
        if get_quota_used_today(db_path) >= quota_limit:
            log.warning(
                "radar.youtube.quota_exhausted_mid_niche",
                alert="youtube_quota_exhausted",
            )
            break

        signals, units_used = await loop.run_in_executor(
            None, _sync_collect_youtube, keyword, lang, api_key
        )

        if units_used > 0:
            log_quota_usage(db_path, units_used, "search+stats+comments")

        for sig in signals:
            url_hash = hashlib.sha256(sig["url"].encode()).hexdigest()
            sig_with_hash = {**sig, "url_hash": url_hash, "niche_slug": niche["slug"]}
            # Upsert via INSERT OR IGNORE on UNIQUE url_hash
            try:
                db["pain_signals"].insert(sig_with_hash, ignore=True)
            except Exception:
                pass
            all_signals.append({**sig, "niche_slug": niche["slug"]})

    return all_signals
