"""Platform scanner abstractions for MIS.

Provides:
- Product dataclass with all required and optional fields
- PlatformScanner ABC extending BaseScraper with abstract scan_niche()
- run_all_scanners() coroutine that runs all configured scanners in parallel
"""
from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

import structlog

log = structlog.get_logger(__name__)


@dataclass
class Product:
    """A scraped product from any platform.

    Mandatory fields (6):
        external_id: Platform-specific unique identifier (slug or ID string)
        title:       Product display name
        url:         Absolute URL to the product page
        platform_id: FK to platforms table
        niche_id:    FK to niches table
        rank:        1-based position in the ranking list (int)

    Optional fields (4):
        price:          Selling price in local currency (float or None)
        commission_pct: Affiliate commission percentage (float or None)
        rating:         Average user rating (float or None)
        thumbnail_url:  URL of the product thumbnail image (str or None)
    """

    external_id: str
    title: str
    url: str
    platform_id: int
    niche_id: int
    rank: int
    price: Optional[float] = None
    commission_pct: Optional[float] = None
    rating: Optional[float] = None
    thumbnail_url: Optional[str] = None


class PlatformScanner(ABC):
    """Abstract base class for platform-specific product scanners.

    Inherits from BaseScraper (via lazy import to avoid circular imports).
    Concrete subclasses must implement scan_niche().

    Usage:
        async with KiwifyScanner() as scanner:
            products = await scanner.scan_niche("emagrecimento", "saude")
    """

    def __init__(self, proxy_url: Optional[str] = None) -> None:
        # Lazy import to avoid circular dependency issues
        from .base_scraper import BaseScraper
        # Re-use BaseScraper init by composition rather than inheritance
        # to avoid MRO issues with ABC + BaseScraper
        self._base = BaseScraper(proxy_url=proxy_url)

    async def __aenter__(self) -> "PlatformScanner":
        await self._base.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self._base.__aexit__(*args)

    async def fetch(self, url: str) -> str:
        """Delegate to BaseScraper.fetch() with retry + rate limiting."""
        return await self._base.fetch(url)

    async def fetch_spa(self, url: str) -> str:
        """Delegate to BaseScraper.fetch_spa() for Playwright-rendered pages."""
        return await self._base.fetch_spa(url)

    @abstractmethod
    async def scan_niche(self, niche_slug: str, platform_slug: str) -> list[Product]:
        """Scan a niche category on this platform and return ranked products.

        Args:
            niche_slug:    The MIS niche slug (e.g. "emagrecimento")
            platform_slug: The platform-specific category slug (e.g. "saude")

        Returns:
            List of Product dataclasses, ordered by rank (rank=1 is top).
            Returns empty list on schema drift or any unrecoverable error.
        """
        ...


async def run_all_scanners(config: dict) -> dict[str, list[Product]]:
    """Run all configured platform scanners in parallel.

    Iterates over niches in config, launching one coroutine per (niche, platform)
    pair using asyncio.gather(return_exceptions=True). A failure in one platform
    does not cancel others.

    Niches without a 'platforms' block are skipped with a warning.

    Args:
        config: Loaded config dict (from load_config()).

    Returns:
        Dict mapping "<niche_slug>.<platform_slug>" to list[Product].
        Keys with exceptions map to empty lists (logged at ERROR level).
    """
    # Lazy imports to avoid circular dependency
    from .scanners.kiwify import KiwifyScanner
    from .scanners.hotmart import HotmartScanner
    from .scanners.clickbank import ClickBankScanner

    SCANNER_MAP = {
        "kiwify": KiwifyScanner,
        "hotmart": HotmartScanner,
        "clickbank": ClickBankScanner,
    }

    niches = config.get("niches", [])
    settings = config.get("settings", {})
    proxy_url: Optional[str] = settings.get("proxy_url") or None

    tasks: list[tuple[str, asyncio.Task]] = []

    async def _run_one(
        scanner_cls,
        niche_slug: str,
        platform_slug: str,
        key: str,
    ) -> tuple[str, list[Product]]:
        async with scanner_cls(proxy_url=proxy_url) as scanner:
            products = await scanner.scan_niche(niche_slug, platform_slug)
        return key, products

    coroutines = []
    keys = []

    for niche in niches:
        niche_slug = niche.get("slug", "")
        platforms = niche.get("platforms")
        if not platforms:
            log.warning(
                "scanner.niche.no_platforms",
                niche=niche_slug,
            )
            continue
        for platform_name, platform_slug in platforms.items():
            scanner_cls = SCANNER_MAP.get(platform_name)
            if scanner_cls is None:
                log.warning(
                    "scanner.platform.not_implemented",
                    platform=platform_name,
                    niche=niche_slug,
                )
                continue
            key = f"{niche_slug}.{platform_name}"
            keys.append(key)
            coroutines.append(
                _run_one(scanner_cls, niche_slug, platform_slug, key)
            )

    results_raw = await asyncio.gather(*coroutines, return_exceptions=True)

    output: dict[str, list[Product]] = {}
    for key, result in zip(keys, results_raw):
        if isinstance(result, Exception):
            log.error(
                "scanner.run_all.platform_failed",
                key=key,
                error=str(result),
            )
            output[key] = []
        else:
            _, products = result
            output[key] = products

    return output
