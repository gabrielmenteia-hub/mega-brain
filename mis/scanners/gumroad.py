"""Gumroad marketplace scanner (SPA with scroll loop).

Uses Playwright + playwright-stealth directly (not self.fetch_spa()) because the scroll
loop needs the page object to call page.evaluate(), page.wait_for_timeout() and
page.query_selector_all() at each iteration. fetch_spa() encapsulates the full browser
lifecycle and returns only the final HTML — without exposing the page for intermediate
manipulation. PLAYWRIGHT_SEMAPHORE is acquired explicitly (same global semaphore) so
OOM protection remains identical to fetch_spa().

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
        """Fetch Gumroad SPA via Playwright with scroll loop.

        Scrolls until product count stabilizes (2 consecutive rounds unchanged = done).
        Acquires PLAYWRIGHT_SEMAPHORE directly for OOM protection (same as fetch_spa()).

        NOTE: Uses Playwright directly (not self.fetch_spa()) because scroll loop needs
        the page object for page.evaluate(), page.wait_for_timeout() and
        page.query_selector_all() at each iteration.
        """
        from mis.base_scraper import PLAYWRIGHT_SEMAPHORE
        from playwright.async_api import async_playwright
        from playwright_stealth import Stealth as _PlaywrightStealth

        async with PLAYWRIGHT_SEMAPHORE:
            async with async_playwright() as pw:
                browser = await pw.chromium.launch()
                try:
                    page = await browser.new_page()
                    await _PlaywrightStealth().apply_stealth_async(page)
                    await page.goto(url, wait_until="networkidle")
                    prev_count = 0
                    stable_rounds = 0
                    for _ in range(20):  # max 20 scrolls
                        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        await page.wait_for_timeout(1500)
                        items = await page.query_selector_all(
                            "article.product-card, [data-component-name='DiscoverProduct'], article"
                        )
                        curr_count = len(items)
                        if curr_count >= limit:
                            break
                        if curr_count == prev_count:
                            stable_rounds += 1
                            if stable_rounds >= 2:  # 2 rounds sem crescimento = fim
                                break
                        else:
                            stable_rounds = 0
                        prev_count = curr_count
                    content = await page.content()
                finally:
                    await browser.close()
        return content

    def _parse_html(self, html: str, niche_id: int) -> list[Product]:
        """Parse Gumroad discover HTML and return Product list.

        Selects article elements, preferring those with class 'product-card'.
        Extracts: link (gumroad.com/l/), external_id (slug), title (h3), price (span.price).

        Args:
            html:     Raw HTML from Gumroad discover page (post-scroll)
            niche_id: FK to niches table

        Returns:
            List of Product sorted by rank (1-based).
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")

        # Try specific selector first, fallback to all articles
        articles = soup.find_all("article", class_="product-card")
        if not articles:
            articles = soup.find_all("article")

        products: list[Product] = []
        rank = 1

        for tag in articles:
            link = tag.find("a", href=lambda h: h and "gumroad.com/l/" in (h or ""))
            if not link:
                continue

            href = link.get("href", "")
            if not href:
                continue

            # Extract slug from URL path (last segment)
            external_id = href.rstrip("/").split("/")[-1]
            if not external_id:
                continue

            # Title from h3 or fallback to link text
            h3 = tag.find("h3")
            title = (
                h3.get_text(strip=True)
                if h3
                else link.get_text(strip=True)
            ) or external_id

            # Price parsing
            price_tag = tag.find("span", class_="price")
            price: Optional[float] = None
            if price_tag:
                price_text = price_tag.get_text(strip=True)
                if price_text.lower() == "free":
                    price = 0.0
                else:
                    cleaned = re.sub(r"[^0-9.]", "", price_text)
                    if cleaned:
                        try:
                            price = float(cleaned)
                        except ValueError:
                            price = None

            products.append(
                Product(
                    external_id=external_id,
                    title=title,
                    url=href,
                    platform_id=GUMROAD_PLATFORM_ID,
                    niche_id=niche_id,
                    rank=rank,
                    price=price,
                )
            )
            rank += 1

        return products
