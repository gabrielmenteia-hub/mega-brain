"""Test contracts for mis.dossier_repository.

RED: All tests fail with ImportError at runtime until plan 05-02 implements
the module. Imports are deferred to function body so pytest can collect
the test IDs even before the module exists.
"""
from datetime import datetime, timezone

import pytest

from mis.db import run_migrations, get_db


def test_get_dossier_by_product_id_returns_none_when_missing(db_path):
    """get_dossier_by_product_id returns None when no dossier exists for product."""
    from mis.dossier_repository import get_dossier_by_product_id  # RED until plan 05-02
    run_migrations(db_path)
    result = get_dossier_by_product_id(db_path, product_id=9999)
    assert result is None


def test_list_dossiers_by_rank_returns_ordered(db_path):
    """list_dossiers_by_rank returns dossiers ordered ASC by product rank."""
    from mis.dossier_repository import list_dossiers_by_rank  # RED until plan 05-02
    run_migrations(db_path)
    db = get_db(db_path)
    now = datetime.now(timezone.utc).isoformat()

    # Insert platform and niche first (FK constraints)
    if "platforms" in db.table_names():
        db.execute(
            "INSERT OR IGNORE INTO platforms (id, name, slug) VALUES (1, 'Hotmart', 'hotmart')"
        )
    if "niches" in db.table_names():
        db.execute(
            "INSERT OR IGNORE INTO niches (id, name, slug) VALUES (1, 'Test Niche', 'test-niche')"
        )

    # Insert 3 products with different ranks
    for rank, ext_id in [(10, "prod-a"), (2, "prod-b"), (5, "prod-c")]:
        db.execute(
            "INSERT INTO products (platform_id, external_id, title, url, niche_id, rank, updated_at) "
            "VALUES (1, ?, 'Title', 'http://example.com', 1, ?, ?)",
            [ext_id, rank, now],
        )

    # Retrieve inserted product IDs
    rows = list(db.execute("SELECT id, rank FROM products ORDER BY rank ASC"))
    # Insert dossiers for each product
    for product_id, _ in rows:
        db.execute(
            "INSERT INTO dossiers (product_id, status, created_at) VALUES (?, 'done', ?)",
            [product_id, now],
        )

    result = list_dossiers_by_rank(db_path)
    # Result should be ordered ASC by rank (2, 5, 10)
    assert len(result) == 3
    ranks = [r["rank"] for r in result]
    assert ranks == sorted(ranks)
