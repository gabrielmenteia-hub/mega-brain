"""Migration 009 — search_sessions, search_session_products.

Creates tables that back the v3.0 manual search engine feature:
  - search_sessions: tracks each manual scan run (one per subniche click)
  - search_session_products: M2M between a session and the products found

Idempotent: uses IF NOT EXISTS for DDL. Safe to run multiple times.
Does NOT touch any pre-existing tables.
"""
import sqlite_utils


def run_migration_009(db_path: str) -> None:
    """Create search_sessions and search_session_products tables.

    Both tables are created with IF NOT EXISTS so the migration is safe
    to call on an already-migrated database.

    search_sessions  — one row per manual search invocation.
    search_session_products — links sessions to the products they found,
      recording the rank and platform at scan time.

    Args:
        db_path: Path to the SQLite database file.
    """
    db = sqlite_utils.Database(db_path)

    db.execute("PRAGMA foreign_keys=ON")

    # ------------------------------------------------------------------
    # 1. search_sessions
    # ------------------------------------------------------------------
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS search_sessions (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            subniche_id       INTEGER NOT NULL REFERENCES subniches(id),
            status            TEXT    NOT NULL DEFAULT 'pending',
            platform_statuses TEXT,
            started_at        TEXT,
            finished_at       TEXT,
            product_count     INTEGER DEFAULT 0
        )
        """
    )

    # ------------------------------------------------------------------
    # 2. search_session_products
    # ------------------------------------------------------------------
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS search_session_products (
            session_id    INTEGER NOT NULL REFERENCES search_sessions(id) ON DELETE CASCADE,
            product_id    INTEGER NOT NULL REFERENCES products(id),
            rank_at_scan  INTEGER,
            platform_slug TEXT,
            PRIMARY KEY (session_id, product_id)
        )
        """
    )

    db.conn.commit()
