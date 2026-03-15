"""Test contracts for mis.pain_repository.

RED: All tests fail with ImportError at runtime until plan 05-02 implements
the module. Imports are deferred to function body so pytest can collect
the test IDs even before the module exists.
"""
import json
from datetime import datetime, timezone

import pytest

from mis.db import run_migrations, get_db


def test_get_latest_report_returns_none_when_empty(db_path):
    """get_latest_report returns None when the pain_reports table is empty."""
    from mis.pain_repository import get_latest_report  # RED until plan 05-02
    run_migrations(db_path)
    result = get_latest_report(db_path, niche_id=1)
    assert result is None


def test_get_historical_reports_returns_list(db_path):
    """get_historical_reports returns all reports for a given niche_id."""
    from mis.pain_repository import get_historical_reports  # RED until plan 05-02
    run_migrations(db_path)
    db = get_db(db_path)
    now = datetime.now(timezone.utc).isoformat()

    # Insert 2 pain reports for niche_id=1
    for cycle in ["2026-03-15T10:00", "2026-03-15T11:00"]:
        db.execute(
            "INSERT INTO pain_reports (niche_id, cycle_at, report_json, created_at) "
            "VALUES (?, ?, ?, ?)",
            [1, cycle, json.dumps({"test": True}), now],
        )

    result = get_historical_reports(db_path, niche_id=1)
    assert len(result) == 2
