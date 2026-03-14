"""BaseScraper — async HTTP scraper base class.

All platform scrapers in the MIS system subclass this.
Provides fetch() via httpx (SSR/JSON endpoints) and fetch_spa() via Playwright (JS SPAs).

Long-lived: one instance per scraping job. Use as async context manager.
"""
import asyncio
import time
from typing import Optional

import httpx
import structlog
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from .exceptions import ScraperError

# Configure structlog JSON output
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)
log = structlog.get_logger()

# Per-domain delays (seconds)
DOMAIN_DELAYS: dict[str, float] = {
    "hotmart.com": 2.0,
    "kiwify.com.br": 2.0,
    "clickbank.com": 2.0,
}
DEFAULT_DELAY: float = 2.0

# Module-level semaphore registry — populated lazily per domain
_SEMAPHORE: dict[str, asyncio.Semaphore] = {}


class BaseScraper:
    """Base class for all MIS scrapers.

    Provides:
        fetch(url)      -> str  — SSR pages and JSON endpoints via httpx
        fetch_spa(url)  -> str  — JS-rendered SPAs via Playwright + stealth

    Usage:
        async with BaseScraper() as scraper:
            html = await scraper.fetch("https://example.com")
    """

    def __init__(self, proxy_url: Optional[str] = None) -> None:
        self._proxy = proxy_url
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "BaseScraper":
        self._client = httpx.AsyncClient(
            http2=True,
            follow_redirects=True,
            timeout=httpx.Timeout(30.0),
            proxy=self._proxy,
        )
        return self

    async def __aexit__(self, *_) -> None:
        if self._client is not None:
            await self._client.aclose()

    def _get_semaphore(self, domain: str) -> asyncio.Semaphore:
        """Return the Semaphore for this domain, creating it lazily."""
        if domain not in _SEMAPHORE:
            _SEMAPHORE[domain] = asyncio.Semaphore(1)
        return _SEMAPHORE[domain]

    def _build_headers(self) -> dict[str, str]:
        """Return realistic HTTP headers with a rotated User-Agent."""
        from fake_useragent import UserAgent
        ua = UserAgent()
        return {
            "User-Agent": ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
        }

    async def fetch(self, url: str) -> str:
        """Fetch a URL via httpx async. Retries up to 3 times with exponential backoff.

        Raises:
            ScraperError: After all retries exhausted.
        """
        domain = httpx.URL(url).host
        delay = DOMAIN_DELAYS.get(domain, DEFAULT_DELAY)

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type(
                (httpx.HTTPStatusError, httpx.HTTPError, httpx.TimeoutException)
            ),
            reraise=True,
        )
        async def _do_fetch() -> str:
            async with self._get_semaphore(domain):
                headers = self._build_headers()
                t0 = time.monotonic()
                response = await self._client.get(url, headers=headers)
                response.raise_for_status()
                duration_ms = int((time.monotonic() - t0) * 1000)
                log.info(
                    "fetch.ok",
                    url=url,
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                    domain=domain,
                )
                await asyncio.sleep(delay)
                return response.text

        try:
            return await _do_fetch()
        except (httpx.HTTPStatusError, httpx.HTTPError, httpx.TimeoutException) as exc:
            log.error(
                "fetch.failed",
                url=url,
                domain=domain,
                exception_type=type(exc).__name__,
                last_error=str(exc),
            )
            raise ScraperError(url=url, attempts=3, cause=exc)

    async def fetch_spa(self, url: str) -> str:
        """Fetch a JS-rendered page via Playwright + playwright-stealth.

        stealth_async() is called BEFORE page.goto() to suppress automation fingerprints.

        Raises:
            ScraperError: After all retries exhausted.
        """
        from playwright.async_api import async_playwright
        from playwright_stealth import stealth_async

        domain = httpx.URL(url).host
        delay = DOMAIN_DELAYS.get(domain, DEFAULT_DELAY)

        async with self._get_semaphore(domain):
            async with async_playwright() as pw:
                browser = await pw.chromium.launch(
                    proxy={"server": self._proxy} if self._proxy else None
                )
                try:
                    page = await browser.new_page()
                    await stealth_async(page)
                    await page.goto(url, wait_until="networkidle")
                    content = await page.content()
                finally:
                    await browser.close()
            await asyncio.sleep(delay)
            return content
