"""mis.radar.meta_ads_collector — Meta Ad Library radar collector (RADAR-04).

Coleta criativos de anuncios ativos por keyword/niche via Meta Ad Library API.
Persiste em pain_signals com source='meta_ads'. Retorna [] graciosamente sem token.
"""
import asyncio
import hashlib
import json
import os
import random
from datetime import datetime, timezone

import httpx
import sqlite_utils
import structlog

log = structlog.get_logger()
META_API_URL = "https://graph.facebook.com/v25.0/ads_archive"


def _url_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()


async def collect_ad_comments(niche: dict, db_path: str) -> list[dict]:
    """Collect Meta Ads creative bodies as pain signals for a niche.

    Fetches active ads from the Meta Ad Library API for each keyword in the niche,
    persists each ad creative body as a pain signal with source='meta_ads'.
    Idempotent: INSERT OR IGNORE on url_hash UNIQUE index prevents duplicates.

    Args:
        niche: Niche config dict with slug, keywords, ad_countries.
        db_path: Path to the SQLite database file.

    Returns:
        List of signal dicts inserted (empty list if no token or no ads found).
    """
    token = os.getenv("META_ACCESS_TOKEN", "").strip()
    if not token:
        log.warning("meta_ads.skipped", reason="no_META_ACCESS_TOKEN")
        return []

    niche_slug = niche["slug"]
    ad_countries = ",".join(niche.get("ad_countries", ["BR"]))
    db = sqlite_utils.Database(db_path)
    collected = []

    for keyword in niche.get("keywords", []):
        params = {
            "access_token": token,
            "search_terms": keyword,
            "ad_reached_countries": ad_countries,
            "ad_active_status": "ACTIVE",
            "ad_type": "ALL",
            "fields": "page_name,ad_snapshot_url,ad_creative_bodies,ad_delivery_start_time",
            "limit": 25,
        }
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(META_API_URL, params=params)
                resp.raise_for_status()
                ads = resp.json().get("data", [])
        except httpx.HTTPStatusError as e:
            log.error("meta_ads_radar.fetch_error", keyword=keyword, niche=niche_slug, error=str(e))
            await asyncio.sleep(random.uniform(1, 2))
            continue

        for ad in ads:
            bodies = ad.get("ad_creative_bodies") or []
            if not bodies:
                log.debug("meta_ads_radar.skipped_no_body", keyword=keyword)
                continue

            content = "\n\n".join(bodies)
            url = ad["ad_snapshot_url"]
            signal = {
                "url_hash": _url_hash(url),
                "url": url,
                "title": content,
                "source": "meta_ads",
                "niche_slug": niche_slug,
                "score": 0,
                "extra_json": json.dumps({
                    "page_name": ad.get("page_name"),
                    "ad_delivery_start_time": ad.get("ad_delivery_start_time"),
                }),
                "collected_at": datetime.now(timezone.utc).isoformat(),
            }
            try:
                db["pain_signals"].insert(signal, ignore=True)
                collected.append(signal)
            except Exception as exc:
                log.warning("meta_ads_radar.persist_failed", error=str(exc))

        log.info("meta_ads_radar.fetched", keyword=keyword, niche=niche_slug, count=len(ads))
        await asyncio.sleep(random.uniform(1, 2))

    log.info("meta_ads_radar.done", niche=niche_slug, count=len(collected))
    return collected
