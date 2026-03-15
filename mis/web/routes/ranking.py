"""Ranking routes for the MIS dashboard."""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from mis import dossier_repository

router = APIRouter()


def is_htmx(request: Request) -> bool:
    """Return True if the request was made by HTMX."""
    return request.headers.get("HX-Request") == "true"


def _get_ranking_context(
    db_path: str,
    platform: str | None,
    niche: str | None,
    order_by: str,
    order_dir: str,
    per_page: int,
    page: int,
) -> dict:
    """Build context dict shared by ranking and ranking_table routes."""
    from mis.db import get_db

    products = dossier_repository.list_dossiers_by_rank(
        db_path,
        platform=platform,
        niche=niche,
        order_by=order_by,
        order_dir=order_dir,
        per_page=per_page,
        page=page,
    )

    db = get_db(db_path)

    # Fetch available platforms
    try:
        platforms = list(
            db.execute("SELECT DISTINCT slug, name FROM platforms ORDER BY name")
        )
        platforms = [{"slug": row[0], "name": row[1]} for row in platforms]
    except Exception:
        platforms = []

    # Fetch available niches
    try:
        niches = list(
            db.execute("SELECT DISTINCT slug, name FROM niches ORDER BY name")
        )
        niches = [{"slug": row[0], "name": row[1]} for row in niches]
    except Exception:
        niches = []

    # Last updated timestamp
    try:
        row = db.execute("SELECT MAX(updated_at) FROM products").fetchone()
        last_updated = row[0] if row else None
    except Exception:
        last_updated = None

    return {
        "products": products,
        "platforms": platforms,
        "niches": niches,
        "last_updated": last_updated,
        "selected_platform": platform,
        "selected_niche": niche,
        "per_page": per_page,
        "page": page,
    }


@router.get("/ranking", response_class=HTMLResponse)
async def ranking(
    request: Request,
    platform: str | None = None,
    niche: str | None = None,
    order_by: str = "rank",
    order_dir: str = "asc",
    per_page: int = 20,
    page: int = 1,
) -> HTMLResponse:
    """Return the ranking page or ranking_table partial for HTMX."""
    db_path = request.app.state.db_path
    templates = request.app.state.templates

    context = _get_ranking_context(
        db_path, platform, niche, order_by, order_dir, per_page, page
    )

    if is_htmx(request):
        return templates.TemplateResponse(
            request=request,
            name="ranking_table.html",
            context=context,
        )

    return templates.TemplateResponse(
        request=request,
        name="ranking.html",
        context=context,
    )


@router.get("/ranking/table", response_class=HTMLResponse)
async def ranking_table(
    request: Request,
    platform: str | None = None,
    niche: str | None = None,
    order_by: str = "rank",
    order_dir: str = "asc",
    per_page: int = 20,
    page: int = 1,
) -> HTMLResponse:
    """Return ranking_table partial — always without base layout."""
    db_path = request.app.state.db_path
    templates = request.app.state.templates

    context = _get_ranking_context(
        db_path, platform, niche, order_by, order_dir, per_page, page
    )

    return templates.TemplateResponse(
        request=request,
        name="ranking_table.html",
        context=context,
    )
