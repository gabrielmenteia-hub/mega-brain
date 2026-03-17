"""Eduzz platform scanner — fallback only.

Eduzz migrou para orbita.eduzz.com (SPA React). Vitrine de afiliados
requer autenticação. Não há marketplace público acessível.

Implementa fallback puro: scan_niche() retorna [] com alert='marketplace_unavailable'.
Dados existentes no DB são marcados is_stale=True via mark_stale().
Quando marketplace for liberado: apenas reimplementar scan_niche().
"""
from __future__ import annotations

import structlog

from mis.scanner import PlatformScanner, Product
from mis.platform_ids import EDUZZ_PLATFORM_ID

log = structlog.get_logger(__name__)


class EduzzScanner(PlatformScanner):
    """Eduzz scanner — marketplace requer autenticação. Implementa fallback."""

    async def scan_niche(
        self,
        niche_slug: str,
        platform_slug: str,
        niche_id: int = 0,
    ) -> list[Product]:
        """Return empty list — Eduzz marketplace requires authentication.

        Emits a structured warning log with alert='marketplace_unavailable'
        so the pipeline can detect and call mark_stale() for this platform.

        Args:
            niche_slug:    MIS niche slug (e.g. "emagrecimento")
            platform_slug: Platform-specific category slug (unused — no public URL)
            niche_id:      FK to niches table (default 0)

        Returns:
            Empty list always.
        """
        log.warning(
            "eduzz_scanner.marketplace_unavailable",
            alert="marketplace_unavailable",
            niche=niche_slug,
            platform_slug=platform_slug,
            reason=(
                "Eduzz marketplace requires authentication — "
                "orbita.eduzz.com is a React SPA with no public product listing"
            ),
        )
        return []
