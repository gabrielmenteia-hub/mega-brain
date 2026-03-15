"""Tests for SalesPageScraper (SPY-01 + SPY-03).

Coverage:
- SPY-01: extract copy fields (headlines, sub_headlines, arguments, ctas, narrative_structure)
- SPY-03: extract offer fields (price, bonuses, guarantees) — same call as SPY-01
- SPA fallback when fetch() raises ScraperError
- Text truncation at 50,000 chars
- ValueError propagation when LLM returns non-JSON
"""
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from mis.spies.sales_page import SalesPageScraper, MAX_TEXT_CHARS
from mis.exceptions import ScraperError

# --- Fixtures paths ---
_FIXTURES = Path(__file__).parent / "fixtures"
_HTML_FIXTURE = _FIXTURES / "sales_page" / "hotmart_sample.html"
_LLM_FIXTURE = _FIXTURES / "llm_responses" / "sales_page_extract.json"


@pytest.fixture
def sample_html() -> str:
    return _HTML_FIXTURE.read_text(encoding="utf-8")


@pytest.fixture
def llm_response_json() -> str:
    """Raw JSON string as returned by LLM (no fencing)."""
    return _LLM_FIXTURE.read_text(encoding="utf-8").strip()


@pytest.fixture
def llm_response_dict(llm_response_json) -> dict:
    return json.loads(llm_response_json)


def _make_llm_response(text: str):
    """Build a mock Anthropic API response object."""
    content_block = MagicMock()
    content_block.text = text
    response = MagicMock()
    response.content = [content_block]
    return response


@pytest.mark.asyncio
async def test_extract_copy_happy_path(sample_html, llm_response_json, llm_response_dict):
    """extract() returns copy fields from fixture HTML via mocked LLM."""
    async with SalesPageScraper() as spy:
        with patch.object(spy, "fetch", new=AsyncMock(return_value=sample_html)):
            with patch("mis.spies.sales_page.AsyncAnthropic") as mock_client_cls:
                mock_client = MagicMock()
                mock_client_cls.return_value = mock_client
                mock_client.messages.create = AsyncMock(
                    return_value=_make_llm_response(llm_response_json)
                )

                result = await spy.extract("https://example.com/sales-page")

    assert result["headlines"], "headlines must not be empty"
    assert result["sub_headlines"], "sub_headlines must not be empty"
    assert result["arguments"], "arguments must not be empty"
    assert result["ctas"], "ctas must not be empty"
    assert result["narrative_structure"], "narrative_structure must not be empty"
    # Verify actual content from fixture
    assert result["headlines"] == llm_response_dict["headlines"]
    assert result["ctas"] == llm_response_dict["ctas"]


@pytest.mark.asyncio
async def test_extract_offer_fields(sample_html, llm_response_json, llm_response_dict):
    """extract() returns offer fields (SPY-03) in the same call as copy (SPY-01)."""
    async with SalesPageScraper() as spy:
        with patch.object(spy, "fetch", new=AsyncMock(return_value=sample_html)):
            with patch("mis.spies.sales_page.AsyncAnthropic") as mock_client_cls:
                mock_client = MagicMock()
                mock_client_cls.return_value = mock_client
                mock_client.messages.create = AsyncMock(
                    return_value=_make_llm_response(llm_response_json)
                )

                result = await spy.extract("https://example.com/sales-page")

    assert result["price"] == llm_response_dict["price"]
    assert len(result["bonuses"]) > 0, "bonuses must not be empty"
    assert len(result["guarantees"]) > 0, "guarantees must not be empty"


@pytest.mark.asyncio
async def test_spa_fallback(sample_html, llm_response_json):
    """When fetch() raises ScraperError, fetch_spa() is called automatically."""
    async with SalesPageScraper() as spy:
        with patch.object(spy, "fetch", new=AsyncMock(side_effect=ScraperError("https://example.com/spa-page", 3, ConnectionError("blocked")))):
            with patch.object(spy, "fetch_spa", new=AsyncMock(return_value=sample_html)) as mock_spa:
                with patch("mis.spies.sales_page.AsyncAnthropic") as mock_client_cls:
                    mock_client = MagicMock()
                    mock_client_cls.return_value = mock_client
                    mock_client.messages.create = AsyncMock(
                        return_value=_make_llm_response(llm_response_json)
                    )

                    result = await spy.extract("https://example.com/spa-page")

    mock_spa.assert_called_once_with("https://example.com/spa-page")
    assert "headlines" in result


@pytest.mark.asyncio
async def test_text_truncated(llm_response_json):
    """When HTML results in text > 50,000 chars, the LLM receives truncated text."""
    # Generate HTML longer than MAX_TEXT_CHARS after conversion
    long_html = "<p>" + "A" * (MAX_TEXT_CHARS + 10_000) + "</p>"

    captured_content = []

    async def capture_create(**kwargs):
        # Capture the 'content' field of the user message
        messages = kwargs.get("messages", [])
        if messages:
            captured_content.append(messages[0]["content"])
        return _make_llm_response(llm_response_json)

    async with SalesPageScraper() as spy:
        with patch.object(spy, "fetch", new=AsyncMock(return_value=long_html)):
            with patch("mis.spies.sales_page.AsyncAnthropic") as mock_client_cls:
                mock_client = MagicMock()
                mock_client_cls.return_value = mock_client
                mock_client.messages.create = AsyncMock(side_effect=capture_create)

                await spy.extract("https://example.com/long-page")

    assert captured_content, "LLM must have been called"
    assert len(captured_content[0]) <= MAX_TEXT_CHARS, (
        f"Text sent to LLM ({len(captured_content[0])} chars) exceeds MAX_TEXT_CHARS ({MAX_TEXT_CHARS})"
    )


@pytest.mark.asyncio
async def test_json_parse_error_propagates(sample_html):
    """When LLM returns non-JSON text, extract() raises ValueError with clear message."""
    not_json = "Aqui está minha análise da página de vendas: A headline principal é muito impactante..."

    async with SalesPageScraper() as spy:
        with patch.object(spy, "fetch", new=AsyncMock(return_value=sample_html)):
            with patch("mis.spies.sales_page.AsyncAnthropic") as mock_client_cls:
                mock_client = MagicMock()
                mock_client_cls.return_value = mock_client
                mock_client.messages.create = AsyncMock(
                    return_value=_make_llm_response(not_json)
                )

                with pytest.raises(ValueError, match="LLM retornou texto não-JSON"):
                    await spy.extract("https://example.com/sales-page")
