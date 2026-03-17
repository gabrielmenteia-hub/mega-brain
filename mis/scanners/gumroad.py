"""Gumroad marketplace scanner (SPA with scroll loop).

Uses Playwright + playwright-stealth to render the discover page,
scrolling until product count stabilizes (2 consecutive rounds unchanged).

Platform ID: 11 (GUMROAD_PLATFORM_ID from mis.platform_ids).
Rank semantics: positional (1-based order in discover results).
URL pattern: https://gumroad.com/discover?sort=most_reviewed&tags={platform_slug}
"""
from __future__ import annotations

import re
from typing import Optional

import structlog

from mis.scanner import PlatformScanner, Product
from mis.platform_ids import GUMROAD_PLATFORM_ID

log = structlog.get_logger(__name__)

GUMROAD_DISCOVER_URL = "https://gumroad.com/discover"


class GumroadScanner(PlatformScanner):
    """Scanner para Gumroad discover page (SPA com scroll infinito).

    Usa _scan_with_scroll() que gerencia Playwright diretamente para realizar
    scroll loop interativo. PLAYWRIGHT_SEMAPHORE e adquirido explicitamente
    (mesmo semaphore global do base_scraper) — protecao OOM mantida.

    Rank semantics: positional (posicao 1-based na lista de descoberta).
    """

    async def scan_niche(
        self, niche_slug: str, platform_slug: str, niche_id: int = 0
    ) -> list[Product]:
        """Scan Gumroad discover for a tag and return ranked products.

        Args:
            niche_slug:    MIS niche slug (e.g. "marketing-digital")
            platform_slug: Gumroad tag (e.g. "marketing")
            niche_id:      FK to niches table (default 0 for tests)

        Returns:
            List of Product sorted by rank (1-based). Empty list on error.
        """
        url = f"{GUMROAD_DISCOVER_URL}?sort=most_reviewed&tags={platform_slug}"
        try:
            html = await self._scan_with_scroll(url)
        except Exception as exc:
            log.warning(
                "gumroad_scanner.marketplace_unavailable",
                alert="marketplace_unavailable",
                niche=niche_slug,
                error=str(exc),
            )
            return []
        return self._parse_html(html, niche_id)

    async def _scan_with_scroll(self, url: str, limit: int = 50) -> str:
        """STUB: delegates to fetch_spa(). Will be replaced with scroll loop in GREEN."""
        return await self.fetch_spa(url)

    def _parse_html(self, html: str, niche_id: int) -> list[Product]:
        """STUB: returns empty list. Will be implemented in GREEN."""
        return []
