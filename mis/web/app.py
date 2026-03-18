"""FastAPI application factory for the MIS dashboard."""
from contextlib import asynccontextmanager
from pathlib import Path

import structlog
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from mis.config import load_config
from mis.db import run_migrations
from mis.health_monitor import register_canary_job, register_platform_canary_jobs, run_schema_integrity_check
from mis.radar import register_radar_jobs
from mis.scheduler import get_scheduler, register_scan_and_spy_job
from mis.search_repository import mark_stale_running_sessions
from mis.web.routes.alerts import router as alerts_router
from mis.web.routes.dossier import router as dossier_router
from mis.web.routes.feed import router as feed_router
from mis.web.routes.health import router as health_router
from mis.web.routes.ranking import router as ranking_router
from mis.web.routes.search import router as search_router

TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"

_log = structlog.get_logger(__name__)


def create_app(db_path: str, start_scheduler: bool = True) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        db_path:         Path to the SQLite database file.  Pass ':memory:' to skip
                         migrations (useful for import-time tests where schema is
                         already applied or not needed).
        start_scheduler: When False, suppresses APScheduler job registration and
                         startup. Useful for v3.0 manual-search mode and tests.
                         The startup hook (mark_stale_running_sessions) always runs
                         regardless of this flag.

    Returns:
        Configured FastAPI application instance.
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup: mark any sessions left in 'running' state as 'timeout'
        # (crash recovery — runs regardless of start_scheduler flag)
        if db_path != ":memory:":
            try:
                count = mark_stale_running_sessions(db_path)
                if count:
                    _log.info("lifespan.stale_sessions_marked_timeout", count=count)
            except Exception as exc:
                _log.warning("lifespan.stale_sessions_error", error=str(exc))

        if start_scheduler:
            # Startup: load config, register jobs, start scheduler
            try:
                config = load_config()
            except Exception as exc:
                _log.warning("lifespan.config_error", error=str(exc))
                config = {}

            try:
                await run_schema_integrity_check(db_path)
            except Exception as exc:
                _log.warning("lifespan.schema_check_failed", error=str(exc))

            for name, fn, args in [
                ("register_scan_and_spy_job", register_scan_and_spy_job, [config]),
                ("register_radar_jobs", register_radar_jobs, [config]),
                ("register_canary_job", register_canary_job, []),
                ("register_platform_canary_jobs", register_platform_canary_jobs, [db_path]),
            ]:
                try:
                    fn(*args)
                except Exception as exc:
                    _log.warning("lifespan.register_failed", job=name, error=str(exc))

            try:
                get_scheduler().start()
                _log.info("lifespan.scheduler_started")
            except Exception as exc:
                _log.warning("lifespan.scheduler_start_failed", error=str(exc))

        yield

        # Teardown: cancel all running manual search tasks
        try:
            from mis.search_orchestrator import _TASK_REGISTRY
            for task in list(_TASK_REGISTRY.values()):
                if not task.done():
                    task.cancel()
            _TASK_REGISTRY.clear()
        except Exception as exc:
            _log.warning("lifespan.search_task_cancel_failed", error=str(exc))

        # Teardown: stop scheduler
        if start_scheduler:
            try:
                get_scheduler().shutdown(wait=False)
                _log.info("lifespan.scheduler_stopped")
            except Exception as exc:
                _log.warning("lifespan.scheduler_stop_failed", error=str(exc))

    app = FastAPI(
        title="MIS Dashboard",
        docs_url=None,
        redoc_url=None,
        lifespan=lifespan,
    )

    # Run migrations at startup (skip for :memory: — separate connections
    # would each get an empty in-memory DB; callers should run run_migrations
    # themselves on a real file path before creating the app)
    if db_path != ":memory:":
        run_migrations(db_path)

    # Shared state
    app.state.db_path = db_path
    app.state.templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

    # Static files
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    # Routers
    app.include_router(ranking_router)
    app.include_router(dossier_router)
    app.include_router(feed_router)
    app.include_router(alerts_router)
    app.include_router(health_router)
    app.include_router(search_router)

    @app.get("/", include_in_schema=False)
    async def root():
        return RedirectResponse(url="/ranking", status_code=302)

    return app
