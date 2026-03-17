"""Tests for JVZooScanner — SSR-only scanner with Incapsula detection (SCAN-INTL-03).

7 tests:
- test_happy_path: respx mock returns listings_category84.html -> >= 1 product, rank=1, platform_id
- test_field_types: rank is int, price is float or None, external_id is non-empty str
- test_bot_detected_http_403: status 403 -> result == [], 'bot_detected' in stdout
- test_bot_detected_incapsula_body: HTML with 'incapsula' -> result == [], 'bot_detected' in stdout
- test_empty_results: HTML without div.product-listing -> result == []
- test_upsert_no_duplicates: upsert product -> reinsert same external_id with rank=2 -> 1 row, rank updated
- test_playwright_semaphore_exists: PLAYWRIGHT_SEMAPHORE in base_scraper with _value == 3

NOTE: test_happy_path and test_field_types are RED (stub returns []).
test_playwright_semaphore_exists is RED until base_scraper is modified in Task 2.
All other tests are GREEN with the stub.
"""
import asyncio
import pytest
import respx
from pathlib import Path
from httpx import Response

from mis.scanners.jvzoo import JVZooScanner, JVZOO_BASE_URL
from mis.platform_ids import JVZOO_PLATFORM_ID

FIXTURE_PATH = Path(__file__).parent / "fixtures/jvzoo/listings_category84.html"
INCAPSULA_PATH = Path(__file__).parent / "fixtures/jvzoo/incapsula_block.html"

JVZOO_LISTINGS_URL = f"{JVZOO_BASE_URL}/listings"


@pytest.mark.asyncio
@respx.mock
async def test_happy_path():
    """scan_niche() with fixture HTML must return >= 1 product with required fields.

    RED: This test FAILS with the stub (returns []).
    Will pass after GREEN implementation in Task 2.
    """
    html_content = FIXTURE_PATH.read_text(encoding="utf-8")

    respx.get(JVZOO_LISTINGS_URL).mock(
        return_value=Response(200, text=html_content)
    )

    async with JVZooScanner() as scanner:
        result = await scanner.scan_niche("marketing-digital", "84", niche_id=1)

    assert len(result) >= 1, f"Expected >= 1 product, got {len(result)}"
    product = result[0]
    assert product.rank == 1, f"Expected rank=1, got {product.rank}"
    assert product.platform_id == JVZOO_PLATFORM_ID, (
        f"Expected platform_id={JVZOO_PLATFORM_ID}, got {product.platform_id}"
    )
    assert product.external_id == "12345", (
        f"Expected external_id='12345', got {product.external_id!r}"
    )


@pytest.mark.asyncio
@respx.mock
async def test_field_types():
    """rank is int, price is float or None, external_id is non-empty str, url contains jvzoomarket.com.

    RED: This test FAILS with the stub (returns []).
    Will pass after GREEN implementation in Task 2.
    """
    html_content = FIXTURE_PATH.read_text(encoding="utf-8")

    respx.get(JVZOO_LISTINGS_URL).mock(
        return_value=Response(200, text=html_content)
    )

    async with JVZooScanner() as scanner:
        result = await scanner.scan_niche("marketing-digital", "84", niche_id=1)

    assert len(result) >= 1, f"Expected >= 1 product, got {len(result)}"
    product = result[0]
    assert isinstance(product.rank, int), f"rank must be int, got {type(product.rank)}"
    assert product.price is None or isinstance(product.price, float), (
        f"price must be float or None, got {type(product.price)}"
    )
    assert isinstance(product.external_id, str) and product.external_id != "", (
        f"external_id must be non-empty str, got {product.external_id!r}"
    )
    assert "jvzoomarket.com" in product.url, (
        f"url must contain 'jvzoomarket.com', got {product.url!r}"
    )


@pytest.mark.asyncio
@respx.mock
async def test_bot_detected_http_403(capsys):
    """HTTP 403 -> ScraperError -> result == [], stdout contains 'bot_detected'.

    GREEN: This test PASSES with the stub (bot detection via ScraperError is implemented).

    NOTE: structlog is configured with PrintLoggerFactory + JSONRenderer in base_scraper.py.
    We verify the structured log via capsys (stdout JSON) rather than capture_logs().
    """
    respx.get(JVZOO_LISTINGS_URL).mock(
        return_value=Response(403)
    )

    async with JVZooScanner() as scanner:
        result = await scanner.scan_niche("marketing-digital", "84", niche_id=1)

    assert result == [], f"Expected [], got {result}"
    captured = capsys.readouterr()
    assert "bot_detected" in captured.out, (
        f"Expected 'bot_detected' in stdout log, got: {captured.out!r}"
    )


@pytest.mark.asyncio
@respx.mock
async def test_bot_detected_incapsula_body(capsys):
    """Status 200 with Incapsula HTML body -> result == [], stdout contains 'bot_detected'.

    GREEN: This test PASSES with the stub (Incapsula HTML detection is implemented).
    """
    incapsula_html = INCAPSULA_PATH.read_text(encoding="utf-8")

    respx.get(JVZOO_LISTINGS_URL).mock(
        return_value=Response(200, text=incapsula_html)
    )

    async with JVZooScanner() as scanner:
        result = await scanner.scan_niche("marketing-digital", "84", niche_id=1)

    assert result == [], f"Expected [], got {result}"
    captured = capsys.readouterr()
    assert "bot_detected" in captured.out, (
        f"Expected 'bot_detected' in stdout log, got: {captured.out!r}"
    )


@pytest.mark.asyncio
@respx.mock
async def test_empty_results():
    """HTML without div.product-listing -> result == [].

    GREEN: Stub returns [] in any case. Will remain GREEN after full implementation.
    """
    empty_html = "<!DOCTYPE html><html><body><p>No products found.</p></body></html>"

    respx.get(JVZOO_LISTINGS_URL).mock(
        return_value=Response(200, text=empty_html)
    )

    async with JVZooScanner() as scanner:
        result = await scanner.scan_niche("marketing-digital", "84", niche_id=1)

    assert result == [], f"Expected [], got {result}"


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
        "VALUES (10, 'JVZoo', 'jvzoo', 'https://www.jvzoomarket.com', '2026-01-01T00:00:00Z')"
    )
    db.execute(
        "INSERT OR IGNORE INTO niches (id, name, slug, created_at) "
        "VALUES (1, 'Marketing Digital', 'marketing-digital', '2026-01-01T00:00:00Z')"
    )
    db.conn.commit()

    product = Product(
        external_id="12345",
        title="Email Marketing Pro 2026",
        url="https://www.jvzoomarket.com/productlibrary/marketframe?pid=12345",
        platform_id=JVZOO_PLATFORM_ID,
        niche_id=1,
        rank=1,
        price=47.0,
    )
    upsert_product(db, product)

    count_1 = list(db.execute(
        "SELECT COUNT(*) FROM products WHERE platform_id=? AND external_id=?",
        [JVZOO_PLATFORM_ID, "12345"],
    ))[0][0]
    assert count_1 == 1, f"Expected 1 row after first upsert, got {count_1}"

    # Re-insert with different rank
    product_v2 = Product(
        external_id="12345",
        title="Email Marketing Pro 2026",
        url="https://www.jvzoomarket.com/productlibrary/marketframe?pid=12345",
        platform_id=JVZOO_PLATFORM_ID,
        niche_id=1,
        rank=2,
        price=47.0,
    )
    upsert_product(db, product_v2)

    count_2 = list(db.execute(
        "SELECT COUNT(*) FROM products WHERE platform_id=? AND external_id=?",
        [JVZOO_PLATFORM_ID, "12345"],
    ))[0][0]
    assert count_2 == 1, f"Expected still 1 row after second upsert, got {count_2}"

    rank_row = list(db.execute(
        "SELECT rank FROM products WHERE platform_id=? AND external_id=?",
        [JVZOO_PLATFORM_ID, "12345"],
    ))[0]
    assert rank_row[0] == 2, f"Expected rank=2 after update, got {rank_row[0]}"


def test_playwright_semaphore_exists():
    """PLAYWRIGHT_SEMAPHORE exists in mis.base_scraper with asyncio.Semaphore and _value == 3.

    RED: This test FAILS until PLAYWRIGHT_SEMAPHORE is added to base_scraper.py in Task 2.
    """
    from mis.base_scraper import PLAYWRIGHT_SEMAPHORE
    assert isinstance(PLAYWRIGHT_SEMAPHORE, asyncio.Semaphore), (
        f"PLAYWRIGHT_SEMAPHORE must be asyncio.Semaphore, got {type(PLAYWRIGHT_SEMAPHORE)}"
    )
    assert PLAYWRIGHT_SEMAPHORE._value == 3, (
        f"PLAYWRIGHT_SEMAPHORE._value must be 3, got {PLAYWRIGHT_SEMAPHORE._value}"
    )
