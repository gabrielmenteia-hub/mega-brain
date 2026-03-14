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


def register_scanner_jobs(config: dict) -> None:
    """Register one APScheduler job per platform scanner.

    Reads scan_schedule from config.settings (crontab string, default "0 3 * * *").
    Registers scanner_hotmart, scanner_clickbank, scanner_kiwify jobs with CronTrigger.
    Uses replace_existing=True — safe to call at startup or on re-registration.

    Call this before start_scheduler(). Each job receives 'config' as its argument.

    Args:
        config: Loaded config dict (from load_config()).
    """
    from apscheduler.triggers.cron import CronTrigger
    from mis.scanners.hotmart import run_hotmart_scan
    from mis.scanners.clickbank import run_clickbank_scan
    from mis.scanners.kiwify import run_kiwify_scan

    scan_schedule = config.get("settings", {}).get("scan_schedule", "0 3 * * *")
    trigger = CronTrigger.from_crontab(scan_schedule)

    scheduler = get_scheduler()

    for job_id, func in [
        ("scanner_hotmart", run_hotmart_scan),
        ("scanner_clickbank", run_clickbank_scan),
        ("scanner_kiwify", run_kiwify_scan),
    ]:
        scheduler.add_job(
            func,
            trigger,
            args=[config],
            id=job_id,
            replace_existing=True,
        )
        log.info("scanner.job.registered", job_id=job_id, schedule=scan_schedule)
