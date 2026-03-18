"""CRUD functions for search_sessions and search_session_products.

All functions accept a db_path string as their first argument and use
get_db() for connections (ensures PRAGMA foreign_keys=ON for CASCADE deletes).

Exported functions:
    create_session              - INSERT new session with status='pending'
    get_session                 - SELECT session by id (platform_statuses deserialized)
    update_session_status       - UPDATE status / platform_statuses / product_count
    list_recent_sessions        - SELECT recent sessions ordered by started_at DESC
    list_session_products       - SELECT products linked to a session (with JOIN)
    delete_session              - DELETE session (CASCADE removes linked products)
    mark_stale_running_sessions - UPDATE running→timeout for crash recovery
"""
import json
from datetime import datetime, timezone

from .db import get_db


def _now_iso() -> str:
    """Return current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


def create_session(db_path: str, subniche_id: int) -> int:
    """Insert a new search session with status='pending'.

    Args:
        db_path:    Path to the SQLite database file.
        subniche_id: FK to the subniches table.

    Returns:
        The integer primary key (id) of the newly created session.
    """
    db = get_db(db_path)
    db.execute(
        """
        INSERT INTO search_sessions (subniche_id, status, started_at)
        VALUES (?, 'pending', ?)
        """,
        [subniche_id, _now_iso()],
    )
    return db.execute("SELECT last_insert_rowid()").fetchone()[0]


def get_session(db_path: str, session_id: int) -> dict | None:
    """Return a session dict by id, or None if not found.

    The platform_statuses column is stored as JSON TEXT in SQLite.
    This function deserializes it to a Python dict before returning.

    Args:
        db_path:    Path to the SQLite database file.
        session_id: Primary key of the session to fetch.

    Returns:
        Dict with keys: id, subniche_id, status, platform_statuses (dict),
        started_at, finished_at, product_count. None if no row found.
    """
    db = get_db(db_path)
    row = db.execute(
        "SELECT id, subniche_id, status, platform_statuses, "
        "started_at, finished_at, product_count "
        "FROM search_sessions WHERE id = ?",
        [session_id],
    ).fetchone()
    if row is None:
        return None
    return {
        "id": row[0],
        "subniche_id": row[1],
        "status": row[2],
        "platform_statuses": json.loads(row[3] or "{}"),
        "started_at": row[4],
        "finished_at": row[5],
        "product_count": row[6],
    }


def update_session_status(
    db_path: str,
    session_id: int,
    status: str,
    platform_statuses: dict,
    product_count: int,
) -> None:
    """Update the status, platform_statuses, and product_count of a session.

    Sets finished_at to the current UTC time when status is one of:
    'done', 'timeout', 'cancelled'.

    Args:
        db_path:           Path to the SQLite database file.
        session_id:        Session to update.
        status:            New status string (e.g. 'running', 'done', 'timeout').
        platform_statuses: Dict mapping platform slug → status string.
        product_count:     Total number of products found in this session.
    """
    terminal_statuses = {"done", "timeout", "cancelled"}
    finished_at = _now_iso() if status in terminal_statuses else None

    db = get_db(db_path)
    db.execute(
        """
        UPDATE search_sessions
           SET status            = ?,
               platform_statuses = ?,
               product_count     = ?,
               finished_at       = ?
         WHERE id = ?
        """,
        [status, json.dumps(platform_statuses), product_count, finished_at, session_id],
    )


def list_recent_sessions(db_path: str, limit: int = 20) -> list[dict]:
    """Return the most recent sessions ordered by started_at DESC.

    Joins with subniches to expose subniche_name for template rendering.

    Args:
        db_path: Path to the SQLite database file.
        limit:   Maximum number of sessions to return (default 20).

    Returns:
        List of dicts with keys: id, subniche_id, subniche_name, status,
        platform_statuses (dict), started_at, finished_at, product_count.
    """
    db = get_db(db_path)
    rows = db.execute(
        """
        SELECT ss.id,
               ss.subniche_id,
               s.name AS subniche_name,
               ss.status,
               ss.platform_statuses,
               ss.started_at,
               ss.finished_at,
               ss.product_count
          FROM search_sessions ss
          LEFT JOIN subniches s ON s.id = ss.subniche_id
         ORDER BY ss.started_at DESC
         LIMIT ?
        """,
        [limit],
    ).fetchall()
    return [
        {
            "id": r[0],
            "subniche_id": r[1],
            "subniche_name": r[2],
            "status": r[3],
            "platform_statuses": json.loads(r[4] or "{}"),
            "started_at": r[5],
            "finished_at": r[6],
            "product_count": r[7],
        }
        for r in rows
    ]


def list_session_products(
    db_path: str,
    session_id: int,
    platform_filter: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    """Return products linked to a session with JOIN data from products/platforms.

    Args:
        db_path:         Path to the SQLite database file.
        session_id:      Session whose products to list.
        platform_filter: Optional platform slug to narrow results.
        limit:           Max rows to return (default 100).
        offset:          Row offset for pagination (default 0).

    Returns:
        List of dicts with keys: rank_at_scan, platform_slug (from ssp),
        title, url, price, commission_pct, thumbnail_url, platform_name.
    """
    db = get_db(db_path)
    params: list = [session_id]
    platform_clause = ""
    if platform_filter:
        platform_clause = "AND ssp.platform_slug = ?"
        params.append(platform_filter)
    params.extend([limit, offset])

    rows = db.execute(
        f"""
        SELECT ssp.rank_at_scan,
               ssp.platform_slug,
               p.title,
               p.url,
               p.price,
               p.commission_pct,
               p.thumbnail_url,
               pl.name AS platform_name
          FROM search_session_products ssp
          JOIN products  p  ON p.id  = ssp.product_id
          JOIN platforms pl ON pl.id = p.platform_id
         WHERE ssp.session_id = ?
           {platform_clause}
         ORDER BY ssp.rank_at_scan ASC
         LIMIT ? OFFSET ?
        """,
        params,
    ).fetchall()
    return [
        {
            "rank_at_scan": r[0],
            "platform_slug": r[1],
            "title": r[2],
            "url": r[3],
            "price": r[4],
            "commission_pct": r[5],
            "thumbnail_url": r[6],
            "platform_name": r[7],
        }
        for r in rows
    ]


def delete_session(db_path: str, session_id: int) -> None:
    """Delete a session by id.

    Uses get_db() (which sets PRAGMA foreign_keys=ON) so that the
    ON DELETE CASCADE on search_session_products fires correctly.

    Args:
        db_path:    Path to the SQLite database file.
        session_id: Session to delete.
    """
    db = get_db(db_path)
    db.execute("DELETE FROM search_sessions WHERE id = ?", [session_id])


def mark_stale_running_sessions(db_path: str) -> int:
    """Mark all 'running' sessions as 'timeout'.

    Called at startup to recover from server crash/restart scenarios
    where sessions were left in 'running' state.

    Args:
        db_path: Path to the SQLite database file.

    Returns:
        Number of sessions updated (rowcount).
    """
    db = get_db(db_path)
    db.execute(
        """
        UPDATE search_sessions
           SET status     = 'timeout',
               finished_at = ?
         WHERE status = 'running'
        """,
        [_now_iso()],
    )
    return db.conn.total_changes
