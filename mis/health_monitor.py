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
