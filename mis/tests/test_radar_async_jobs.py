"""Tests for DEFECT-3: radar job wrappers must be async def, not sync def.

RED phase: this test FAILS before the fix in mis/radar/__init__.py.

DEFECT-3: The 5 job wrappers inside register_radar_jobs() use asyncio.run()
which raises RuntimeError when called inside an already-running event loop
(the AsyncIOScheduler's loop). Fix: convert all 5 wrappers to async def.
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from apscheduler.schedulers.asyncio import AsyncIOScheduler


def _make_mock_config():
    """Minimal config dict for register_radar_jobs tests."""
    return {
        "niches": [
            {"slug": "emagrecimento", "name": "Emagrecimento", "keywords": ["emagrecer"]},
        ],
        "settings": {},
    }


def test_async_radar_jobs_no_runtime_error():
    """All 5 radar job wrapper functions registered by register_radar_jobs() must be async def.

    DEFECT-3: Before fix, wrappers are `def sync + asyncio.run()` which raises
    RuntimeError inside AsyncIOScheduler's event loop.

    After fix: all wrappers are `async def` — verified via
    asyncio.iscoroutinefunction(job_func) is True.

    This approach is more reliable than actually dispatching jobs in a test
    because it verifies the fix at the correct structural level without
    requiring a live event loop.
    """
    from mis.radar import register_radar_jobs

    isolated_scheduler = AsyncIOScheduler()
    config = _make_mock_config()

    with (
        patch("mis.radar.get_scheduler", return_value=isolated_scheduler),
        patch("mis.radar._run_all_trends", new_callable=AsyncMock),
        patch("mis.radar._run_all_reddit_quora", new_callable=AsyncMock),
        patch("mis.radar._run_all_youtube", new_callable=AsyncMock),
        patch("mis.radar._run_all_synthesizers", new_callable=AsyncMock),
        patch("mis.radar._run_cleanup", new_callable=MagicMock),
    ):
        register_radar_jobs(config)

    expected_job_ids = [
        "radar_trends",
        "radar_reddit_quora",
        "radar_youtube",
        "radar_synthesizer",
        "radar_cleanup",
    ]

    for job_id in expected_job_ids:
        job = isolated_scheduler.get_job(job_id)
        assert job is not None, f"Job '{job_id}' was not registered"

        job_func = job.func
        assert asyncio.iscoroutinefunction(job_func), (
            f"Job '{job_id}' wrapper must be 'async def', but "
            f"asyncio.iscoroutinefunction({job_func.__name__!r}) returned False. "
            f"DEFECT-3: sync wrapper with asyncio.run() causes RuntimeError in AsyncIOScheduler."
        )
