"""Tests for mis.radar.youtube_collector — YouTube pain signal collection via Data API v3.

RED scaffolds: these tests fail with ImportError because mis.radar.youtube_collector
does not exist yet. This is intentional — Wave 2 will implement the module.
"""
from mis.radar.youtube_collector import collect_youtube_signals, get_quota_used_today, log_quota_usage
import pytest


@pytest.mark.asyncio
async def test_collect_youtube_signals_returns_list(tmp_path):
    """collect_youtube_signals() returns a list of signal dicts."""
    pytest.skip("RED: module not implemented yet")


@pytest.mark.asyncio
async def test_quota_guard_disables_when_limit_reached(tmp_path):
    """When daily quota >= youtube_quota_daily_limit, collector returns [] without API call."""
    pytest.skip("RED: module not implemented yet")


@pytest.mark.asyncio
async def test_quota_log_persisted_in_db(tmp_path):
    """After collect_youtube_signals(), quota usage is recorded in youtube_quota_log table."""
    pytest.skip("RED: module not implemented yet")


@pytest.mark.asyncio
async def test_youtube_signals_have_required_fields():
    """Each YouTube signal has url_hash, url, title, source='youtube', niche_slug, score, extra_json."""
    pytest.skip("RED: module not implemented yet")
