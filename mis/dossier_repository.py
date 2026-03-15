"""Dossier query layer for the MIS dashboard.

Provides read-only queries over the dossiers and products tables.

Functions:
    get_dossier_by_product_id — fetch a single dossier with parsed JSON fields
    list_dossiers_by_rank     — paginated list of products with dossier presence,
                                ordered by rank ASC by default
"""
from __future__ import annotations

import json

import structlog

from .db import get_db

log = structlog.get_logger(__name__)


def get_dossier_by_product_id(db_path: str, product_id: int) -> dict | None:
    """Fetch a dossier by its product_id, with JSON fields parsed.

    Args:
        db_path:    Path to the SQLite database file.
        product_id: Primary key of the product to look up.

    Returns:
        A dict representation of the dossier row with JSON string columns
        parsed into Python objects, or None if no dossier exists.

        Parsed columns (if present and non-null): dossier_json -> dossier,
        ads_json -> ads, copy_json -> copy, reviews_json -> reviews.
    """
    db = get_db(db_path)
    rows = list(
        db.execute(
            "SELECT * FROM dossiers WHERE product_id = ? LIMIT 1",
            [product_id],
        )
    )
    if not rows:
        return None

    # Convert row to dict using cursor description
    cursor = db.execute(
        "SELECT * FROM dossiers WHERE product_id = ? LIMIT 1",
        [product_id],
    )
    columns = [desc[0] for desc in cursor.description]
    row = cursor.fetchone()
    result = dict(zip(columns, row))

    # Parse JSON text columns
    for src_col, dest_key in [
        ("dossier_json", "dossier"),
        ("ads_json", "ads"),
        ("copy_json", "copy"),
        ("reviews_json", "reviews"),
    ]:
        if src_col in result and result[src_col]:
            try:
                result[dest_key] = json.loads(result[src_col])
            except (json.JSONDecodeError, TypeError):
                result[dest_key] = None

    return result


def list_dossiers_by_rank(
    db_path: str,
    platform: str | None = None,
    niche: str | None = None,
    order_by: str = "rank",
    order_dir: str = "asc",
    per_page: int = 20,
    page: int = 1,
) -> list[dict]:
    """List products with dossier presence, ordered by rank.

    Performs a LEFT JOIN between products and dossiers so products without
    a dossier are still returned (has_dossier=False). Joins platforms and
    niches to include human-readable names and slugs.

    Args:
        db_path:   Path to the SQLite database file.
        platform:  Optional platform slug to filter results.
        niche:     Optional niche slug to filter results.
        order_by:  Column to sort by (default: 'rank').
        order_dir: 'asc' or 'desc' (default: 'asc').
        per_page:  Number of results per page (default: 20).
        page:      1-based page number (default: 1).

    Returns:
        List of dicts with keys: id, title, url, platform_name, platform_slug,
        niche_name, niche_slug, rank, opportunity_score, confidence_score,
        has_dossier.
    """
    db = get_db(db_path)

    # Validate order direction to prevent SQL injection
    order_dir_safe = "ASC" if order_dir.lower() != "desc" else "DESC"

    params: list = []
    where_clauses: list[str] = []

    if platform:
        where_clauses.append("pl.slug = ?")
        params.append(platform)
    if niche:
        where_clauses.append("n.slug = ?")
        params.append(niche)

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    offset = (page - 1) * per_page

    sql = f"""
        SELECT
            p.id,
            p.title,
            p.url,
            pl.name  AS platform_name,
            pl.slug  AS platform_slug,
            n.name   AS niche_name,
            n.slug   AS niche_slug,
            p.rank,
            d.opportunity_score,
            d.confidence_score,
            CASE WHEN d.id IS NOT NULL THEN 1 ELSE 0 END AS has_dossier
        FROM products p
        JOIN platforms pl ON pl.id = p.platform_id
        JOIN niches    n  ON n.id  = p.niche_id
        LEFT JOIN dossiers d ON d.product_id = p.id
        {where_sql}
        ORDER BY p.{order_by} {order_dir_safe}
        LIMIT ? OFFSET ?
    """
    params.extend([per_page, offset])

    cursor = db.execute(sql, params)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    results = []
    for row in rows:
        item = dict(zip(columns, row))
        item["has_dossier"] = bool(item["has_dossier"])
        results.append(item)

    return results
