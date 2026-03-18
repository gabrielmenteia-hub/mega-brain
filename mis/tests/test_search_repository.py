"""RED tests for search_repository and migration _009.

These tests define the observable contract for:
  - SEARCH-01: create/list search session
  - SEARCH-02: list_session_products
  - SEARCH-03: startup marks stale 'running' sessions as 'timeout'

All tests FAIL with ImportError or ModuleNotFoundError because the
modules referenced (search_repository, migrations._009_search_sessions)
do not yet exist. This is the expected RED state.
"""
import pytest

# RED imports — these modules do not exist yet.
# Expected failure: ModuleNotFoundError / ImportError.
from mis.search_repository import (  # noqa: F401
    create_session,
    delete_session,
    get_session,
    list_recent_sessions,
    list_session_products,
    mark_stale_running_sessions,
    update_session_status,
)
from mis.migrations._009_search_sessions import run_migration_009  # noqa: F401
from mis.db import run_migrations  # already exists — import succeeds


# ---------------------------------------------------------------------------
# SEARCH-01: migration + session lifecycle
# ---------------------------------------------------------------------------


def test_migration_009_creates_tables(db_path):
    """run_migrations() must create 'search_sessions' and
    'search_session_products' tables in the database.

    Verifies that migration _009 is registered in run_migrations() and
    that both tables are created during schema setup.
    """
    run_migrations(db_path)

    import sqlite3
    conn = sqlite3.connect(db_path)
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    conn.close()

    assert "search_sessions" in tables, "search_sessions table not found"
    assert "search_session_products" in tables, "search_session_products table not found"


def test_create_and_list_session(db_path):
    """create_session returns an int session_id; list_recent_sessions
    returns a list with that session; item contains 'subniche_id'.

    Covers SEARCH-01: session creation and basic listing.
    """
    run_migrations(db_path)

    session_id = create_session(db_path, subniche_id=1)
    assert isinstance(session_id, int), "create_session must return int"

    sessions = list_recent_sessions(db_path)
    assert isinstance(sessions, list)
    assert len(sessions) == 1
    assert sessions[0]["subniche_id"] == 1


def test_get_session_returns_dict(db_path):
    """get_session returns a dict with required keys; platform_statuses
    must be a Python dict (deserialized from JSON TEXT in SQLite), not a string.

    PITFALL: platform_statuses is stored as JSON TEXT — get_session()
    must deserialize it before returning.
    """
    run_migrations(db_path)

    session_id = create_session(db_path, subniche_id=2)
    platform_statuses = {"hotmart": "done", "kiwify": "running"}
    update_session_status(db_path, session_id, "done", platform_statuses, product_count=5)

    session = get_session(db_path, session_id)
    assert isinstance(session, dict)
    assert "id" in session
    assert "status" in session
    assert "subniche_id" in session
    assert "platform_statuses" in session
    assert isinstance(session["platform_statuses"], dict), (
        "platform_statuses must be deserialized to dict, not left as JSON string"
    )
    assert session["platform_statuses"]["hotmart"] == "done"


def test_list_session_products(db_path):
    """list_session_products returns list of products linked to the session.

    Each item must have 'rank_at_scan' and 'platform_slug' columns from
    the search_session_products join.

    Setup: create session, update_session_status to link products.
    The update_session_status implementation must also populate
    search_session_products from the products scanned.

    NOTE: This test verifies the contract shape. The actual linking
    logic in update_session_status is an implementation detail tested
    end-to-end in Plan 21-02 (GREEN phase).
    """
    run_migrations(db_path)

    session_id = create_session(db_path, subniche_id=1)

    # Verify list_session_products returns list type (may be empty until GREEN)
    products = list_session_products(db_path, session_id)
    assert isinstance(products, list)

    # Each returned item must have these keys if products exist
    for item in products:
        assert "rank_at_scan" in item
        assert "platform_slug" in item


# ---------------------------------------------------------------------------
# SEARCH-03: startup timeout hook
# ---------------------------------------------------------------------------


def test_startup_marks_running_as_timeout(db_path):
    """Inserting a session with status='running' then calling
    mark_stale_running_sessions() must transition that session to 'timeout'.

    Covers SEARCH-03: crash recovery — sessions left 'running' after a
    server restart are marked 'timeout' on next startup.
    """
    run_migrations(db_path)

    session_id = create_session(db_path, subniche_id=1)
    # Manually set status to 'running' (simulating an in-progress scan
    # that was interrupted by a server crash/restart)
    update_session_status(db_path, session_id, "running", {}, product_count=0)

    count = mark_stale_running_sessions(db_path)
    assert isinstance(count, int)
    assert count >= 1, "At least one session should be marked as timeout"

    session = get_session(db_path, session_id)
    assert session["status"] == "timeout"


# ---------------------------------------------------------------------------
# Deletion with cascade
# ---------------------------------------------------------------------------


def test_delete_session_cascades(db_path):
    """delete_session removes the session and list_recent_sessions returns
    empty list afterward.

    IMPORTANT: delete_session relies on ON DELETE CASCADE in SQLite.
    This only works when the connection has PRAGMA foreign_keys=ON, which
    get_db() guarantees via its connection setup. Tests that call
    delete_session must use a db_path opened by get_db(), not raw sqlite3.
    """
    run_migrations(db_path)

    session_id = create_session(db_path, subniche_id=3)
    sessions_before = list_recent_sessions(db_path)
    assert len(sessions_before) == 1

    delete_session(db_path, session_id)

    sessions_after = list_recent_sessions(db_path)
    assert len(sessions_after) == 0
