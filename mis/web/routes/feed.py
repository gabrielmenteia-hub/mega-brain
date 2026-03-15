"""Feed routes for the MIS pain dashboard."""
import sqlite3
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from mis import pain_repository
from .ranking import is_htmx

router = APIRouter()


def _compute_time_ago(cycle_at: str) -> str:
    """Return a human-readable 'time ago' string from an ISO timestamp.

    Args:
        cycle_at: ISO 8601 timestamp string (e.g. '2026-03-15T10:00:00Z').

    Returns:
        String like 'há 2h 15min' or 'há 45 minutos'.
    """
    now = datetime.now(timezone.utc)
    cycle_dt = datetime.fromisoformat(cycle_at.replace("Z", "+00:00"))
    delta = now - cycle_dt
    hours = int(delta.total_seconds() // 3600)
    minutes = int((delta.total_seconds() % 3600) // 60)
    return f"há {hours}h {minutes}min" if hours > 0 else f"há {minutes} minutos"


def _get_niches(db_path: str) -> list[dict]:
    """Fetch all available niches from the DB.

    Returns:
        List of dicts with keys {id, slug, name}.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT id, slug, name FROM niches ORDER BY name"
        ).fetchall()
        return [dict(row) for row in rows]
    except Exception:
        return []
    finally:
        conn.close()


def _niche_id_for_slug(db_path: str, slug: str) -> Optional[int]:
    """Return the niche_id for a given slug, or None if not found."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT id FROM niches WHERE slug = ? LIMIT 1", [slug]
        ).fetchone()
        return row["id"] if row else None
    except Exception:
        return None
    finally:
        conn.close()


@router.get("/feed", response_class=HTMLResponse)
async def feed(
    request: Request,
    niche: Optional[str] = None,
    report_id: Optional[int] = None,
) -> HTMLResponse:
    """Return the feed page showing pain reports by niche.

    Args:
        request:   FastAPI request object.
        niche:     Optional niche slug to activate on load.
        report_id: Optional specific report ID to load.

    Returns:
        Full HTML feed page.
    """
    db_path = request.app.state.db_path
    templates = request.app.state.templates

    niches = _get_niches(db_path)

    # Determine active niche
    active_niche_slug = niche or (niches[0]["slug"] if niches else None)

    # Load reports for each niche (just latest, for tab hints)
    report = None
    time_ago = None
    history = []

    if active_niche_slug:
        niche_id = _niche_id_for_slug(db_path, active_niche_slug)
        if niche_id is not None:
            report = pain_repository.get_latest_report(db_path, niche_id)
            history = pain_repository.get_historical_reports(db_path, niche_id, limit=48)
            if report and report.get("cycle_at"):
                time_ago = _compute_time_ago(report["cycle_at"])

    context = {
        "niches": niches,
        "active_niche": active_niche_slug,
        "report": report,
        "time_ago": time_ago,
        "history": history,
        "niche_slug": active_niche_slug,
    }

    return templates.TemplateResponse(
        request=request,
        name="feed.html",
        context=context,
    )


@router.get("/feed/niche/{niche_slug}", response_class=HTMLResponse)
async def feed_niche(
    request: Request,
    niche_slug: str,
    report_id: Optional[int] = None,
) -> HTMLResponse:
    """Return the feed page or partial for a specific niche.

    Args:
        request:    FastAPI request object.
        niche_slug: Niche slug to load.
        report_id:  Optional specific report ID to display.

    Returns:
        HTML fragment (HTMX partial) if HX-Request header present, else full page.
    """
    db_path = request.app.state.db_path
    templates = request.app.state.templates

    niche_id = _niche_id_for_slug(db_path, niche_slug)

    report = None
    time_ago = None
    history = []

    if niche_id is not None:
        if report_id:
            # Load specific historical report
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            try:
                import json
                row = conn.execute(
                    "SELECT * FROM pain_reports WHERE id = ? AND niche_id = ? LIMIT 1",
                    [report_id, niche_id],
                ).fetchone()
                if row:
                    report = dict(row)
                    if report.get("report_json"):
                        try:
                            report["report"] = json.loads(report["report_json"])
                        except (json.JSONDecodeError, TypeError):
                            report["report"] = None
                    # signal_count for this historical report
                    count_row = conn.execute(
                        "SELECT COUNT(*) FROM pain_signals WHERE niche_slug = ? AND collected_at >= ?",
                        [niche_slug, report["cycle_at"]],
                    ).fetchone()
                    report["signal_count"] = count_row[0] if count_row else 0
            finally:
                conn.close()
        else:
            report = pain_repository.get_latest_report(db_path, niche_id)

        history = pain_repository.get_historical_reports(db_path, niche_id, limit=48)

    if report and report.get("cycle_at"):
        time_ago = _compute_time_ago(report["cycle_at"])

    context = {
        "report": report,
        "time_ago": time_ago,
        "history": history,
        "niche_slug": niche_slug,
    }

    if is_htmx(request):
        return templates.TemplateResponse(
            request=request,
            name="feed_report.html",
            context=context,
        )

    # Full page — also need niches list
    niches = _get_niches(db_path)
    context["niches"] = niches
    context["active_niche"] = niche_slug

    return templates.TemplateResponse(
        request=request,
        name="feed.html",
        context=context,
    )
