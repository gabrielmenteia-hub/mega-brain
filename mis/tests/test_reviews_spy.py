"""Tests for ReviewsScraper (SPY-04).

Coverage:
- Reviews extraídos do HTML da Hotmart com campos corretos (text, valence, rating, source)
- Valência positiva para rating >= 4.0
- Valência negativa para rating < 4.0
- Google fallback chamado para plataformas sem reviews nativos
- Falha graciosa: retorna [] quando fetch() lança ScraperError
"""
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from mis.spies.reviews import ReviewsScraper
from mis.exceptions import ScraperError

_FIXTURE = (
    Path(__file__).parent / "fixtures" / "reviews" / "hotmart_reviews.html"
)


@pytest.fixture
def hotmart_html() -> str:
    return _FIXTURE.read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_hotmart_reviews_extracted(hotmart_html):
    """Dado fixture HTML com reviews da Hotmart, retorna lista de dicts com campos corretos."""
    async with ReviewsScraper() as scraper:
        with patch.object(scraper, "fetch", new=AsyncMock(return_value=hotmart_html)):
            reviews = await scraper.collect(
                platform="hotmart",
                product_url="https://hotmart.com/product/produto-x/P12345",
            )

    assert len(reviews) == 3
    for r in reviews:
        assert "text" in r
        assert "valence" in r
        assert "rating" in r
        assert "source" in r
        assert r["source"] == "hotmart"
        assert r["text"]  # não vazio


@pytest.mark.asyncio
async def test_valence_positive(hotmart_html):
    """Review com rating >= 4.0 tem valence='positive'."""
    async with ReviewsScraper() as scraper:
        with patch.object(scraper, "fetch", new=AsyncMock(return_value=hotmart_html)):
            reviews = await scraper.collect(
                platform="hotmart",
                product_url="https://hotmart.com/product/produto-x/P12345",
            )

    positive_reviews = [r for r in reviews if r["rating"] >= 4.0]
    assert all(r["valence"] == "positive" for r in positive_reviews), (
        f"Reviews com rating >= 4.0 devem ser 'positive': {positive_reviews}"
    )


@pytest.mark.asyncio
async def test_valence_negative(hotmart_html):
    """Review com rating < 4.0 tem valence='negative'."""
    async with ReviewsScraper() as scraper:
        with patch.object(scraper, "fetch", new=AsyncMock(return_value=hotmart_html)):
            reviews = await scraper.collect(
                platform="hotmart",
                product_url="https://hotmart.com/product/produto-x/P12345",
            )

    negative_reviews = [r for r in reviews if r["rating"] < 4.0]
    assert len(negative_reviews) >= 1, "Deve haver ao menos um review negativo na fixture"
    assert all(r["valence"] == "negative" for r in negative_reviews), (
        f"Reviews com rating < 4.0 devem ser 'negative': {negative_reviews}"
    )


@pytest.mark.asyncio
async def test_google_fallback_called():
    """Para plataforma desconhecida (gumroad), collect() chama _google_fallback()."""
    async with ReviewsScraper() as scraper:
        with patch.object(
            scraper, "_google_fallback", new=AsyncMock(return_value=[])
        ) as mock_fallback:
            await scraper.collect(
                platform="gumroad",
                product_url="https://gumroad.com/l/produto",
                product_title="Produto Gumroad",
            )

    mock_fallback.assert_called_once_with("Produto Gumroad")


@pytest.mark.asyncio
async def test_scraper_error_returns_empty():
    """Quando fetch() lança ScraperError, retorna [] sem propagar exceção."""
    async with ReviewsScraper() as scraper:
        with patch.object(
            scraper,
            "fetch",
            new=AsyncMock(
                side_effect=ScraperError(
                    url="https://hotmart.com/product/x",
                    attempts=3,
                    cause=ConnectionError("timeout"),
                )
            ),
        ):
            reviews = await scraper.collect(
                platform="hotmart",
                product_url="https://hotmart.com/product/x",
            )

    assert reviews == [], "Deve retornar [] em caso de ScraperError"
