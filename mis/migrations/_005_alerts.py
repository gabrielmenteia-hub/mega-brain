"""Migration 005 — Alerts table.

Creates the alerts table used by the dashboard layer to surface new products
and ranking changes to the user.

Idempotent: uses IF NOT EXISTS guards throughout.
Safe to run multiple times without side effects or errors.
"""
import sqlite_utils


def run_migration_005(db_path: str) -> None:
    """Apply Alerts migration.

    Creates the following table if it does not already exist:

        alerts:
            id           (int PK autoincrement)
            product_id   (int NOT NULL) — FK reference (not enforced at DB level for flexibility)
            platform_slug (text)         — e.g. 'hotmart', 'clickbank', 'kiwify'
            niche_slug   (text)          — e.g. 'emagrecimento'
            position     (int NOT NULL)  — rank position at time of alert
            seen         (int DEFAULT 0) — 0 = unseen, 1 = seen
            created_at   (text NOT NULL) — ISO-8601 UTC timestamp
            expires_at   (text NOT NULL) — ISO-8601 UTC timestamp (created_at + 7 days)

    Indexes created:
        idx_alerts_created ON alerts(created_at)
        idx_alerts_seen    ON alerts(seen, expires_at)

    Args:
        db_path: Path to the SQLite database file.
    """
    db = sqlite_utils.Database(db_path)

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id   INTEGER NOT NULL,
            platform_slug TEXT,
            niche_slug   TEXT,
            position     INTEGER NOT NULL,
            seen         INTEGER DEFAULT 0,
            created_at   TEXT NOT NULL,
            expires_at   TEXT NOT NULL
        )
        """
    )

    db.execute(
        "CREATE INDEX IF NOT EXISTS idx_alerts_created "
        "ON alerts(created_at)"
    )

    db.execute(
        "CREATE INDEX IF NOT EXISTS idx_alerts_seen "
        "ON alerts(seen, expires_at)"
    )

    # Add created_at to dossiers if absent (backfill from generated_at column
    # added in _001 — this column was missing from _003 which only added status,
    # dossier_json, ads_json, incomplete, updated_at).
    if "dossiers" in db.table_names():
        existing_cols = {col.name for col in db["dossiers"].columns}
        if "created_at" not in existing_cols:
            db["dossiers"].add_column("created_at", str)
