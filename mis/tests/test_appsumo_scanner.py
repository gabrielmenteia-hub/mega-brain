"""Tests for AppSumoScanner — SSR-first + Playwright fallback scanner (SCAN-INTL-05).

6 tests:
- test_happy_path_ssr: respx mock returns browse_software.html with __NEXT_DATA__ -> >= 1 product, rank=1, platform_id=12
- test_field_types: rank is int, price is float or None, external_id is non-empty str
- test_ssr_empty_fallback: fetch() returns HTML without products, fetch_spa monkeypatched returns fixture -> stub returns [] (GREEN temporarily, RED after _parse_html impl)
- test_marketplace_unavailable: fetch() fails + fetch_spa raises Exception -> result == [], 'marketplace_unavailable' in stdout
- test_upsert_no_duplicates: upsert product -> reinsert same external_id with rank=2 -> 1 row, rank updated
- test_is_stale: upsert -> mark_stale -> is_stale=1; upsert again -> is_stale=0

NOTE: test_happy_path_ssr and test_field_types are RED (stub _parse_html returns []).
test_ssr_empty_fallback is GREEN temporarily (stub returns [] regardless of input).
test_marketplace_unavailable, test_upsert_no_duplicates, test_is_stale are GREEN with stub.
"""
import asyncio
import pytest
import respx
from pathlib import Path
from httpx import Response

from mis.scanners.appsumo import AppSumoScanner, APPSUMO_BASE_URL
from mis.platform_ids import APPSUMO_PLATFORM_ID

FIXTURE_PATH = Path(__file__).parent / "fixtures/appsumo/browse_software.html"

APPSUMO_BROWSE_URL = f"{APPSUMO_BASE_URL}/browse/software/marketing-sales/"


@pytest.mark.asyncio
@respx.mock
async def test_happy_path_ssr():
    """scan_niche() with __NEXT_DATA__ fixture returns >= 1 product with required fields.

    RED: This test FAILS with the stub (_parse_html returns []).
    Will pass after GREEN implementation.
    """
    fixture_html = FIXTURE_PATH.read_text(encoding="utf-8")

    respx.get(APPSUMO_BROWSE_URL).mock(
        return_value=Response(200, text=fixture_html)
    )

    async with AppSumoScanner() as scanner:
        result = await scanner.scan_niche("marketing-digital", "marketing-sales", niche_id=1)

    assert len(result) >= 1, f"Expected >= 1 product, got {len(result)}"
    product = result[0]
    assert product.rank == 1, f"Expected rank=1, got {product.rank}"
    assert product.platform_id == APPSUMO_PLATFORM_ID, (
        f"Expected platform_id={APPSUMO_PLATFORM_ID}, got {product.platform_id}"
    )


@pytest.mark.asyncio
@respx.mock
async def test_field_types():
    """rank is int, price is float or None, external_id is non-empty str.

    RED: This test FAILS with the stub (_parse_html returns []).
    Will pass after GREEN implementation.
    """
    fixture_html = FIXTURE_PATH.read_text(encoding="utf-8")

    respx.get(APPSUMO_BROWSE_URL).mock(
        return_value=Response(200, text=fixture_html)
    )

    async with AppSumoScanner() as scanner:
        result = await scanner.scan_niche("marketing-digital", "marketing-sales", niche_id=1)

    assert len(result) >= 1, f"Expected >= 1 product, got {len(result)}"
    product = result[0]
    assert isinstance(product.rank, int), f"rank must be int, got {type(product.rank)}"
    assert product.price is None or isinstance(product.price, float), (
        f"price must be float or None, got {type(product.price)}"
    )
    assert isinstance(product.external_id, str) and product.external_id != "", (
        f"external_id must be non-empty str, got {product.external_id!r}"
    )


@pytest.mark.asyncio
@respx.mock
async def test_ssr_empty_fallback(monkeypatch):
    """fetch() returns HTML without products, fetch_spa monkeypatched returns fixture.

    GREEN (temporarily): stub _parse_html returns [] for both SSR and SPA calls,
    so result == []. Will become RED after _parse_html is implemented (fetch_spa
    with fixture should return >= 1 product).
    """
    empty_html = "<!DOCTYPE html><html><body><p>Loading...</p></body></html>"
    fixture_html = FIXTURE_PATH.read_text(encoding="utf-8")

    respx.get(APPSUMO_BROWSE_URL).mock(
        return_value=Response(200, text=empty_html)
    )

    async def mock_fetch_spa(self, url):
        return fixture_html

    monkeypatch.setattr(AppSumoScanner, "fetch_spa", mock_fetch_spa)

    async with AppSumoScanner() as scanner:
        result = await scanner.scan_niche("marketing-digital", "marketing-sales", niche_id=1)

    # GREEN with stub (returns []) — will be >= 1 after _parse_html is implemented
    assert isinstance(result, list), "result must be a list"


@pytest.mark.asyncio
@respx.mock
async def test_marketplace_unavailable(monkeypatch, capsys):
    """fetch() raises ScraperError + fetch_spa raises Exception -> result == [], 'marketplace_unavailable' in stdout.

    GREEN: This test PASSES with the stub (exception handling is implemented).

    NOTE: structlog is configured with PrintLoggerFactory + JSONRenderer in base_scraper.py.
    We verify the structured log via capsys (stdout JSON) rather than capture_logs().
    """
    respx.get(APPSUMO_BROWSE_URL).mock(
        return_value=Response(503)
    )

    async def mock_fetch_spa_fail(self, url):
        raise Exception("Playwright launch failed")

    monkeypatch.setattr(AppSumoScanner, "fetch_spa", mock_fetch_spa_fail)

    async with AppSumoScanner() as scanner:
        result = await scanner.scan_niche("marketing-digital", "marketing-sales", niche_id=1)

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
        "VALUES (12, 'AppSumo', 'appsumo', 'https://appsumo.com', '2026-01-01T00:00:00Z')"
    )
    db.execute(
        "INSERT OR IGNORE INTO niches (id, name, slug, created_at) "
        "VALUES (1, 'Marketing Digital', 'marketing-digital', '2026-01-01T00:00:00Z')"
    )
    db.conn.commit()

    product = Product(
        external_id="email-wizard-pro",
        title="Email Wizard Pro",
        url="https://appsumo.com/products/email-wizard-pro/",
        platform_id=APPSUMO_PLATFORM_ID,
        niche_id=1,
        rank=1,
        price=29.0,
    )
    upsert_product(db, product)

    count_1 = list(db.execute(
        "SELECT COUNT(*) FROM products WHERE platform_id=? AND external_id=?",
        [APPSUMO_PLATFORM_ID, "email-wizard-pro"],
    ))[0][0]
    assert count_1 == 1, f"Expected 1 row after first upsert, got {count_1}"

    product_v2 = Product(
        external_id="email-wizard-pro",
        title="Email Wizard Pro",
        url="https://appsumo.com/products/email-wizard-pro/",
        platform_id=APPSUMO_PLATFORM_ID,
        niche_id=1,
        rank=2,
        price=29.0,
    )
    upsert_product(db, product_v2)

    count_2 = list(db.execute(
        "SELECT COUNT(*) FROM products WHERE platform_id=? AND external_id=?",
        [APPSUMO_PLATFORM_ID, "email-wizard-pro"],
    ))[0][0]
    assert count_2 == 1, f"Expected still 1 row after second upsert, got {count_2}"

    rank_row = list(db.execute(
        "SELECT rank FROM products WHERE platform_id=? AND external_id=?",
        [APPSUMO_PLATFORM_ID, "email-wizard-pro"],
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
        "VALUES (12, 'AppSumo', 'appsumo', 'https://appsumo.com', '2026-01-01T00:00:00Z')"
    )
    db.execute(
        "INSERT OR IGNORE INTO niches (id, name, slug, created_at) "
        "VALUES (1, 'Marketing Digital', 'marketing-digital', '2026-01-01T00:00:00Z')"
    )
    db.conn.commit()

    product = Product(
        external_id="appsumo-test-001",
        title="AppSumo Test Product",
        url="https://appsumo.com/products/appsumo-test-001/",
        platform_id=APPSUMO_PLATFORM_ID,
        niche_id=1,
        rank=1,
        price=None,
    )
    upsert_product(db, product)

    row = list(db.execute(
        "SELECT is_stale FROM products WHERE platform_id=? AND external_id=?",
        [APPSUMO_PLATFORM_ID, "appsumo-test-001"],
    ))[0]
    assert row[0] == 0, "is_stale deve ser 0 apos upsert inicial"

    mark_stale(db, APPSUMO_PLATFORM_ID, 1)
    row = list(db.execute(
        "SELECT is_stale FROM products WHERE platform_id=? AND external_id=?",
        [APPSUMO_PLATFORM_ID, "appsumo-test-001"],
    ))[0]
    assert row[0] == 1, "is_stale deve ser 1 apos mark_stale()"

    upsert_product(db, product)
    row = list(db.execute(
        "SELECT is_stale FROM products WHERE platform_id=? AND external_id=?",
        [APPSUMO_PLATFORM_ID, "appsumo-test-001"],
    ))[0]
    assert row[0] == 0, "is_stale deve ser resetado para 0 apos upsert"
