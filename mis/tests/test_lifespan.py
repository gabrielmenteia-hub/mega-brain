"""Tests for FastAPI lifespan hook in create_app().

These tests verify SCAN-04 gap closure: create_app() must register and start
APScheduler via a lifespan hook, and shut it down cleanly on exit.

Wave 0 (RED): All 3 tests fail before the fix because create_app() has no
lifespan parameter yet.
"""
from unittest.mock import AsyncMock, MagicMock, patch, call

import pytest
from fastapi.testclient import TestClient


def test_lifespan_registers_jobs_on_startup(tmp_path):
    """Startup lifespan must call register_scan_and_spy_job, register_radar_jobs, register_canary_job,
    run_schema_integrity_check (async), and register_platform_canary_jobs."""
    db_path = str(tmp_path / "mis.db")

    mock_scheduler = MagicMock()
    mock_scheduler.running = False

    with patch("mis.web.app.register_scan_and_spy_job") as mock_scan, \
         patch("mis.web.app.register_radar_jobs") as mock_radar, \
         patch("mis.web.app.register_canary_job") as mock_canary, \
         patch("mis.web.app.run_schema_integrity_check", new=AsyncMock(return_value=True)) as mock_schema_check, \
         patch("mis.web.app.register_platform_canary_jobs") as mock_platform_canary, \
         patch("mis.web.app.get_scheduler", return_value=mock_scheduler), \
         patch("mis.web.app.load_config", return_value={}):

        from mis.web.app import create_app
        app = create_app(db_path)

        with TestClient(app):
            # Inside context: lifespan startup has run
            mock_scan.assert_called_once()
            mock_radar.assert_called_once()
            mock_canary.assert_called_once()
            mock_schema_check.assert_called_once_with(db_path)
            mock_platform_canary.assert_called_once()


def test_lifespan_shutdown_on_exit(tmp_path):
    """Lifespan teardown must call scheduler.shutdown(wait=False)."""
    db_path = str(tmp_path / "mis.db")

    mock_scheduler = MagicMock()
    mock_scheduler.running = False

    with patch("mis.web.app.register_scan_and_spy_job"), \
         patch("mis.web.app.register_radar_jobs"), \
         patch("mis.web.app.register_canary_job"), \
         patch("mis.web.app.get_scheduler", return_value=mock_scheduler), \
         patch("mis.web.app.load_config", return_value={}):

        from mis.web.app import create_app
        app = create_app(db_path)

        with TestClient(app):
            pass  # Enter and exit

        # After context exit: shutdown called with wait=False
        mock_scheduler.shutdown.assert_called_once_with(wait=False)


def test_register_platform_canary_jobs_registers_3_jobs(tmp_path):
    """register_platform_canary_jobs(db_path) must register 3 APScheduler jobs with correct IDs."""
    from unittest.mock import MagicMock, patch

    db_path = str(tmp_path / "mis.db")
    mock_scheduler = MagicMock()
    added_jobs = []

    def fake_add_job(func, trigger=None, hours=None, id=None, kwargs=None, replace_existing=None):
        added_jobs.append(id)

    mock_scheduler.add_job.side_effect = fake_add_job

    with patch("mis.scheduler.get_scheduler", return_value=mock_scheduler):
        from mis.health_monitor import register_platform_canary_jobs
        register_platform_canary_jobs(db_path)

    assert len(added_jobs) == 3
    assert "canary_hotmart" in added_jobs
    assert "canary_clickbank" in added_jobs
    assert "canary_kiwify" in added_jobs


def test_lifespan_scheduler_has_jobs(tmp_path):
    """Scheduler must be running during request handling when real scheduler used."""
    from mis.scheduler import stop_scheduler, get_scheduler
    import mis.web.app as app_module

    db_path = str(tmp_path / "mis.db")

    # Clean scheduler state before test
    stop_scheduler()

    # Stub out job registration to avoid config/DB dependencies
    with patch("mis.web.app.register_scan_and_spy_job"), \
         patch("mis.web.app.register_radar_jobs"), \
         patch("mis.web.app.register_canary_job"), \
         patch("mis.web.app.load_config", return_value={}):

        from mis.web.app import create_app
        app = create_app(db_path)

        try:
            with TestClient(app):
                scheduler = get_scheduler()
                assert scheduler.running is True
        finally:
            stop_scheduler()
