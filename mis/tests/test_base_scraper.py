"""Tests for mis.base_scraper — BaseScraper class.

Coverage: FOUND-02
"""
import asyncio
import pytest
import respx
import httpx
from mis.base_scraper import BaseScraper
from mis.exceptions import ScraperError


@pytest.mark.asyncio
async def test_fetch_success():
    with respx.mock:
        respx.get("https://example.com").mock(return_value=httpx.Response(200, text="hello"))
        async with BaseScraper() as s:
            result = await s.fetch("https://example.com")
        assert "hello" in result


@pytest.mark.asyncio
async def test_fetch_retries_on_429():
    with respx.mock:
        respx.get("https://example.com").mock(side_effect=[
            httpx.Response(429),
            httpx.Response(429),
            httpx.Response(200, text="success"),
        ])
        async with BaseScraper() as s:
            result = await s.fetch("https://example.com")
        assert "success" in result


@pytest.mark.asyncio
async def test_rate_limiting(monkeypatch):
    sleep_calls = []

    async def fake_sleep(t):
        sleep_calls.append(t)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    with respx.mock:
        respx.get("https://example.com").mock(return_value=httpx.Response(200, text="ok"))
        async with BaseScraper() as s:
            await s.fetch("https://example.com")
    assert len(sleep_calls) >= 1


@pytest.mark.asyncio
async def test_headers_not_default():
    with respx.mock:
        route = respx.get("https://example.com").mock(return_value=httpx.Response(200, text="ok"))
        async with BaseScraper() as s:
            await s.fetch("https://example.com")
        ua = route.calls.last.request.headers["user-agent"]
        assert "python-httpx" not in ua
        assert len(ua) > 0


@pytest.mark.asyncio
async def test_scraper_error_raised():
    with respx.mock:
        respx.get("https://example.com").mock(return_value=httpx.Response(500))
        async with BaseScraper() as s:
            with pytest.raises(ScraperError) as exc_info:
                await s.fetch("https://example.com")
        assert exc_info.value.url == "https://example.com"
        assert exc_info.value.attempts >= 1


@pytest.mark.asyncio
async def test_client_closed_on_exit():
    with respx.mock:
        async with BaseScraper() as s:
            pass
        assert s._client.is_closed
