"""Hotmart platform scanner.

Scrapes the Hotmart marketplace using SSR HTML parsing with BeautifulSoup4.
Confirmed by live inspection (2026-03-14): Hotmart marketplace is SSR — products
are embedded in the HTML response. httpx is sufficient; Playwright is NOT needed.

Confirmed structure:
    URL:         https://hotmart.com/pt-br/marketplace/produtos?category={category_slug}
    Primary:     a.product-link (24 products confirmed in fixture)
    external_id: alphanumeric code from URL (e.g. E45853768C, A1412453A)
    title:       aria-label attribute, text before ' - '
    price:       None (not present in SSR HTML)
    rank:        positional (1-based)

Platform ID convention:
    1 = Hotmart  ← this scanner
    2 = ClickBank
    3 = Kiwify

Usage:
    async with HotmartScanner() as scanner:
        products = await scanner.scan_niche("saude", "saude-e-fitness")
"""
from __future__ import annotations

import re
from typing import Optional

import structlog
from bs4 import BeautifulSoup

from mis.scanner import PlatformScanner, Product

log = structlog.get_logger(__name__)

HOTMART_PLATFORM_ID = 1
HOTMART_BASE_URL = "https://hotmart.com/pt-br/marketplace/produtos"

# Ordered selector list: primary first, fallbacks in order.
# Each entry: (css_selector, title_strategy)
# title_strategy: "aria_label" — use aria-label attr, split on " - "
_SELECTORS_ORDERED = [
    "a.product-link",                          # primary — confirmed live (24 products)
    ".product-card-alt a[aria-label]",         # fallback 1
    "[class*='product'] a[href*='/produtos/']", # fallback 2
]


def _extract_external_id(href: str) -> str:
    """Extract external_id from a Hotmart product URL.

    Strategy: find the alphanumeric product code before '?' in the path.
    Example: '/produtos/nome/E45853768C?sck=HOTMART_SITE' → 'E45853768C'
    Fallback: last path segment (URL slug).
    """
    # Match capital letter followed by 6-10 uppercase alphanumeric chars before '?'
    code_match = re.search(r"/([A-Z][0-9A-Z]{6,10})\?", href)
    if code_match:
        return code_match.group(1)
    # Fallback: last non-empty segment of the path (without query)
    path = href.split("?")[0]
    parts = [p for p in path.rstrip("/").split("/") if p]
    return parts[-1] if parts else href


def _extract_title(aria_label: str) -> str:
    """Extract product title from aria-label attribute.

    Format: 'Product Name - Author Name: '
    We take everything before the first ' - '.
    """
    if " - " in aria_label:
        return aria_label.split(" - ")[0].strip()
    return aria_label.strip()


def _parse_cards(soup: BeautifulSoup, selector: str, niche_id: int) -> list[Product]:
    """Parse product cards for a given CSS selector."""
    cards = soup.select(selector)
    products = []
    for rank, card in enumerate(cards, start=1):
        href = card.get("href", "")
        aria = card.get("aria-label", "")

        if not href:
            continue

        external_id = _extract_external_id(href)
        title = _extract_title(aria) if aria else external_id

        products.append(
            Product(
                external_id=external_id,
                title=title,
                url=href,
                platform_id=HOTMART_PLATFORM_ID,
                niche_id=niche_id,
                rank=rank,
                price=None,  # Not available in Hotmart SSR HTML
            )
        )
    return products


class HotmartScanner(PlatformScanner):
    """Hotmart marketplace scanner using SSR HTML + BeautifulSoup4.

    Fetches the marketplace page via httpx (SSR — no Playwright needed).
    Tries multiple CSS selectors in order for resilience against layout changes.
    Emits alert='schema_drift' via structlog when all selectors fail.

    Attributes:
        HOTMART_PLATFORM_ID: DB platform ID for Hotmart (= 1)
    """

    def __init__(
        self,
        proxy_url: Optional[str] = None,
        proxy_list: Optional[list[str]] = None,
        niche_id: int = 0,
    ) -> None:
        super().__init__(proxy_url=proxy_url, proxy_list=proxy_list)
        self._default_niche_id = niche_id

    async def scan_niche(
        self,
        niche_slug: str,
        platform_slug: str,
        niche_id: int = 0,
    ) -> list[Product]:
        """Scan a Hotmart marketplace category and return ranked products.

        URL pattern: https://hotmart.com/pt-br/marketplace/produtos?category={platform_slug}

        Tries selectors in _SELECTORS_ORDERED order. Emits alert='schema_drift'
        and returns [] when all selectors fail.

        Never raises exceptions — errors are caught and logged.

        Args:
            niche_slug:    MIS niche slug (e.g. "saude") — used for logging
            platform_slug: Hotmart category slug (e.g. "saude-e-fitness")
            niche_id:      DB niche ID for the Product dataclass (0 if unknown)

        Returns:
            List of Product dataclasses ordered by rank, or [] on drift/error.
        """
        effective_niche_id = niche_id or self._default_niche_id
        url = f"{HOTMART_BASE_URL}?category={platform_slug}"

        try:
            html = await self.fetch(url)
        except Exception as exc:
            log.error(
                "hotmart_scanner.fetch_failed",
                niche=niche_slug,
                platform_slug=platform_slug,
                url=url,
                error=str(exc),
            )
            return []

        soup = BeautifulSoup(html, "lxml")

        # Try selectors in order, return first non-empty result
        for selector in _SELECTORS_ORDERED:
            cards = soup.select(selector)
            if cards:
                products = _parse_cards(soup, selector, effective_niche_id)
                if products:
                    log.info(
                        "hotmart_scanner.scan_complete",
                        niche=niche_slug,
                        platform_slug=platform_slug,
                        selector_used=selector,
                        count=len(products),
                    )
                    return products

        # All selectors failed → schema drift
        log.warning(
            "hotmart_scanner.schema_drift",
            alert="schema_drift",
            niche=niche_slug,
            platform_slug=platform_slug,
            url=url,
            selectors_tried=_SELECTORS_ORDERED,
        )
        return []


async def run_hotmart_scan(config: dict) -> None:
    """Top-level coroutine invoked by the APScheduler job.

    Iterates over niches in config that have a 'hotmart' platform key,
    scans each, and saves results to the DB.

    Args:
        config: Loaded config dict (from load_config()).
    """
    from mis.db import get_db, run_migrations
    from mis.scanner import save_batch_with_alerts

    db_path = config.get("settings", {}).get("db_path", "mis.db")

    for niche in config.get("niches", []):
        niche_slug = niche.get("slug", "")
        platforms = niche.get("platforms", {})
        platform_slug = platforms.get("hotmart")
        if not platform_slug:
            continue

        niche_id = niche.get("id", 0)

        try:
            async with HotmartScanner() as scanner:
                products = await scanner.scan_niche(niche_slug, platform_slug, niche_id=niche_id)

            if products:
                db = get_db(db_path)
                save_batch_with_alerts(db, db_path, products)
                log.info(
                    "hotmart_scanner.job.complete",
                    niche=niche_slug,
                    saved=len(products),
                )
        except Exception as exc:
            log.error(
                "hotmart_scanner.job.error",
                niche=niche_slug,
                error=str(exc),
            )
