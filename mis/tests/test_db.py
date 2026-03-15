"""Tests for mis.db — schema migrations and DB connection helpers.

Coverage: FOUND-01
"""
import sqlite3
import pytest
import sqlite_utils

from mis.db import get_db, run_migrations


def test_all_tables_exist(db_path):
    """After run_migrations(), exactly 7 tables must exist (includes _003 spy tables)."""
    run_migrations(db_path)
    db = sqlite_utils.Database(db_path)
    assert set(db.table_names()) == {
        "platforms", "niches", "products", "pains", "dossiers",
        "reviews", "llm_calls",
    }


def test_migration_idempotent(db_path):
    """Running run_migrations() twice must not raise any exception."""
    run_migrations(db_path)
    run_migrations(db_path)  # second call must not fail
    db = sqlite_utils.Database(db_path)
    # All 7 tables must still exist after the second run
    assert set(db.table_names()) == {
        "platforms", "niches", "products", "pains", "dossiers",
        "reviews", "llm_calls",
    }


def test_foreign_key_constraint(db_path):
    """Inserting a product with a non-existent platform_id must raise IntegrityError."""
    run_migrations(db_path)
    db = get_db(db_path)  # get_db ensures PRAGMA foreign_keys=ON
    with pytest.raises(sqlite3.IntegrityError):
        db["products"].insert(
            {
                "platform_id": 9999,  # no such platform
                "niche_id": None,
                "external_id": "test-001",
                "title": "Test Product",
                "url": "https://example.com/product",
                "rank_score": 0.0,
                "price": 97.0,
                "currency": "BRL",
                "scraped_at": "2026-03-14T00:00:00",
                "raw_data": "{}",
            }
        )
