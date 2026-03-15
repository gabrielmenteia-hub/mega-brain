"""Alert routes for the MIS dashboard.

Provides:
- GET /alerts       — full alerts page with seen/unseen list
- GET /alerts/badge — HTMX fragment for navbar badge with unseen count
- POST /alerts/{alert_id}/mark-seen — mark an alert as seen, redirect to /alerts
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from mis.alert_repository import expire_old_alerts, get_unseen_count, mark_seen
from mis.db import get_db

router = APIRouter()


@router.get("/alerts")
async def alerts_page(request: Request):
    """Render the alerts list page.

    Expires stale alerts before rendering, then queries all alerts joined
    with their product info, ordered newest first.
    """
    db_path: str = request.app.state.db_path
    templates = request.app.state.templates

    expire_old_alerts(db_path)

    db = get_db(db_path)
    rows = list(
        db.execute(
            """
            SELECT a.id,
                   a.product_id,
                   a.platform_slug,
                   a.niche_slug,
                   a.position,
                   a.seen,
                   a.created_at,
                   p.title  AS product_title,
                   p.url    AS product_url
              FROM alerts a
              JOIN products p ON p.id = a.product_id
             ORDER BY a.created_at DESC
            """
        )
    )

    col_names = [
        "id", "product_id", "platform_slug", "niche_slug",
        "position", "seen", "created_at", "product_title", "product_url",
    ]
    alerts = [dict(zip(col_names, row)) for row in rows]

    unseen_count = get_unseen_count(db_path)

    return templates.TemplateResponse(
        "alerts.html",
        {
            "request": request,
            "alerts": alerts,
            "unseen_count": unseen_count,
        },
    )


@router.get("/alerts/badge")
async def alerts_badge(request: Request):
    """Return the HTMX badge fragment with the current unseen alert count.

    Always returns a fragment (no base.html extension) so HTMX can swap
    the outer span via hx-swap="outerHTML".
    """
    db_path: str = request.app.state.db_path
    templates = request.app.state.templates

    unseen_count = get_unseen_count(db_path)

    return templates.TemplateResponse(
        "alerts_badge.html",
        {
            "request": request,
            "unseen_count": unseen_count,
        },
    )


@router.post("/alerts/{alert_id}/mark-seen")
async def mark_alert_seen(alert_id: int, request: Request):
    """Mark a single alert as seen and redirect back to the alerts page.

    Returns:
        303 redirect to /alerts on success.
        404 if the alert_id does not exist.
    """
    db_path: str = request.app.state.db_path

    found = mark_seen(db_path, alert_id)
    if not found:
        raise HTTPException(status_code=404, detail="Alert not found")

    return RedirectResponse("/alerts", status_code=303)
