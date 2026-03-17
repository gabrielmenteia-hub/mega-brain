"""AppSumo marketplace scanner (SSR-first with Playwright fallback).

Tries SSR fetch() first — AppSumo uses Next.js with __NEXT_DATA__ server-side rendering.
Falls back to fetch_spa() (Playwright) when SSR returns empty or fails.

Platform ID: 12 (APPSUMO_PLATFORM_ID from mis.platform_ids).
Rank semantics: positional (1-based order in browse results).
URL pattern: https://appsumo.com/browse/software/{platform_slug}/
"""
from __future__ import annotations

import json
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
        """Parse AppSumo browse HTML and return Product list.

        Attempt 1: Extract __NEXT_DATA__ JSON embedded by Next.js SSR.
        Attempt 2 (CSS fallback): Extract product links with /products/ in href.

        Args:
            html:     Raw HTML from AppSumo browse page
            niche_id: FK to niches table

        Returns:
            List of Product sorted by rank (1-based).
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        products: list[Product] = []

        # Attempt 1: __NEXT_DATA__ JSON (Next.js SSR)
        script_tag = soup.find("script", id="__NEXT_DATA__")
        if script_tag and script_tag.string:
            try:
                data = json.loads(script_tag.string)
                products_raw = (
                    data.get("props", {})
                    .get("pageProps", {})
                    .get("products", [])
                )
                if products_raw:
                    for rank, item in enumerate(products_raw, start=1):
                        external_id = item.get("slug", "")
                        if not external_id:
                            continue
                        title = item.get("name", external_id)
                        # deal_price preferred, fallback to price, then None
                        raw_price = item.get("deal_price") or item.get("price")
                        price: Optional[float] = float(raw_price) if raw_price is not None else None
                        item_url = item.get("url", "")
                        full_url = APPSUMO_BASE_URL + item_url if item_url else f"{APPSUMO_BASE_URL}/products/{external_id}/"
                        products.append(
                            Product(
                                external_id=external_id,
                                title=title,
                                url=full_url,
                                platform_id=APPSUMO_PLATFORM_ID,
                                niche_id=niche_id,
                                rank=rank,
                                price=price,
                            )
                        )
                    return products
            except (json.JSONDecodeError, KeyError, TypeError):
                pass  # Fall through to CSS fallback

        # Attempt 2: CSS fallback — links with /products/ in href
        links = soup.find_all(
            "a", href=lambda h: h and "/products/" in (h or "")
        )
        seen_slugs: set[str] = set()
        rank = 1
        for link in links:
            href = link.get("href", "")
            # Extract slug from /products/{slug}/ path
            parts = [p for p in href.strip("/").split("/") if p]
            if len(parts) < 2 or parts[-2] != "products":
                # Try to find products at any position
                try:
                    prod_idx = parts.index("products")
                    if prod_idx + 1 < len(parts):
                        slug = parts[prod_idx + 1]
                    else:
                        continue
                except ValueError:
                    continue
            else:
                slug = parts[-1]

            if not slug or slug in seen_slugs:
                continue
            seen_slugs.add(slug)

            title = link.get_text(strip=True) or slug
            full_url = APPSUMO_BASE_URL + href if href.startswith("/") else href

            products.append(
                Product(
                    external_id=slug,
                    title=title,
                    url=full_url,
                    platform_id=APPSUMO_PLATFORM_ID,
                    niche_id=niche_id,
                    rank=rank,
                    price=None,  # No price data in CSS fallback
                )
            )
            rank += 1

        return products
