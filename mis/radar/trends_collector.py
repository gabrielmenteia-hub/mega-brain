"""Google Trends signal collector for Pain Radar.

Collects interest-over-time signals from Google Trends via pytrends.
Uses anchor term for normalization and returns peak_index (0-100).

Rate limiting: each keyword call is followed by a random 5-10s sleep
to avoid triggering Google Trends rate limits.
"""
import asyncio
import hashlib
import json
import random
from datetime import datetime, timezone

import sqlite_utils
import structlog
from pytrends.request import TrendReq

log = structlog.get_logger()


def _url_hash(url: str) -> str:
    """SHA-256 of URL as deduplication key."""
    return hashlib.sha256(url.encode()).hexdigest()


async def collect_trends_signal(
    keyword: str,
    anchor: str,
    niche_slug: str,
) -> dict | None:
    """Collect Google Trends peak interest for a single keyword relative to anchor.

    Args:
        keyword: The search keyword to track (e.g. 'emagrecer rapido').
        anchor: Reference term for normalization (e.g. 'academia').
        niche_slug: Niche identifier to tag the signal.

    Returns:
        Signal dict with peak_index (int 0-100) or None if rate limited.
    """
    try:
        pytrends = TrendReq(hl="pt-BR", tz=360)
        pytrends.build_payload([keyword, anchor], timeframe="now 7-d")

        df = pytrends.interest_over_time()

        if df.empty or keyword not in df.columns:
            log.warning(
                "radar.trends.empty_result",
                keyword=keyword,
                niche_slug=niche_slug,
            )
            # Delay before next call
            await asyncio.sleep(random.uniform(5, 10))
            return None

        # Filter out partial rows (last row is often partial)
        if "isPartial" in df.columns:
            df = df[df["isPartial"] == False]  # noqa: E712

        if df.empty or keyword not in df.columns:
            await asyncio.sleep(random.uniform(5, 10))
            return None

        peak_index = int(df[keyword].max())
        url = f"https://trends.google.com/trends/explore?q={keyword}"

        signal = {
            "url_hash": _url_hash(url),
            "url": url,
            "title": f"Google Trends: {keyword}",
            "source": "google_trends",
            "niche_slug": niche_slug,
            "score": peak_index,
            "peak_index": peak_index,
            "extra_json": json.dumps({"anchor": anchor, "keyword": keyword}),
            "collected_at": datetime.now(timezone.utc).isoformat(),
        }

        # Delay between calls to respect rate limits
        await asyncio.sleep(random.uniform(5, 10))
        return signal

    except Exception as exc:
        log.error(
            "radar.trends.failed",
            keyword=keyword,
            niche_slug=niche_slug,
            error=str(exc),
            alert="trends_ratelimited",
        )
        return None


async def collect_niche_trends(niche: dict, db_path: str) -> list[dict]:
    """Collect Google Trends signals for all keywords in a niche.

    Iterates through niche keywords and persists each signal into pain_signals
    via INSERT OR IGNORE on url_hash UNIQUE constraint.

    Args:
        niche: Niche dict with slug, keywords, and radar sub-dict.
        db_path: Path to the SQLite database file.

    Returns:
        List of signal dicts collected (excludes None results from rate-limited calls).
    """
    anchor = niche.get("radar", {}).get("anchor_term", "")
    niche_slug = niche["slug"]
    db = sqlite_utils.Database(db_path)
    collected = []

    for keyword in niche.get("keywords", []):
        signal = await collect_trends_signal(keyword, anchor, niche_slug)
        if signal is None:
            continue

        # Persist via INSERT OR IGNORE on UNIQUE url_hash
        try:
            db["pain_signals"].insert(
                {k: v for k, v in signal.items() if k != "peak_index"},
                ignore=True,
            )
        except Exception as exc:
            log.warning(
                "radar.trends.persist_failed",
                keyword=keyword,
                error=str(exc),
            )

        collected.append(signal)

    return collected
