"""Tests for ClickBankScanner — TDD RED phase.

These tests cover SCAN-03 requirements:
  1. test_happy_path           — scan_niche returns >= 5 products with all mandatory fields
  2. test_field_types          — rank is int, external_id is non-empty str, price is float or None
  3. test_fallback_gravity     — gravity as int (rounded), falls back to positional rank if None
  4. test_drift_alert          — alert='schema_drift' when GraphQL returns empty hits
  5. test_upsert_no_duplicates — DB upsert: same external_id twice → 1 row with updated rank

ClickBank marketplace uses a React SPA backed by GraphQL API (POST /graphql).
No authentication required for public marketplace search.
external_id = product 'site' field (uppercase ClickBank vendor ID, e.g. "BRAINSONGX").
gravity = marketplaceStats.gravity (float → int conversion) or positional rank if None.

All tests use respx.mock to intercept httpx POST requests to the GraphQL endpoint.
DB tests use real SQLite DB in tmp_path.
"""
import json
import pytest
import respx
from pathlib import Path
from httpx import Response
from structlog.testing import capture_logs

FIXTURE_HEALTH = Path(__file__).parent / "fixtures/clickbank/marketplace_health.json"
FIXTURE_MKTG = Path(__file__).parent / "fixtures/clickbank/marketplace_mktg.json"
CB_GRAPHQL_URL = "https://accounts.clickbank.com/graphql"


# NOTE: These tests are written in RED phase — ClickBankScanner does not exist yet.
# All tests are expected to fail with ImportError or AttributeError.


@pytest.mark.asyncio
@respx.mock
async def test_happy_path(tmp_path):
    """scan_niche returns >= 5 products, all with mandatory fields."""
    from mis.scanners.clickbank import ClickBankScanner
    from mis.scanner import Product

    health_data = json.loads(FIXTURE_HEALTH.read_text(encoding="utf-8"))
    respx.post(CB_GRAPHQL_URL).mock(
        return_value=Response(200, json=health_data)
    )

    async with ClickBankScanner() as scanner:
        products = await scanner.scan_niche("health", "Health & Fitness")

    assert len(products) >= 5, f"Expected >= 5 products, got {len(products)}"

    mandatory_fields = ("external_id", "title", "url", "platform_id", "niche_id", "rank")
    for p in products:
        for field_name in mandatory_fields:
            assert getattr(p, field_name) is not None, (
                f"Field {field_name!r} is None in {p}"
            )
        assert isinstance(p, Product)


@pytest.mark.asyncio
@respx.mock
async def test_field_types(tmp_path):
    """rank is int, external_id is non-empty str, price is float or None."""
    from mis.scanners.clickbank import ClickBankScanner

    health_data = json.loads(FIXTURE_HEALTH.read_text(encoding="utf-8"))
    respx.post(CB_GRAPHQL_URL).mock(
        return_value=Response(200, json=health_data)
    )

    async with ClickBankScanner() as scanner:
        products = await scanner.scan_niche("health", "Health & Fitness")

    assert len(products) >= 1, "Need at least one product to check types"
    for p in products:
        assert isinstance(p.rank, int), (
            f"rank should be int, got {type(p.rank)} = {p.rank!r}"
        )
        assert isinstance(p.external_id, str) and len(p.external_id) > 0, (
            f"external_id should be non-empty str, got {p.external_id!r}"
        )
        if p.price is not None:
            assert isinstance(p.price, float), (
                f"price should be float or None, got {type(p.price)}"
            )


@pytest.mark.asyncio
@respx.mock
async def test_fallback_gravity(tmp_path):
    """When gravity is None in response, rank falls back to positional (1-indexed)."""
    from mis.scanners.clickbank import ClickBankScanner

    # Craft a response where gravity is None (e.g. unauthorized / private stats)
    no_gravity_data = {
        "data": {
            "marketplaceSearch": {
                "totalHits": 3,
                "offset": 0,
                "hits": [
                    {
                        "site": "PRODUCT_A",
                        "title": "Product A",
                        "description": "Desc A",
                        "url": "https://productA.com/",
                        "offerImageUrl": None,
                        "marketplaceStats": {
                            "category": "Health & Fitness",
                            "gravity": None,
                            "rank": None,
                            "biGravity": None,
                            "averageDollarsPerSale": 100.0,
                            "initialDollarsPerSale": 100.0,
                        },
                    },
                    {
                        "site": "PRODUCT_B",
                        "title": "Product B",
                        "description": "Desc B",
                        "url": "https://productB.com/",
                        "offerImageUrl": None,
                        "marketplaceStats": {
                            "category": "Health & Fitness",
                            "gravity": None,
                            "rank": None,
                            "biGravity": None,
                            "averageDollarsPerSale": 80.0,
                            "initialDollarsPerSale": 80.0,
                        },
                    },
                    {
                        "site": "PRODUCT_C",
                        "title": "Product C",
                        "description": "Desc C",
                        "url": "https://productC.com/",
                        "offerImageUrl": None,
                        "marketplaceStats": {
                            "category": "Health & Fitness",
                            "gravity": None,
                            "rank": None,
                            "biGravity": None,
                            "averageDollarsPerSale": 60.0,
                            "initialDollarsPerSale": 60.0,
                        },
                    },
                ],
            }
        }
    }
    respx.post(CB_GRAPHQL_URL).mock(
        return_value=Response(200, json=no_gravity_data)
    )

    async with ClickBankScanner() as scanner:
        products = await scanner.scan_niche("health", "Health & Fitness")

    assert len(products) == 3, f"Expected 3 products, got {len(products)}"
    # Positional rank: 1-indexed
    assert products[0].rank == 1
    assert products[1].rank == 2
    assert products[2].rank == 3


@pytest.mark.asyncio
@respx.mock
async def test_drift_alert(tmp_path):
    """When GraphQL returns empty hits, alert='schema_drift' emitted and [] returned."""
    from mis.scanners.clickbank import ClickBankScanner

    # Empty hits — triggers schema_drift
    empty_data = {
        "data": {
            "marketplaceSearch": {
                "totalHits": 0,
                "offset": 0,
                "hits": [],
            }
        }
    }
    respx.post(CB_GRAPHQL_URL).mock(
        return_value=Response(200, json=empty_data)
    )

    with capture_logs() as cap:
        async with ClickBankScanner() as scanner:
            products = await scanner.scan_niche("health", "Health & Fitness")

    assert products == [], f"Expected empty list on drift, got {products}"
    assert any(
        e.get("alert") == "schema_drift" for e in cap
    ), f"Expected alert='schema_drift' in logs. Got: {cap}"


@pytest.mark.asyncio
@respx.mock
async def test_upsert_no_duplicates(tmp_path):
    """DB upsert: inserting same product twice with different rank → 1 row, latest rank."""
    from mis.db import get_db, run_migrations
    from mis.migrations._002_product_enrichment import run_migration_002
    from mis.product_repository import upsert_product
    from mis.scanner import Product

    db_path = str(tmp_path / "mis.db")
    run_migrations(db_path)
    run_migration_002(db_path)

    db = get_db(db_path)
    # Insert platform entry (ClickBank = platform_id 2)
    db["platforms"].insert(
        {
            "id": 2,
            "name": "ClickBank",
            "slug": "clickbank",
            "base_url": "https://accounts.clickbank.com",
            "created_at": "2026-01-01T00:00:00Z",
        },
        ignore=True,
    )
    db["niches"].insert(
        {
            "id": 1,
            "name": "Health",
            "slug": "health",
            "created_at": "2026-01-01T00:00:00Z",
        },
        ignore=True,
    )

    CLICKBANK_PLATFORM_ID = 2

    product_v1 = Product(
        external_id="BRAINSONGX",
        title="The Brain Song",
        url="https://forbrainsong.com/",
        platform_id=CLICKBANK_PLATFORM_ID,
        niche_id=1,
        rank=5,
        price=55.0,
    )
    product_v2 = Product(
        external_id="BRAINSONGX",
        title="The Brain Song",
        url="https://forbrainsong.com/",
        platform_id=CLICKBANK_PLATFORM_ID,
        niche_id=1,
        rank=1,  # rank updated
        price=55.0,
    )

    upsert_product(db, product_v1)
    upsert_product(db, product_v2)

    rows = list(
        db["products"].rows_where(
            "platform_id = ? AND external_id = ?",
            [CLICKBANK_PLATFORM_ID, "BRAINSONGX"],
        )
    )

    assert len(rows) == 1, f"Expected 1 row after 2 upserts, got {len(rows)}"
    assert rows[0]["rank"] == 1, f"Expected rank=1 (latest), got {rows[0]['rank']}"
