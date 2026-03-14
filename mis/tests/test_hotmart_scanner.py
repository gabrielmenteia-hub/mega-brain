"""Tests for HotmartScanner — TDD RED phase.

These tests cover SCAN-01 requirements:
  1. test_happy_path          — scan_niche returns >= 10 products with all mandatory fields
  2. test_field_types         — rank is int, external_id is non-empty str, price is None (SSR has no price)
  3. test_fallback_selector   — fallback selector works when primary selector is absent
  4. test_drift_alert         — alert='schema_drift' emitted when no selector matches
  5. test_upsert_no_duplicates — DB upsert: same product twice → 1 row, rank updated

Hotmart marketplace is SSR (confirmed by live inspection 2026-03-14).
Products are embedded in HTML — httpx is sufficient, no Playwright needed.
URL: https://hotmart.com/pt-br/marketplace/produtos?category={category_slug}
Primary selector: a.product-link (24 products confirmed in fixture)
external_id: alphanumeric code from URL (e.g. E45853768C)

All tests use respx.mock to intercept httpx requests (fixture HTML served locally).
DB tests use real SQLite DB in tmp_path.
"""
import pytest
import respx
from pathlib import Path
from httpx import Response
from structlog.testing import capture_logs

FIXTURE_HTML = Path(__file__).parent / "fixtures/hotmart/catalog_saude.html"
HOTMART_PRODUCTS_URL = "https://hotmart.com/pt-br/marketplace/produtos"


# NOTE: These tests are written in RED phase — HotmartScanner does not exist yet.
# All tests are expected to fail with ImportError or AttributeError.


@pytest.mark.asyncio
@respx.mock
async def test_happy_path(tmp_path):
    """scan_niche returns >= 10 products, all with mandatory fields."""
    from mis.scanners.hotmart import HotmartScanner
    from mis.scanner import Product

    html = FIXTURE_HTML.read_text(encoding="utf-8")
    respx.get(HOTMART_PRODUCTS_URL).mock(return_value=Response(200, text=html))

    async with HotmartScanner() as scanner:
        products = await scanner.scan_niche("saude", "saude-e-fitness")

    assert len(products) >= 10, f"Expected >= 10 products, got {len(products)}"

    mandatory_fields = ("external_id", "title", "url", "platform_id", "niche_id", "rank")
    for p in products:
        for field in mandatory_fields:
            assert getattr(p, field) is not None, f"Field {field!r} is None in {p}"
        assert isinstance(p, Product)


@pytest.mark.asyncio
@respx.mock
async def test_field_types(tmp_path):
    """rank is int, external_id is non-empty str, price is None (not in SSR HTML)."""
    from mis.scanners.hotmart import HotmartScanner

    html = FIXTURE_HTML.read_text(encoding="utf-8")
    respx.get(HOTMART_PRODUCTS_URL).mock(return_value=Response(200, text=html))

    async with HotmartScanner() as scanner:
        products = await scanner.scan_niche("saude", "saude-e-fitness")

    assert len(products) >= 1, "Need at least one product to check types"
    for p in products:
        assert isinstance(p.rank, int), f"rank should be int, got {type(p.rank)}"
        assert isinstance(p.external_id, str) and len(p.external_id) > 0, (
            f"external_id should be non-empty str, got {p.external_id!r}"
        )
        # Price is not available in Hotmart SSR HTML
        assert p.price is None, f"price should be None (SSR has no price), got {p.price!r}"


@pytest.mark.asyncio
@respx.mock
async def test_fallback_selector(tmp_path):
    """When primary selector (a.product-link) is absent, fallback selector returns products."""
    from mis.scanners.hotmart import HotmartScanner

    # HTML without the primary selector but WITH the fallback selector
    fallback_html = """
    <html><body>
    <div class="product-card-alt">
      <a href="https://hotmart.com/pt-br/marketplace/produtos/produto-fallback-1/A1234567B?sck=X"
         aria-label="Produto Fallback 1 - Autor Teste: ">
        Produto Fallback 1
      </a>
    </div>
    <div class="product-card-alt">
      <a href="https://hotmart.com/pt-br/marketplace/produtos/produto-fallback-2/B9876543A?sck=X"
         aria-label="Produto Fallback 2 - Autor Teste: ">
        Produto Fallback 2
      </a>
    </div>
    <div class="product-card-alt">
      <a href="https://hotmart.com/pt-br/marketplace/produtos/produto-fallback-3/C1122334D?sck=X"
         aria-label="Produto Fallback 3 - Autor Teste: ">
        Produto Fallback 3
      </a>
    </div>
    </body></html>
    """
    respx.get(HOTMART_PRODUCTS_URL).mock(return_value=Response(200, text=fallback_html))

    async with HotmartScanner() as scanner:
        products = await scanner.scan_niche("saude", "saude-e-fitness")

    assert len(products) >= 1, "Fallback selector should return at least one product"
    for p in products:
        assert p.external_id is not None
        assert p.title is not None


@pytest.mark.asyncio
@respx.mock
async def test_drift_alert(tmp_path):
    """When no selector matches, capture_logs shows alert='schema_drift' and [] is returned."""
    from mis.scanners.hotmart import HotmartScanner

    # HTML with no recognized selectors
    broken_html = "<html><body><div class='completely-unknown'>nothing here</div></body></html>"
    respx.get(HOTMART_PRODUCTS_URL).mock(return_value=Response(200, text=broken_html))

    with capture_logs() as cap:
        async with HotmartScanner() as scanner:
            products = await scanner.scan_niche("saude", "saude-e-fitness")

    assert products == [], f"Expected empty list on drift, got {products}"
    assert any(
        e.get("alert") == "schema_drift" for e in cap
    ), f"Expected alert='schema_drift' in logs. Got: {cap}"


@pytest.mark.asyncio
async def test_upsert_no_duplicates(tmp_path):
    """DB upsert: inserting same product twice with different rank → 1 row, latest rank."""
    from mis.db import get_db, run_migrations
    from mis.migrations._002_product_enrichment import run_migration_002
    from mis.product_repository import upsert_product
    from mis.scanner import Product

    db_path = str(tmp_path / "mis.db")
    run_migrations(db_path)
    run_migration_002(db_path)

    # Insert a platform entry so FK constraint is satisfied
    db = get_db(db_path)
    db["platforms"].insert(
        {"id": 1, "name": "Hotmart", "slug": "hotmart", "base_url": "https://hotmart.com", "created_at": "2026-01-01T00:00:00Z"},
        ignore=True,
    )
    db["niches"].insert(
        {"id": 1, "name": "Saude", "slug": "saude", "created_at": "2026-01-01T00:00:00Z"},
        ignore=True,
    )

    product_v1 = Product(
        external_id="E45853768C",
        title="Curso de Cutilagem para Manicures",
        url="https://hotmart.com/pt-br/marketplace/produtos/aulas-de-manicure/E45853768C",
        platform_id=1,
        niche_id=1,
        rank=5,
        price=None,
    )
    product_v2 = Product(
        external_id="E45853768C",
        title="Curso de Cutilagem para Manicures",
        url="https://hotmart.com/pt-br/marketplace/produtos/aulas-de-manicure/E45853768C",
        platform_id=1,
        niche_id=1,
        rank=1,  # rank updated
        price=None,
    )

    upsert_product(db, product_v1)
    upsert_product(db, product_v2)

    rows = list(db["products"].rows_where(
        "platform_id = ? AND external_id = ?",
        [1, "E45853768C"],
    ))

    assert len(rows) == 1, f"Expected 1 row after 2 upserts, got {len(rows)}"
    assert rows[0]["rank"] == 1, f"Expected rank=1 (latest), got {rows[0]['rank']}"
