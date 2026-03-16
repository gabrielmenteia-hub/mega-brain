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


@pytest.mark.asyncio
async def test_proxy_rotation_selects_from_list():
    """Verifica que proxy_list com 3 proxies resulta em selecao aleatoria diversa."""
    proxies = ["http://proxy1:8080", "http://proxy2:8080", "http://proxy3:8080"]
    scraper = BaseScraper(proxy_list=proxies)
    selected = set()
    for _ in range(20):
        p = scraper._select_proxy()
        selected.add(p)
    assert len(selected) > 1, "Esperava mais de 1 proxy unico em 20 draws"


@pytest.mark.asyncio
async def test_proxy_rotation_no_proxy_returns_none():
    """Verifica que sem proxy_list, _select_proxy retorna None."""
    scraper = BaseScraper()
    assert scraper._select_proxy() is None


@pytest.mark.asyncio
async def test_fetch_spa_uses_select_proxy_not_self_proxy():
    """fetch_spa() must use _select_proxy() for proxy rotation, not self._proxy directly.

    When proxy_list is provided, fetch_spa() must call _select_proxy() and pass the
    result to chromium.launch(), not use self._proxy (which is None when proxy_list is set).
    """
    from unittest.mock import AsyncMock, MagicMock, patch

    proxies = ["http://proxy1:8080", "http://proxy2:8080"]
    scraper = BaseScraper(proxy_list=proxies)

    # self._proxy must be None (proxy_list takes precedence)
    assert scraper._proxy is None

    captured_launch_kwargs = {}

    mock_page = AsyncMock()
    mock_page.content = AsyncMock(return_value="<html>SPA content</html>")

    mock_browser = AsyncMock()
    mock_browser.new_page = AsyncMock(return_value=mock_page)

    async def fake_launch(**kwargs):
        captured_launch_kwargs.update(kwargs)
        return mock_browser

    mock_chromium = MagicMock()
    mock_chromium.launch = fake_launch

    mock_pw = AsyncMock()
    mock_pw.__aenter__ = AsyncMock(return_value=mock_pw)
    mock_pw.__aexit__ = AsyncMock(return_value=False)
    mock_pw.chromium = mock_chromium

    mock_stealth = MagicMock()
    mock_stealth.apply_stealth_async = AsyncMock()
    with patch("mis.base_scraper.async_playwright", return_value=mock_pw), \
         patch("mis.base_scraper._PlaywrightStealth", return_value=mock_stealth), \
         patch("asyncio.sleep", new=AsyncMock()):
        await scraper.fetch_spa("https://example.com")

    # Assert proxy kwarg was set to a server from the proxy_list (not None)
    proxy_kwarg = captured_launch_kwargs.get("proxy")
    assert proxy_kwarg is not None, "proxy kwarg must not be None when proxy_list is set"
    assert "server" in proxy_kwarg
    assert proxy_kwarg["server"] in proxies
