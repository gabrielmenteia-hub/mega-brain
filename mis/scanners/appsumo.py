"""AppSumo marketplace scanner (SSR-first with Playwright fallback).

Tries SSR fetch() first — AppSumo uses Next.js with __NEXT_DATA__ server-side rendering.
Falls back to fetch_spa() (Playwright) when SSR returns empty or fails.

Platform ID: 12 (APPSUMO_PLATFORM_ID from mis.platform_ids).
Rank semantics: positional (1-based order in browse results).
URL pattern: https://appsumo.com/browse/software/{platform_slug}/
"""
from __future__ import annotations

from typing import Optional

import structlog

from mis.scanner import PlatformScanner, Product
from mis.platform_ids import APPSUMO_PLATFORM_ID
from mis.exceptions import ScraperError

log = structlog.get_logger(__name__)

APPSUMO_BASE_URL = "https://appsumo.com"


class AppSumoScanner(PlatformScanner):
    """Scanner para AppSumo marketplace (SSR-first + Playwright fallback).

    Estrategia:
      1. Tenta fetch() HTTP simples — AppSumo SSR embute __NEXT_DATA__ JSON
      2. Se SSR retornar vazio ou falhar, faz fallback para fetch_spa() (Playwright)
      3. Se ambas falharem, retorna [] com alert='marketplace_unavailable'

    Rank semantics: positional (posicao 1-based na lista de browse).
    """

    async def scan_niche(
        self, niche_slug: str, platform_slug: str, niche_id: int = 0
    ) -> list[Product]:
        """Scan AppSumo browse for a category and return ranked products.

        Args:
            niche_slug:    MIS niche slug (e.g. "marketing-digital")
            platform_slug: AppSumo category slug (e.g. "marketing-sales")
            niche_id:      FK to niches table (default 0 for tests)

        Returns:
            List of Product sorted by rank (1-based). Empty list on error.
        """
        url = f"{APPSUMO_BASE_URL}/browse/software/{platform_slug}/"
        try:
            html = await self.fetch(url)
            products = self._parse_html(html, niche_id)
            if products:
                return products
            log.info("appsumo_scanner.ssr_empty_fallback", niche=niche_slug)
        except ScraperError:
            log.info("appsumo_scanner.fetch_failed_fallback", niche=niche_slug)

        try:
            html = await self.fetch_spa(url)
            return self._parse_html(html, niche_id)
        except Exception as exc:
            log.warning(
                "appsumo_scanner.marketplace_unavailable",
                alert="marketplace_unavailable",
                niche=niche_slug,
                error=str(exc),
            )
            return []

    def _parse_html(self, html: str, niche_id: int) -> list[Product]:
        """STUB: returns empty list. Will be implemented in GREEN."""
        return []
