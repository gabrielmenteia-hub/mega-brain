"""Tests for mis.radar — APScheduler job registration for Pain Radar pipeline.

RED scaffolds: these tests fail with ImportError because mis.radar does not
expose register_radar_jobs yet. This is intentional — Wave 3 will implement it.
"""
from mis.radar import register_radar_jobs
import pytest


def test_register_radar_jobs_adds_four_jobs():
    """register_radar_jobs() registers exactly 4 scheduled jobs."""
    pytest.skip("RED: module not implemented yet")


def test_radar_trends_job_cron_hourly():
    """The Google Trends collection job runs on an hourly cron trigger."""
    pytest.skip("RED: module not implemented yet")


def test_radar_youtube_job_cron_every_4h():
    """The YouTube collection job runs every 4 hours to respect quota limits."""
    pytest.skip("RED: module not implemented yet")


def test_radar_synthesizer_offset_30min():
    """The synthesizer job runs with a 30-minute offset relative to collector jobs."""
    pytest.skip("RED: module not implemented yet")
