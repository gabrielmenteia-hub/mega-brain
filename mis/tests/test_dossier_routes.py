"""RED tests for Phase 22 dossier route extensions (SPY-V3-03).

These tests define the observable contract for:
  - GET /dossier/{id}?from_search=42 inclui back_url e back_label no contexto
  - GET /dossier/{id}/tab/oferta retorna 200 e renderiza dossier_tab_oferta.html

All tests FAIL because:
  - dossier.py does not read ?from_search query param
  - 'oferta' is not in _VALID_TABS and dossier_tab_oferta.html does not exist
"""
import json
import sqlite3
from datetime import datetime

import pytest

from mis.db import get_db, run_migrations


# ---------------------------------------------------------------------------
# Shared fixture: app_client with a seeded product + dossier
# ---------------------------------------------------------------------------


@pytest.fixture
def dossier_client(tmp_path):
    """TestClient backed by a fresh DB with a product and a dossier."""
    db_path = str(tmp_path / "mis.db")
    run_migrations(db_path)

    # Seed the DB
    db = get_db(db_path)
    now = datetime.utcnow().isoformat()

    db.execute(
        "INSERT OR IGNORE INTO platforms (id, name, slug, base_url, created_at) "
        "VALUES (1, 'Hotmart', 'hotmart', 'https://hotmart.com', ?)", [now]
    )
    db.execute(
        "INSERT OR IGNORE INTO niches (id, name, slug, created_at) "
        "VALUES (1, 'Marketing Digital', 'marketing-digital', ?)", [now]
    )
    db.execute(
        "INSERT OR IGNORE INTO products "
        "(id, platform_id, niche_id, external_id, title, url, "
        "rank, rank_score, price, currency, scraped_at, raw_data) "
        "VALUES (1, 1, 1, 'prod-001', 'Produto Teste', "
        "'https://hotmart.com/produto/1', 1, 0.0, 197.0, 'BRL', ?, '{}')",
        [now],
    )

    dossier_json = json.dumps({
        "why_it_sells": ["Endereça dor financeira"],
        "pains_addressed": [{"pain": "Renda baixa", "source": "copy"}],
        "modeling_template": {
            "sections": ["Hook", "CTA"],
            "key_arguments": ["Garantia"],
            "offer_structure": {"price_anchor": "alto"},
        },
        "opportunity_score": {"score": 78, "justification": "Mercado aquecido"},
        "offer_data": {
            "price": 197.0,
            "bonuses": ["Bônus 1", "Bônus 2"],
            "guarantee": "30 dias",
            "upsells": ["Upsell Premium"],
            "downsells": [],
        },
    })

    db.execute(
        "INSERT INTO dossiers "
        "(product_id, status, dossier_json, analysis, "
        "opportunity_score, confidence_score, generated_at) "
        "VALUES (1, 'done', ?, '{}', 0.8, 80, ?)",
        [dossier_json, now],
    )

    # Also create a search session for from_search tests
    # niches_v3 is seeded by migration _008 — just pick any existing row
    subniche_row = db.execute(
        "SELECT id FROM subniches LIMIT 1"
    ).fetchone()
    if subniche_row:
        subniche_id = subniche_row[0]
    else:
        # Fallback: insert minimal subniche (niches_v3 already seeded by migration)
        db.execute(
            "INSERT INTO subniches (niche_id, name, slug) "
            "VALUES (1, 'Trafego Pago', 'trafego-pago')"
        )
        subniche_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    db.execute(
        "INSERT INTO search_sessions (id, subniche_id, status, started_at) "
        "VALUES (42, ?, 'done', ?)",
        [subniche_id, now],
    )

    from mis.web.app import create_app
    from fastapi.testclient import TestClient

    app = create_app(db_path=db_path, start_scheduler=False)
    with TestClient(app) as client:
        yield client


# ---------------------------------------------------------------------------
# SPY-V3-03: ?from_search param on dossier detail route
# ---------------------------------------------------------------------------


def test_from_search_param(dossier_client):
    """GET /dossier/1?from_search=42 deve incluir back_url e back_label
    no contexto do template.

    back_url deve ser '/search/42/results'
    back_label deve ser '← Voltar aos resultados'

    FAILS: dossier.py route handler ignores ?from_search query param.
    The template context never receives back_url or back_label.
    """
    resp = dossier_client.get("/dossier/1", params={"from_search": "42"})

    assert resp.status_code == 200, (
        f"GET /dossier/1?from_search=42 deve retornar 200, got {resp.status_code}"
    )

    body = resp.text

    # The rendered HTML must contain the back link to search results
    assert "/search/42/results" in body, (
        "Dossier com ?from_search=42 deve conter link '/search/42/results' no HTML"
    )
    assert "Voltar aos resultados" in body, (
        "Dossier com ?from_search=42 deve exibir 'Voltar aos resultados' no HTML"
    )


# ---------------------------------------------------------------------------
# SPY-V3-03: oferta tab
# ---------------------------------------------------------------------------


def test_oferta_tab_renders(dossier_client):
    """GET /dossier/1/tab/oferta deve retornar 200 e renderizar
    dossier_tab_oferta.html.

    FAILS: 'oferta' is not in _VALID_TABS (dossier.py line 13), so the
    route returns HTTP 400. The template dossier_tab_oferta.html does not
    exist yet.
    """
    resp = dossier_client.get("/dossier/1/tab/oferta")

    assert resp.status_code == 200, (
        f"GET /dossier/1/tab/oferta deve retornar 200, "
        f"got {resp.status_code}. "
        f"'oferta' must be added to _VALID_TABS and dossier_tab_oferta.html must exist."
    )
