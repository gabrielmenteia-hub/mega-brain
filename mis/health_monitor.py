"""Health monitor with canary check for the MIS scraping system.

Exports: run_canary_check, register_canary_job, CANARY_URL, CANARY_MIN_LENGTH
"""
import structlog

from .base_scraper import BaseScraper
from .exceptions import ScraperError

log = structlog.get_logger()

CANARY_URL = "https://httpbin.org/get"
CANARY_MIN_LENGTH = 100


async def run_canary_check() -> bool:
    """Run one canary check against a known-good URL.

    Returns True if healthy, False if degraded. Never propagates exceptions.
    Emits structured alert logs on failure for external parsing.
    """
    async with BaseScraper() as scraper:
        try:
            content = await scraper.fetch(CANARY_URL)
            if len(content) < CANARY_MIN_LENGTH:
                log.warning(
                    "health.canary.empty",
                    url=CANARY_URL,
                    content_length=len(content),
                    alert="SCRAPER_RETURNING_EMPTY_RESPONSE",
                )
                return False
            log.info("health.canary.ok", url=CANARY_URL, content_length=len(content))
            return True
        except ScraperError as exc:
            log.error(
                "health.canary.failed",
                url=CANARY_URL,
                attempts=exc.attempts,
                cause=str(exc.cause),
                alert="SCRAPER_BROKEN_CANARY_FAILED",
            )
            return False
        except Exception as exc:
            log.error(
                "health.canary.unexpected_error",
                url=CANARY_URL,
                error=str(exc),
                alert="SCRAPER_BROKEN_CANARY_FAILED",
            )
            return False


def register_canary_job() -> None:
    """Register the canary health check job in the global APScheduler.

    Runs every 15 minutes. Safe to call multiple times (job is replaced if exists).
    """
    from .scheduler import get_scheduler

    scheduler = get_scheduler()
    scheduler.add_job(
        run_canary_check,
        trigger="interval",
        minutes=15,
        id="health_canary",
        replace_existing=True,
    )
    log.info("health.canary.registered", interval_minutes=15)


async def run_platform_canary(
    db_path: str,
    platform_id: int,
    platform_name: str,
    threshold_hours: int = 25,
) -> bool:
    """Check if a platform's scraped data is fresh (DB-based, no live request).

    Queries SELECT MAX(updated_at) FROM products WHERE platform_id = ? and
    compares to the threshold. Emits alert='platform_data_stale' via structlog
    when data is stale or absent.

    Never raises exceptions — errors are caught and logged.

    Args:
        db_path:         Path to the SQLite database file.
        platform_id:     Platform DB ID to check (e.g. 1 for Hotmart).
        platform_name:   Human-readable platform name for log context.
        threshold_hours: Hours after which data is considered stale (default 25).

    Returns:
        True if data is fresh, False if stale or absent.
    """
    import sqlite3
    from datetime import datetime, timezone, timedelta

    try:
        with sqlite3.connect(db_path) as conn:
            row = conn.execute(
                "SELECT MAX(updated_at) as last_update FROM products WHERE platform_id = ?",
                (platform_id,),
            ).fetchone()

        last_update_str = row[0] if row else None

        if not last_update_str:
            log.warning(
                "health.platform_canary.no_data",
                alert="platform_data_stale",
                platform=platform_name,
                platform_id=platform_id,
                last_update=None,
                threshold_hours=threshold_hours,
            )
            return False

        # Parse ISO format timestamp
        last_update = datetime.fromisoformat(last_update_str)
        # Ensure timezone-aware for comparison
        if last_update.tzinfo is None:
            last_update = last_update.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        threshold = timedelta(hours=threshold_hours)

        if (now - last_update) > threshold:
            log.warning(
                "health.platform_canary.stale",
                alert="platform_data_stale",
                platform=platform_name,
                platform_id=platform_id,
                last_update=last_update_str,
                hours_since_update=round((now - last_update).total_seconds() / 3600, 1),
                threshold_hours=threshold_hours,
            )
            return False

        log.info(
            "health.platform_canary.ok",
            platform=platform_name,
            platform_id=platform_id,
            last_update=last_update_str,
        )
        return True

    except Exception as exc:
        log.error(
            "health.platform_canary.error",
            alert="platform_data_stale",
            platform=platform_name,
            platform_id=platform_id,
            error=str(exc),
        )
        return False
