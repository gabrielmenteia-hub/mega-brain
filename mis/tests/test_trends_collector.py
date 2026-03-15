"""Tests for mis.radar.trends_collector — Google Trends signal collection."""
import hashlib
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from mis.radar.trends_collector import collect_trends_signal, collect_niche_trends, _url_hash


def _make_df(keyword: str, anchor: str, peak_value: int = 75) -> pd.DataFrame:
    """Helper to create a minimal pytrends interest_over_time DataFrame."""
    return pd.DataFrame(
        {
            keyword: [50, peak_value, 60, 40],
            anchor: [80, 90, 70, 85],
            "isPartial": [False, False, False, True],
        }
    )


@pytest.mark.asyncio
async def test_collect_trends_signal_returns_peak_index(monkeypatch):
    """collect_trends_signal() returns a dict with peak_index as int."""
    keyword = "emagrecer rapido"
    anchor = "academia"
    niche_slug = "emagrecimento"

    mock_pytrends = MagicMock()
    mock_pytrends.interest_over_time.return_value = _make_df(keyword, anchor, peak_value=75)

    with patch("mis.radar.trends_collector.TrendReq", return_value=mock_pytrends):
        with patch("mis.radar.trends_collector.asyncio.sleep"):
            result = await collect_trends_signal(keyword, anchor, niche_slug)

    assert result is not None
    assert result["source"] == "google_trends"
    assert result["niche_slug"] == niche_slug
    assert "peak_index" in result
    assert result["score"] == result["peak_index"]


@pytest.mark.asyncio
async def test_ratelimited_returns_none_with_alert(monkeypatch, capsys):
    """When pytrends raises Exception (rate limit), returns None and emits alert."""
    keyword = "emagrecer rapido"
    anchor = "academia"
    niche_slug = "emagrecimento"

    mock_pytrends = MagicMock()
    mock_pytrends.interest_over_time.side_effect = Exception("429 Too Many Requests")

    captured_events = []

    def mock_log_error(*args, **kwargs):
        captured_events.append(kwargs)

    with patch("mis.radar.trends_collector.TrendReq", return_value=mock_pytrends):
        with patch("mis.radar.trends_collector.asyncio.sleep"):
            with patch("mis.radar.trends_collector.log") as mock_log:
                mock_log.error = mock_log_error
                result = await collect_trends_signal(keyword, anchor, niche_slug)

    assert result is None
    assert any(e.get("alert") == "trends_ratelimited" for e in captured_events)


@pytest.mark.asyncio
async def test_peak_index_is_int(monkeypatch):
    """The peak_index field in the returned signal is always an int (not float)."""
    keyword = "dieta low carb"
    anchor = "academia"
    niche_slug = "emagrecimento"

    mock_pytrends = MagicMock()
    # Use float values to verify conversion to int
    df = pd.DataFrame(
        {
            keyword: [50.5, 73.0, 60.2, 40.1],
            anchor: [80.0, 90.0, 70.0, 85.0],
            "isPartial": [False, False, False, True],
        }
    )
    mock_pytrends.interest_over_time.return_value = df

    with patch("mis.radar.trends_collector.TrendReq", return_value=mock_pytrends):
        with patch("mis.radar.trends_collector.asyncio.sleep"):
            result = await collect_trends_signal(keyword, anchor, niche_slug)

    assert result is not None
    assert isinstance(result["peak_index"], int)


@pytest.mark.asyncio
async def test_collect_niche_trends_persists_signals(tmp_path, monkeypatch):
    """collect_niche_trends() persists a signal per keyword into pain_signals table."""
    from mis.db import run_migrations

    db_path = str(tmp_path / "mis.db")
    run_migrations(db_path)

    niche = {
        "slug": "emagrecimento",
        "keywords": ["emagrecer rapido", "dieta low carb"],
        "radar": {
            "anchor_term": "academia",
            "relevance_language": "pt",
        },
    }

    call_count = [0]

    async def mock_collect_signal(keyword, anchor, niche_slug):
        call_count[0] += 1
        url = f"https://trends.google.com/trends/explore?q={keyword}"
        url_hash = hashlib.sha256(url.encode()).hexdigest()
        return {
            "url_hash": url_hash,
            "url": url,
            "title": f"Google Trends: {keyword}",
            "source": "google_trends",
            "niche_slug": niche_slug,
            "score": 70,
            "peak_index": 70,
            "extra_json": "{}",
            "collected_at": "2026-03-15T15:00:00",
        }

    with patch("mis.radar.trends_collector.collect_trends_signal", side_effect=mock_collect_signal):
        signals = await collect_niche_trends(niche, db_path)

    import sqlite_utils

    db = sqlite_utils.Database(db_path)
    count = db.execute("SELECT COUNT(*) FROM pain_signals").fetchone()[0]

    assert count == len(niche["keywords"])
    assert len(signals) == len(niche["keywords"])
