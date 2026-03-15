"""Tests for mis.radar.reddit_collector — Reddit pain signal collection via PRAW."""
import time
from unittest.mock import MagicMock, patch

import pytest

from mis.radar.reddit_collector import collect_reddit_signals


def _make_niche():
    return {
        "slug": "emagrecimento",
        "keywords": ["emagrecer rapido"],
        "radar": {
            "anchor_term": "academia",
            "subreddits": ["loseit", "Dieta"],
        },
    }


def _make_mock_post(title: str, permalink: str, score: int, age_hours: float = 1.0):
    """Create a mock PRAW submission object."""
    post = MagicMock()
    post.title = title
    post.permalink = permalink
    post.score = score
    # created_utc: age_hours ago from now
    post.created_utc = time.time() - (age_hours * 3600)
    return post


@pytest.mark.asyncio
async def test_collect_reddit_signals_returns_list(monkeypatch):
    """collect_reddit_signals() returns a list of signal dicts when mocked."""
    niche = _make_niche()

    mock_sub = MagicMock()
    mock_sub.new.return_value = [
        _make_mock_post("How to lose weight fast?", "/r/loseit/comments/abc", 142, age_hours=1.0),
        _make_mock_post("Best diets 2025?", "/r/Dieta/comments/def", 89, age_hours=2.0),
    ]

    mock_reddit = MagicMock()
    mock_reddit.subreddit.return_value = mock_sub

    with patch("mis.radar.reddit_collector.praw") as mock_praw:
        mock_praw.Reddit.return_value = mock_reddit
        signals = await collect_reddit_signals(niche)

    assert isinstance(signals, list)
    assert len(signals) > 0


@pytest.mark.asyncio
async def test_reddit_posts_have_required_fields(monkeypatch):
    """Each Reddit signal has url, title, score (int), collected_at, niche_slug, source."""
    niche = _make_niche()

    mock_sub = MagicMock()
    mock_sub.new.return_value = [
        _make_mock_post("Weight loss tips", "/r/loseit/comments/xyz", 55, age_hours=3.0),
    ]

    mock_reddit = MagicMock()
    mock_reddit.subreddit.return_value = mock_sub

    with patch("mis.radar.reddit_collector.praw") as mock_praw:
        mock_praw.Reddit.return_value = mock_reddit
        signals = await collect_reddit_signals(niche)

    assert len(signals) > 0
    for sig in signals:
        assert "url" in sig
        assert "title" in sig
        assert "score" in sig
        assert isinstance(sig["score"], int)
        assert "collected_at" in sig
        assert sig["niche_slug"] == niche["slug"]
        assert sig["source"] == "reddit"


@pytest.mark.asyncio
async def test_reddit_collector_degraded_returns_empty_list(monkeypatch):
    """When PRAW raises Exception, collect_reddit_signals() returns [] without propagating."""
    niche = _make_niche()

    captured_events = []

    def mock_log_error(*args, **kwargs):
        captured_events.append(kwargs)

    with patch("mis.radar.reddit_collector.praw") as mock_praw:
        mock_praw.Reddit.side_effect = Exception("PRAW auth error")
        with patch("mis.radar.reddit_collector.log") as mock_log:
            mock_log.error = mock_log_error
            signals = await collect_reddit_signals(niche)

    assert signals == []
    assert any(e.get("alert") == "radar_collector_failed" for e in captured_events)


@pytest.mark.asyncio
async def test_reddit_old_posts_filtered(monkeypatch):
    """Posts older than 24h are filtered out from the results."""
    niche = _make_niche()

    mock_sub = MagicMock()
    mock_sub.new.return_value = [
        _make_mock_post("Recent post", "/r/loseit/comments/new", 100, age_hours=1.0),
        _make_mock_post("Old post", "/r/loseit/comments/old", 200, age_hours=25.0),  # older than 24h
    ]

    mock_reddit = MagicMock()
    mock_reddit.subreddit.return_value = mock_sub

    with patch("mis.radar.reddit_collector.praw") as mock_praw:
        mock_praw.Reddit.return_value = mock_reddit
        signals = await collect_reddit_signals(niche)

    titles = [s["title"] for s in signals]
    assert "Recent post" in titles
    assert "Old post" not in titles
