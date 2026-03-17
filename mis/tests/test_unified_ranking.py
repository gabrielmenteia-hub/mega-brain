"""Tests for list_unified_ranking() in product_repository.

12 tests covering DASH-V2-01/02/03 requirements.
All tests are RED until list_unified_ranking() is implemented (Task 2).
"""
from __future__ import annotations

import sqlite_utils
import pytest

from mis.product_repository import list_unified_ranking


# ---------------------------------------------------------------------------
# DB setup helper
# ---------------------------------------------------------------------------

def _setup_db(db_path: str) -> sqlite_utils.Database:
    """Create minimal schema for unified ranking tests."""
    db = sqlite_utils.Database(db_path)
    db.execute(
        "CREATE TABLE IF NOT EXISTS platforms "
        "(id INTEGER PRIMARY KEY, name TEXT, slug TEXT UNIQUE, rank_type TEXT)"
    )
    db.execute(
        "CREATE TABLE IF NOT EXISTS niches "
        "(id INTEGER PRIMARY KEY, name TEXT, slug TEXT UNIQUE)"
    )
    db.execute(
        "CREATE TABLE IF NOT EXISTS products "
        "(id INTEGER PRIMARY KEY AUTOINCREMENT, platform_id INTEGER, "
        "external_id TEXT, title TEXT, url TEXT, rank REAL, "
        "is_stale INTEGER DEFAULT 0, niche_id INTEGER, "
        "updated_at TEXT)"
    )
    db.execute(
        "CREATE TABLE IF NOT EXISTS dossiers "
        "(id INTEGER PRIMARY KEY, product_id INTEGER)"
    )
    db.conn.commit()
    return db


def _insert_platform(db: sqlite_utils.Database, pid: int, name: str, slug: str, rank_type: str) -> None:
    db.execute(
        "INSERT OR IGNORE INTO platforms (id, name, slug, rank_type) VALUES (?, ?, ?, ?)",
        [pid, name, slug, rank_type],
    )
    db.conn.commit()


def _insert_niche(db: sqlite_utils.Database, nid: int, name: str, slug: str) -> None:
    db.execute(
        "INSERT OR IGNORE INTO niches (id, name, slug) VALUES (?, ?, ?)",
        [nid, name, slug],
    )
    db.conn.commit()


def _insert_product(
    db: sqlite_utils.Database,
    *,
    platform_id: int,
    niche_id: int,
    title: str,
    rank: float | None,
    is_stale: int = 0,
    external_id: str = "",
    updated_at: str = "2026-01-01T00:00:00",
) -> None:
    db.execute(
        "INSERT INTO products (platform_id, niche_id, title, rank, is_stale, "
        "external_id, url, updated_at) VALUES (?, ?, ?, ?, ?, ?, '', ?)",
        [platform_id, niche_id, title, rank, is_stale, external_id, updated_at],
    )
    db.conn.commit()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_unified_score_order(db_path):
    """Products must be returned sorted by unified_score DESC."""
    db = _setup_db(db_path)
    _insert_platform(db, 1, "PlatA", "plat-a", "positional")
    _insert_platform(db, 2, "PlatB", "plat-b", "positional")
    _insert_niche(db, 1, "Marketing", "marketing")

    # Platform A: 5 products (rank 1-5)
    for i in range(1, 6):
        _insert_product(db, platform_id=1, niche_id=1, title=f"PlatA Product {i}", rank=float(i))

    # Platform B: 5 products (rank 1-5)
    for i in range(1, 6):
        _insert_product(db, platform_id=2, niche_id=1, title=f"PlatB Product {i}", rank=float(i))

    result = list_unified_ranking(db_path, niche="marketing", multi_platform_only=0, per_page=20, page=1)
    products = result["products"]
    assert len(products) > 0
    scores = [p["unified_score"] for p in products]
    assert scores == sorted(scores, reverse=True), "Products must be sorted by unified_score DESC"


def test_percentile_positional(db_path):
    """Rank #1 in a group of 5 positional products → unified_score = 80.0."""
    db = _setup_db(db_path)
    _insert_platform(db, 1, "PlatA", "plat-a", "positional")
    _insert_niche(db, 1, "Marketing", "marketing")

    for i in range(1, 6):
        _insert_product(db, platform_id=1, niche_id=1, title=f"Product {i}", rank=float(i))

    result = list_unified_ranking(db_path, niche="marketing", multi_platform_only=0, per_page=20, page=1)
    products = result["products"]
    # rank=1, total=5 → score = (1 - 1/5) * 100 = 80.0
    top = products[0]
    assert top["rank"] == 1.0
    assert top["unified_score"] == 80.0, f"Expected 80.0 got {top['unified_score']}"


def test_percentile_gravity(db_path):
    """Gravity platform: product with max gravity → unified_score = 100.0."""
    db = _setup_db(db_path)
    _insert_platform(db, 1, "ClickBank", "clickbank", "gravity")
    _insert_niche(db, 1, "Marketing", "marketing")

    gravities = [100.0, 80.0, 60.0, 40.0, 20.0]
    for i, g in enumerate(gravities, start=1):
        _insert_product(db, platform_id=1, niche_id=1, title=f"CB Product {i}", rank=g)

    result = list_unified_ranking(db_path, niche="marketing", multi_platform_only=0, per_page=20, page=1)
    products = result["products"]
    # product with gravity=100.0 (max) → score = 100.0 / 100.0 * 100 = 100.0
    top = products[0]
    assert top["unified_score"] == 100.0, f"Expected 100.0 got {top['unified_score']}"


def test_null_rank_excluded(db_path):
    """Products with rank=NULL must not appear in results."""
    db = _setup_db(db_path)
    _insert_platform(db, 1, "PlatA", "plat-a", "positional")
    _insert_niche(db, 1, "Marketing", "marketing")

    for i in range(1, 6):
        _insert_product(db, platform_id=1, niche_id=1, title=f"Product {i}", rank=float(i))
    # Insert product with NULL rank
    _insert_product(db, platform_id=1, niche_id=1, title="NULL rank product", rank=None)

    result = list_unified_ranking(db_path, niche="marketing", multi_platform_only=0, per_page=20, page=1)
    products = result["products"]
    null_products = [p for p in products if p["rank"] is None]
    assert null_products == [], "Products with NULL rank must be excluded"


def test_min_products_threshold(db_path):
    """Platform with < 5 products excluded; platform with 5 products included."""
    db = _setup_db(db_path)
    _insert_platform(db, 1, "SmallPlat", "small-plat", "positional")  # 3 products — excluded
    _insert_platform(db, 2, "BigPlat", "big-plat", "positional")       # 5 products — included
    _insert_niche(db, 1, "Marketing", "marketing")

    # Small platform: 3 products (< MIN=5)
    for i in range(1, 4):
        _insert_product(db, platform_id=1, niche_id=1, title=f"Small {i}", rank=float(i))

    # Big platform: 5 products
    for i in range(1, 6):
        _insert_product(db, platform_id=2, niche_id=1, title=f"Big {i}", rank=float(i))

    result = list_unified_ranking(db_path, niche="marketing", multi_platform_only=0, per_page=20, page=1)
    products = result["products"]
    platform_slugs = {p["platform_slug"] for p in products}
    assert "small-plat" not in platform_slugs, "Platform with < 5 products must be excluded"
    assert "big-plat" in platform_slugs, "Platform with 5 products must be included"


def test_niche_filter(db_path):
    """Filter by niche returns only products from that niche."""
    db = _setup_db(db_path)
    _insert_platform(db, 1, "PlatA", "plat-a", "positional")
    _insert_niche(db, 1, "Marketing", "marketing")
    _insert_niche(db, 2, "Health", "health")

    # 5 products in niche 1
    for i in range(1, 6):
        _insert_product(db, platform_id=1, niche_id=1, title=f"Marketing {i}", rank=float(i))

    # 5 products in niche 2
    for i in range(1, 6):
        _insert_product(db, platform_id=1, niche_id=2, title=f"Health {i}", rank=float(i))

    result = list_unified_ranking(db_path, niche="marketing", multi_platform_only=0, per_page=20, page=1)
    products = result["products"]
    niche_names = {p["niche_name"] for p in products}
    assert niche_names == {"Marketing"}, f"Expected only Marketing niche, got {niche_names}"
    assert len(products) == 5


def test_multi_platform_filter(db_path):
    """Toggle ON: only products whose title appears in 2+ platforms."""
    db = _setup_db(db_path)
    _insert_platform(db, 1, "PlatA", "plat-a", "positional")
    _insert_platform(db, 2, "PlatB", "plat-b", "positional")
    _insert_niche(db, 1, "Marketing", "marketing")

    # Shared title: present in both platforms (5 products each)
    for i in range(1, 6):
        _insert_product(db, platform_id=1, niche_id=1, title="Shared Course", rank=float(i))
        _insert_product(db, platform_id=2, niche_id=1, title="Shared Course", rank=float(i))

    # Exclusive title: only in platform A (5 products)
    for i in range(1, 6):
        _insert_product(db, platform_id=1, niche_id=1, title=f"Exclusive {i}", rank=float(i + 10))

    # toggle OFF → all products returned
    result_off = list_unified_ranking(db_path, niche="marketing", multi_platform_only=0, per_page=100, page=1)
    exclusive_off = [p for p in result_off["products"] if p["title"].startswith("Exclusive")]
    assert len(exclusive_off) > 0, "Toggle OFF must include exclusive products"

    # toggle ON → only shared products
    result_on = list_unified_ranking(db_path, niche="marketing", multi_platform_only=1, per_page=100, page=1)
    exclusive_on = [p for p in result_on["products"] if p["title"].startswith("Exclusive")]
    assert exclusive_on == [], "Toggle ON must exclude products from only 1 platform"


def test_title_normalization(db_path):
    """Accented and unaccented versions of the same title must be treated as one."""
    db = _setup_db(db_path)
    _insert_platform(db, 1, "PlatA", "plat-a", "positional")
    _insert_platform(db, 2, "PlatB", "plat-b", "positional")
    _insert_niche(db, 1, "Marketing", "marketing")

    # Platform A: "Café Marketing" (with accent)
    for i in range(1, 6):
        _insert_product(db, platform_id=1, niche_id=1, title="Café Marketing", rank=float(i))

    # Platform B: "cafe marketing" (without accent, lowercase)
    for i in range(1, 6):
        _insert_product(db, platform_id=2, niche_id=1, title="cafe marketing", rank=float(i))

    result = list_unified_ranking(db_path, niche="marketing", multi_platform_only=1, per_page=100, page=1)
    products = result["products"]
    # Both titles should normalize to "cafe marketing" → treated as same → both included
    assert len(products) > 0, "Normalized titles must match across platforms"


def test_result_fields(db_path):
    """Each product dict must contain all required fields."""
    db = _setup_db(db_path)
    _insert_platform(db, 1, "PlatA", "plat-a", "positional")
    _insert_niche(db, 1, "Marketing", "marketing")

    for i in range(1, 6):
        _insert_product(db, platform_id=1, niche_id=1, title=f"Product {i}", rank=float(i))

    result = list_unified_ranking(db_path, niche="marketing", multi_platform_only=0, per_page=20, page=1)
    products = result["products"]
    assert len(products) > 0

    required_fields = {
        "id", "title", "platform_name", "platform_slug",
        "niche_name", "unified_score", "rank", "rank_type",
        "is_stale", "has_dossier",
    }
    for product in products:
        missing = required_fields - set(product.keys())
        assert not missing, f"Product missing fields: {missing}"


def test_stale_included(db_path):
    """Products with is_stale=1 must appear with is_stale=True."""
    db = _setup_db(db_path)
    _insert_platform(db, 1, "PlatA", "plat-a", "positional")
    _insert_niche(db, 1, "Marketing", "marketing")

    for i in range(1, 5):
        _insert_product(db, platform_id=1, niche_id=1, title=f"Fresh {i}", rank=float(i), is_stale=0)
    _insert_product(db, platform_id=1, niche_id=1, title="Stale Product", rank=5.0, is_stale=1)

    result = list_unified_ranking(db_path, niche="marketing", multi_platform_only=0, per_page=20, page=1)
    products = result["products"]
    stale = [p for p in products if p["title"] == "Stale Product"]
    assert len(stale) == 1, "Stale product must appear in results"
    assert stale[0]["is_stale"] is True, f"Expected is_stale=True, got {stale[0]['is_stale']}"


def test_single_platform_warning(db_path):
    """warning_single_platform=True when niche has data from only 1 platform."""
    db = _setup_db(db_path)
    _insert_platform(db, 1, "PlatA", "plat-a", "positional")
    _insert_niche(db, 1, "Marketing", "marketing")

    for i in range(1, 6):
        _insert_product(db, platform_id=1, niche_id=1, title=f"Product {i}", rank=float(i))

    result = list_unified_ranking(db_path, niche="marketing", multi_platform_only=0, per_page=20, page=1)
    assert result["warning_single_platform"] is True, "Must warn when only 1 platform has data"


def test_pagination(db_path):
    """With 10 products total, page=2 and per_page=5 returns products 6-10."""
    db = _setup_db(db_path)
    _insert_platform(db, 1, "PlatA", "plat-a", "positional")
    _insert_niche(db, 1, "Marketing", "marketing")

    for i in range(1, 11):
        _insert_product(db, platform_id=1, niche_id=1, title=f"Product {i}", rank=float(i))

    result = list_unified_ranking(db_path, niche="marketing", multi_platform_only=0, per_page=5, page=2)
    assert result["total"] == 10, f"Expected total=10, got {result['total']}"
    assert len(result["products"]) == 5, f"Expected 5 products on page 2, got {len(result['products'])}"
