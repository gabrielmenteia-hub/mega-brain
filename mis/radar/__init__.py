"""mis.radar — Pain Radar: coleta sinais de mercado e sintetiza relatórios horários.

Phase 4: Exposes register_radar_jobs and run_radar_cycle as public API.
"""
import asyncio
import os
from datetime import datetime, timedelta, timezone

import structlog

from .trends_collector import collect_niche_trends
from .reddit_collector import collect_reddit_signals
from .quora_collector import collect_quora_signals
from .youtube_collector import collect_youtube_signals
from .synthesizer import synthesize_niche_pains
from .meta_ads_collector import collect_ad_comments

log = structlog.get_logger()

# Default DB path: env var MIS_DB_PATH → falls back to data/mis.db
_DEFAULT_DB_PATH = "data/mis.db"


def _get_db_path() -> str:
    """Return DB path from env or default."""
    return os.environ.get("MIS_DB_PATH", _DEFAULT_DB_PATH)


# ---------------------------------------------------------------------------
# Scheduler import (lazy to avoid circular imports)
# ---------------------------------------------------------------------------

def get_scheduler():
    """Return the global APScheduler singleton from mis.scheduler."""
    from mis.scheduler import get_scheduler as _get_scheduler
    return _get_scheduler()


# ---------------------------------------------------------------------------
# Async helpers for each collector type (iterate over all niches)
# ---------------------------------------------------------------------------

async def _run_all_trends(config: dict, db_path: str) -> None:
    """Run trends collection for all niches. Errors per niche are logged, not raised."""
    niches = config.get("niches", [])
    for niche in niches:
        try:
            signals = await collect_niche_trends(niche, db_path)
            log.info("radar.trends.done", niche=niche.get("slug"), count=len(signals))
        except Exception as e:
            log.error("radar.trends.error", niche=niche.get("slug"), error=str(e))


async def _run_all_reddit_quora(config: dict, db_path: str) -> None:
    """Run Reddit + Quora collection for all niches. Each niche is independent."""
    niches = config.get("niches", [])
    for niche in niches:
        results = await asyncio.gather(
            collect_reddit_signals(niche, db_path),
            collect_quora_signals(niche, db_path),
            return_exceptions=True,
        )
        for source, result in zip(["reddit", "quora"], results):
            if isinstance(result, Exception):
                log.error("radar.reddit_quora.error", niche=niche.get("slug"),
                          source=source, error=str(result))
            else:
                log.info("radar.reddit_quora.done", niche=niche.get("slug"),
                         source=source, count=len(result))


async def _run_all_youtube(config: dict, db_path: str) -> None:
    """Run YouTube collection for all niches. Errors per niche are logged, not raised."""
    niches = config.get("niches", [])
    for niche in niches:
        try:
            signals = await collect_youtube_signals(niche, db_path, config)
            log.info("radar.youtube.done", niche=niche.get("slug"), count=len(signals))
        except Exception as e:
            log.error("radar.youtube.error", niche=niche.get("slug"), error=str(e))


async def _run_all_synthesizers(config: dict, db_path: str) -> None:
    """Run pain synthesizer for all niches. Errors per niche are logged, not raised."""
    import sqlite_utils

    niches = config.get("niches", [])
    cycle_at = datetime.now(tz=timezone.utc).replace(second=0, microsecond=0).isoformat()

    db = sqlite_utils.Database(db_path)
    for niche in niches:
        niche_slug = niche.get("slug")
        try:
            row = next(db["niches"].rows_where("slug = ?", [niche_slug]), None)
            niche_id = row["id"] if row else None
            if not niche_id:
                log.warning("radar.synthesizer.niche_not_in_db", niche_slug=niche_slug)
                continue
            report = await synthesize_niche_pains(
                niche_id, niche.get("name", niche_slug), niche_slug, cycle_at, db_path
            )
            if report:
                log.info("radar.synthesizer.done", niche=niche_slug,
                         pains_count=len(report.get("pains", [])))
        except Exception as e:
            log.error("radar.synthesizer.error", niche=niche_slug, error=str(e))


async def _run_all_meta_ads(config: dict, db_path: str) -> None:
    """Run Meta Ads collection for all niches. Errors per niche are logged, not raised."""
    niches = config.get("niches", [])
    for niche in niches:
        try:
            signals = await collect_ad_comments(niche, db_path)
            log.info("radar.meta_ads.done", niche=niche.get("slug"), count=len(signals))
        except Exception as e:
            log.error("radar.meta_ads.error", niche=niche.get("slug"), error=str(e))


def _run_cleanup(db_path: str) -> None:
    """Delete pain_signals older than 30 days to keep DB size manageable."""
    import sqlite3

    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("DELETE FROM pain_signals WHERE collected_at < ?", [cutoff])
        conn.commit()
        log.info("radar.cleanup.done", cutoff=cutoff)
    except Exception as e:
        log.error("radar.cleanup.error", cutoff=cutoff, error=str(e))
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def register_radar_jobs(config: dict) -> None:
    """Register the 5 Pain Radar jobs in APScheduler singleton.

    Jobs registered:
      - radar_trends: every hour at minute=0
      - radar_reddit_quora: every hour at minute=0
      - radar_youtube: every 4 hours at minute=0
      - radar_synthesizer: every hour at minute=30 (offset to let collectors finish first)
      - radar_cleanup: daily at 03:00 UTC

    All jobs use replace_existing=True — safe to call multiple times at startup.

    Args:
        config: Loaded config dict (from load_config()).
    """
    from apscheduler.triggers.cron import CronTrigger

    scheduler = get_scheduler()
    db_path = _get_db_path()

    # Async wrappers — AsyncIOExecutor detects async def via iscoroutinefunction_partial
    # and schedules them via create_task() instead of run_in_executor() (DEFECT-3 fix)
    async def _trends_job():
        await _run_all_trends(config, db_path)

    async def _reddit_quora_job():
        await _run_all_reddit_quora(config, db_path)

    async def _youtube_job():
        await _run_all_youtube(config, db_path)

    async def _synthesizer_job():
        await _run_all_synthesizers(config, db_path)

    async def _cleanup_job():
        await asyncio.to_thread(_run_cleanup, db_path)

    async def _meta_ads_job():
        await _run_all_meta_ads(config, db_path)

    _job_specs = [
        ("radar_trends", _trends_job, CronTrigger(minute=0)),
        ("radar_reddit_quora", _reddit_quora_job, CronTrigger(minute=0)),
        ("radar_youtube", _youtube_job, CronTrigger(hour="*/4", minute=0)),
        ("radar_synthesizer", _synthesizer_job, CronTrigger(minute=30)),
        ("radar_cleanup", _cleanup_job, CronTrigger(hour=3, minute=0)),
        ("radar_meta_ads", _meta_ads_job, CronTrigger(minute=0)),
    ]

    for job_id, func, trigger in _job_specs:
        # Explicit remove before add ensures idempotency for both running and
        # paused schedulers (replace_existing only applies when scheduler is running
        # in APScheduler 3.x when paused).
        existing = scheduler.get_job(job_id)
        if existing is not None:
            scheduler.remove_job(job_id)
        scheduler.add_job(func, trigger, id=job_id, replace_existing=True)

    log.info("scheduler.radar_jobs_registered", job_count=6)


async def run_radar_cycle(niche_slug: str, config: dict, db_path: str) -> dict | None:
    """Execute a full collection + synthesis cycle for a single niche.

    Runs trends, reddit, and quora collectors in parallel (return_exceptions=True
    so a failure in one source does not cancel others). Then synthesizes pains.

    Args:
        niche_slug: Niche slug as configured in config.yaml.
        config: Loaded config dict (from load_config()).
        db_path: Path to the SQLite database file.

    Returns:
        Pain synthesis report dict, or None if no signals were collected.
    """
    import sqlite_utils

    niches = config.get("niches", [])
    niche = next((n for n in niches if n["slug"] == niche_slug), None)
    if not niche:
        log.error("radar.cycle.niche_not_found", niche_slug=niche_slug)
        return None

    cycle_at = datetime.now(tz=timezone.utc).replace(second=0, microsecond=0).isoformat()

    # Parallel collection — failure of one source does not cancel others
    results = await asyncio.gather(
        collect_niche_trends(niche, db_path),
        collect_reddit_signals(niche, db_path),
        collect_quora_signals(niche, db_path),
        return_exceptions=True,
    )
    log.info("radar.cycle.collection_done", niche=niche_slug, cycle_at=cycle_at,
             signals=[len(r) if isinstance(r, list) else "error" for r in results])

    # Resolve niche_id from DB
    db = sqlite_utils.Database(db_path)
    row = next(db["niches"].rows_where("slug = ?", [niche_slug]), None)
    niche_id = row["id"] if row else None
    if not niche_id:
        log.error("radar.cycle.niche_not_in_db", niche_slug=niche_slug)
        return None

    return await synthesize_niche_pains(niche_id, niche["name"], niche_slug, cycle_at, db_path)
