"""Test contracts for mis.alert_repository.

RED: All tests fail with ImportError at runtime until plan 05-03 implements
the module. Imports are deferred to function body so pytest can collect
the test IDs even before the module exists.
"""
from datetime import datetime, timezone, timedelta

import pytest

from mis.db import run_migrations, get_db


def test_create_alert_inserts_row(db_path):
    """create_alert(db_path, product_id=1, position=5) inserts a row into alerts."""
    from mis.alert_repository import create_alert  # RED until plan 05-03
    run_migrations(db_path)
    alert_id = create_alert(db_path, product_id=1, position=5)
    db = get_db(db_path)
    rows = list(db.execute("SELECT id FROM alerts WHERE id = ?", [alert_id]))
    assert len(rows) == 1


def test_get_unseen_count_returns_zero_initially(db_path):
    """get_unseen_count on an empty DB returns 0."""
    from mis.alert_repository import get_unseen_count  # RED until plan 05-03
    run_migrations(db_path)
    count = get_unseen_count(db_path)
    assert count == 0


def test_mark_seen_updates_flag(db_path):
    """mark_seen(db_path, alert_id) sets seen=1 on the alert row."""
    from mis.alert_repository import create_alert, mark_seen  # RED until plan 05-03
    run_migrations(db_path)
    alert_id = create_alert(db_path, product_id=2, position=3)
    mark_seen(db_path, alert_id)
    db = get_db(db_path)
    row = list(db.execute("SELECT seen FROM alerts WHERE id = ?", [alert_id]))[0]
    assert row[0] == 1


def test_expire_old_alerts_removes_expired(db_path):
    """expire_old_alerts() deletes alerts whose expires_at is in the past."""
    from mis.alert_repository import expire_old_alerts  # RED until plan 05-03
    run_migrations(db_path)
    # Insert an alert with expires_at in the past directly via SQL
    past = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    db = get_db(db_path)
    db.execute(
        "INSERT INTO alerts (product_id, position, seen, expires_at, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        [1, 1, 0, past, datetime.now(timezone.utc).isoformat()],
    )
    expire_old_alerts(db_path)
    rows = list(db.execute("SELECT id FROM alerts"))
    assert len(rows) == 0
