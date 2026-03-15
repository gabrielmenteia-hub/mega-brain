"""Alert persistence layer for the MIS dashboard.

Provides CRUD operations on the alerts table.

Functions:
    create_alert      — insert an alert (idempotent: 24h dedup on product_id+position)
    get_unseen_count  — count unseen, non-expired alerts
    mark_seen         — mark a single alert as seen
    expire_old_alerts — delete alerts whose expires_at has passed
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone, timedelta

import structlog

log = structlog.get_logger(__name__)


def create_alert(
    db_path: str,
    product_id: int,
    position: int,
    platform_slug: str | None = None,
    niche_slug: str | None = None,
) -> int:
    """Insert an alert for a product rank position.

    Idempotency: if an alert for the same (product_id, position) already exists
    within the last 24 hours, the existing id is returned without inserting.

    Args:
        db_path:       Path to the SQLite database file.
        product_id:    FK to products.id.
        position:      Rank position at the time of the alert.
        platform_slug: Optional slug of the platform (e.g. 'hotmart').
        niche_slug:    Optional slug of the niche (e.g. 'emagrecimento').

    Returns:
        The id of the inserted (or existing duplicate) alert row.
    """
    now = datetime.now(timezone.utc)
    cutoff_24h = (now - timedelta(hours=24)).isoformat()
    now_iso = now.isoformat()
    expires_iso = (now + timedelta(days=7)).isoformat()

    with sqlite3.connect(db_path) as conn:
        # Idempotency check: existing alert within 24h for same product+position
        row = conn.execute(
            "SELECT id FROM alerts "
            "WHERE product_id = ? AND position = ? AND created_at >= ?",
            [product_id, position, cutoff_24h],
        ).fetchone()
        if row:
            log.debug(
                "alert_repository.create_alert.duplicate_skipped",
                product_id=product_id,
                position=position,
                existing_id=row[0],
            )
            return row[0]

        cursor = conn.execute(
            "INSERT INTO alerts "
            "(product_id, platform_slug, niche_slug, position, seen, created_at, expires_at) "
            "VALUES (?, ?, ?, ?, 0, ?, ?)",
            [product_id, platform_slug, niche_slug, position, now_iso, expires_iso],
        )
        conn.commit()
        alert_id = cursor.lastrowid

    log.info(
        "alert_repository.create_alert.inserted",
        alert_id=alert_id,
        product_id=product_id,
        position=position,
    )
    return alert_id


def get_unseen_count(db_path: str) -> int:
    """Return the number of unseen, non-expired alerts.

    Args:
        db_path: Path to the SQLite database file.

    Returns:
        Count of alerts where seen=0 and expires_at > now.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT COUNT(*) FROM alerts WHERE seen = 0 AND expires_at > ?",
            [now_iso],
        ).fetchone()
    return row[0] if row else 0


def mark_seen(db_path: str, alert_id: int) -> bool:
    """Mark an alert as seen.

    Args:
        db_path:  Path to the SQLite database file.
        alert_id: Primary key of the alert to update.

    Returns:
        True if the alert was found and updated, False otherwise.
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            "UPDATE alerts SET seen = 1 WHERE id = ?",
            [alert_id],
        )
        conn.commit()
        updated = cursor.rowcount > 0

    if updated:
        log.info("alert_repository.mark_seen", alert_id=alert_id)
    else:
        log.warning("alert_repository.mark_seen.not_found", alert_id=alert_id)
    return updated


def expire_old_alerts(db_path: str) -> int:
    """Delete alerts whose expires_at timestamp has passed.

    Args:
        db_path: Path to the SQLite database file.

    Returns:
        Number of alerts deleted.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            "DELETE FROM alerts WHERE expires_at < ?",
            [now_iso],
        )
        conn.commit()
        deleted = cursor.rowcount

    if deleted:
        log.info("alert_repository.expire_old_alerts.deleted", count=deleted)
    return deleted
