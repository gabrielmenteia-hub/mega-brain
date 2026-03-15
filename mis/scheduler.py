"""APScheduler for MIS.

Phase 1: Only the health check job is registered.
Phase 2: Platform scanner jobs (register_scanner_jobs).
Phase 3: Spy pipeline chained after scan (register_scan_and_spy_job / _scan_and_spy_job).

Public scan+spy entry point:
    _scan_and_spy_job() — runs run_all_scanners, then run_spy_batch for top SPY_TOP_N
    register_scan_and_spy_job(config) — registers _scan_and_spy_job in APScheduler

SPY_TOP_N is imported from spy_orchestrator (hardcoded=10, not configurable).
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
import structlog

import os

from .db import get_db
from .scanner import run_all_scanners, save_batch_with_alerts
from .spy_orchestrator import run_spy_batch, SPY_TOP_N

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


async def _scan_and_spy_job() -> None:
    """Scan all platforms, then spy the top SPY_TOP_N products per platform.

    This is the combined scan+spy pipeline job. Called by the scheduler or
    directly in tests.

    Collects products from run_all_scanners(), selects the top SPY_TOP_N by
    rank per platform key, and dispatches to run_spy_batch().

    Products to spy are identified by their DB ID. If a Product in the scanner
    result does not have a DB ID attribute, it is skipped with a warning log.
    The Product dataclass from scanner.py has external_id + rank but no DB ID —
    the scheduler passes the product rank as a proxy; actual DB lookup happens
    inside run_spy() per product.

    Note: This function does not read spy config — max_concurrent_spy is applied
    inside run_spy_batch() via _get_spy_config().
    """
    from .config import load_config

    log.info("scan_and_spy_job.start")
    try:
        config = load_config()
    except Exception as e:
        log.error("scan_and_spy_job.config_error", error=str(e))
        config = {}

    results = await run_all_scanners(config)

    db_path = os.environ.get("MIS_DB_PATH", "data/mis.db")
    db = get_db(db_path)

    products_to_spy: list[dict] = []
    for platform_key, platform_products in results.items():
        if not platform_products:
            continue
        save_batch_with_alerts(db, db_path, platform_products)
        top_products = platform_products[:SPY_TOP_N]
        for p in top_products:
            rows = list(db.execute(
                "SELECT id FROM products WHERE platform_id=? AND external_id=?",
                [p.platform_id, p.external_id],
            ))
            if not rows:
                log.warning(
                    "scan_and_spy_job.product_no_db_id",
                    platform_key=platform_key,
                    external_id=getattr(p, "external_id", "unknown"),
                )
                continue
            products_to_spy.append({"id": rows[0][0], "rank": getattr(p, "rank", 999)})

    if products_to_spy:
        log.info("scan_and_spy_job.spy_start", count=len(products_to_spy))
        await run_spy_batch(products_to_spy)
    else:
        log.info("scan_and_spy_job.no_products")

    log.info("scan_and_spy_job.done", spied=len(products_to_spy))


def register_scan_and_spy_job(config: dict) -> None:
    """Register the combined scan+spy job in APScheduler.

    Reads scan_schedule from config.settings. Replaces existing job safely.
    """
    from apscheduler.triggers.cron import CronTrigger

    scan_schedule = config.get("settings", {}).get("scan_schedule", "0 3 * * *")
    trigger = CronTrigger.from_crontab(scan_schedule)
    scheduler = get_scheduler()
    scheduler.add_job(
        _scan_and_spy_job,
        trigger,
        id="scan_and_spy",
        replace_existing=True,
    )
    log.info("scan_and_spy_job.registered", schedule=scan_schedule)


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
