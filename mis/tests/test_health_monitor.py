"""Tests for mis.health_monitor — canary check health monitoring.

Coverage: FOUND-04
"""
import pytest
from unittest.mock import AsyncMock, patch
import structlog
from mis.health_monitor import run_canary_check
from mis.exceptions import ScraperError


@pytest.mark.asyncio
async def test_canary_healthy():
    with patch("mis.health_monitor.BaseScraper") as MockScraper:
        instance = MockScraper.return_value.__aenter__.return_value
        instance.fetch = AsyncMock(return_value="x" * 200)
        result = await run_canary_check()
    assert result is True


@pytest.mark.asyncio
async def test_canary_empty_response():
    with structlog.testing.capture_logs() as cap_logs:
        with patch("mis.health_monitor.BaseScraper") as MockScraper:
            instance = MockScraper.return_value.__aenter__.return_value
            instance.fetch = AsyncMock(return_value="x" * 50)
            result = await run_canary_check()
    assert result is False
    assert any(log.get("alert") == "SCRAPER_RETURNING_EMPTY_RESPONSE" for log in cap_logs)


@pytest.mark.asyncio
async def test_canary_scraper_error():
    with structlog.testing.capture_logs() as cap_logs:
        with patch("mis.health_monitor.BaseScraper") as MockScraper:
            instance = MockScraper.return_value.__aenter__.return_value
            instance.fetch = AsyncMock(
                side_effect=ScraperError("https://httpbin.org/get", 3, Exception("timeout"))
            )
            result = await run_canary_check()
    assert result is False
    assert any(log.get("alert") == "SCRAPER_BROKEN_CANARY_FAILED" for log in cap_logs)
