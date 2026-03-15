"""Tests for MetaAdsScraper (SPY-02).

Coverage:
- fetch_ads() retorna lista de dicts com campos corretos (com token)
- fetch_ads() retorna [] quando META_ACCESS_TOKEN ausente
- ad_reached_countries=BR sempre incluído nos params da chamada HTTP
- HTTP 4xx levanta ScraperError
- API retornando {"data": []} retorna [] sem erro
"""
import json
import os
from pathlib import Path

import httpx
import pytest
import respx

from mis.spies.meta_ads import MetaAdsScraper, META_API_URL
from mis.exceptions import ScraperError

_FIXTURE = (
    Path(__file__).parent / "fixtures" / "meta_ads" / "ads_archive_response.json"
)


@pytest.fixture
def ads_fixture() -> dict:
    return json.loads(_FIXTURE.read_text(encoding="utf-8"))


@pytest.mark.asyncio
async def test_fetch_ads_with_token(monkeypatch, ads_fixture):
    """Com token presente, retorna lista de dicts com campos page_name, ad_snapshot_url, ad_creative_bodies."""
    monkeypatch.setenv("META_ACCESS_TOKEN", "fake_token_123")

    with respx.mock:
        respx.get(META_API_URL).mock(
            return_value=httpx.Response(200, json=ads_fixture)
        )
        scraper = MetaAdsScraper()
        ads = await scraper.fetch_ads("Produto Digital X")

    assert len(ads) == 2
    assert ads[0]["page_name"] == "Produto Digital X"
    assert "ad_snapshot_url" in ads[0]
    assert "ad_creative_bodies" in ads[0]
    assert isinstance(ads[0]["ad_creative_bodies"], list)


@pytest.mark.asyncio
async def test_no_token_returns_empty(monkeypatch):
    """Quando META_ACCESS_TOKEN não está em os.environ, retorna [] graciosamente."""
    monkeypatch.delenv("META_ACCESS_TOKEN", raising=False)

    scraper = MetaAdsScraper()
    ads = await scraper.fetch_ads("Produto X")

    assert ads == []


@pytest.mark.asyncio
async def test_ad_reached_countries_always_included(monkeypatch, ads_fixture):
    """Verificar via mock que a chamada HTTP sempre inclui ad_reached_countries=BR nos params."""
    monkeypatch.setenv("META_ACCESS_TOKEN", "fake_token_456")

    captured_request = {}

    with respx.mock:
        route = respx.get(META_API_URL).mock(
            return_value=httpx.Response(200, json=ads_fixture)
        )
        scraper = MetaAdsScraper()
        await scraper.fetch_ads("Produto Y")

        assert route.called
        req = route.calls[0].request
        # URL params
        url = httpx.URL(str(req.url))
        params = dict(url.params)

    assert params.get("ad_reached_countries") == "BR", (
        f"ad_reached_countries deve ser 'BR', got: {params.get('ad_reached_countries')}"
    )


@pytest.mark.asyncio
async def test_http_error_raises_scraper_error(monkeypatch):
    """Quando httpx retorna 4xx, levanta ScraperError."""
    monkeypatch.setenv("META_ACCESS_TOKEN", "invalid_token")

    with respx.mock:
        respx.get(META_API_URL).mock(
            return_value=httpx.Response(400, json={"error": {"message": "Invalid token"}})
        )
        scraper = MetaAdsScraper()
        with pytest.raises(ScraperError):
            await scraper.fetch_ads("Produto Z")


@pytest.mark.asyncio
async def test_empty_data_field(monkeypatch):
    """Quando API retorna {"data": []}, retorna [] sem erro."""
    monkeypatch.setenv("META_ACCESS_TOKEN", "fake_token_789")

    with respx.mock:
        respx.get(META_API_URL).mock(
            return_value=httpx.Response(200, json={"data": []})
        )
        scraper = MetaAdsScraper()
        ads = await scraper.fetch_ads("Produto Sem Anuncios")

    assert ads == []
