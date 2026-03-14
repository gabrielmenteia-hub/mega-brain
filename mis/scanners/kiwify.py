"""Kiwify platform scanner.

Scrapes the Kiwify marketplace using SSR HTML parsing with BeautifulSoup4.
Tries multiple CSS selectors in order (primary → fallbacks) for resilience
against layout changes. Emits alert='schema_drift' via structlog when all
selectors fail.

Platform ID convention:
    1 = Hotmart
    2 = ClickBank
    3 = Kiwify  ← this scanner

Usage:
    async with KiwifyScanner() as scanner:
        products = await scanner.scan_niche("emagrecimento", "saude")
"""
from __future__ import annotations

import re
from typing import Optional
from urllib.parse import urljoin

import structlog
from bs4 import BeautifulSoup

from mis.scanner import PlatformScanner, Product

log = structlog.get_logger(__name__)

KIWIFY_PLATFORM_ID = 3
# Niche ID is looked up at runtime from the DB or passed by the caller.
# When called via run_all_scanners(), niche_id must be resolved externally.
# For standalone use (tests), niche_id defaults to 0 and should be overridden.
KIWIFY_BASE_URL = "https://kiwify.com.br"
KIWIFY_MARKETPLACE_URL = "https://kiwify.com.br/marketplace"

# Ordered selector list: primary first, fallbacks in order.
# The scanner tries each until it finds results, then stops.
SELECTORS_ORDERED = [
    # Primary: standard product card used in the known HTML structure
    "article.product-card",
    # Fallback 1: data-testid based (may appear in A/B tests or future redesigns)
    "[data-testid='product-item']",
    # Fallback 2: generic marketplace item class
    ".marketplace-item",
]


def _extract_external_id(url: str) -> str:
    """Extract external_id from a Kiwify product URL.

    Strategy: take the last non-empty path segment.
    Example: '/produto/emagreca-de-vez-pro' → 'emagreca-de-vez-pro'
             '/produto/nome-123' → 'nome-123'

    Falls back to the data-product-id attribute when available (caller's job).
    """
    parts = [p for p in url.rstrip("/").split("/") if p]
    return parts[-1] if parts else url


def _parse_price(text: str | None) -> Optional[float]:
    """Parse a Brazilian price string into float.

    Examples:
        'R$ 197,00' → 197.0
        'R$ 1.997,00' → 1997.0
        None → None
    """
    if not text:
        return None
    # Remove currency symbol and whitespace
    cleaned = re.sub(r"[R$\s]", "", text.strip())
    # Remove thousands separator (dot), replace decimal comma with dot
    cleaned = cleaned.replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_rating(text: str | None) -> Optional[float]:
    """Parse a rating string into float."""
    if not text:
        return None
    try:
        return float(text.strip())
    except ValueError:
        return None


def _extract_products_from_primary(
    soup: BeautifulSoup,
    niche_id: int,
) -> list[Product]:
    """Extract products using primary selector: article.product-card."""
    cards = soup.select("article.product-card")
    products = []
    for rank, card in enumerate(cards, start=1):
        # Try href from first anchor
        link_tag = card.find("a", href=True)
        if not link_tag:
            continue
        href = link_tag["href"]
        abs_url = urljoin(KIWIFY_BASE_URL, href)

        # external_id: prefer data-product-id attr, fallback to URL slug
        ext_id = card.get("data-product-id") or _extract_external_id(href)

        # Title: h2 inside card
        title_tag = card.find("h2")
        title = title_tag.get_text(strip=True) if title_tag else ext_id

        # Price
        price_tag = card.find(class_="product-card__price")
        price = _parse_price(price_tag.get_text(strip=True) if price_tag else None)

        # Rating
        rating_tag = card.find(class_="product-card__rating")
        rating = _parse_rating(rating_tag.get_text(strip=True) if rating_tag else None)

        # Thumbnail
        img_tag = card.find("img")
        thumbnail_url = img_tag.get("src") if img_tag else None

        products.append(
            Product(
                external_id=ext_id,
                title=title,
                url=abs_url,
                platform_id=KIWIFY_PLATFORM_ID,
                niche_id=niche_id,
                rank=rank,
                price=price,
                rating=rating,
                thumbnail_url=thumbnail_url,
            )
        )
    return products


def _extract_products_from_testid(
    soup: BeautifulSoup,
    niche_id: int,
) -> list[Product]:
    """Extract products using fallback 1 selector: [data-testid='product-item']."""
    items = soup.select("[data-testid='product-item']")
    products = []
    for rank, item in enumerate(items, start=1):
        link_tag = item.find("a", href=True)
        if not link_tag:
            continue
        href = link_tag["href"]
        abs_url = urljoin(KIWIFY_BASE_URL, href)

        ext_id = item.get("data-product-id") or _extract_external_id(href)

        # Title: h2 or first heading
        title_tag = item.find(re.compile(r"h[1-6]"))
        title = title_tag.get_text(strip=True) if title_tag else ext_id

        # Price
        price_tag = item.find(class_="price")
        price = _parse_price(price_tag.get_text(strip=True) if price_tag else None)

        products.append(
            Product(
                external_id=ext_id,
                title=title,
                url=abs_url,
                platform_id=KIWIFY_PLATFORM_ID,
                niche_id=niche_id,
                rank=rank,
                price=price,
            )
        )
    return products


def _extract_products_from_marketplace_item(
    soup: BeautifulSoup,
    niche_id: int,
) -> list[Product]:
    """Extract products using fallback 2 selector: .marketplace-item."""
    items = soup.select(".marketplace-item")
    products = []
    for rank, item in enumerate(items, start=1):
        link_tag = item.find("a", href=True)
        if not link_tag:
            continue
        href = link_tag["href"]
        abs_url = urljoin(KIWIFY_BASE_URL, href)
        ext_id = _extract_external_id(href)

        title_tag = item.find(re.compile(r"h[1-6]"))
        title = title_tag.get_text(strip=True) if title_tag else ext_id

        products.append(
            Product(
                external_id=ext_id,
                title=title,
                url=abs_url,
                platform_id=KIWIFY_PLATFORM_ID,
                niche_id=niche_id,
                rank=rank,
            )
        )
    return products


# Map selector → extractor function for the ordered fallback loop
_SELECTOR_EXTRACTORS = [
    ("article.product-card", _extract_products_from_primary),
    ("[data-testid='product-item']", _extract_products_from_testid),
    (".marketplace-item", _extract_products_from_marketplace_item),
]


class KiwifyScanner(PlatformScanner):
    """Kiwify marketplace scanner using SSR HTML + BeautifulSoup4.

    Attributes:
        KIWIFY_PLATFORM_ID: DB platform ID for Kiwify (= 3)
        niche_id:           Override per-scan; default 0 (caller must set)
    """

    def __init__(
        self,
        proxy_url: Optional[str] = None,
        niche_id: int = 0,
    ) -> None:
        super().__init__(proxy_url=proxy_url)
        self._default_niche_id = niche_id

    async def scan_niche(
        self,
        niche_slug: str,
        platform_slug: str,
        niche_id: int = 0,
    ) -> list[Product]:
        """Scan a Kiwify marketplace category and return ranked products.

        URL pattern: https://kiwify.com.br/marketplace?category={platform_slug}

        Tries selectors in SELECTORS_ORDERED order. Emits alert='schema_drift'
        and returns [] when all selectors fail.

        Never raises exceptions — errors are caught and logged.

        Args:
            niche_slug:    MIS niche slug (e.g. "emagrecimento") — used for logging
            platform_slug: Kiwify category slug (e.g. "saude")
            niche_id:      DB niche ID for the Product dataclass (0 if unknown)

        Returns:
            List of Product dataclasses ordered by rank, or [] on drift/error.
        """
        effective_niche_id = niche_id or self._default_niche_id
        url = f"{KIWIFY_MARKETPLACE_URL}?category={platform_slug}"

        try:
            html = await self.fetch(url)
        except Exception as exc:
            log.error(
                "kiwify_scanner.fetch_failed",
                niche=niche_slug,
                platform_slug=platform_slug,
                url=url,
                error=str(exc),
            )
            return []

        soup = BeautifulSoup(html, "lxml")

        # Try selectors in order, return first non-empty result
        for selector, extractor in _SELECTOR_EXTRACTORS:
            if soup.select(selector):
                products = extractor(soup, effective_niche_id)
                if products:
                    log.info(
                        "kiwify_scanner.scan_complete",
                        niche=niche_slug,
                        platform_slug=platform_slug,
                        selector_used=selector,
                        count=len(products),
                    )
                    return products

        # All selectors failed → schema drift
        log.warning(
            "kiwify_scanner.schema_drift",
            alert="schema_drift",
            niche=niche_slug,
            platform_slug=platform_slug,
            url=url,
            selectors_tried=[s for s, _ in _SELECTOR_EXTRACTORS],
        )
        return []


async def run_kiwify_scan(config: dict) -> None:
    """Top-level coroutine invoked by the APScheduler job.

    Iterates over niches in config that have a 'kiwify' platform key,
    scans each, and saves results to the DB.

    Args:
        config: Loaded config dict (from load_config()).
    """
    import structlog as _structlog
    from mis.db import get_db
    from mis.product_repository import save_batch

    _log = _structlog.get_logger(__name__)
    db_path = config.get("settings", {}).get("db_path", "mis.db")

    for niche in config.get("niches", []):
        niche_slug = niche.get("slug", "")
        platforms = niche.get("platforms", {})
        platform_slug = platforms.get("kiwify")
        if not platform_slug:
            continue

        niche_id = niche.get("id", 0)

        try:
            async with KiwifyScanner() as scanner:
                products = await scanner.scan_niche(niche_slug, platform_slug)

            if products:
                db = get_db(db_path)
                save_batch(db, products)
                _log.info(
                    "kiwify_scanner.job.complete",
                    niche=niche_slug,
                    saved=len(products),
                )
        except Exception as exc:
            _log.error(
                "kiwify_scanner.job.error",
                niche=niche_slug,
                error=str(exc),
            )
