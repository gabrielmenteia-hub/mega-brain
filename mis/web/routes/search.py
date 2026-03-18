"""Search routes for the MIS dashboard (v3.0 manual search)."""
import asyncio

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from mis.niche_repository import list_niches, list_subniches
from mis.search_orchestrator import cancel_task, register_task, run_manual_search
from mis.search_repository import (
    create_session,
    delete_session,
    get_session,
    list_recent_sessions,
    list_session_products,
)

router = APIRouter()


def is_htmx(request: Request) -> bool:
    """Return True if the request was made by HTMX."""
    return request.headers.get("HX-Request") == "true"


# ---------------------------------------------------------------------------
# GET /pesquisar — main search page
# ---------------------------------------------------------------------------


@router.get("/pesquisar", response_class=HTMLResponse)
async def pesquisar(
    request: Request,
    niche: str | None = None,
    subniche: str | None = None,
) -> HTMLResponse:
    """Return the main search page with nicho/subnicho form and recent sessions."""
    db_path = request.app.state.db_path
    templates = request.app.state.templates

    niches = list_niches(db_path)
    recentes = list_recent_sessions(db_path, limit=10)

    return templates.TemplateResponse(
        request=request,
        name="pesquisar.html",
        context={
            "niches": niches,
            "recentes": recentes,
            "selected_niche": niche,
            "selected_subniche": subniche,
        },
    )


# ---------------------------------------------------------------------------
# GET /pesquisar/subniches — HTMX partial for subniche select options
# ---------------------------------------------------------------------------


@router.get("/pesquisar/subniches", response_class=HTMLResponse)
async def pesquisar_subniches(
    request: Request,
    niche_slug: str = "",
) -> HTMLResponse:
    """Return <option> elements for the subniche select (HTMX partial)."""
    db_path = request.app.state.db_path

    if not niche_slug:
        return HTMLResponse("")

    subniches = list_subniches(db_path, niche_slug)
    options = "".join(
        f'<option value="{s["id"]}">{s["name"]}</option>' for s in subniches
    )
    return HTMLResponse(options)


# ---------------------------------------------------------------------------
# POST /search/run — creates session and starts scan
# ---------------------------------------------------------------------------


@router.post("/search/run")
async def search_run(
    request: Request,
    subniche_id: int = Form(...),
) -> RedirectResponse:
    """Create a search session and launch async scan.

    If a session is already running for the same subniche, redirect to it
    without creating a new session.
    """
    db_path = request.app.state.db_path

    # Check for existing running session
    sessions = list_recent_sessions(db_path)
    running = next(
        (
            s
            for s in sessions
            if s["subniche_id"] == subniche_id and s["status"] == "running"
        ),
        None,
    )

    if running:
        return RedirectResponse(
            url=f"/search/{running['id']}/status", status_code=302
        )

    # Create new session and launch async scan
    session_id = create_session(db_path, subniche_id)
    task = asyncio.create_task(run_manual_search(session_id, subniche_id, db_path))
    register_task(session_id, task)

    return RedirectResponse(url=f"/search/{session_id}/status", status_code=302)


# ---------------------------------------------------------------------------
# GET /search/{session_id}/status — progress page
# ---------------------------------------------------------------------------


@router.get("/search/{session_id}/status", response_class=HTMLResponse)
async def search_status(
    request: Request,
    session_id: int,
) -> HTMLResponse:
    """Return the status page for a search session, or redirect if done."""
    db_path = request.app.state.db_path
    templates = request.app.state.templates

    session = get_session(db_path, session_id)
    if session is None:
        return RedirectResponse(url="/pesquisar", status_code=302)

    if session["status"] in ("done", "timeout", "cancelled"):
        return RedirectResponse(
            url=f"/search/{session_id}/results", status_code=302
        )

    # Get subniche name for display
    niches = list_niches(db_path)
    subniche_name = ""
    niche_name = ""
    for niche in niches:
        subniches = list_subniches(db_path, niche["slug"])
        for s in subniches:
            if s["id"] == session["subniche_id"]:
                subniche_name = s["name"]
                niche_name = niche["name"]
                break
        if subniche_name:
            break

    return templates.TemplateResponse(
        request=request,
        name="search_status.html",
        context={
            "session": session,
            "subniche_name": subniche_name,
            "niche_name": niche_name,
        },
    )


# ---------------------------------------------------------------------------
# GET /search/{session_id}/status/poll — HTMX polling partial
# ---------------------------------------------------------------------------


@router.get("/search/{session_id}/status/poll", response_class=HTMLResponse)
async def search_status_poll(
    request: Request,
    session_id: int,
) -> HTMLResponse:
    """Return the polling partial. On completion, send HX-Redirect header."""
    db_path = request.app.state.db_path
    templates = request.app.state.templates

    session = get_session(db_path, session_id)
    if session is None:
        # Session not found — redirect to search list
        response = HTMLResponse("")
        response.headers["HX-Redirect"] = "/pesquisar"
        return response

    if session["status"] in ("done", "timeout", "cancelled"):
        response = HTMLResponse("")
        response.headers["HX-Redirect"] = f"/search/{session_id}/results"
        return response

    return templates.TemplateResponse(
        request=request,
        name="search_status_poll.html",
        context={"session": session},
    )


# ---------------------------------------------------------------------------
# GET /search/{session_id}/results — results page
# ---------------------------------------------------------------------------


@router.get("/search/{session_id}/results", response_class=HTMLResponse)
async def search_results(
    request: Request,
    session_id: int,
    platform: str | None = None,
) -> HTMLResponse:
    """Return the results page (or table partial for HTMX)."""
    db_path = request.app.state.db_path
    templates = request.app.state.templates

    session = get_session(db_path, session_id)
    if session is None:
        return RedirectResponse(url="/pesquisar", status_code=302)

    products = list_session_products(
        db_path,
        session_id,
        platform_filter=platform,
        limit=20,
        offset=0,
    )

    # Build breadcrumb context: find subniche name + niche for back link
    niches = list_niches(db_path)
    subniche_name = ""
    niche_slug = ""
    subniche_slug = ""
    for niche in niches:
        subniches = list_subniches(db_path, niche["slug"])
        for s in subniches:
            if s["id"] == session["subniche_id"]:
                subniche_name = s["name"]
                niche_slug = niche["slug"]
                subniche_slug = s["slug"]
                break
        if subniche_name:
            break

    # Count platforms with products
    platforms_with_products = set(p["platform_slug"] for p in products)
    platform_statuses = session.get("platform_statuses", {})
    total_platforms_done = len(
        [s for s in platform_statuses.values() if s in ("done", "error")]
    )
    platforms_ok = len(
        [s for s in platform_statuses.values() if s == "done"]
    )

    # Get unique platforms for filter dropdown
    all_products = list_session_products(db_path, session_id, limit=1000, offset=0)
    available_platforms = []
    seen = set()
    for p in all_products:
        slug = p["platform_slug"]
        if slug not in seen:
            seen.add(slug)
            available_platforms.append(
                {"slug": slug, "name": p["platform_name"]}
            )

    context = {
        "session": session,
        "products": products,
        "subniche_name": subniche_name,
        "niche_slug": niche_slug,
        "subniche_slug": subniche_slug,
        "selected_platform": platform,
        "available_platforms": available_platforms,
        "platforms_ok": platforms_ok,
        "total_platforms_done": total_platforms_done,
        "per_page": 20,
    }

    if is_htmx(request):
        return templates.TemplateResponse(
            request=request,
            name="search_results_table.html",
            context=context,
        )

    return templates.TemplateResponse(
        request=request,
        name="search_results.html",
        context=context,
    )


# ---------------------------------------------------------------------------
# GET /search/{session_id}/results/table — always returns table partial
# ---------------------------------------------------------------------------


@router.get("/search/{session_id}/results/table", response_class=HTMLResponse)
async def search_results_table(
    request: Request,
    session_id: int,
    platform: str | None = None,
) -> HTMLResponse:
    """Return the results table partial (always, regardless of HX-Request)."""
    db_path = request.app.state.db_path
    templates = request.app.state.templates

    session = get_session(db_path, session_id)
    if session is None:
        return HTMLResponse("<p class='text-gray-400'>Sessão não encontrada.</p>")

    products = list_session_products(
        db_path,
        session_id,
        platform_filter=platform,
        limit=20,
        offset=0,
    )

    return templates.TemplateResponse(
        request=request,
        name="search_results_table.html",
        context={
            "session": session,
            "products": products,
            "selected_platform": platform,
            "per_page": 20,
        },
    )


# ---------------------------------------------------------------------------
# DELETE /search/{session_id} — cancel + delete session
# ---------------------------------------------------------------------------


@router.delete("/search/{session_id}")
async def search_delete(
    request: Request,
    session_id: int,
) -> RedirectResponse:
    """Cancel running task (if any) and delete the session."""
    db_path = request.app.state.db_path

    cancel_task(session_id)
    try:
        delete_session(db_path, session_id)
    except Exception:
        pass  # Non-existent session — redirect anyway

    response = RedirectResponse(url="/pesquisar", status_code=302)
    response.headers["HX-Trigger"] = '{"showToast": "Pesquisa removida"}'
    return response
