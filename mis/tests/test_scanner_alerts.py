"""Test contracts for mis.scanner.save_batch_with_alerts (DASH-04).

Tests that top-20 entry alerts are created correctly and that
existing top-20 products do not generate duplicate alerts.
"""
import pytest

from mis.db import run_migrations, get_db


@pytest.fixture
def db_path(tmp_path):
    path = str(tmp_path / "scanner_alerts.db")
    run_migrations(path)
    return path


def _make_product(external_id, platform_id, niche_id, rank, title="Product"):
    """Helper to create a Product dataclass instance."""
    from mis.scanner import Product
    return Product(
        external_id=external_id,
        title=title,
        url=f"https://example.com/{external_id}",
        platform_id=platform_id,
        niche_id=niche_id,
        rank=rank,
    )


def _seed_platform_and_niche(db_path):
    """Insert platform and niche rows required by FK constraints."""
    import sqlite3
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO platforms (id, name, slug) VALUES (1, 'Hotmart', 'hotmart')"
        )
        conn.execute(
            "INSERT OR IGNORE INTO niches (id, name, slug) VALUES (1, 'Saude', 'saude')"
        )
        conn.commit()


def test_alert_created_on_top20_entry(db_path):
    """Product with rank > 20 that enters top 20 generates a create_alert call."""
    from mis.scanner import save_batch_with_alerts  # RED until implemented
    _seed_platform_and_niche(db_path)
    db = get_db(db_path)

    # Insert product at rank 25 first (outside top 20)
    import sqlite3
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO products (external_id, title, url, platform_id, niche_id, rank) "
            "VALUES ('ext-1', 'Test Product', 'https://example.com/1', 1, 1, 25)"
        )
        conn.commit()

    # Now call save_batch_with_alerts with rank=5 (enters top 20)
    product = _make_product("ext-1", platform_id=1, niche_id=1, rank=5)
    save_batch_with_alerts(db, db_path, [product])

    # Alert should exist in DB
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT id FROM alerts").fetchall()
    assert len(rows) == 1, "Expected exactly 1 alert for new top-20 entry"


def test_no_alert_when_already_top20(db_path):
    """Product already in top 20 does NOT generate a new alert."""
    from mis.scanner import save_batch_with_alerts  # RED until implemented
    _seed_platform_and_niche(db_path)
    db = get_db(db_path)

    # Insert product already at rank 10 (inside top 20)
    import sqlite3
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO products (external_id, title, url, platform_id, niche_id, rank) "
            "VALUES ('ext-2', 'Top Product', 'https://example.com/2', 1, 1, 10)"
        )
        conn.commit()

    # Upsert at same rank (still in top 20 — no new entry)
    product = _make_product("ext-2", platform_id=1, niche_id=1, rank=8)
    save_batch_with_alerts(db, db_path, [product])

    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT id FROM alerts").fetchall()
    assert len(rows) == 0, "Expected no alert for product already in top 20"


def test_alert_created_for_brand_new_top20_product(db_path):
    """Brand-new product (not in DB) with rank <= 20 generates an alert."""
    from mis.scanner import save_batch_with_alerts  # RED until implemented
    _seed_platform_and_niche(db_path)
    db = get_db(db_path)

    product = _make_product("ext-new", platform_id=1, niche_id=1, rank=3)
    save_batch_with_alerts(db, db_path, [product])

    import sqlite3
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT id FROM alerts").fetchall()
    assert len(rows) == 1, "Expected 1 alert for brand-new product entering top 20"


def test_no_alert_for_product_outside_top20(db_path):
    """Brand-new product with rank > 20 does NOT generate an alert."""
    from mis.scanner import save_batch_with_alerts  # RED until implemented
    _seed_platform_and_niche(db_path)
    db = get_db(db_path)

    product = _make_product("ext-out", platform_id=1, niche_id=1, rank=25)
    save_batch_with_alerts(db, db_path, [product])

    import sqlite3
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT id FROM alerts").fetchall()
    assert len(rows) == 0, "Expected no alert for product outside top 20"
