"""Monetizze platform scanner — fallback only.

Monetizze affiliate storefront requires authentication (app.monetizze.com.br).
Returns 403 without login. Não há marketplace público acessível.

Implementa fallback puro: scan_niche() retorna [] com alert='marketplace_unavailable'.
Dados existentes no DB são marcados is_stale=True via mark_stale().
Quando marketplace for liberado: apenas reimplementar scan_niche().
"""
from __future__ import annotations

import structlog

from mis.scanner import PlatformScanner, Product
from mis.platform_ids import MONETIZZE_PLATFORM_ID

log = structlog.get_logger(__name__)


class MonetizzeScanner(PlatformScanner):
    """Monetizze scanner — marketplace requer autenticação. Implementa fallback."""

    async def scan_niche(
        self,
        niche_slug: str,
        platform_slug: str,
        niche_id: int = 0,
    ) -> list[Product]:
        """Return empty list — Monetizze storefront requires authentication.

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
            "monetizze_scanner.marketplace_unavailable",
            alert="marketplace_unavailable",
            niche=niche_slug,
            platform_slug=platform_slug,
            reason=(
                "Monetizze affiliate storefront requires authentication — "
                "app.monetizze.com.br returns 403 without login"
            ),
        )
        return []
