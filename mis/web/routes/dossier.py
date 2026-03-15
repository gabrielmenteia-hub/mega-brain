"""Dossier detail routes for the MIS dashboard."""
import sqlite3
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from mis import dossier_repository
from .ranking import is_htmx

router = APIRouter()

_VALID_TABS = {"visao-geral", "copy", "anuncios", "reviews", "template"}


def _tab_to_template(tab_name: str) -> str:
    """Convert tab slug to template filename."""
    return f"dossier_tab_{tab_name.replace('-', '_')}.html"


@router.get("/dossier/{product_id}", response_class=HTMLResponse)
async def dossier_detail(request: Request, product_id: int) -> HTMLResponse:
    """Return the dossier detail page for a product.

    Args:
        request:    FastAPI request object.
        product_id: Primary key of the product.

    Returns:
        HTML page with dossier info and tabs.

    Raises:
        HTTPException 404: If product does not exist.
    """
    db_path = request.app.state.db_path
    templates = request.app.state.templates

    # Fetch product with platform and niche info
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute(
            """
            SELECT p.*, pl.name AS platform_name, pl.slug AS platform_slug,
                   n.name AS niche_name, n.slug AS niche_slug
              FROM products p
              JOIN platforms pl ON pl.id = p.platform_id
              JOIN niches n ON n.id = p.niche_id
             WHERE p.id = ?
            """,
            [product_id],
        )
        row = cursor.fetchone()
    finally:
        conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    product = dict(row)

    # Fetch dossier (may be None if analysis not yet done)
    dossier = dossier_repository.get_dossier_by_product_id(db_path, product_id)

    # Prev / Next navigation by rank
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        prev_row = conn.execute(
            "SELECT id FROM products WHERE rank < ? ORDER BY rank DESC LIMIT 1",
            [product["rank"]],
        ).fetchone()
        next_row = conn.execute(
            "SELECT id FROM products WHERE rank > ? ORDER BY rank ASC LIMIT 1",
            [product["rank"]],
        ).fetchone()
    finally:
        conn.close()

    prev_id = prev_row["id"] if prev_row else None
    next_id = next_row["id"] if next_row else None

    # Active tab from query param
    active_tab = request.query_params.get("tab", "visao-geral")
    if active_tab not in _VALID_TABS:
        active_tab = "visao-geral"

    context = {
        "product": product,
        "dossier": dossier,
        "active_tab": active_tab,
        "prev_id": prev_id,
        "next_id": next_id,
        "tabs": [
            {"slug": "visao-geral", "label": "Visão Geral"},
            {"slug": "copy", "label": "Copy"},
            {"slug": "anuncios", "label": "Anúncios"},
            {"slug": "reviews", "label": "Reviews"},
            {"slug": "template", "label": "Template"},
        ],
    }

    return templates.TemplateResponse(
        request=request,
        name="dossier.html",
        context=context,
    )


@router.get("/dossier/{product_id}/tab/{tab_name}", response_class=HTMLResponse)
async def dossier_tab(
    request: Request, product_id: int, tab_name: str
) -> HTMLResponse:
    """Return a tab fragment for HTMX swap.

    Args:
        request:    FastAPI request object.
        product_id: Primary key of the product.
        tab_name:   Tab slug (visao-geral, copy, anuncios, reviews, template).

    Returns:
        HTML fragment for the requested tab.

    Raises:
        HTTPException 400: If tab_name is not valid.
    """
    if tab_name not in _VALID_TABS:
        raise HTTPException(status_code=400, detail=f"Tab inválida: {tab_name}")

    db_path = request.app.state.db_path
    templates = request.app.state.templates

    dossier = dossier_repository.get_dossier_by_product_id(db_path, product_id)

    # If product doesn't exist, still return partial with empty state
    context = {
        "dossier": dossier,
        "product_id": product_id,
    }

    template_name = _tab_to_template(tab_name)
    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context=context,
    )
