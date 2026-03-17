"""JVZoo marketplace scanner (SSR-only, sem Playwright).

Detects Incapsula bot detection via HTTP status ou corpo HTML.
Platform ID: 10 (JVZOO_PLATFORM_ID de mis.platform_ids).

Rank semantics: gravity-based sales velocity (posicao 1-based na lista de resultados).
URL padrao: https://www.jvzoomarket.com/listings?category={platform_slug}&sort=sales
"""
from __future__ import annotations

import re
from typing import Optional

import structlog

from mis.scanner import PlatformScanner, Product
from mis.platform_ids import JVZOO_PLATFORM_ID
from mis.exceptions import ScraperError

log = structlog.get_logger(__name__)

JVZOO_BASE_URL = "https://www.jvzoomarket.com"


class JVZooScanner(PlatformScanner):
    """Scanner para JVZoo marketplace (SSR-only).

    Usa fetch() HTTP simples — JVZoo renderiza HTML no servidor.
    Detecta bloqueio Incapsula via status 403/503 (ScraperError) ou
    via corpo HTML contendo 'incapsula' ou 'incident id'.

    Rank semantics: gravity (posicao 1-based por volume de vendas).
    """

    async def scan_niche(
        self, niche_slug: str, platform_slug: str, niche_id: int = 0
    ) -> list[Product]:
        """Scan JVZoo listings for a category and return ranked products.

        Args:
            niche_slug:    MIS niche slug (e.g. "marketing-digital")
            platform_slug: JVZoo category ID (e.g. "84")
            niche_id:      FK to niches table (default 0 for tests)

        Returns:
            List of Product sorted by rank (1-based). Empty list on bot detection or error.
        """
        url = f"{JVZOO_BASE_URL}/listings?category={platform_slug}&sort=sales"
        try:
            html = await self.fetch(url)
        except ScraperError:
            log.warning(
                "jvzoo_scanner.bot_detected",
                alert="bot_detected",
                niche=niche_slug,
                reason="http_error",
            )
            return []

        if "incapsula" in html.lower() or "incident id" in html.lower():
            log.warning(
                "jvzoo_scanner.bot_detected",
                alert="bot_detected",
                niche=niche_slug,
                reason="incapsula_challenge_page",
            )
            return []

        return self._parse_listings(html, niche_id)

    def _parse_listings(self, html: str, niche_id: int) -> list[Product]:
        """Parse JVZoo listings HTML and return Product list.

        Args:
            html:     Raw HTML from JVZoo listings page
            niche_id: FK to niches table

        Returns:
            List of Product sorted by rank (1-based, gravity order).
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        listings = soup.find_all("div", class_="product-listing")
        products: list[Product] = []

        for rank, listing in enumerate(listings, start=1):
            link = listing.find("a", href=lambda h: h and "marketframe?pid=" in h)
            if not link:
                continue

            href = link.get("href", "")
            pid_match = re.search(r"pid=(\d+)", href)
            if not pid_match:
                continue

            external_id = pid_match.group(1)
            title = link.get_text(strip=True) or external_id

            price_tag = listing.find("span", class_="price")
            price: Optional[float] = None
            if price_tag:
                try:
                    price = float(
                        price_tag.get_text(strip=True).replace("$", "").replace(",", "")
                    )
                except (ValueError, AttributeError):
                    price = None

            products.append(
                Product(
                    external_id=external_id,
                    title=title,
                    url=f"https://www.jvzoomarket.com{href}",
                    platform_id=JVZOO_PLATFORM_ID,
                    niche_id=niche_id,
                    rank=rank,
                    price=price,
                )
            )

        return products
