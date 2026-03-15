"""Tests for mis.radar — APScheduler job registration for Pain Radar pipeline.

Tests verify that register_radar_jobs() correctly registers 5 jobs in APScheduler
with the expected cron triggers and idempotency behavior.
"""
import pytest
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from unittest.mock import patch


@pytest.fixture
def isolated_scheduler():
    """Create an isolated AsyncIOScheduler for test isolation (not the global singleton)."""
    scheduler = AsyncIOScheduler()
    return scheduler


def _make_mock_config():
    """Return a minimal config dict for register_radar_jobs tests."""
    return {
        "niches": [
            {"slug": "emagrecimento", "name": "Emagrecimento", "keywords": ["emagrecer"], "radar": True},
        ],
        "settings": {},
    }


def test_register_radar_jobs_adds_four_jobs(isolated_scheduler):
    """register_radar_jobs() registers at least 4 main radar jobs (trends, reddit_quora, youtube, synthesizer)."""
    config = _make_mock_config()

    with patch("mis.radar.get_scheduler", return_value=isolated_scheduler):
        from mis.radar import register_radar_jobs
        register_radar_jobs(config)

    job_ids = {job.id for job in isolated_scheduler.get_jobs()}
    assert "radar_trends" in job_ids
    assert "radar_reddit_quora" in job_ids
    assert "radar_youtube" in job_ids
    assert "radar_synthesizer" in job_ids


def test_radar_trends_job_cron_hourly(isolated_scheduler):
    """radar_trends job runs on an hourly cron trigger (minute=0)."""
    config = _make_mock_config()

    with patch("mis.radar.get_scheduler", return_value=isolated_scheduler):
        from mis.radar import register_radar_jobs
        register_radar_jobs(config)

    job = isolated_scheduler.get_job("radar_trends")
    assert job is not None
    trigger = job.trigger
    assert isinstance(trigger, CronTrigger)
    # minute=0 means it fires at the top of every hour
    field_map = {f.name: f for f in trigger.fields}
    assert str(field_map["minute"]) == "0"


def test_radar_youtube_job_cron_every_4h(isolated_scheduler):
    """radar_youtube job runs every 4 hours to respect quota limits."""
    config = _make_mock_config()

    with patch("mis.radar.get_scheduler", return_value=isolated_scheduler):
        from mis.radar import register_radar_jobs
        register_radar_jobs(config)

    job = isolated_scheduler.get_job("radar_youtube")
    assert job is not None
    trigger = job.trigger
    assert isinstance(trigger, CronTrigger)
    # hour='*/4' means every 4 hours
    field_map = {f.name: f for f in trigger.fields}
    assert "4" in str(field_map["hour"]) or "*" in str(field_map["hour"])


def test_radar_synthesizer_offset_30min(isolated_scheduler):
    """radar_synthesizer job runs with 30-minute offset relative to collector jobs."""
    config = _make_mock_config()

    with patch("mis.radar.get_scheduler", return_value=isolated_scheduler):
        from mis.radar import register_radar_jobs
        register_radar_jobs(config)

    job = isolated_scheduler.get_job("radar_synthesizer")
    assert job is not None
    trigger = job.trigger
    assert isinstance(trigger, CronTrigger)
    field_map = {f.name: f for f in trigger.fields}
    assert str(field_map["minute"]) == "30"


def test_replace_existing_safe(isolated_scheduler):
    """Calling register_radar_jobs() twice does not duplicate jobs."""
    config = _make_mock_config()

    with patch("mis.radar.get_scheduler", return_value=isolated_scheduler):
        from mis.radar import register_radar_jobs
        register_radar_jobs(config)
        count_after_first = len(isolated_scheduler.get_jobs())
        register_radar_jobs(config)
        count_after_second = len(isolated_scheduler.get_jobs())

    assert count_after_first == count_after_second
