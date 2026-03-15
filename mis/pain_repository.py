"""Pain report query layer for the MIS dashboard.

Provides read-only queries over the pain_reports and pain_signals tables.

Functions:
    get_latest_report      — fetch the most recent report for a niche
    get_historical_reports — list past report cycles for a niche (no report_json)
"""
from __future__ import annotations

import json

import structlog

from .db import get_db

log = structlog.get_logger(__name__)


def get_latest_report(db_path: str, niche_id: int) -> dict | None:
    """Fetch the most recent pain report for a niche.

    Args:
        db_path:  Path to the SQLite database file.
        niche_id: Primary key of the niche in the niches table.

    Returns:
        A dict with all pain_report columns, plus:
            report (parsed from report_json),
            signal_count (count of pain_signals collected since cycle_at).
        Returns None if no report exists for the niche.
    """
    db = get_db(db_path)

    cursor = db.execute(
        """
        SELECT pr.*
          FROM pain_reports pr
         WHERE pr.niche_id = ?
         ORDER BY pr.cycle_at DESC
         LIMIT 1
        """,
        [niche_id],
    )
    columns = [desc[0] for desc in cursor.description]
    row = cursor.fetchone()

    if row is None:
        return None

    result = dict(zip(columns, row))

    # Parse report_json into result["report"]
    if result.get("report_json"):
        try:
            result["report"] = json.loads(result["report_json"])
        except (json.JSONDecodeError, TypeError):
            result["report"] = None

    # Count pain_signals collected since this cycle
    # pain_signals uses niche_slug; resolve it from niches table
    niche_row = db.execute(
        "SELECT slug FROM niches WHERE id = ?", [niche_id]
    ).fetchone()
    if niche_row:
        niche_slug = niche_row[0]
        count_row = db.execute(
            "SELECT COUNT(*) FROM pain_signals "
            "WHERE niche_slug = ? AND collected_at >= ?",
            [niche_slug, result["cycle_at"]],
        ).fetchone()
        result["signal_count"] = count_row[0] if count_row else 0
    else:
        result["signal_count"] = 0

    return result


def get_historical_reports(
    db_path: str,
    niche_id: int,
    limit: int = 48,
) -> list[dict]:
    """List past pain report cycles for a niche without the full report payload.

    This is used for the cycle selector in the dashboard — callers only need
    the id and cycle_at to build a dropdown list. Skips report_json to keep
    the response lightweight.

    Args:
        db_path:  Path to the SQLite database file.
        niche_id: Primary key of the niche in the niches table.
        limit:    Maximum number of reports to return (default: 48).

    Returns:
        List of dicts with keys {id, cycle_at}, ordered newest-first.
    """
    db = get_db(db_path)

    cursor = db.execute(
        """
        SELECT pr.id, pr.cycle_at
          FROM pain_reports pr
         WHERE pr.niche_id = ?
         ORDER BY pr.cycle_at DESC
         LIMIT ?
        """,
        [niche_id, limit],
    )
    rows = cursor.fetchall()
    return [{"id": row[0], "cycle_at": row[1]} for row in rows]
