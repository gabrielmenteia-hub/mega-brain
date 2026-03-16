"""Quora signal collector for Pain Radar.

Collects pain signals from Quora question pages via Playwright (fetch_spa).
Quora is a React SPA — SSR fetch is insufficient; Playwright renders JS.

Gracefully degrades to empty list on any error (CAPTCHA, 403, network failure).
This is by design — Quora is NOT a blocking data source for the MVP.
"""
import hashlib
import json
from datetime import datetime, timezone

import sqlite_utils
import structlog
from bs4 import BeautifulSoup

from mis.base_scraper import BaseScraper
from mis.exceptions import ScraperError

log = structlog.get_logger()


def _url_hash(url: str) -> str:
    """SHA-256 of URL as deduplication key."""
    return hashlib.sha256(url.encode()).hexdigest()


def _extract_questions(html: str, niche_slug: str) -> list[dict]:
    """Extract question links from Quora HTML via BeautifulSoup.

    Attempts multiple selectors in fallback order:
    1. <a> tags with /What- or /How- in href
    2. <span> tags with 'question' in class name

    Args:
        html: Rendered HTML from Quora search page.
        niche_slug: Niche identifier to tag each signal.

    Returns:
        List of signal dicts (up to 25 per call).
    """
    soup = BeautifulSoup(html, "html.parser")

    # Strategy 1: <a> tags with Quora question URL pattern
    links = soup.find_all(
        "a",
        href=lambda h: h and ("/What-" in h or "/How-" in h or "/Why-" in h or "/Is-" in h),
    )

    if not links:
        # Strategy 2: <span> tags with 'question' in class
        spans = soup.find_all("span", class_=lambda c: c and "question" in c.lower())
        # Try to find parent <a> for each span
        links = []
        for span in spans:
            parent_a = span.find_parent("a")
            if parent_a and parent_a.get("href"):
                links.append(parent_a)

    if not links:
        return []

    signals = []
    seen_urls = set()

    for link in links[:25]:
        href = link.get("href", "")
        if not href:
            continue

        # Build full URL for relative hrefs
        if href.startswith("/"):
            url = f"https://www.quora.com{href}"
        elif href.startswith("https://"):
            url = href
        else:
            continue

        if url in seen_urls:
            continue
        seen_urls.add(url)

        title = link.get_text(strip=True) or href.replace("-", " ").strip("/")

        signals.append({
            "url_hash": _url_hash(url),
            "url": url,
            "title": title,
            "source": "quora",
            "niche_slug": niche_slug,
            "score": 0,
            "extra_json": "{}",
            "collected_at": datetime.now(timezone.utc).isoformat(),
        })

    return signals


async def collect_quora_signals(
    niche: dict,
    db_path: str | None = None,
) -> list[dict]:
    """Collect Quora pain signals for all keywords in a niche.

    Uses Playwright via BaseScraper.fetch_spa() because Quora is a React SPA.
    Returns [] on any failure mode (CAPTCHA, 403, network error, empty shell).

    Args:
        niche: Niche dict with slug and keywords.
        db_path: If provided, persists signals to SQLite pain_signals table.

    Returns:
        List of signal dicts (may be [] if Quora blocked — graceful degradation).
    """
    niche_slug = niche["slug"]
    keywords = niche.get("keywords", [])
    all_signals = []

    scraper = BaseScraper()

    for keyword in keywords:
        query = keyword.replace(" ", "+")
        url = f"https://www.quora.com/search?q={query}"

        try:
            html = await scraper.fetch_spa(url)

            # Detect empty SPA shell (React app shell without content)
            if len(html) < 5000:
                log.warning(
                    "radar.quora.empty_response",
                    keyword=keyword,
                    html_len=len(html),
                    alert="quora_empty_response",
                )
                continue

            signals = _extract_questions(html, niche_slug)
            all_signals.extend(signals)

        except ScraperError as exc:
            log.error(
                "radar.quora.scraper_error",
                keyword=keyword,
                niche_slug=niche_slug,
                error=str(exc),
                alert="radar_collector_failed",
            )
            return []

        except Exception as exc:
            log.error(
                "radar.quora.failed",
                keyword=keyword,
                niche_slug=niche_slug,
                error=str(exc),
                alert="radar_collector_failed",
            )
            return []

    if db_path and all_signals:
        db = sqlite_utils.Database(db_path)
        for sig in all_signals:
            try:
                db["pain_signals"].insert(sig, ignore=True)
            except Exception as exc:
                log.warning(
                    "radar.quora.persist_failed",
                    error=str(exc),
                )

    return all_signals
