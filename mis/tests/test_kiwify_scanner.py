"""Tests for KiwifyScanner — TDD RED phase.

These tests cover SCAN-02 requirements:
  1. test_happy_path        — scan_niche returns >= 10 products with all mandatory fields
  2. test_field_types       — price is float or None, rank is int, external_id is non-empty str
  3. test_fallback_selector — fallback selector works when primary selector is absent
  4. test_drift_alert       — alert='schema_drift' emitted when no selector matches
  5. test_upsert_no_duplicates — DB upsert: same product twice → 1 row with updated rank

All tests use respx.mock to intercept httpx requests (fixtures HTML served locally).
DB tests use real SQLite DB in tmp_path.
"""
import pytest
import respx
from pathlib import Path
from httpx import Response
from structlog.testing import capture_logs

FIXTURE_SAUDE = Path(__file__).parent / "fixtures/kiwify/catalog_saude.html"
KIWIFY_SAUDE_URL = "https://kiwify.com.br/marketplace?category=saude"

# NOTE: These tests are written in RED phase — KiwifyScanner does not exist yet.
# All tests are expected to fail with ImportError or AttributeError.


@pytest.mark.asyncio
@respx.mock
async def test_happy_path(tmp_path):
    """scan_niche returns >= 10 products, all with mandatory fields."""
    from mis.scanners.kiwify import KiwifyScanner
    from mis.scanner import Product

    html = FIXTURE_SAUDE.read_text(encoding="utf-8")
    respx.get(KIWIFY_SAUDE_URL).mock(return_value=Response(200, text=html))

    async with KiwifyScanner() as scanner:
        products = await scanner.scan_niche("emagrecimento", "saude")

    assert len(products) >= 10, f"Expected >= 10 products, got {len(products)}"

    mandatory_fields = ("external_id", "title", "url", "platform_id", "niche_id", "rank")
    for p in products:
        for field in mandatory_fields:
            assert getattr(p, field) is not None, f"Field {field!r} is None in {p}"
        assert isinstance(p, Product)


@pytest.mark.asyncio
@respx.mock
async def test_field_types(tmp_path):
    """price is float or None, rank is int, external_id is non-empty str."""
    from mis.scanners.kiwify import KiwifyScanner

    html = FIXTURE_SAUDE.read_text(encoding="utf-8")
    respx.get(KIWIFY_SAUDE_URL).mock(return_value=Response(200, text=html))

    async with KiwifyScanner() as scanner:
        products = await scanner.scan_niche("emagrecimento", "saude")

    assert len(products) >= 1, "Need at least one product to check types"
    for p in products:
        assert isinstance(p.rank, int), f"rank should be int, got {type(p.rank)}"
        assert isinstance(p.external_id, str) and len(p.external_id) > 0, (
            f"external_id should be non-empty str, got {p.external_id!r}"
        )
        if p.price is not None:
            assert isinstance(p.price, float), (
                f"price should be float or None, got {type(p.price)}"
            )


@pytest.mark.asyncio
@respx.mock
async def test_fallback_selector(tmp_path):
    """When primary selector absent, fallback selector still returns products."""
    from mis.scanners.kiwify import KiwifyScanner

    # HTML that does NOT have primary selector (.product-card)
    # but DOES have fallback selector ([data-testid='product-item'])
    fallback_html = """
    <html><body>
    <div data-testid="product-item" data-product-id="fallback-produto-1">
      <a href="/produto/fallback-produto-1">
        <h2>Produto Fallback 1</h2>
        <span class="price">R$ 97,00</span>
      </a>
    </div>
    <div data-testid="product-item" data-product-id="fallback-produto-2">
      <a href="/produto/fallback-produto-2">
        <h2>Produto Fallback 2</h2>
        <span class="price">R$ 147,00</span>
      </a>
    </div>
    <div data-testid="product-item" data-product-id="fallback-produto-3">
      <a href="/produto/fallback-produto-3">
        <h2>Produto Fallback 3</h2>
      </a>
    </div>
    <div data-testid="product-item" data-product-id="fallback-produto-4">
      <a href="/produto/fallback-produto-4">
        <h2>Produto Fallback 4</h2>
      </a>
    </div>
    <div data-testid="product-item" data-product-id="fallback-produto-5">
      <a href="/produto/fallback-produto-5">
        <h2>Produto Fallback 5</h2>
      </a>
    </div>
    <div data-testid="product-item" data-product-id="fallback-produto-6">
      <a href="/produto/fallback-produto-6">
        <h2>Produto Fallback 6</h2>
      </a>
    </div>
    <div data-testid="product-item" data-product-id="fallback-produto-7">
      <a href="/produto/fallback-produto-7">
        <h2>Produto Fallback 7</h2>
      </a>
    </div>
    <div data-testid="product-item" data-product-id="fallback-produto-8">
      <a href="/produto/fallback-produto-8">
        <h2>Produto Fallback 8</h2>
      </a>
    </div>
    <div data-testid="product-item" data-product-id="fallback-produto-9">
      <a href="/produto/fallback-produto-9">
        <h2>Produto Fallback 9</h2>
      </a>
    </div>
    <div data-testid="product-item" data-product-id="fallback-produto-10">
      <a href="/produto/fallback-produto-10">
        <h2>Produto Fallback 10</h2>
      </a>
    </div>
    </body></html>
    """
    respx.get(KIWIFY_SAUDE_URL).mock(return_value=Response(200, text=fallback_html))

    async with KiwifyScanner() as scanner:
        products = await scanner.scan_niche("emagrecimento", "saude")

    assert len(products) >= 1, "Fallback selector should return at least one product"
    # Confirm products have mandatory fields
    for p in products:
        assert p.external_id is not None
        assert p.title is not None


@pytest.mark.asyncio
@respx.mock
async def test_drift_alert(tmp_path):
    """When no selector matches, capture_logs shows alert='schema_drift' and [] returned."""
    from mis.scanners.kiwify import KiwifyScanner

    # HTML with no recognized selectors
    empty_html = """
    <html><body>
      <div class="completely-unknown-structure">
        <span>Some random content</span>
      </div>
    </body></html>
    """
    respx.get(KIWIFY_SAUDE_URL).mock(return_value=Response(200, text=empty_html))

    with capture_logs() as cap:
        async with KiwifyScanner() as scanner:
            products = await scanner.scan_niche("emagrecimento", "saude")

    assert products == [], f"Expected empty list on drift, got {products}"
    assert any(
        e.get("alert") == "schema_drift" for e in cap
    ), f"Expected alert='schema_drift' in logs. Got: {cap}"


@pytest.mark.asyncio
@respx.mock
async def test_upsert_no_duplicates(tmp_path):
    """DB upsert: inserting same product twice with different rank → 1 row, latest rank."""
    from mis.scanners.kiwify import KiwifyScanner
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
        {"id": 3, "name": "Kiwify", "slug": "kiwify", "base_url": "https://kiwify.com.br", "created_at": "2026-01-01T00:00:00Z"},
        ignore=True,
    )
    db["niches"].insert(
        {"id": 1, "name": "Emagrecimento", "slug": "emagrecimento", "created_at": "2026-01-01T00:00:00Z"},
        ignore=True,
    )

    product_v1 = Product(
        external_id="emagreca-de-vez-pro",
        title="Emagreça de Vez Pro",
        url="https://kiwify.com.br/produto/emagreca-de-vez-pro",
        platform_id=3,
        niche_id=1,
        rank=5,
        price=197.0,
    )
    product_v2 = Product(
        external_id="emagreca-de-vez-pro",
        title="Emagreça de Vez Pro",
        url="https://kiwify.com.br/produto/emagreca-de-vez-pro",
        platform_id=3,
        niche_id=1,
        rank=1,  # rank updated
        price=197.0,
    )

    upsert_product(db, product_v1)
    upsert_product(db, product_v2)

    rows = list(db["products"].rows_where(
        "platform_id = ? AND external_id = ?",
        [3, "emagreca-de-vez-pro"],
    ))

    assert len(rows) == 1, f"Expected 1 row after 2 upserts, got {len(rows)}"
    assert rows[0]["rank"] == 1, f"Expected rank=1 (latest), got {rows[0]['rank']}"
