"""SalesPageScraper — platform-agnostic sales page intelligence extractor.

Extracts copy (headlines, arguments, CTAs, narrative structure) and offer
structure (price, bonuses, guarantees, upsells, downsells) from any sales
page URL using an LLM as the universal parser.

Features:
- httpx fetch with automatic SPA fallback via Playwright (inherited from BaseScraper)
- HTML → clean text via markdownify before sending to LLM
- Text truncation to MAX_TEXT_CHARS to control token usage
- Tenacity retry (3 attempts) on LLM connection/rate-limit errors
- Raises ValueError with clear message if LLM returns non-JSON

Usage:
    async with SalesPageScraper() as spy:
        data = await spy.extract("https://hotmart.com/product/...")
        # data["headlines"], data["price"], data["bonuses"], etc.
"""
import json
import os
from pathlib import Path

import markdownify
import structlog
from anthropic import APIConnectionError, AsyncAnthropic, RateLimitError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from ..base_scraper import BaseScraper
from ..exceptions import ScraperError

log = structlog.get_logger()

MAX_TEXT_CHARS = 50_000
_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "sales_page_extractor.md"


class SalesPageScraper(BaseScraper):
    """Platform-agnostic spy that extracts copy and offer from any sales page.

    Inherits HTTP/Playwright/stealth from BaseScraper. Uses LLM as the sole
    parser — no platform-specific selectors.
    """

    async def extract(self, url: str) -> dict:
        """Extract copy and offer structure from a sales page URL.

        Fetches the page HTML, converts to clean text, truncates if needed,
        and calls the LLM to extract structured data.

        Args:
            url: Full URL of the sales page to analyze.

        Returns:
            dict with keys: headlines, sub_headlines, arguments, ctas,
            narrative_structure, price, bonuses, guarantees, upsells, downsells.

        Raises:
            ValueError: If LLM returns non-JSON response.
            ScraperError: If both httpx and Playwright fetch fail.
        """
        log.info("sales_page.fetch_start", url=url)

        # 1. Fetch HTML — httpx first, SPA fallback via Playwright
        try:
            html = await self.fetch(url)
        except ScraperError:
            log.info("sales_page.spa_fallback", url=url)
            html = await self.fetch_spa(url)

        # 2. Convert HTML → clean Markdown text and truncate
        clean = markdownify.markdownify(
            html,
            strip=["script", "style", "noscript", "meta", "head", "aside", "footer", "nav"],
            heading_style=markdownify.ATX,
        )
        clean = clean[:MAX_TEXT_CHARS]
        log.info("sales_page.text_prepared", chars=len(clean), url=url)

        # 3. Call LLM with retry
        result_text = await self._call_llm(clean)

        # 4. Parse JSON — raise ValueError if LLM returned non-JSON
        try:
            return json.loads(result_text)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"LLM retornou texto não-JSON: {result_text[:200]}"
            ) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((APIConnectionError, RateLimitError)),
        reraise=True,
    )
    async def _call_llm(self, content: str) -> str:
        """Call the Anthropic API with the sales page text.

        Args:
            content: Cleaned, truncated text of the sales page.

        Returns:
            Raw text response from the LLM (expected to be JSON).
        """
        system_prompt = _PROMPT_PATH.read_text(encoding="utf-8")
        client = AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
        response = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": content}],
        )
        return response.content[0].text
