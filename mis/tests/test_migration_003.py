"""Tests for migration _003 — spy dossiers schema expansion.

Verifies:
- New columns added to dossiers table
- Legacy columns preserved
- reviews and llm_calls tables created
- Migration is idempotent
"""
import pytest
import sqlite_utils

from mis.migrations._001_initial import run_migrations
from mis.migrations._003_spy_dossiers import run_migration_003


@pytest.fixture
def migrated_db(db_path):
    """DB with _001 + _003 applied."""
    run_migrations(db_path)
    run_migration_003(db_path)
    return sqlite_utils.Database(db_path)


def test_migration_adds_columns(migrated_db):
    """After run_migration_003(), dossiers table has new spy columns."""
    col_names = {col.name for col in migrated_db["dossiers"].columns}
    assert "status" in col_names
    assert "dossier_json" in col_names
    assert "ads_json" in col_names
    assert "incomplete" in col_names
    assert "updated_at" in col_names


def test_migration_preserves_legacy(migrated_db):
    """Legacy dossiers columns survive — no DROP TABLE was issued."""
    col_names = {col.name for col in migrated_db["dossiers"].columns}
    assert "analysis" in col_names
    assert "opportunity_score" in col_names
    assert "confidence_score" in col_names
    assert "generated_at" in col_names
    assert "product_id" in col_names


def test_migration_idempotent(db_path):
    """Running run_migration_003() twice must not raise any exception."""
    run_migrations(db_path)
    run_migration_003(db_path)
    run_migration_003(db_path)  # Should not raise


def test_reviews_table_created(migrated_db):
    """reviews table exists with expected columns after migration."""
    assert "reviews" in migrated_db.table_names()
    col_names = {col.name for col in migrated_db["reviews"].columns}
    assert "id" in col_names
    assert "product_id" in col_names
    assert "text" in col_names
    assert "valence" in col_names
    assert "rating" in col_names
    assert "source" in col_names
    assert "created_at" in col_names


def test_llm_calls_table_created(migrated_db):
    """llm_calls table exists with expected columns after migration."""
    assert "llm_calls" in migrated_db.table_names()
    col_names = {col.name for col in migrated_db["llm_calls"].columns}
    assert "id" in col_names
    assert "dossier_id" in col_names
    assert "model" in col_names
    assert "stage" in col_names
    assert "input_tokens" in col_names
    assert "output_tokens" in col_names
    assert "cost_usd" in col_names
    assert "created_at" in col_names
