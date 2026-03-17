"""Tests for MonetizzeScanner — fallback-only scanner (SCAN-BR-02).

6 tests (structure identical to EduzzScanner tests with MONETIZZE_PLATFORM_ID=5):
- test_happy_path: scan_niche() returns []
- test_field_types: return value is a list (no TypeError)
- test_fallback_selector: [] returned is actually [] (type check)
- test_drift_alert: logs alert='marketplace_unavailable' after scan_niche()
- test_upsert_no_duplicates: scan_niche() returns [] -> mark_stale() -> no new rows in DB
- test_is_stale: upsert -> mark_stale -> is_stale=True; upsert again -> is_stale=False
"""
import pytest
import structlog
import structlog.testing

from mis.scanners.monetizze import MonetizzeScanner
from mis.platform_ids import MONETIZZE_PLATFORM_ID


@pytest.mark.asyncio
async def test_happy_path():
    """scan_niche() must return empty list — no marketplace available."""
    async with MonetizzeScanner() as scanner:
        result = await scanner.scan_niche("emagrecimento", "saude", niche_id=1)
    assert result == []


@pytest.mark.asyncio
async def test_field_types():
    """Return value must be a list (no TypeError on iteration)."""
    async with MonetizzeScanner() as scanner:
        result = await scanner.scan_niche("marketing-digital", "marketing", niche_id=2)
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_fallback_selector():
    """[] returned is same singleton [] — trivial identity check."""
    async with MonetizzeScanner() as scanner:
        result = await scanner.scan_niche("financas", "financas", niche_id=3)
    assert result == [] and len(result) == 0


@pytest.mark.asyncio
async def test_drift_alert():
    """scan_niche() must emit log event with alert='marketplace_unavailable'."""
    with structlog.testing.capture_logs() as cap:
        async with MonetizzeScanner() as scanner:
            await scanner.scan_niche("emagrecimento", "saude", niche_id=1)

    alerts = [e for e in cap if e.get("alert") == "marketplace_unavailable"]
    assert len(alerts) >= 1, (
        f"Expected at least 1 event with alert='marketplace_unavailable', got: {cap}"
    )


@pytest.mark.asyncio
async def test_upsert_no_duplicates(tmp_path):
    """scan_niche() returns [] -> mark_stale() called -> no new rows inserted."""
    from mis.db import run_migrations, get_db
    from mis.product_repository import mark_stale

    db_path = str(tmp_path / "mis.db")
    run_migrations(db_path)
    db = get_db(db_path)

    db.execute(
        "INSERT OR IGNORE INTO platforms (id, name, slug, base_url, created_at) "
        "VALUES (5, 'Monetizze', 'monetizze', 'https://monetizze.com.br', '2026-01-01T00:00:00Z')"
    )
    db.execute(
        "INSERT OR IGNORE INTO niches (id, name, slug, created_at) "
        "VALUES (1, 'Saude', 'saude', '2026-01-01T00:00:00Z')"
    )

    count_before = list(db.execute(
        "SELECT COUNT(*) FROM products WHERE platform_id=?", [MONETIZZE_PLATFORM_ID]
    ))[0][0]

    async with MonetizzeScanner() as scanner:
        result = await scanner.scan_niche("saude", "saude", niche_id=1)

    # Result is [] — call mark_stale (as run_all_scanners would)
    if not result:
        mark_stale(db, MONETIZZE_PLATFORM_ID, 1)

    count_after = list(db.execute(
        "SELECT COUNT(*) FROM products WHERE platform_id=?", [MONETIZZE_PLATFORM_ID]
    ))[0][0]

    assert count_after == count_before, (
        f"Expected no new rows; before={count_before}, after={count_after}"
    )


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
        "VALUES (5, 'Monetizze', 'monetizze', 'https://monetizze.com.br', '2026-01-01T00:00:00Z')"
    )
    db.execute(
        "INSERT OR IGNORE INTO niches (id, name, slug, created_at) "
        "VALUES (1, 'Saude', 'saude', '2026-01-01T00:00:00Z')"
    )

    product = Product(
        external_id="monetizze-test-001",
        title="Produto Monetizze Teste",
        url="https://monetizze.com.br/produto-teste",
        platform_id=MONETIZZE_PLATFORM_ID,
        niche_id=1,
        rank=1,
        price=97.0,
    )
    upsert_product(db, product)
    row = list(db.execute(
        "SELECT is_stale FROM products WHERE platform_id=? AND external_id=?",
        [MONETIZZE_PLATFORM_ID, "monetizze-test-001"],
    ))[0]
    assert row[0] == 0, "is_stale deve ser 0 após upsert"

    mark_stale(db, MONETIZZE_PLATFORM_ID, 1)
    row = list(db.execute(
        "SELECT is_stale FROM products WHERE platform_id=? AND external_id=?",
        [MONETIZZE_PLATFORM_ID, "monetizze-test-001"],
    ))[0]
    assert row[0] == 1, "is_stale deve ser 1 após mark_stale()"

    upsert_product(db, product)
    row = list(db.execute(
        "SELECT is_stale FROM products WHERE platform_id=? AND external_id=?",
        [MONETIZZE_PLATFORM_ID, "monetizze-test-001"],
    ))[0]
    assert row[0] == 0, "is_stale deve ser resetado para 0 após upsert"
