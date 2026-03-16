"""Tests for DEFECT-1: run_all_scanners() must resolve niche_id via DB.

RED phase: these tests FAIL before the fix in scanner.py.

DEFECT-1: Products saved by run_all_scanners() all have niche_id=0 because
the function never looks up niche IDs from the niches table. This makes the
dashboard niche filter completely inoperative.
"""
import asyncio
import os
import sqlite3
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


def _run_migrations_for_test(db_path: str) -> None:
    """Apply full DB schema (all migrations) to a fresh test DB."""
    from mis.db import run_migrations
    run_migrations(db_path)


def _insert_niche(db_path: str, slug: str, name: str) -> int:
    """Insert a niche row and return its auto-assigned ID."""
    conn = sqlite3.connect(db_path)
    cur = conn.execute(
        "INSERT INTO niches (slug, name, created_at) VALUES (?, ?, ?)",
        (slug, name, "2026-01-01T00:00:00Z"),
    )
    niche_id = cur.lastrowid
    conn.commit()
    conn.close()
    return niche_id


def _get_products_from_db(db_path: str) -> list[dict]:
    """Fetch all rows from products table as dicts."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@pytest.mark.asyncio
async def test_niche_id_resolved_correctly(tmp_path, monkeypatch):
    """Products saved by run_all_scanners() must have niche_id matching the DB niches row.

    DEFECT-1: Before fix, niche_id is always 0 because run_all_scanners()
    never looks up the niche ID from the niches table.

    After fix: niche_id matches the ID of the 'emagrecimento' row in niches table.
    """
    from mis.scanner import run_all_scanners, Product
    from mis.db import get_db

    db_path = str(tmp_path / "mis.db")
    _run_migrations_for_test(db_path)

    # Insert the niche into the DB and capture its real auto-assigned ID
    expected_niche_id = _insert_niche(db_path, "emagrecimento", "Emagrecimento")
    assert expected_niche_id > 0, "Niche insert must return a positive ID"

    # Also insert a platform row so product save doesn't fail FK constraint
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT OR IGNORE INTO platforms (id, name, slug, base_url, created_at) VALUES (?, ?, ?, ?, ?)",
        (3, "Kiwify", "kiwify", "https://kiwify.com.br", "2026-01-01T00:00:00Z"),
    )
    conn.commit()
    conn.close()

    # Set the env var so run_all_scanners can find the DB
    monkeypatch.setenv("MIS_DB_PATH", db_path)

    # The product returned by the scanner has niche_id=0 (simulating current behavior)
    fake_product = Product(
        external_id="EMAG_PROD_001",
        title="Produto Emagrecimento",
        url="https://kiwify.com.br/produto/emag",
        platform_id=3,
        niche_id=0,   # Scanner returns 0 — run_all_scanners must fix this
        rank=1,
    )

    config = {
        "niches": [
            {
                "slug": "emagrecimento",
                "name": "Emagrecimento",
                "platforms": {"kiwify": "emagrecimento"},
            }
        ],
        "settings": {},
    }

    # Patch KiwifyScanner to return our fake product without doing real HTTP
    mock_scanner_instance = AsyncMock()
    mock_scanner_instance.scan_niche = AsyncMock(return_value=[fake_product])
    mock_scanner_instance.__aenter__ = AsyncMock(return_value=mock_scanner_instance)
    mock_scanner_instance.__aexit__ = AsyncMock(return_value=None)

    with patch("mis.scanners.kiwify.KiwifyScanner", return_value=mock_scanner_instance):
        result = await run_all_scanners(config)

    # run_all_scanners should return products with the resolved niche_id
    assert "emagrecimento.kiwify" in result, f"Key not found, got: {list(result.keys())}"
    products = result["emagrecimento.kiwify"]
    assert len(products) == 1, f"Expected 1 product, got {len(products)}"

    # CRITICAL: niche_id must be resolved to the real DB ID, NOT 0
    assert products[0].niche_id == expected_niche_id, (
        f"niche_id should be {expected_niche_id} (from DB), got {products[0].niche_id}"
    )


@pytest.mark.asyncio
async def test_unknown_slug_skipped(tmp_path, monkeypatch, caplog):
    """run_all_scanners() with a slug not in niches table must skip it without raising.

    When a niche slug from config has no matching row in the niches table,
    run_all_scanners() should:
    1. NOT raise any exception
    2. Emit a warning log with key 'scanner.niche.slug_not_in_db'
    3. Return an empty output (the niche is simply skipped)
    """
    from mis.scanner import run_all_scanners

    db_path = str(tmp_path / "mis.db")
    _run_migrations_for_test(db_path)
    # Intentionally NOT inserting 'niche-inexistente' into the DB

    monkeypatch.setenv("MIS_DB_PATH", db_path)

    config = {
        "niches": [
            {
                "slug": "niche-inexistente",
                "name": "Niche Nao Existe",
                "platforms": {"kiwify": "inexistente"},
            }
        ],
        "settings": {},
    }

    # Should not raise — unknown slug is skipped gracefully
    import structlog
    from structlog.testing import capture_logs

    with capture_logs() as cap:
        result = await run_all_scanners(config)

    # No exception raised — result is empty dict or empty list for the skipped niche
    assert isinstance(result, dict), "result must be a dict"

    # Warning must have been logged for the missing slug
    warning_keys = [e.get("log_level") for e in cap]
    event_keys = [e.get("event") for e in cap]
    assert any(
        "slug_not_in_db" in str(e.get("event", "")) or
        "slug_not_in_db" in str(e.get("niche_slug", ""))
        for e in cap
    ), (
        f"Expected a log warning with 'slug_not_in_db'. Got events: {event_keys}"
    )
