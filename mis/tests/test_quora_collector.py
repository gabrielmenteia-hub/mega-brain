"""Tests for mis.radar.quora_collector — Quora pain signal collection via scraping.

RED scaffolds: these tests fail with ImportError because mis.radar.quora_collector
does not exist yet. This is intentional — Wave 2 will implement the module.
"""
from mis.radar.quora_collector import collect_quora_signals
import pytest


@pytest.mark.asyncio
async def test_collect_quora_signals_returns_list(tmp_path):
    """collect_quora_signals() returns a list of signal dicts."""
    pytest.skip("RED: module not implemented yet")


@pytest.mark.asyncio
async def test_quora_empty_spa_returns_empty_list():
    """When Quora SPA returns no question links, collect_quora_signals() returns []."""
    pytest.skip("RED: module not implemented yet")
