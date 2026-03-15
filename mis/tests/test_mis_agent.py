"""Tests for mis/mis_agent.py — MIS/MEGABRAIN bridge.

Three test scenarios:
    test_empty_db        — get_briefing_data() with an empty DB returns correct structure
    test_with_data       — get_briefing_data() with populated DB returns top-10 products
    test_incremental_export — export_to_megabrain() is idempotent (second call exports 0 new files)
"""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _seed_db(db_path: str, n_products: int = 12) -> None:
    """Seed a migrated DB with platforms, niches, products, and dossiers."""
    with sqlite3.connect(db_path) as conn:
        # Platforms
        conn.execute(
            "INSERT OR IGNORE INTO platforms (id, name, slug) VALUES (1, 'Hotmart', 'hotmart')"
        )
        # Niches
        conn.execute(
            "INSERT OR IGNORE INTO niches (id, name, slug) VALUES (1, 'Marketing Digital', 'marketing-digital')"
        )
        conn.execute(
            "INSERT OR IGNORE INTO niches (id, name, slug) VALUES (2, 'Emagrecimento', 'emagrecimento')"
        )
        conn.execute(
            "INSERT OR IGNORE INTO niches (id, name, slug) VALUES (3, 'Financas Pessoais', 'financas-pessoais')"
        )

        now_iso = datetime.now(timezone.utc).isoformat()
        for i in range(1, n_products + 1):
            conn.execute(
                "INSERT OR IGNORE INTO products (id, external_id, title, url, platform_id, niche_id, rank) "
                "VALUES (?, ?, ?, ?, 1, 1, ?)",
                [i, f"prod_{i:04d}", f"Product {i}", f"https://example.com/{i}", i],
            )
            # Some products get dossiers with an opportunity_score
            if i <= 5:
                conn.execute(
                    "INSERT OR IGNORE INTO dossiers "
                    "(product_id, status, opportunity_score, confidence_score, dossier_json, generated_at) "
                    "VALUES (?, 'done', ?, 0.9, ?, ?)",
                    [
                        i,
                        round(1.0 - i * 0.05, 2),  # scores: 0.95, 0.90, 0.85, 0.80, 0.75
                        json.dumps(
                            {
                                "why_sells": f"Why {i}",
                                "copy": f"Copy {i}",
                                "ads": [],
                                "reviews": [],
                                "template": f"Template {i}",
                            }
                        ),
                        now_iso,
                    ],
                )

        # One pain_report for niche 1
        conn.execute(
            "INSERT OR IGNORE INTO pain_reports (niche_id, cycle_at, report_json, created_at) VALUES (1, ?, ?, ?)",
            [
                now_iso,
                json.dumps(
                    {
                        "pains": [
                            {"title": f"Pain {j}", "interest_level": 10 - j}
                            for j in range(8)
                        ]
                    }
                ),
                now_iso,
            ],
        )
        conn.commit()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_empty_db(tmp_path, monkeypatch):
    """get_briefing_data() with an empty (but migrated) DB returns correct structure."""
    db_file = str(tmp_path / "mis.db")
    monkeypatch.setenv("MIS_DB_PATH", db_file)

    # Run migrations first so the schema exists
    from mis.db import run_migrations

    run_migrations(db_file)

    # Import AFTER setting env so _init_db() picks up the right path
    import importlib
    import mis.mis_agent as agent_mod

    importlib.reload(agent_mod)

    result = agent_mod.get_briefing_data()

    assert result["status"] == "ok"
    assert result["products"] == []
    assert isinstance(result["pains_by_niche"], dict)
    assert result["unseen_alerts"] == 0
    assert isinstance(result["health"], dict)
    assert result["last_cycle"] is None
    assert "db_path" in result


def test_with_data(tmp_path, monkeypatch):
    """get_briefing_data() with populated DB returns top-10 products and pains."""
    db_file = str(tmp_path / "mis.db")
    monkeypatch.setenv("MIS_DB_PATH", db_file)

    from mis.db import run_migrations

    run_migrations(db_file)
    _seed_db(db_file, n_products=12)

    import importlib
    import mis.mis_agent as agent_mod

    importlib.reload(agent_mod)

    result = agent_mod.get_briefing_data()

    assert result["status"] == "ok"
    # top-10 products
    assert len(result["products"]) <= 10
    # pains_by_niche is a dict (may be empty if config niches not in DB)
    assert isinstance(result["pains_by_niche"], dict)
    assert result["unseen_alerts"] >= 0
    assert isinstance(result["health"], dict)


def test_incremental_export(tmp_path, monkeypatch):
    """export_to_megabrain() is idempotent — second call with same data exports 0 new files."""
    db_file = str(tmp_path / "mis.db")
    monkeypatch.setenv("MIS_DB_PATH", db_file)

    from mis.db import run_migrations

    run_migrations(db_file)
    _seed_db(db_file, n_products=5)

    import importlib
    import mis.mis_agent as agent_mod

    importlib.reload(agent_mod)

    dest = str(tmp_path / "export")

    # First export — should export N > 0 files
    result1 = agent_mod.export_to_megabrain(dest=dest)
    assert result1["status"] == "ok"
    assert result1["exported"] > 0  # must export at least 1 dossier with status='done'
    first_count = result1["exported"] + result1["skipped"]

    # Second identical export — all files already exist with same content
    result2 = agent_mod.export_to_megabrain(dest=dest)
    assert result2["status"] == "ok"
    # skipped should equal total files (no new exports)
    assert result2["exported"] == 0
    assert result2["skipped"] == first_count


def test_health_with_dossier_today(tmp_path, monkeypatch):
    """get_briefing_data() returns last_cycle non-null and dossiers_today=True when a dossier was generated today."""
    import json
    import sqlite3
    from datetime import datetime, timezone
    from unittest.mock import AsyncMock, patch

    db_file = str(tmp_path / "mis.db")
    monkeypatch.setenv("MIS_DB_PATH", db_file)

    from mis.db import run_migrations

    run_migrations(db_file)

    today_iso = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(db_file) as conn:
        # Insert platform, niche, product
        conn.execute(
            "INSERT OR IGNORE INTO platforms (id, name, slug) VALUES (1, 'Hotmart', 'hotmart')"
        )
        conn.execute(
            "INSERT OR IGNORE INTO niches (id, name, slug) VALUES (1, 'Marketing', 'marketing')"
        )
        conn.execute(
            "INSERT OR IGNORE INTO products (id, external_id, title, url, platform_id, niche_id, rank) "
            "VALUES (1, 'prod_today', 'Product Today', 'https://example.com/1', 1, 1, 1)"
        )
        # Insert dossier with generated_at = today
        conn.execute(
            "INSERT OR IGNORE INTO dossiers "
            "(product_id, status, opportunity_score, confidence_score, dossier_json, generated_at) "
            "VALUES (?, 'done', 0.95, 0.9, ?, ?)",
            [
                1,
                json.dumps({"why_sells": "Test", "copy": "Copy", "ads": [], "reviews": [], "template": "T"}),
                today_iso,
            ],
        )
        conn.commit()

    import importlib
    import mis.mis_agent as agent_mod

    importlib.reload(agent_mod)

    # Mock run_canary_check to avoid network calls and timeout in tests
    with patch("mis.health_monitor.run_canary_check", new=AsyncMock(return_value=False)):
        result = agent_mod.get_briefing_data()

    assert result["status"] == "ok"
    assert result["last_cycle"] is not None, "last_cycle must be non-null when dossier exists"
    assert result["health"]["dossiers_today"] is True, "dossiers_today must be True when a dossier was generated today"
