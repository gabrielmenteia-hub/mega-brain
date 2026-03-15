"""Tests for mis.radar.quora_collector — Quora pain signal collection via scraping."""
from unittest.mock import AsyncMock, patch

import pytest

from mis.radar.quora_collector import collect_quora_signals
from mis.exceptions import ScraperError


def _make_niche():
    return {
        "slug": "emagrecimento",
        "keywords": ["emagrecer rapido"],
        "radar": {
            "anchor_term": "academia",
        },
    }


QUORA_HTML_WITH_QUESTIONS = """
<html>
<body>
  <div class="question_link">
    <a href="/What-is-the-best-diet-for-weight-loss">What is the best diet for weight loss?</a>
  </div>
  <div class="question_link">
    <a href="/How-can-I-lose-20kg-fast">How can I lose 20kg fast?</a>
  </div>
  <div class="question_link">
    <a href="/What-foods-should-I-avoid">What foods should I avoid to lose weight?</a>
  </div>
</body>
</html>
""" * 20  # Repeat to make it > 5KB


QUORA_HTML_EMPTY_SHELL = "<html><body><div id='root'></div></body></html>"  # < 5KB shell


@pytest.mark.asyncio
async def test_collect_quora_signals_returns_list(monkeypatch):
    """collect_quora_signals() returns a list with title and url when questions are found."""
    niche = _make_niche()

    mock_scraper_instance = AsyncMock()
    mock_scraper_instance.fetch_spa = AsyncMock(return_value=QUORA_HTML_WITH_QUESTIONS)
    mock_scraper_instance.__aenter__ = AsyncMock(return_value=mock_scraper_instance)
    mock_scraper_instance.__aexit__ = AsyncMock(return_value=None)

    with patch("mis.radar.quora_collector.BaseScraper", return_value=mock_scraper_instance):
        signals = await collect_quora_signals(niche)

    assert isinstance(signals, list)
    assert len(signals) > 0
    for sig in signals:
        assert "title" in sig
        assert "url" in sig


@pytest.mark.asyncio
async def test_quora_empty_spa_returns_empty_list(monkeypatch):
    """When SPA returns < 5KB HTML shell (no content), returns [] with quora_empty_response alert."""
    niche = _make_niche()

    captured_events = []

    def mock_log_warning(*args, **kwargs):
        captured_events.append(kwargs)

    mock_scraper_instance = AsyncMock()
    mock_scraper_instance.fetch_spa = AsyncMock(return_value=QUORA_HTML_EMPTY_SHELL)
    mock_scraper_instance.__aenter__ = AsyncMock(return_value=mock_scraper_instance)
    mock_scraper_instance.__aexit__ = AsyncMock(return_value=None)

    with patch("mis.radar.quora_collector.BaseScraper", return_value=mock_scraper_instance):
        with patch("mis.radar.quora_collector.log") as mock_log:
            mock_log.warning = mock_log_warning
            signals = await collect_quora_signals(niche)

    assert signals == []
    assert any(e.get("alert") == "quora_empty_response" for e in captured_events)


@pytest.mark.asyncio
async def test_quora_fetch_error_returns_empty_list(monkeypatch):
    """When fetch_spa raises ScraperError, collect_quora_signals() returns [] without propagating."""
    niche = _make_niche()

    captured_events = []

    def mock_log_error(*args, **kwargs):
        captured_events.append(kwargs)

    dummy_exc = Exception("dummy")
    mock_scraper_instance = AsyncMock()
    mock_scraper_instance.fetch_spa = AsyncMock(
        side_effect=ScraperError(url="https://quora.com", attempts=3, cause=dummy_exc)
    )
    mock_scraper_instance.__aenter__ = AsyncMock(return_value=mock_scraper_instance)
    mock_scraper_instance.__aexit__ = AsyncMock(return_value=None)

    with patch("mis.radar.quora_collector.BaseScraper", return_value=mock_scraper_instance):
        with patch("mis.radar.quora_collector.log") as mock_log:
            mock_log.error = mock_log_error
            signals = await collect_quora_signals(niche)

    assert signals == []
    assert any(e.get("alert") == "radar_collector_failed" for e in captured_events)


@pytest.mark.asyncio
async def test_quora_signals_have_required_fields(monkeypatch):
    """Each Quora signal has url, title, source=='quora', niche_slug, collected_at."""
    niche = _make_niche()

    mock_scraper_instance = AsyncMock()
    mock_scraper_instance.fetch_spa = AsyncMock(return_value=QUORA_HTML_WITH_QUESTIONS)
    mock_scraper_instance.__aenter__ = AsyncMock(return_value=mock_scraper_instance)
    mock_scraper_instance.__aexit__ = AsyncMock(return_value=None)

    with patch("mis.radar.quora_collector.BaseScraper", return_value=mock_scraper_instance):
        signals = await collect_quora_signals(niche)

    assert len(signals) > 0
    for sig in signals:
        assert "url" in sig
        assert "title" in sig
        assert sig["source"] == "quora"
        assert sig["niche_slug"] == niche["slug"]
        assert "collected_at" in sig
