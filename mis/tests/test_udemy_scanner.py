"""Tests for UdemyScanner — REST API v2.0 courses scanner (SCAN-INTL-02).

6 tests:
- test_happy_path: respx.mock GET returns courses_marketing.json -> >= 1 product, rank=1, platform_id, url starts with https://www.udemy.com
- test_field_types: rank is int, rating is float or None, price is float or None, external_id is str
- test_missing_credentials: UDEMY_CLIENT_ID or UDEMY_CLIENT_SECRET absent -> result == [], alert='missing_credentials'
- test_empty_results: respx returns {"count": 0, "results": []} -> result == []
- test_api_discontinued_fallback: respx returns HTTP 401 -> result == [], log contains alert='api_discontinued'
- test_upsert_no_duplicates: upsert product -> reinsert same external_id with rank=2 -> 1 row, rank updated

NOTE: test_happy_path and test_field_types are RED (stubs return []).
test_missing_credentials, test_api_discontinued_fallback are GREEN (stub implements these paths).
"""
import json
import pytest
import respx
from pathlib import Path
from httpx import Response

from mis.scanners.udemy import UdemyScanner, UDEMY_API_URL
from mis.platform_ids import UDEMY_PLATFORM_ID

FIXTURE_PATH = Path(__file__).parent / "fixtures/udemy/courses_marketing.json"


@pytest.mark.asyncio
@respx.mock
async def test_happy_path(monkeypatch):
    """scan_niche() with fixture JSON must return >= 1 product with required fields.

    RED: This test FAILS with the stub (returns []).
    Will pass after GREEN implementation in plan 15-02.
    """
    monkeypatch.setenv("UDEMY_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("UDEMY_CLIENT_SECRET", "test-client-secret")
    fixture_data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    respx.get(UDEMY_API_URL).mock(
        return_value=Response(200, json=fixture_data)
    )

    async with UdemyScanner() as scanner:
        result = await scanner.scan_niche("marketing-digital", "Marketing", niche_id=1)

    assert len(result) >= 1, f"Expected >= 1 product, got {len(result)}"
    product = result[0]
    assert product.rank == 1, f"Expected rank=1, got {product.rank}"
    assert product.platform_id == UDEMY_PLATFORM_ID, (
        f"Expected platform_id={UDEMY_PLATFORM_ID}, got {product.platform_id}"
    )
    assert product.url.startswith("https://www.udemy.com"), (
        f"Expected url to start with 'https://www.udemy.com', got {product.url!r}"
    )


@pytest.mark.asyncio
@respx.mock
async def test_field_types(monkeypatch):
    """rank is int, rating is float or None, price is float or None, external_id is str.

    RED: This test FAILS with the stub (returns []).
    Will pass after GREEN implementation in plan 15-02.
    """
    monkeypatch.setenv("UDEMY_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("UDEMY_CLIENT_SECRET", "test-client-secret")
    fixture_data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    respx.get(UDEMY_API_URL).mock(
        return_value=Response(200, json=fixture_data)
    )

    async with UdemyScanner() as scanner:
        result = await scanner.scan_niche("marketing-digital", "Marketing", niche_id=1)

    assert len(result) >= 1, f"Expected >= 1 product, got {len(result)}"
    product = result[0]
    assert isinstance(product.rank, int), f"rank must be int, got {type(product.rank)}"
    assert isinstance(product.external_id, str), (
        f"external_id must be str, got {type(product.external_id)}"
    )
    if product.rating is not None:
        assert isinstance(product.rating, float), (
            f"rating must be float or None, got {type(product.rating)}"
        )
    if product.price is not None:
        assert isinstance(product.price, float), (
            f"price must be float or None, got {type(product.price)}"
        )
    if product.thumbnail_url is not None:
        assert isinstance(product.thumbnail_url, str), (
            f"thumbnail_url must be str or None, got {type(product.thumbnail_url)}"
        )


@pytest.mark.asyncio
async def test_missing_credentials(monkeypatch, capsys):
    """UDEMY_CLIENT_ID or UDEMY_CLIENT_SECRET absent -> result == [], alert='missing_credentials'.

    GREEN: This test PASSES with the stub (credential check is implemented).

    NOTE: structlog is configured with PrintLoggerFactory + JSONRenderer in base_scraper.py.
    We verify the structured log via capsys (stdout JSON) rather than capture_logs().
    """
    monkeypatch.delenv("UDEMY_CLIENT_ID", raising=False)
    monkeypatch.delenv("UDEMY_CLIENT_SECRET", raising=False)

    async with UdemyScanner() as scanner:
        result = await scanner.scan_niche("marketing-digital", "Marketing", niche_id=1)

    assert result == [], f"Expected [], got {result}"
    captured = capsys.readouterr()
    assert "missing_credentials" in captured.out, (
        f"Expected 'missing_credentials' in stdout log, got: {captured.out!r}"
    )


@pytest.mark.asyncio
@respx.mock
async def test_empty_results(monkeypatch):
    """respx returns count=0, results=[] -> result == [].

    Behavior depends on implementation — stub returns [] in any case.
    Will remain GREEN after full implementation.
    """
    monkeypatch.setenv("UDEMY_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("UDEMY_CLIENT_SECRET", "test-client-secret")

    empty_response = {"count": 0, "results": []}

    respx.get(UDEMY_API_URL).mock(
        return_value=Response(200, json=empty_response)
    )

    async with UdemyScanner() as scanner:
        result = await scanner.scan_niche("marketing-digital", "Marketing", niche_id=1)

    assert result == [], f"Expected [], got {result}"


@pytest.mark.asyncio
@respx.mock
async def test_api_discontinued_fallback(monkeypatch, capsys):
    """respx returns HTTP 401 -> result == [], log contains alert='api_discontinued'.

    GREEN: This test PASSES with the stub (HTTP error handling is implemented).

    NOTE: structlog is configured with PrintLoggerFactory + JSONRenderer in base_scraper.py.
    We verify the structured log via capsys (stdout JSON) rather than capture_logs().
    """
    monkeypatch.setenv("UDEMY_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("UDEMY_CLIENT_SECRET", "test-client-secret")

    respx.get(UDEMY_API_URL).mock(
        return_value=Response(401, json={"detail": "Authentication credentials were not provided."})
    )

    async with UdemyScanner() as scanner:
        result = await scanner.scan_niche("marketing-digital", "Marketing", niche_id=1)

    assert result == [], f"Expected [], got {result}"
    captured = capsys.readouterr()
    assert "api_discontinued" in captured.out, (
        f"Expected 'api_discontinued' in stdout log, got: {captured.out!r}"
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
        "VALUES (9, 'Udemy', 'udemy', 'https://www.udemy.com', '2026-01-01T00:00:00Z')"
    )
    db.execute(
        "INSERT OR IGNORE INTO niches (id, name, slug, created_at) "
        "VALUES (1, 'Marketing Digital', 'marketing-digital', '2026-01-01T00:00:00Z')"
    )

    product = Product(
        external_id="1234567",
        title="Complete Digital Marketing Course 2024",
        url="https://www.udemy.com/course/complete-digital-marketing-course/",
        platform_id=UDEMY_PLATFORM_ID,
        niche_id=1,
        rank=1,
        price=19.99,
        rating=4.6,
        thumbnail_url="https://img-c.udemycdn.com/course/480x270/1234567_abc1_3.jpg",
    )
    upsert_product(db, product)

    count_1 = list(db.execute(
        "SELECT COUNT(*) FROM products WHERE platform_id=? AND external_id=?",
        [UDEMY_PLATFORM_ID, "1234567"],
    ))[0][0]
    assert count_1 == 1, f"Expected 1 row after first upsert, got {count_1}"

    # Re-insert with different rank
    product_v2 = Product(
        external_id="1234567",
        title="Complete Digital Marketing Course 2024",
        url="https://www.udemy.com/course/complete-digital-marketing-course/",
        platform_id=UDEMY_PLATFORM_ID,
        niche_id=1,
        rank=2,
        price=19.99,
        rating=4.6,
        thumbnail_url="https://img-c.udemycdn.com/course/480x270/1234567_abc1_3.jpg",
    )
    upsert_product(db, product_v2)

    count_2 = list(db.execute(
        "SELECT COUNT(*) FROM products WHERE platform_id=? AND external_id=?",
        [UDEMY_PLATFORM_ID, "1234567"],
    ))[0][0]
    assert count_2 == 1, f"Expected still 1 row after second upsert, got {count_2}"

    rank_row = list(db.execute(
        "SELECT rank FROM products WHERE platform_id=? AND external_id=?",
        [UDEMY_PLATFORM_ID, "1234567"],
    ))[0]
    assert rank_row[0] == 2, f"Expected rank=2 after update, got {rank_row[0]}"
