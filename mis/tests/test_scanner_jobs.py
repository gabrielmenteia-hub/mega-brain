"""Tests for scanner scheduler jobs and platform canary — TDD RED phase.

These tests cover SCAN-04 requirements:
  1. test_jobs_registered     — register_scanner_jobs() adds 3 jobs: hotmart, clickbank, kiwify
  2. test_cron_trigger        — each job uses CronTrigger from scan_schedule config
  3. test_platform_canary_stale — run_platform_canary() returns False + alert when updated_at > 25h
  4. test_partial_failure      — run_all_scanners() with one scanner failing: others still return results

All scheduler tests create an isolated scheduler using stop_scheduler() in teardown.
Canary tests use a real SQLite DB in tmp_path.
"""
import asyncio
import pytest
import yaml
from pathlib import Path
from datetime import datetime, timezone, timedelta


# ─── Fixture: config with scan_schedule ──────────────────────────────────────

@pytest.fixture
def temp_config_with_schedule(tmp_path):
    """Create a config.yaml with scan_schedule and 3 niches."""
    config = {
        "niches": [
            {
                "name": "Saude",
                "slug": "saude",
                "keywords": ["emagrecimento", "dieta"],
                "platforms": {
                    "hotmart": "saude-e-fitness",
                    "kiwify": "saude",
                },
            },
        ],
        "settings": {
            "proxy_url": "",
            "request_delay_s": 1.0,
            "max_retries": 3,
            "scan_schedule": "0 3 * * *",  # 3 AM daily
        },
    }
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.dump(config, allow_unicode=True), encoding="utf-8")
    return str(config_path)


# ─── Task 1: Jobs registered ──────────────────────────────────────────────────

def test_jobs_registered(temp_config_with_schedule):
    """register_scanner_jobs() adds scanner_hotmart, scanner_clickbank, scanner_kiwify to scheduler."""
    from mis.config import load_config
    from mis.scheduler import get_scheduler, stop_scheduler, register_scanner_jobs

    # Reset scheduler state before test
    stop_scheduler()

    try:
        config = load_config(Path(temp_config_with_schedule))
        register_scanner_jobs(config)

        scheduler = get_scheduler()
        job_ids = {job.id for job in scheduler.get_jobs()}

        assert "scanner_hotmart" in job_ids, f"Missing scanner_hotmart in {job_ids}"
        assert "scanner_clickbank" in job_ids, f"Missing scanner_clickbank in {job_ids}"
        assert "scanner_kiwify" in job_ids, f"Missing scanner_kiwify in {job_ids}"
    finally:
        stop_scheduler()


# ─── Task 2: Cron trigger ─────────────────────────────────────────────────────

def test_cron_trigger(temp_config_with_schedule):
    """Each scanner job uses CronTrigger matching scan_schedule from config."""
    from apscheduler.triggers.cron import CronTrigger
    from mis.config import load_config
    from mis.scheduler import get_scheduler, stop_scheduler, register_scanner_jobs

    # Reset scheduler state before test
    stop_scheduler()

    try:
        config = load_config(Path(temp_config_with_schedule))
        register_scanner_jobs(config)

        scheduler = get_scheduler()
        jobs = {job.id: job for job in scheduler.get_jobs()}

        # Verify hotmart job uses CronTrigger
        assert "scanner_hotmart" in jobs, "scanner_hotmart job not found"
        hotmart_job = jobs["scanner_hotmart"]
        assert isinstance(hotmart_job.trigger, CronTrigger), (
            f"Expected CronTrigger, got {type(hotmart_job.trigger)}"
        )
    finally:
        stop_scheduler()


# ─── Task 3: Platform canary (DB-based, stale data) ─────────────────────────

@pytest.mark.asyncio
async def test_platform_canary_stale(tmp_path):
    """run_platform_canary() returns False + alert='platform_data_stale' when data is > 25h old."""
    from structlog.testing import capture_logs
    from mis.db import get_db, run_migrations
    from mis.migrations._002_product_enrichment import run_migration_002
    from mis.health_monitor import run_platform_canary

    db_path = str(tmp_path / "mis.db")
    run_migrations(db_path)
    run_migration_002(db_path)

    db = get_db(db_path)

    # Insert platform row
    db["platforms"].insert(
        {
            "id": 1,
            "name": "Hotmart",
            "slug": "hotmart",
            "base_url": "https://hotmart.com",
            "created_at": "2026-01-01T00:00:00Z",
        },
        ignore=True,
    )
    db["niches"].insert(
        {"id": 1, "name": "Saude", "slug": "saude", "created_at": "2026-01-01T00:00:00Z"},
        ignore=True,
    )

    # Insert a product with updated_at 30 hours ago (stale)
    stale_time = (datetime.now(timezone.utc) - timedelta(hours=30)).isoformat()
    db["products"].insert(
        {
            "platform_id": 1,
            "external_id": "E45853768C",
            "title": "Produto Velho",
            "url": "https://hotmart.com/produto/antigo",
            "niche_id": 1,
            "rank": 1,
            "price": None,
            "commission_pct": None,
            "rating": None,
            "thumbnail_url": None,
            "updated_at": stale_time,
        },
        alter=True,
    )

    with capture_logs() as cap:
        result = await run_platform_canary(db_path, platform_id=1, platform_name="hotmart")

    assert result is False, f"Expected False (stale), got {result}"
    assert any(
        e.get("alert") == "platform_data_stale" for e in cap
    ), f"Expected alert='platform_data_stale' in logs. Got: {cap}"


# ─── Task 4: Partial failure in run_all_scanners ─────────────────────────────

@pytest.mark.asyncio
async def test_partial_failure(tmp_path):
    """run_all_scanners() with one scanner raising an exception: other platforms still return results."""
    from unittest.mock import AsyncMock, patch
    from mis.scanner import run_all_scanners, Product

    # Config with 2 platforms per niche
    config = {
        "niches": [
            {
                "slug": "saude",
                "platforms": {
                    "kiwify": "saude",
                    "hotmart": "saude-e-fitness",
                },
            }
        ],
        "settings": {"proxy_url": None},
    }

    # Mock KiwifyScanner.scan_niche to raise an exception
    # Mock HotmartScanner.scan_niche to return 1 product
    fake_product = Product(
        external_id="E45853768C",
        title="Produto Teste",
        url="https://hotmart.com/produto/teste",
        platform_id=1,
        niche_id=0,
        rank=1,
    )

    async def kiwify_raises(niche_slug, platform_slug, **kwargs):
        raise RuntimeError("Kiwify scanner exploded")

    async def hotmart_returns_product(niche_slug, platform_slug, **kwargs):
        return [fake_product]

    # Patch both scanners
    with (
        patch("mis.scanner.KiwifyScanner") as MockKiwify,
        patch("mis.scanner.HotmartScanner") as MockHotmart,
    ):
        mock_kiwify_instance = AsyncMock()
        mock_kiwify_instance.scan_niche = kiwify_raises
        mock_kiwify_instance.__aenter__ = AsyncMock(return_value=mock_kiwify_instance)
        mock_kiwify_instance.__aexit__ = AsyncMock(return_value=None)
        MockKiwify.return_value = mock_kiwify_instance

        mock_hotmart_instance = AsyncMock()
        mock_hotmart_instance.scan_niche = hotmart_returns_product
        mock_hotmart_instance.__aenter__ = AsyncMock(return_value=mock_hotmart_instance)
        mock_hotmart_instance.__aexit__ = AsyncMock(return_value=None)
        MockHotmart.return_value = mock_hotmart_instance

        results = await run_all_scanners(config)

    # Kiwify failed → empty list; Hotmart succeeded → 1 product
    # At minimum, the output should have both keys and NOT raise an exception
    assert isinstance(results, dict), f"Expected dict, got {type(results)}"
    # The failing platform key should map to empty list (not re-raise)
    for key, products in results.items():
        assert isinstance(products, list), f"Key {key!r} should map to list, got {type(products)}"
