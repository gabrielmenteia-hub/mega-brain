"""APScheduler skeleton for MIS.

Phase 1: Only the health check job is registered.
Phase 2+: Platform scraper jobs are added here.

Usage in Phase 2:
    from mis.scheduler import get_scheduler
    scheduler = get_scheduler()
    scheduler.add_job(
        scrape_hotmart,
        "interval",
        hours=6,
        id="hotmart_scraper",
        replace_existing=True,
    )
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
import structlog

log = structlog.get_logger()

_scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    """Return the global scheduler instance, creating it if needed."""
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler()
        _scheduler.add_listener(_on_job_event, EVENT_JOB_ERROR | EVENT_JOB_EXECUTED)
    return _scheduler


def start_scheduler() -> None:
    """Start the scheduler. Safe to call multiple times."""
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()
        log.info("scheduler.started")


def stop_scheduler() -> None:
    """Stop the scheduler gracefully."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        log.info("scheduler.stopped")
    _scheduler = None


def _on_job_event(event) -> None:
    if hasattr(event, "exception") and event.exception:
        log.error(
            "scheduler.job.error",
            job_id=event.job_id,
            exception=str(event.exception),
        )
    else:
        log.info("scheduler.job.executed", job_id=event.job_id)
