"""Tests for mis.radar.reddit_collector — Reddit pain signal collection via PRAW.

RED scaffolds: these tests fail with ImportError because mis.radar.reddit_collector
does not exist yet. This is intentional — Wave 2 will implement the module.
"""
from mis.radar.reddit_collector import collect_reddit_signals
import pytest


@pytest.mark.asyncio
async def test_collect_reddit_signals_returns_list(tmp_path):
    """collect_reddit_signals() returns a list of signal dicts."""
    pytest.skip("RED: module not implemented yet")


@pytest.mark.asyncio
async def test_reddit_posts_have_required_fields():
    """Each Reddit signal has url_hash, url, title, source, niche_slug, score, extra_json."""
    pytest.skip("RED: module not implemented yet")


@pytest.mark.asyncio
async def test_reddit_collector_degraded_returns_empty_list():
    """When PRAW raises PRAWException, returns [] without propagating exception."""
    pytest.skip("RED: module not implemented yet")
