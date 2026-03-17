"""PerfectPay platform scanner — fallback only.

PerfectPay é plataforma de checkout e gestão de pagamentos.
Não possui marketplace centralizado público — vitrine de afiliados
disponível apenas no painel autenticado (app.perfectpay.com.br).

Implementa fallback puro: scan_niche() retorna [] com alert='marketplace_unavailable'.
Dados existentes no DB são preservados e marcados is_stale=True via mark_stale().
"""
from __future__ import annotations

import structlog

from mis.scanner import PlatformScanner, Product
from mis.platform_ids import PERFECTPAY_PLATFORM_ID

log = structlog.get_logger(__name__)


class PerfectPayScanner(PlatformScanner):
    """PerfectPay scanner — plataforma de checkout sem marketplace público."""

    async def scan_niche(
        self,
        niche_slug: str,
        platform_slug: str,
        niche_id: int = 0,
    ) -> list[Product]:
        """Return empty list — PerfectPay has no public marketplace.

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
            "perfectpay_scanner.marketplace_unavailable",
            alert="marketplace_unavailable",
            niche=niche_slug,
            platform_slug=platform_slug,
            reason=(
                "PerfectPay is a checkout platform with no public marketplace — "
                "affiliate store requires authentication at app.perfectpay.com.br"
            ),
        )
        return []
