"""Tests for migration _004 — Pain Radar schema.

Verifies:
- pain_signals, pain_reports, youtube_quota_log tables created
- UNIQUE index on pain_signals.url_hash enforced
- UNIQUE index on (pain_reports.niche_id, pain_reports.cycle_at) enforced
- Upsert on pain_signals is idempotent (COUNT == 1)
- Migration is idempotent (double-run does not raise)
"""
import pytest
import sqlite3
import sqlite_utils

from mis.migrations._001_initial import run_migrations as run_001
from mis.migrations._004_pain_radar import run_migration_004


@pytest.fixture
def migrated_db(db_path):
    """DB with _001 + _004 applied."""
    run_001(db_path)
    run_migration_004(db_path)
    return sqlite_utils.Database(db_path)


def test_tables_created(migrated_db):
    """After run_migration_004(), three new tables exist in the database."""
    names = migrated_db.table_names()
    assert "pain_signals" in names
    assert "pain_reports" in names
    assert "youtube_quota_log" in names


def test_pain_signals_unique_index(migrated_db, db_path):
    """Inserting two rows with the same url_hash raises IntegrityError."""
    migrated_db["pain_signals"].insert({
        "url_hash": "abc123",
        "url": "https://example.com/post/1",
        "title": "Test post",
        "source": "reddit",
        "niche_slug": "emagrecimento",
        "score": 10,
        "extra_json": "{}",
        "collected_at": "2026-01-01T00:00:00Z",
    })
    with pytest.raises(Exception):  # sqlite3.IntegrityError
        migrated_db["pain_signals"].insert({
            "url_hash": "abc123",
            "url": "https://example.com/post/2",
            "title": "Duplicate hash",
            "source": "reddit",
            "niche_slug": "emagrecimento",
            "score": 5,
            "extra_json": "{}",
            "collected_at": "2026-01-01T01:00:00Z",
        })


def test_pain_reports_unique_index(migrated_db):
    """Inserting two rows with same (niche_id, cycle_at) raises IntegrityError."""
    migrated_db["pain_reports"].insert({
        "niche_id": 1,
        "cycle_at": "2026-01-01T00:00Z",
        "report_json": "{}",
        "created_at": "2026-01-01T00:00:00Z",
    })
    with pytest.raises(Exception):  # sqlite3.IntegrityError
        migrated_db["pain_reports"].insert({
            "niche_id": 1,
            "cycle_at": "2026-01-01T00:00Z",
            "report_json": '{"updated": true}',
            "created_at": "2026-01-01T01:00:00Z",
        })


def test_upsert_idempotent(migrated_db):
    """Upserting the same pain_signal twice results in exactly 1 row.

    Uses INSERT OR IGNORE (idempotent by url_hash UNIQUE constraint) to
    simulate the real upsert pattern used by the collector modules.
    """
    sql = """
        INSERT OR IGNORE INTO pain_signals
            (url_hash, url, title, source, niche_slug, score, extra_json, collected_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    args = (
        "deadbeef",
        "https://reddit.com/r/loseit/abc",
        "How to lose weight?",
        "reddit",
        "emagrecimento",
        50,
        "{}",
        "2026-01-01T00:00:00Z",
    )
    migrated_db.execute(sql, args)
    migrated_db.execute(sql, args)  # second insert is ignored
    count = migrated_db.execute("SELECT COUNT(*) FROM pain_signals").fetchone()[0]
    assert count == 1


def test_migration_idempotent(db_path):
    """Running run_migration_004() twice must not raise any exception."""
    run_001(db_path)
    run_migration_004(db_path)
    run_migration_004(db_path)  # Should not raise
