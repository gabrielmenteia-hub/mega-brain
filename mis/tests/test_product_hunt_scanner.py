"""Tests for ProductHuntScanner — GraphQL API v2 trending scanner (SCAN-INTL-01).

6 tests:
- test_happy_path: respx.mock POST returns trending_today.json -> >= 1 product, rank=1, platform_id, external_id
- test_field_types: rank is int, price is None, external_id is non-empty str, thumbnail_url is str or None
- test_missing_credentials: PRODUCT_HUNT_API_TOKEN absent -> result == [], alert='missing_credentials'
- test_empty_results: respx returns edges=[] -> result == []
- test_upsert_no_duplicates: upsert product -> reinsert same external_id with rank=2 -> 1 row, rank updated
- test_is_stale: upsert -> mark_stale -> is_stale=1; upsert again -> is_stale=0

NOTE: test_happy_path and test_field_types are RED (stubs return []).
test_missing_credentials is GREEN (stub implements credential check).
"""
import json
import pytest
import respx
from pathlib import Path
from httpx import Response
import structlog.testing

from mis.scanners.product_hunt import ProductHuntScanner, PRODUCT_HUNT_GRAPHQL_URL
from mis.platform_ids import PRODUCT_HUNT_PLATFORM_ID

FIXTURE_PATH = Path(__file__).parent / "fixtures/product_hunt/trending_today.json"


@pytest.mark.asyncio
@respx.mock
async def test_happy_path(monkeypatch):
    """scan_niche() with fixture JSON must return >= 1 product with required fields.

    RED: This test FAILS with the stub (returns []).
    Will pass after GREEN implementation in plan 15-02.
    """
    monkeypatch.setenv("PRODUCT_HUNT_API_TOKEN", "test-token-abc123")
    fixture_data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    respx.post(PRODUCT_HUNT_GRAPHQL_URL).mock(
        return_value=Response(200, json=fixture_data)
    )

    async with ProductHuntScanner() as scanner:
        result = await scanner.scan_niche("marketing-digital", "trending", niche_id=1)

    assert len(result) >= 1, f"Expected >= 1 product, got {len(result)}"
    product = result[0]
    assert product.rank == 1, f"Expected rank=1, got {product.rank}"
    assert product.platform_id == PRODUCT_HUNT_PLATFORM_ID, (
        f"Expected platform_id={PRODUCT_HUNT_PLATFORM_ID}, got {product.platform_id}"
    )
    assert product.external_id == "jarvis-ai-assistant", (
        f"Expected external_id='jarvis-ai-assistant', got {product.external_id!r}"
    )


@pytest.mark.asyncio
@respx.mock
async def test_field_types(monkeypatch):
    """rank is int, price is None, external_id is non-empty str, thumbnail_url is str or None.

    RED: This test FAILS with the stub (returns []).
    Will pass after GREEN implementation in plan 15-02.
    """
    monkeypatch.setenv("PRODUCT_HUNT_API_TOKEN", "test-token-abc123")
    fixture_data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    respx.post(PRODUCT_HUNT_GRAPHQL_URL).mock(
        return_value=Response(200, json=fixture_data)
    )

    async with ProductHuntScanner() as scanner:
        result = await scanner.scan_niche("marketing-digital", "trending", niche_id=1)

    assert len(result) >= 1, f"Expected >= 1 product, got {len(result)}"
    product = result[0]
    assert isinstance(product.rank, int), f"rank must be int, got {type(product.rank)}"
    assert product.price is None, (
        f"price must be None for ProductHunt (no monetary price in API), got {product.price}"
    )
    assert isinstance(product.external_id, str) and product.external_id != "", (
        f"external_id must be non-empty str, got {product.external_id!r}"
    )
    assert product.thumbnail_url is None or isinstance(product.thumbnail_url, str), (
        f"thumbnail_url must be str or None, got {type(product.thumbnail_url)}"
    )


@pytest.mark.asyncio
async def test_missing_credentials(monkeypatch):
    """PRODUCT_HUNT_API_TOKEN absent -> result == [], log contains alert='missing_credentials'.

    GREEN: This test PASSES with the stub (credential check is implemented).
    """
    monkeypatch.delenv("PRODUCT_HUNT_API_TOKEN", raising=False)

    with structlog.testing.capture_logs() as cap:
        async with ProductHuntScanner() as scanner:
            result = await scanner.scan_niche("marketing-digital", "trending", niche_id=1)

    assert result == [], f"Expected [], got {result}"
    alerts = [e for e in cap if e.get("alert") == "missing_credentials"]
    assert len(alerts) >= 1, (
        f"Expected at least 1 event with alert='missing_credentials', got: {cap}"
    )


@pytest.mark.asyncio
@respx.mock
async def test_empty_results(monkeypatch):
    """respx returns edges=[], hasNextPage=false -> result == [].

    Behavior depends on implementation — stub returns [] in any case.
    Will remain GREEN after full implementation.
    """
    monkeypatch.setenv("PRODUCT_HUNT_API_TOKEN", "test-token-abc123")

    empty_response = {
        "data": {
            "posts": {
                "edges": [],
                "pageInfo": {
                    "hasNextPage": False,
                    "endCursor": None,
                },
            }
        }
    }

    respx.post(PRODUCT_HUNT_GRAPHQL_URL).mock(
        return_value=Response(200, json=empty_response)
    )

    async with ProductHuntScanner() as scanner:
        result = await scanner.scan_niche("marketing-digital", "trending", niche_id=1)

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
        "VALUES (8, 'Product Hunt', 'product_hunt', 'https://www.producthunt.com', '2026-01-01T00:00:00Z')"
    )
    db.execute(
        "INSERT OR IGNORE INTO niches (id, name, slug, created_at) "
        "VALUES (1, 'Marketing Digital', 'marketing-digital', '2026-01-01T00:00:00Z')"
    )

    product = Product(
        external_id="jarvis-ai-assistant",
        title="Jarvis AI Assistant",
        url="https://www.producthunt.com/posts/jarvis-ai-assistant",
        platform_id=PRODUCT_HUNT_PLATFORM_ID,
        niche_id=1,
        rank=1,
        price=None,
        thumbnail_url="https://ph-files.imgix.net/abc123/jarvis-thumb.png",
    )
    upsert_product(db, product)

    count_1 = list(db.execute(
        "SELECT COUNT(*) FROM products WHERE platform_id=? AND external_id=?",
        [PRODUCT_HUNT_PLATFORM_ID, "jarvis-ai-assistant"],
    ))[0][0]
    assert count_1 == 1, f"Expected 1 row after first upsert, got {count_1}"

    # Re-insert with different rank
    product_v2 = Product(
        external_id="jarvis-ai-assistant",
        title="Jarvis AI Assistant",
        url="https://www.producthunt.com/posts/jarvis-ai-assistant",
        platform_id=PRODUCT_HUNT_PLATFORM_ID,
        niche_id=1,
        rank=2,
        price=None,
        thumbnail_url="https://ph-files.imgix.net/abc123/jarvis-thumb.png",
    )
    upsert_product(db, product_v2)

    count_2 = list(db.execute(
        "SELECT COUNT(*) FROM products WHERE platform_id=? AND external_id=?",
        [PRODUCT_HUNT_PLATFORM_ID, "jarvis-ai-assistant"],
    ))[0][0]
    assert count_2 == 1, f"Expected still 1 row after second upsert, got {count_2}"

    rank_row = list(db.execute(
        "SELECT rank FROM products WHERE platform_id=? AND external_id=?",
        [PRODUCT_HUNT_PLATFORM_ID, "jarvis-ai-assistant"],
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
        "VALUES (8, 'Product Hunt', 'product_hunt', 'https://www.producthunt.com', '2026-01-01T00:00:00Z')"
    )
    db.execute(
        "INSERT OR IGNORE INTO niches (id, name, slug, created_at) "
        "VALUES (1, 'Marketing Digital', 'marketing-digital', '2026-01-01T00:00:00Z')"
    )

    product = Product(
        external_id="ph-test-001",
        title="Product Hunt Test",
        url="https://www.producthunt.com/posts/ph-test-001",
        platform_id=PRODUCT_HUNT_PLATFORM_ID,
        niche_id=1,
        rank=1,
        price=None,
    )
    upsert_product(db, product)

    row = list(db.execute(
        "SELECT is_stale FROM products WHERE platform_id=? AND external_id=?",
        [PRODUCT_HUNT_PLATFORM_ID, "ph-test-001"],
    ))[0]
    assert row[0] == 0, "is_stale deve ser 0 apos upsert inicial"

    mark_stale(db, PRODUCT_HUNT_PLATFORM_ID, 1)
    row = list(db.execute(
        "SELECT is_stale FROM products WHERE platform_id=? AND external_id=?",
        [PRODUCT_HUNT_PLATFORM_ID, "ph-test-001"],
    ))[0]
    assert row[0] == 1, "is_stale deve ser 1 apos mark_stale()"

    upsert_product(db, product)
    row = list(db.execute(
        "SELECT is_stale FROM products WHERE platform_id=? AND external_id=?",
        [PRODUCT_HUNT_PLATFORM_ID, "ph-test-001"],
    ))[0]
    assert row[0] == 0, "is_stale deve ser resetado para 0 apos upsert"
