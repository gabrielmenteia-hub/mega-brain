"""Tests for mis.radar.youtube_collector — YouTube pain signal collection via Data API v3.

Wave 2 GREEN implementation tests.
"""
import json
import hashlib
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
import sqlite_utils

from mis.radar.youtube_collector import collect_youtube_signals, get_quota_used_today, log_quota_usage
from mis.migrations._004_pain_radar import run_migration_004


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _setup_db(tmp_path):
    """Create a test DB with Pain Radar schema."""
    db_path = str(tmp_path / "mis.db")
    run_migration_004(db_path)
    return db_path


def _make_youtube_mock(search_items, stats_items, comments_by_video=None):
    """Build a mock googleapiclient YouTube resource."""
    youtube = MagicMock()

    # search().list().execute()
    search_resp = {"items": search_items}
    youtube.search.return_value.list.return_value.execute.return_value = search_resp

    # videos().list().execute()
    stats_resp = {"items": stats_items}
    youtube.videos.return_value.list.return_value.execute.return_value = stats_resp

    # commentThreads().list().execute()
    def comment_execute_side_effect(*args, **kwargs):
        # Extract videoId from the mock call kwargs
        return {"items": []}

    comments_by_video = comments_by_video or {}

    def get_comment_threads():
        ct_mock = MagicMock()

        def list_call(**kwargs):
            vid_id = kwargs.get("videoId", "")
            comments = comments_by_video.get(vid_id, [])
            inner = MagicMock()
            inner.execute.return_value = {"items": [
                {"snippet": {"topLevelComment": {"snippet": {"textDisplay": c}}}}
                for c in comments
            ]}
            return inner

        ct_mock.list.side_effect = list_call
        return ct_mock

    youtube.commentThreads.side_effect = get_comment_threads

    return youtube


# ---------------------------------------------------------------------------
# Test 1: collect_youtube_signals returns list with required fields
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_collect_youtube_signals_returns_list(tmp_path, monkeypatch):
    """collect_youtube_signals() returns list with url, title, source='youtube', niche_slug."""
    db_path = _setup_db(tmp_path)

    search_items = [
        {"id": {"videoId": "vid001"}, "snippet": {"title": "Como emagrecer em 30 dias"}},
        {"id": {"videoId": "vid002"}, "snippet": {"title": "Dieta low carb resultado"}},
    ]
    stats_items = [
        {"id": "vid001", "statistics": {"viewCount": "15000", "likeCount": "300"}},
        {"id": "vid002", "statistics": {"viewCount": "8000", "likeCount": "120"}},
    ]
    comments_by_video = {
        "vid001": ["Muito bom!", "Funcionou comigo"],
        "vid002": ["Excelente dica"],
    }

    mock_youtube = _make_youtube_mock(search_items, stats_items, comments_by_video)

    monkeypatch.setenv("YOUTUBE_DATA_API_KEY", "fake_api_key")

    with patch("mis.radar.youtube_collector.build", return_value=mock_youtube):
        niche = {
            "slug": "emagrecimento",
            "keywords": ["emagrecer rapido"],
            "radar": {"relevance_language": "pt"},
        }
        config = {"settings": {"youtube_quota_daily_limit": 9000}}
        result = await collect_youtube_signals(niche, db_path, config)

    assert isinstance(result, list)
    assert len(result) == 2

    for sig in result:
        assert "url" in sig
        assert "title" in sig
        assert sig["source"] == "youtube"
        assert sig["niche_slug"] == "emagrecimento"


# ---------------------------------------------------------------------------
# Test 2: quota guard disables collector when daily limit reached
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_quota_guard_disables_when_limit_reached(tmp_path, monkeypatch):
    """When youtube_quota_log has >= quota_limit units today, returns [] without API call."""
    db_path = _setup_db(tmp_path)

    # Insert 9000+ units in quota log (today, after 07:00 UTC)
    db = sqlite_utils.Database(db_path)
    now_utc = datetime.utcnow()
    # Make sure logged_at is after today's reset (07:00 UTC)
    reset_today = now_utc.replace(hour=7, minute=0, second=0, microsecond=0)
    if now_utc.hour < 7:
        # If before reset, put it after yesterday's reset (which means it's still "today")
        logged_at = (now_utc - timedelta(hours=1)).isoformat()
    else:
        logged_at = (reset_today + timedelta(minutes=10)).isoformat()

    db["youtube_quota_log"].insert({
        "units": 9500,
        "operation": "search.list",
        "logged_at": logged_at,
    })

    monkeypatch.setenv("YOUTUBE_DATA_API_KEY", "fake_api_key")

    import structlog
    log_output = []

    def capture_log(event_dict):
        log_output.append(event_dict)
        return event_dict

    with patch("mis.radar.youtube_collector.build") as mock_build:
        niche = {
            "slug": "emagrecimento",
            "keywords": ["emagrecer"],
            "radar": {"relevance_language": "pt"},
        }
        config = {"settings": {"youtube_quota_daily_limit": 9000}}
        result = await collect_youtube_signals(niche, db_path, config)

    # API should NOT have been called
    mock_build.assert_not_called()

    # Result should be empty list
    assert result == []


# ---------------------------------------------------------------------------
# Test 3: log_quota_usage persists in youtube_quota_log
# ---------------------------------------------------------------------------

def test_quota_log_persisted_in_db(tmp_path):
    """log_quota_usage() inserts a record in youtube_quota_log with correct units."""
    db_path = _setup_db(tmp_path)

    log_quota_usage(db_path, 100, "search.list")

    db = sqlite_utils.Database(db_path)
    rows = list(db["youtube_quota_log"].rows_where("operation = ?", ["search.list"]))

    assert len(rows) == 1
    assert rows[0]["units"] == 100
    assert rows[0]["operation"] == "search.list"
    assert "logged_at" in rows[0]


# ---------------------------------------------------------------------------
# Test 4: get_quota_used_today respects daily reset at 07:00 UTC
# ---------------------------------------------------------------------------

def test_get_quota_used_today_resets_at_midnight(tmp_path):
    """Quota entries before today's 07:00 UTC reset are NOT counted."""
    db_path = _setup_db(tmp_path)
    db = sqlite_utils.Database(db_path)

    now_utc = datetime.utcnow()
    # Compute today's reset time
    reset_today = now_utc.replace(hour=7, minute=0, second=0, microsecond=0)
    if now_utc.hour < 7:
        # We're before today's reset — yesterday's reset is what matters
        reset_today = reset_today - timedelta(days=1)

    # Insert an old entry — 2 hours BEFORE reset (should NOT be counted)
    old_logged_at = (reset_today - timedelta(hours=2)).isoformat()
    db["youtube_quota_log"].insert({
        "units": 500,
        "operation": "search.list",
        "logged_at": old_logged_at,
    })

    # Quota used today should NOT include the old entry
    used = get_quota_used_today(db_path)
    assert used == 0


# ---------------------------------------------------------------------------
# Test 5: YouTube signals have all required fields
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_youtube_signals_have_required_fields(tmp_path, monkeypatch):
    """Each YouTube signal has url, title, score (int = view_count), extra_json with top_comments, collected_at."""
    db_path = _setup_db(tmp_path)

    search_items = [
        {"id": {"videoId": "vid003"}, "snippet": {"title": "Renda passiva em 2024"}},
    ]
    stats_items = [
        {"id": "vid003", "statistics": {"viewCount": "22000", "likeCount": "800"}},
    ]
    comments_by_video = {
        "vid003": ["Incrivel conteudo", "Me ajudou muito"],
    }

    mock_youtube = _make_youtube_mock(search_items, stats_items, comments_by_video)

    monkeypatch.setenv("YOUTUBE_DATA_API_KEY", "fake_api_key")

    with patch("mis.radar.youtube_collector.build", return_value=mock_youtube):
        niche = {
            "slug": "financas-pessoais",
            "keywords": ["renda passiva"],
            "radar": {"relevance_language": "pt"},
        }
        config = {"settings": {"youtube_quota_daily_limit": 9000}}
        result = await collect_youtube_signals(niche, db_path, config)

    assert len(result) == 1
    sig = result[0]

    # Required fields
    assert "url" in sig
    assert "title" in sig
    assert sig["source"] == "youtube"
    assert isinstance(sig["score"], int)
    assert sig["score"] == 22000

    # extra_json must be a valid JSON string with top_comments and like_count
    extra = json.loads(sig["extra_json"])
    assert "top_comments" in extra
    assert isinstance(extra["top_comments"], list)
    assert "like_count" in extra

    assert "collected_at" in sig
