"""Reddit signal collector for Pain Radar.

Collects pain signals from Reddit subreddits via PRAW (Python Reddit API Wrapper).
PRAW is synchronous — runs inside asyncio executor to avoid blocking the event loop.

Posts older than 24 hours are filtered out to keep signals fresh.
Gracefully degrades to empty list on any PRAW error.
"""
import asyncio
import hashlib
import json
import os
from datetime import datetime, timezone

import praw
import sqlite_utils
import structlog

log = structlog.get_logger()


def _url_hash(url: str) -> str:
    """SHA-256 of URL as deduplication key."""
    import hashlib as _hashlib
    return _hashlib.sha256(url.encode()).hexdigest()


def _sync_collect_reddit(niche: dict) -> list[dict]:
    """Collect Reddit signals synchronously for all subreddits in the niche.

    Intended to be called via loop.run_in_executor() to avoid blocking async event loop.

    Args:
        niche: Niche dict with slug and radar.subreddits fields.

    Returns:
        List of signal dicts. Returns [] on any PRAW error.
    """
    try:
        reddit = praw.Reddit(
            client_id=os.environ.get("REDDIT_CLIENT_ID", ""),
            client_secret=os.environ.get("REDDIT_CLIENT_SECRET", ""),
            user_agent=os.environ.get("REDDIT_USER_AGENT", "mis-pain-radar/1.0"),
        )

        niche_slug = niche["slug"]
        subreddits = niche.get("radar", {}).get("subreddits", [])
        signals = []
        now = datetime.now(timezone.utc)

        for subreddit_name in subreddits:
            try:
                sub = reddit.subreddit(subreddit_name)
                for post in sub.new(limit=25):
                    # Filter posts older than 24 hours
                    post_dt = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
                    age_hours = (now - post_dt).total_seconds() / 3600
                    if age_hours > 24:
                        continue

                    url = f"https://www.reddit.com{post.permalink}"
                    signals.append({
                        "url_hash": _url_hash(url),
                        "url": url,
                        "title": post.title,
                        "source": "reddit",
                        "niche_slug": niche_slug,
                        "score": int(post.score),
                        "extra_json": "{}",
                        "collected_at": datetime.now(timezone.utc).isoformat(),
                    })
            except Exception as sub_exc:
                log.error(
                    "radar.reddit.subreddit_failed",
                    subreddit=subreddit_name,
                    error=str(sub_exc),
                    alert="radar_collector_failed",
                )
                continue

        return signals

    except Exception as exc:
        log.error(
            "radar.reddit.failed",
            niche_slug=niche.get("slug"),
            error=str(exc),
            alert="radar_collector_failed",
        )
        return []


async def collect_reddit_signals(
    niche: dict,
    db_path: str | None = None,
) -> list[dict]:
    """Collect Reddit pain signals for all subreddits in a niche.

    Wraps synchronous PRAW call in asyncio executor to avoid blocking the event loop.
    Optionally persists signals to pain_signals table via INSERT OR IGNORE.

    Args:
        niche: Niche dict with slug and radar.subreddits.
        db_path: If provided, persists signals to SQLite pain_signals table.

    Returns:
        List of signal dicts (may be empty on PRAW error — graceful degradation).
    """
    loop = asyncio.get_event_loop()
    signals = await loop.run_in_executor(None, _sync_collect_reddit, niche)

    if db_path and signals:
        db = sqlite_utils.Database(db_path)
        for sig in signals:
            try:
                db["pain_signals"].insert(sig, ignore=True)
            except Exception as exc:
                log.warning(
                    "radar.reddit.persist_failed",
                    error=str(exc),
                )

    return signals
