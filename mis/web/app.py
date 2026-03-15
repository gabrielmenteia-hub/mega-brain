"""FastAPI application factory for the MIS dashboard."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from mis.db import run_migrations
from mis.web.routes.health import router as health_router
from mis.web.routes.ranking import router as ranking_router

TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"


def create_app(db_path: str) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        db_path: Path to the SQLite database file.  Pass ':memory:' to skip
                 migrations (useful for import-time tests where schema is
                 already applied or not needed).

    Returns:
        Configured FastAPI application instance.
    """
    app = FastAPI(
        title="MIS Dashboard",
        docs_url=None,
        redoc_url=None,
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
    app.include_router(health_router)

    @app.get("/", include_in_schema=False)
    async def root():
        return RedirectResponse(url="/ranking", status_code=302)

    return app
