"""Tests for migration _006 — v2.0 platform rows + rank_type column.

These tests verify INFRA-01 (all 12 platforms inserted) and
INFRA-03 (rank_type column populated with valid semantics).
"""
import sqlite_utils
import pytest

from mis.migrations._006_v2_platforms import run_migration_006
from mis.db import run_migrations


def test_all_12_platforms_inserted(db_path):
    """After run_migration_006(), platforms table must have exactly 12 rows."""
    run_migrations(db_path)
    db = sqlite_utils.Database(db_path)
    count = next(db.execute("SELECT COUNT(*) FROM platforms"))[0]
    assert count == 12, f"Expected 12 platforms, got {count}"


def test_migration_idempotent(db_path):
    """Calling run_migration_006() twice must not raise any exception."""
    run_migrations(db_path)
    # Call the specific migration again to test idempotency
    run_migration_006(db_path)


def test_rank_type_populated(db_path):
    """After migration, hotmart platform must have rank_type='positional'."""
    run_migrations(db_path)
    db = sqlite_utils.Database(db_path)
    row = next(db.execute("SELECT rank_type FROM platforms WHERE slug='hotmart'"))
    rank_type = row[0]
    assert rank_type is not None, "rank_type must not be NULL"
    assert rank_type != "", "rank_type must not be empty string"
    assert rank_type == "positional", f"Expected 'positional', got '{rank_type}'"


def test_rank_type_not_null_for_all(db_path):
    """All 12 platform rows must have a non-NULL rank_type after migration."""
    run_migrations(db_path)
    db = sqlite_utils.Database(db_path)
    rows = list(db.execute(
        "SELECT slug, rank_type FROM platforms WHERE rank_type IS NULL OR rank_type = ''"
    ))
    assert len(rows) == 0, (
        f"Found platforms with NULL/empty rank_type: {[r[0] for r in rows]}"
    )
