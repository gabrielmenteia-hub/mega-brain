"""Database connection helpers for the MIS system.

Provides get_db() for creating a sqlite-utils Database with correct PRAGMAs,
and re-exports run_migrations() for convenient top-level access.

Usage:
    from mis.db import get_db, run_migrations

    run_migrations("/path/to/mis.db")
    db = get_db("/path/to/mis.db")
    db["products"].rows_where("platform_id = ?", [1])
"""
import sqlite_utils

from .migrations._001_initial import run_migrations  # noqa: F401 (re-exported)


def get_db(db_path: str) -> sqlite_utils.Database:
    """Return a sqlite-utils Database with WAL mode and foreign keys enabled.

    Args:
        db_path: Path to the SQLite database file. Use ':memory:' for in-memory DBs.

    Returns:
        A sqlite_utils.Database instance with PRAGMAs applied.
    """
    db = sqlite_utils.Database(db_path)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")
    return db
