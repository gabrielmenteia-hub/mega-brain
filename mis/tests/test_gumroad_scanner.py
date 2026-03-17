"""Tests for GumroadScanner — SPA with scroll loop scanner (SCAN-INTL-04).

6 tests:
- test_happy_path: _scan_with_scroll monkeypatched returns discover_marketing.html -> >= 1 product, rank=1, platform_id=11
- test_field_types: rank is int, external_id is non-empty str, url contains 'gumroad.com'
- test_empty_results: _scan_with_scroll returns HTML without articles -> result == []
- test_marketplace_unavailable: _scan_with_scroll raises Exception -> result == [], 'marketplace_unavailable' in stdout
- test_upsert_no_duplicates: upsert product -> reinsert same external_id with rank=2 -> 1 row, rank updated
- test_is_stale: upsert -> mark_stale -> is_stale=1; upsert again -> is_stale=0

NOTE: test_happy_path and test_field_types are RED (stub _parse_html returns []).
All other tests are GREEN with the stub.
"""
import asyncio
import pytest
from pathlib import Path

from mis.scanners.gumroad import GumroadScanner, GUMROAD_DISCOVER_URL
from mis.platform_ids import GUMROAD_PLATFORM_ID

FIXTURE_PATH = Path(__file__).parent / "fixtures/gumroad/discover_marketing.html"


@pytest.mark.asyncio
async def test_happy_path(monkeypatch):
    """scan_niche() with fixture HTML must return >= 1 product with required fields.

    RED: This test FAILS with the stub (_parse_html returns []).
    Will pass after GREEN implementation.
    """
    fixture_html = FIXTURE_PATH.read_text(encoding="utf-8")

    async def mock_scan_with_scroll(self, url, limit=50):
        return fixture_html

    monkeypatch.setattr(GumroadScanner, "_scan_with_scroll", mock_scan_with_scroll)

    async with GumroadScanner() as scanner:
        result = await scanner.scan_niche("marketing-digital", "marketing", niche_id=1)

    assert len(result) >= 1, f"Expected >= 1 product, got {len(result)}"
    product = result[0]
    assert product.rank == 1, f"Expected rank=1, got {product.rank}"
    assert product.platform_id == GUMROAD_PLATFORM_ID, (
        f"Expected platform_id={GUMROAD_PLATFORM_ID}, got {product.platform_id}"
    )


@pytest.mark.asyncio
async def test_field_types(monkeypatch):
    """rank is int, external_id is non-empty str, url contains 'gumroad.com'.

    RED: This test FAILS with the stub (_parse_html returns []).
    Will pass after GREEN implementation.
    """
    fixture_html = FIXTURE_PATH.read_text(encoding="utf-8")

    async def mock_scan_with_scroll(self, url, limit=50):
        return fixture_html

    monkeypatch.setattr(GumroadScanner, "_scan_with_scroll", mock_scan_with_scroll)

    async with GumroadScanner() as scanner:
        result = await scanner.scan_niche("marketing-digital", "marketing", niche_id=1)

    assert len(result) >= 1, f"Expected >= 1 product, got {len(result)}"
    product = result[0]
    assert isinstance(product.rank, int), f"rank must be int, got {type(product.rank)}"
    assert isinstance(product.external_id, str) and product.external_id != "", (
        f"external_id must be non-empty str, got {product.external_id!r}"
    )
    assert "gumroad.com" in product.url, (
        f"url must contain 'gumroad.com', got {product.url!r}"
    )


@pytest.mark.asyncio
async def test_empty_results(monkeypatch):
    """_scan_with_scroll returns HTML without articles -> result == [].

    GREEN: Stub _parse_html returns [] in any case. Will remain GREEN after full implementation.
    """
    empty_html = "<html><body><p>No products found.</p></body></html>"

    async def mock_scan_with_scroll(self, url, limit=50):
        return empty_html

    monkeypatch.setattr(GumroadScanner, "_scan_with_scroll", mock_scan_with_scroll)

    async with GumroadScanner() as scanner:
        result = await scanner.scan_niche("marketing-digital", "marketing", niche_id=1)

    assert result == [], f"Expected [], got {result}"


@pytest.mark.asyncio
async def test_marketplace_unavailable(monkeypatch, capsys):
    """_scan_with_scroll raises Exception -> result == [], 'marketplace_unavailable' in stdout.

    GREEN: This test PASSES with the stub (exception handling is implemented).

    NOTE: structlog is configured with PrintLoggerFactory + JSONRenderer in base_scraper.py.
    We verify the structured log via capsys (stdout JSON) rather than capture_logs().
    """
    async def mock_scan_with_scroll_fail(self, url, limit=50):
        raise Exception("timeout")

    monkeypatch.setattr(GumroadScanner, "_scan_with_scroll", mock_scan_with_scroll_fail)

    async with GumroadScanner() as scanner:
        result = await scanner.scan_niche("marketing-digital", "marketing", niche_id=1)

    assert result == [], f"Expected [], got {result}"
    captured = capsys.readouterr()
    assert "marketplace_unavailable" in captured.out, (
        f"Expected 'marketplace_unavailable' in stdout log, got: {captured.out!r}"
    )


@pytest.mark.asyncio
async def test_upsert_no_duplicates(tmp_path):
    """Insert product -> reinsert same external_id with rank=2 -> 1 row in DB, rank updated.

    GREEN: Tests the upsert behavior in product_repository, not the scanner itself.
    """
    from mis.db import get_db, run_migrations
    from mis.product_repository import upsert_product
    from mis.scanner import Product

    db_path = str(tmp_path / "mis.db")
    run_migrations(db_path)
    db = get_db(db_path)

    db.execute(
        "INSERT OR IGNORE INTO platforms (id, name, slug, base_url, created_at) "
        "VALUES (11, 'Gumroad', 'gumroad', 'https://gumroad.com', '2026-01-01T00:00:00Z')"
    )
    db.execute(
        "INSERT OR IGNORE INTO niches (id, name, slug, created_at) "
        "VALUES (1, 'Marketing Digital', 'marketing-digital', '2026-01-01T00:00:00Z')"
    )
    db.conn.commit()

    product = Product(
        external_id="emailpro",
        title="Email Marketing Pro Bundle",
        url="https://gumroad.com/l/emailpro",
        platform_id=GUMROAD_PLATFORM_ID,
        niche_id=1,
        rank=1,
        price=29.0,
    )
    upsert_product(db, product)

    count_1 = list(db.execute(
        "SELECT COUNT(*) FROM products WHERE platform_id=? AND external_id=?",
        [GUMROAD_PLATFORM_ID, "emailpro"],
    ))[0][0]
    assert count_1 == 1, f"Expected 1 row after first upsert, got {count_1}"

    product_v2 = Product(
        external_id="emailpro",
        title="Email Marketing Pro Bundle",
        url="https://gumroad.com/l/emailpro",
        platform_id=GUMROAD_PLATFORM_ID,
        niche_id=1,
        rank=2,
        price=29.0,
    )
    upsert_product(db, product_v2)

    count_2 = list(db.execute(
        "SELECT COUNT(*) FROM products WHERE platform_id=? AND external_id=?",
        [GUMROAD_PLATFORM_ID, "emailpro"],
    ))[0][0]
    assert count_2 == 1, f"Expected still 1 row after second upsert, got {count_2}"

    rank_row = list(db.execute(
        "SELECT rank FROM products WHERE platform_id=? AND external_id=?",
        [GUMROAD_PLATFORM_ID, "emailpro"],
    ))[0]
    assert rank_row[0] == 2, f"Expected rank=2 after update, got {rank_row[0]}"


@pytest.mark.asyncio
async def test_is_stale(tmp_path):
    """upsert product -> mark_stale -> is_stale=1; upsert again -> is_stale=0.

    GREEN: Tests mark_stale behavior in product_repository.
    """
    from mis.db import get_db, run_migrations
    from mis.product_repository import upsert_product, mark_stale
    from mis.scanner import Product

    db_path = str(tmp_path / "mis.db")
    run_migrations(db_path)
    db = get_db(db_path)

    db.execute(
        "INSERT OR IGNORE INTO platforms (id, name, slug, base_url, created_at) "
        "VALUES (11, 'Gumroad', 'gumroad', 'https://gumroad.com', '2026-01-01T00:00:00Z')"
    )
    db.execute(
        "INSERT OR IGNORE INTO niches (id, name, slug, created_at) "
        "VALUES (1, 'Marketing Digital', 'marketing-digital', '2026-01-01T00:00:00Z')"
    )
    db.conn.commit()

    product = Product(
        external_id="gumroad-test-001",
        title="Gumroad Test Product",
        url="https://gumroad.com/l/gumroad-test-001",
        platform_id=GUMROAD_PLATFORM_ID,
        niche_id=1,
        rank=1,
        price=None,
    )
    upsert_product(db, product)

    row = list(db.execute(
        "SELECT is_stale FROM products WHERE platform_id=? AND external_id=?",
        [GUMROAD_PLATFORM_ID, "gumroad-test-001"],
    ))[0]
    assert row[0] == 0, "is_stale deve ser 0 apos upsert inicial"

    mark_stale(db, GUMROAD_PLATFORM_ID, 1)
    row = list(db.execute(
        "SELECT is_stale FROM products WHERE platform_id=? AND external_id=?",
        [GUMROAD_PLATFORM_ID, "gumroad-test-001"],
    ))[0]
    assert row[0] == 1, "is_stale deve ser 1 apos mark_stale()"

    upsert_product(db, product)
    row = list(db.execute(
        "SELECT is_stale FROM products WHERE platform_id=? AND external_id=?",
        [GUMROAD_PLATFORM_ID, "gumroad-test-001"],
    ))[0]
    assert row[0] == 0, "is_stale deve ser resetado para 0 apos upsert"
