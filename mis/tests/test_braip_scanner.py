"""Tests for BraipScanner — Nuxt.js SSR marketplace scanner (SCAN-BR-04).

6 tests:
- test_happy_path: scan_niche() with fixture HTML returns >= 1 product with all required fields
- test_field_types: rank is int, price is float (centavos/100), external_id is non-empty str
- test_fallback_selector: HTML without window.__NUXT__ -> returns []
- test_drift_alert: HTML without __NUXT__ or __NUXT_DATA__ -> alert='schema_drift' in logs
- test_upsert_no_duplicates: insert product -> reinsert with different rank -> 1 row, rank updated
- test_is_stale: upsert -> mark_stale -> is_stale=1; upsert again -> is_stale=0
"""
import pytest
import respx
from pathlib import Path
from httpx import Response
import structlog
import structlog.testing

from mis.scanners.braip import BraipScanner, _parse_nuxt_products
from mis.platform_ids import BRAIP_PLATFORM_ID

FIXTURE_HTML = Path(__file__).parent / "fixtures/braip/catalog_cursos-online.html"
BRAIP_SEARCH_URL = "https://marketplace.braip.com/search"


@pytest.mark.asyncio
@respx.mock
async def test_happy_path():
    """scan_niche() with fixture HTML must return >= 1 product with all required fields."""
    html_content = FIXTURE_HTML.read_text(encoding="utf-8")
    respx.get(BRAIP_SEARCH_URL).mock(
        return_value=Response(200, text=html_content)
    )

    async with BraipScanner() as scanner:
        result = await scanner.scan_niche("marketing-digital", "cursos-online", niche_id=2)

    assert len(result) >= 1, f"Expected >= 1 product, got {len(result)}"
    product = result[0]
    assert product.external_id != "", "external_id must be non-empty"
    assert product.title != "", "title must be non-empty"
    assert product.url.startswith("https://"), "url must be absolute HTTPS"
    assert product.platform_id == BRAIP_PLATFORM_ID
    assert product.niche_id == 2
    assert product.rank == 1


@pytest.mark.asyncio
@respx.mock
async def test_field_types():
    """rank is int, price is float (centavos/100), external_id is non-empty str."""
    html_content = FIXTURE_HTML.read_text(encoding="utf-8")
    respx.get(BRAIP_SEARCH_URL).mock(
        return_value=Response(200, text=html_content)
    )

    async with BraipScanner() as scanner:
        result = await scanner.scan_niche("marketing-digital", "cursos-online", niche_id=2)

    assert len(result) >= 1
    product = result[0]
    assert isinstance(product.rank, int), f"rank must be int, got {type(product.rank)}"
    assert isinstance(product.external_id, str) and product.external_id != "", (
        f"external_id must be non-empty str, got {product.external_id!r}"
    )
    if product.price is not None:
        assert isinstance(product.price, float), f"price must be float, got {type(product.price)}"
        # Price should be centavos/100 (e.g. 2990 -> 29.90)
        # Not an integer value (would mean centavos not divided)
        assert product.price < 10000, f"price looks like centavos, not divided by 100: {product.price}"


@pytest.mark.asyncio
@respx.mock
async def test_fallback_selector():
    """HTML without window.__NUXT__ returns [] — graceful degradation."""
    plain_html = "<html><body><p>No NUXT data here</p></body></html>"
    respx.get(BRAIP_SEARCH_URL).mock(
        return_value=Response(200, text=plain_html)
    )

    async with BraipScanner() as scanner:
        result = await scanner.scan_niche("marketing-digital", "cursos-online", niche_id=2)

    assert result == [], f"Expected [], got {result}"


@pytest.mark.asyncio
@respx.mock
async def test_drift_alert():
    """HTML without __NUXT__ or __NUXT_DATA__ -> alert='schema_drift' in logs."""
    plain_html = "<html><body><p>No NUXT data here</p></body></html>"
    respx.get(BRAIP_SEARCH_URL).mock(
        return_value=Response(200, text=plain_html)
    )

    with structlog.testing.capture_logs() as cap:
        async with BraipScanner() as scanner:
            await scanner.scan_niche("marketing-digital", "cursos-online", niche_id=2)

    alerts = [e for e in cap if e.get("alert") == "schema_drift"]
    assert len(alerts) >= 1, (
        f"Expected at least 1 event with alert='schema_drift', got: {cap}"
    )


@pytest.mark.asyncio
async def test_upsert_no_duplicates(tmp_path):
    """Insert product -> reinsert with different rank -> 1 row in DB, rank updated."""
    from mis.db import get_db, run_migrations
    from mis.product_repository import upsert_product
    from mis.scanner import Product

    db_path = str(tmp_path / "mis.db")
    run_migrations(db_path)
    db = get_db(db_path)

    db.execute(
        "INSERT OR IGNORE INTO platforms (id, name, slug, base_url, created_at) "
        "VALUES (7, 'Braip', 'braip', 'https://marketplace.braip.com', '2026-01-01T00:00:00Z')"
    )
    db.execute(
        "INSERT OR IGNORE INTO niches (id, name, slug, created_at) "
        "VALUES (2, 'Marketing', 'marketing-digital', '2026-01-01T00:00:00Z')"
    )

    product = Product(
        external_id="proown9j",
        title="Braip Pages",
        url="https://marketplace.braip.com/braip-pages",
        platform_id=BRAIP_PLATFORM_ID,
        niche_id=2,
        rank=1,
        price=29.90,
    )
    upsert_product(db, product)

    count_1 = list(db.execute(
        "SELECT COUNT(*) FROM products WHERE platform_id=? AND external_id=?",
        [BRAIP_PLATFORM_ID, "proown9j"],
    ))[0][0]
    assert count_1 == 1, f"Expected 1 row after first upsert, got {count_1}"

    # Re-insert with different rank
    product_v2 = Product(
        external_id="proown9j",
        title="Braip Pages",
        url="https://marketplace.braip.com/braip-pages",
        platform_id=BRAIP_PLATFORM_ID,
        niche_id=2,
        rank=3,
        price=29.90,
    )
    upsert_product(db, product_v2)

    count_2 = list(db.execute(
        "SELECT COUNT(*) FROM products WHERE platform_id=? AND external_id=?",
        [BRAIP_PLATFORM_ID, "proown9j"],
    ))[0][0]
    assert count_2 == 1, f"Expected still 1 row after second upsert, got {count_2}"

    rank_row = list(db.execute(
        "SELECT rank FROM products WHERE platform_id=? AND external_id=?",
        [BRAIP_PLATFORM_ID, "proown9j"],
    ))[0]
    assert rank_row[0] == 3, f"Expected rank=3 after update, got {rank_row[0]}"


@pytest.mark.asyncio
async def test_is_stale(tmp_path):
    """upsert product -> mark_stale -> is_stale=1; upsert again -> is_stale=0."""
    from mis.db import get_db, run_migrations
    from mis.product_repository import upsert_product, mark_stale
    from mis.scanner import Product

    db_path = str(tmp_path / "mis.db")
    run_migrations(db_path)
    db = get_db(db_path)

    db.execute(
        "INSERT OR IGNORE INTO platforms (id, name, slug, base_url, created_at) "
        "VALUES (7, 'Braip', 'braip', 'https://marketplace.braip.com', '2026-01-01T00:00:00Z')"
    )
    db.execute(
        "INSERT OR IGNORE INTO niches (id, name, slug, created_at) "
        "VALUES (2, 'Marketing', 'marketing-digital', '2026-01-01T00:00:00Z')"
    )

    product = Product(
        external_id="braip-test-001",
        title="Produto Braip Teste",
        url="https://marketplace.braip.com/produto-teste",
        platform_id=BRAIP_PLATFORM_ID,
        niche_id=2,
        rank=1,
        price=29.90,
    )
    upsert_product(db, product)
    row = list(db.execute(
        "SELECT is_stale FROM products WHERE platform_id=? AND external_id=?",
        [BRAIP_PLATFORM_ID, "braip-test-001"],
    ))[0]
    assert row[0] == 0, "is_stale deve ser 0 após upsert"

    mark_stale(db, BRAIP_PLATFORM_ID, 2)
    row = list(db.execute(
        "SELECT is_stale FROM products WHERE platform_id=? AND external_id=?",
        [BRAIP_PLATFORM_ID, "braip-test-001"],
    ))[0]
    assert row[0] == 1, "is_stale deve ser 1 após mark_stale()"

    upsert_product(db, product)
    row = list(db.execute(
        "SELECT is_stale FROM products WHERE platform_id=? AND external_id=?",
        [BRAIP_PLATFORM_ID, "braip-test-001"],
    ))[0]
    assert row[0] == 0, "is_stale deve ser resetado para 0 após upsert"
