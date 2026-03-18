"""Database connection helpers for the MIS system.

Provides get_db() for creating a sqlite-utils Database with correct PRAGMAs,
and re-exports run_migrations() for convenient top-level access.

Usage:
    from mis.db import get_db, run_migrations

    run_migrations("/path/to/mis.db")
    db = get_db("/path/to/mis.db")
    db["products"].rows_where("platform_id = ?", [1])
"""
import sqlite3

import sqlite_utils

from .migrations._001_initial import run_migrations as _run_001
from .migrations._002_product_enrichment import run_migration_002 as _run_002
from .migrations._003_spy_dossiers import run_migration_003 as _run_003
from .migrations._004_pain_radar import run_migration_004 as _run_004
from .migrations._005_alerts import run_migration_005 as _run_005
from .migrations._006_v2_platforms import run_migration_006 as _run_006
from .migrations._007_is_stale import run_migration_007 as _run_007
from .migrations._008_niche_v3 import run_migration_008 as _run_008
from .migrations._009_search_sessions import run_migration_009 as _run_009


def run_migrations(db_path: str) -> None:  # noqa: F401 (re-exported)
    """Apply all migrations in order.

    Runs _001 (initial schema), _002 (product enrichment), _003 (spy
    dossiers), _004 (pain radar), _005 (alerts), _006 (v2 platforms),
    _007 (is_stale column), _008 (niche v3 hierarchy), and _009 (search
    sessions) sequentially.
    Each migration is idempotent — safe to call on an already-migrated
    database.

    Args:
        db_path: Path to the SQLite database file.
    """
    _run_001(db_path)
    _run_002(db_path)
    _run_003(db_path)
    _run_004(db_path)
    _run_005(db_path)
    _run_006(db_path)
    _run_007(db_path)
    _run_008(db_path)
    _run_009(db_path)


def get_db(db_path: str) -> sqlite_utils.Database:
    """Return a sqlite-utils Database with WAL mode, foreign keys, and autocommit.

    Uses isolation_level=None (autocommit) so that writes are immediately
    visible to other connections without an explicit commit call. This is
    required for multi-connection patterns used by the web repository layer.

    Args:
        db_path: Path to the SQLite database file. Use ':memory:' for in-memory DBs.

    Returns:
        A sqlite_utils.Database instance with PRAGMAs and autocommit applied.
    """
    conn = sqlite3.connect(db_path, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return sqlite_utils.Database(conn)
