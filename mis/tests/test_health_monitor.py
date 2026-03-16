"""Tests for mis.health_monitor — canary check health monitoring.

Coverage: FOUND-04
"""
import sqlite3
import pytest
from unittest.mock import AsyncMock, patch
import structlog
from mis.health_monitor import run_canary_check, run_schema_integrity_check
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


@pytest.mark.asyncio
async def test_schema_integrity_check_ok(tmp_path):
    """Verifica retorno True quando todas as 5 tabelas existem."""
    db_path = str(tmp_path / "mis.db")
    with sqlite3.connect(db_path) as conn:
        for table in ["products", "platforms", "niches", "pains", "dossiers"]:
            conn.execute(f"CREATE TABLE {table} (id INTEGER PRIMARY KEY)")
    result = await run_schema_integrity_check(db_path)
    assert result is True


@pytest.mark.asyncio
async def test_schema_integrity_check_missing_table(tmp_path):
    """Verifica retorno False quando alguma tabela esta ausente."""
    db_path = str(tmp_path / "mis.db")
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE products (id INTEGER PRIMARY KEY)")
        # Ausentes: platforms, niches, pains, dossiers
    result = await run_schema_integrity_check(db_path)
    assert result is False
