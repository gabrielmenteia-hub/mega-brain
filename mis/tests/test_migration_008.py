"""Tests for migration _008 — niches_v3, subniches, subniche_platform_slugs.

These tests are written RED first (TDD): they fail with ImportError because
_008_niche_v3.py does not exist yet. Plan 02 implements the migration.

Covers:
  NICHE-01: 4 niches, >=40 subniches created via run_migrations()
  NICHE-02: subniche slug lookups per platform via subniche_platform_slugs table
"""
import sqlite_utils
import pytest

from mis.migrations._008_niche_v3 import run_migration_008
from mis.db import run_migrations


def test_migration_008_creates_tables(db_path):
    """After run_migrations(), niches_v3, subniches and subniche_platform_slugs must exist."""
    run_migrations(db_path)
    db = sqlite_utils.Database(db_path)
    tables = db.table_names()
    assert "niches_v3" in tables, "niches_v3 table must be created by migration _008"
    assert "subniches" in tables, "subniches table must be created by migration _008"
    assert "subniche_platform_slugs" in tables, (
        "subniche_platform_slugs table must be created by migration _008"
    )


def test_4_niches_v3_inserted(db_path):
    """After run_migrations(), niches_v3 must contain exactly 4 rows."""
    run_migrations(db_path)
    db = sqlite_utils.Database(db_path)
    count = next(db.execute("SELECT COUNT(*) FROM niches_v3"))[0]
    assert count == 4, f"Expected 4 niches in niches_v3, got {count}"


def test_subniche_count_at_least_40(db_path):
    """After run_migrations(), subniches table must have at least 40 rows."""
    run_migrations(db_path)
    db = sqlite_utils.Database(db_path)
    count = next(db.execute("SELECT COUNT(*) FROM subniches"))[0]
    assert count >= 40, f"Expected at least 40 subniches, got {count}"


def test_platform_slug_lookup(db_path):
    """Slug lookup: emagrecimento + clickbank must return 'health'."""
    run_migrations(db_path)
    db = sqlite_utils.Database(db_path)
    row = db.execute(
        """
        SELECT sps.search_slug
          FROM subniche_platform_slugs sps
          JOIN subniches s ON s.id = sps.subniche_id
          JOIN platforms pl ON pl.id = sps.platform_id
         WHERE s.slug = 'emagrecimento'
           AND pl.slug = 'clickbank'
        """
    ).fetchone()
    assert row is not None, "No slug mapping found for emagrecimento + clickbank"
    assert row[0] == "health", f"Expected 'health', got '{row[0]}'"


def test_platform_slug_lookup_hotmart(db_path):
    """Slug lookup: emagrecimento + hotmart must return 'saude-e-fitness'."""
    run_migrations(db_path)
    db = sqlite_utils.Database(db_path)
    row = db.execute(
        """
        SELECT sps.search_slug
          FROM subniche_platform_slugs sps
          JOIN subniches s ON s.id = sps.subniche_id
          JOIN platforms pl ON pl.id = sps.platform_id
         WHERE s.slug = 'emagrecimento'
           AND pl.slug = 'hotmart'
        """
    ).fetchone()
    assert row is not None, "No slug mapping found for emagrecimento + hotmart"
    assert row[0] == "saude-e-fitness", f"Expected 'saude-e-fitness', got '{row[0]}'"


def test_migration_idempotent(db_path):
    """Calling run_migration_008() twice must not raise any exception and counts stay equal."""
    run_migrations(db_path)
    db = sqlite_utils.Database(db_path)
    count_before = next(db.execute("SELECT COUNT(*) FROM niches_v3"))[0]

    # Second call — must be safe
    run_migration_008(db_path)

    count_after = next(db.execute("SELECT COUNT(*) FROM niches_v3"))[0]
    assert count_before == count_after, (
        f"Count changed after second call: {count_before} -> {count_after}"
    )


def test_existing_products_preserved(db_path):
    """Products inserted before migration _008 must survive run_migration_008() being called again.

    Uses niche_id=1 as FK to the legacy niches table (not niches_v3).
    The legacy niches table must remain intact after the migration runs.
    """
    # Step 1: create full schema (includes legacy niches table with niche_id=1)
    run_migrations(db_path)
    db = sqlite_utils.Database(db_path)

    # Step 2: insert a product referencing legacy niche_id=1
    db.execute(
        """
        INSERT INTO products (platform_id, niche_id, title, url, price, rank)
        VALUES (1, 1, 'Test Product Legacy', 'https://example.com/test', 99.0, 1)
        """
    )

    # Step 3: run migration _008 again (idempotent call)
    run_migration_008(db_path)

    # Step 4: verify the product still exists with the original niche_id
    row = db.execute(
        "SELECT niche_id FROM products WHERE url = 'https://example.com/test'"
    ).fetchone()
    assert row is not None, "Product was deleted after run_migration_008() — should be preserved"
    assert row[0] == 1, f"Expected niche_id=1, got {row[0]}"
