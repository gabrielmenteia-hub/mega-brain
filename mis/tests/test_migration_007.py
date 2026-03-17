"""Tests for migration _007 — is_stale column.

5 tests covering:
- Column existence after run_migrations()
- Migration idempotency
- upsert_product() sets is_stale=0 by default
- mark_stale() sets is_stale=1 for all products in platform+niche
- upsert_product() resets is_stale to 0
"""
import pytest
import sqlite_utils

from mis.migrations._007_is_stale import run_migration_007
from mis.db import run_migrations, get_db
from mis.product_repository import upsert_product, mark_stale
from mis.scanner import Product

# Using platform_id=7 (Braip) and niche_id=1 for FK tests


def _insert_fk_rows(db: sqlite_utils.Database) -> None:
    """Insert platform and niche rows required as FK for products."""
    db.execute(
        "INSERT OR IGNORE INTO platforms "
        "(id, name, slug, base_url, created_at) "
        "VALUES (7, 'Braip', 'braip', 'https://braip.com', '2026-01-01T00:00:00Z')"
    )
    db.execute(
        "INSERT OR IGNORE INTO niches "
        "(id, name, slug, created_at) "
        "VALUES (1, 'Saude', 'saude', '2026-01-01T00:00:00Z')"
    )


def _make_product(external_id: str = "braip-test-001") -> Product:
    return Product(
        external_id=external_id,
        title="Produto Braip Teste",
        url="https://braip.com/produto-teste",
        platform_id=7,
        niche_id=1,
        rank=1,
        price=97.0,
    )


def test_is_stale_column_added(db_path):
    """After run_migrations(), products table must have is_stale column."""
    run_migrations(db_path)
    db = get_db(db_path)
    # If column does not exist, this SELECT raises OperationalError
    db.execute("SELECT is_stale FROM products WHERE 1=0")


def test_migration_idempotent(db_path):
    """Calling run_migration_007() twice must not raise an exception."""
    run_migrations(db_path)
    # Call a second time — must be safe
    run_migration_007(db_path)


def test_is_stale_default_false(db_path):
    """Products inserted via upsert_product() have is_stale=0 (False)."""
    run_migrations(db_path)
    db = get_db(db_path)
    _insert_fk_rows(db)

    upsert_product(db, _make_product())

    row = list(db.execute(
        "SELECT is_stale FROM products WHERE platform_id=7 AND external_id=?",
        ["braip-test-001"],
    ))[0]
    assert row[0] == 0, f"Expected is_stale=0 after upsert, got {row[0]}"


def test_mark_stale_sets_true(db_path):
    """mark_stale(db, platform_id, niche_id) sets is_stale=1 for all matching rows."""
    run_migrations(db_path)
    db = get_db(db_path)
    _insert_fk_rows(db)

    upsert_product(db, _make_product("braip-001"))
    upsert_product(db, _make_product("braip-002"))

    mark_stale(db, platform_id=7, niche_id=1)

    rows = list(db.execute(
        "SELECT external_id, is_stale FROM products WHERE platform_id=7 ORDER BY external_id",
    ))
    for ext_id, is_stale in rows:
        assert is_stale == 1, f"Expected is_stale=1 for {ext_id}, got {is_stale}"


def test_upsert_resets_stale(db_path):
    """A product with is_stale=1 receives upsert -> is_stale resets to 0."""
    run_migrations(db_path)
    db = get_db(db_path)
    _insert_fk_rows(db)

    product = _make_product()
    upsert_product(db, product)
    mark_stale(db, platform_id=7, niche_id=1)

    # Confirm is_stale=1
    row = list(db.execute(
        "SELECT is_stale FROM products WHERE platform_id=7 AND external_id=?",
        ["braip-test-001"],
    ))[0]
    assert row[0] == 1, "Pre-condition: is_stale must be 1 before upsert"

    # Upsert again — should reset is_stale to 0
    upsert_product(db, product)
    row = list(db.execute(
        "SELECT is_stale FROM products WHERE platform_id=7 AND external_id=?",
        ["braip-test-001"],
    ))[0]
    assert row[0] == 0, f"Expected is_stale=0 after upsert, got {row[0]}"
