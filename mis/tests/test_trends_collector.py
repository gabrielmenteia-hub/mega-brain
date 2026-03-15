"""Tests for mis.radar.trends_collector — Google Trends signal collection.

RED scaffolds: these tests fail with ImportError because mis.radar.trends_collector
does not exist yet. This is intentional — Wave 2 will implement the module.
"""
from mis.radar.trends_collector import collect_trends_signal, _url_hash
import pytest


@pytest.mark.asyncio
async def test_collect_trends_signal_returns_peak_index(tmp_path):
    """collect_trends_signal() returns a dict with peak_index as int."""
    pytest.skip("RED: module not implemented yet")


@pytest.mark.asyncio
async def test_ratelimited_returns_none_with_alert():
    """When pytrends-modern raises TooManyRequestsError, returns None and emits alert."""
    pytest.skip("RED: module not implemented yet")


@pytest.mark.asyncio
async def test_peak_index_is_int():
    """The peak_index field in the returned signal is always an int (0..100)."""
    pytest.skip("RED: module not implemented yet")
