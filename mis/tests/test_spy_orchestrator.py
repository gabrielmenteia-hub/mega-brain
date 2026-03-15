"""Tests for mis.spy_orchestrator — TDD RED phase.

Tests: run_spy, run_spy_url, run_spy_batch, and scheduler wiring.
All external I/O (scrapers, LLM) is mocked.
"""
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mis.db import run_migrations, get_db
from mis.spies.completeness_gate import SpyData

# ─── Shared fixtures ───────────────────────────────────────────────────────────

COPY_TEXT = (
    "Descubra o método definitivo para ganhar renda extra online. "
    "Mais de 50.000 alunos já transformaram suas finanças. "
    "Sem precisar largar seu emprego. Comece hoje mesmo. "
    "Garantia de 30 dias ou dinheiro de volta. Acesse agora."
)


def _make_spy_mocks():
    """Return mocks for all three spies with realistic responses."""
    sales_mock = AsyncMock()
    sales_mock.__aenter__ = AsyncMock(return_value=sales_mock)
    sales_mock.__aexit__ = AsyncMock(return_value=False)
    sales_mock.extract = AsyncMock(return_value={
        "headlines": ["Transforme suas finanças"],
        "sub_headlines": ["Método comprovado"],
        "arguments": ["50.000 alunos"],
        "ctas": ["Compre agora"],
        "narrative_structure": COPY_TEXT,
        "price": 497.0,
        "bonuses": ["Bônus 1"],
        "guarantees": ["30 dias"],
        "upsells": [],
        "downsells": [],
    })

    meta_mock = MagicMock()
    meta_mock.fetch_ads = AsyncMock(return_value=[
        {"creative_id": "ad_001", "headline": "De zero a 10k por mês"}
    ])

    reviews_mock = AsyncMock()
    reviews_mock.__aenter__ = AsyncMock(return_value=reviews_mock)
    reviews_mock.__aexit__ = AsyncMock(return_value=False)
    reviews_mock.collect = AsyncMock(return_value=[
        {"rating": 5, "text": f"Review {i}"} for i in range(12)
    ])

    return sales_mock, meta_mock, reviews_mock


def _make_llm_mocks():
    """Return mocks for copy_analyzer and dossier_generator."""
    copy_analysis = {
        "framework_type": "PAS",
        "emotional_triggers": ["medo", "desejo"],
        "narrative_structure": "Problema → Solução",
        "social_proof_elements": ["50.000 alunos"],
    }
    dossier_data = {
        "why_it_sells": ["Endereça dor financeira"],
        "pains_addressed": [{"pain": "Renda baixa", "source": "copy"}],
        "modeling_template": {
            "sections": ["Hook", "CTA"],
            "key_arguments": ["Garantia"],
            "offer_structure": {"price_anchor": "alto"},
        },
        "opportunity_score": {"score": 78, "justification": "Mercado aquecido"},
    }
    return copy_analysis, dossier_data


@pytest.fixture
def migrated_db(tmp_path):
    """DB with all migrations applied and a seeded product."""
    db_path = str(tmp_path / "mis.db")
    run_migrations(db_path)
    db = get_db(db_path)

    now = datetime.utcnow().isoformat()
    db["platforms"].insert(
        {"id": 1, "name": "Hotmart", "slug": "hotmart",
         "base_url": "https://hotmart.com", "created_at": now},
        ignore=True,
    )
    db["niches"].insert(
        {"id": 1, "name": "Marketing Digital", "slug": "marketing-digital", "created_at": now},
        ignore=True,
    )
    db["products"].insert(
        {"id": 1, "platform_id": 1, "niche_id": 1, "external_id": "test-product",
         "title": "Produto Teste", "url": "https://hotmart.com/produto/test",
         "rank_score": 0.0, "price": 297.0, "currency": "BRL",
         "scraped_at": now, "raw_data": "{}"},
        ignore=True,
    )
    return db_path


# ─── Tests ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_run_spy_happy_path(migrated_db, monkeypatch):
    """run_spy(product_id) executa pipeline completo e persiste dossier com status='done'."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("MIS_DB_PATH", migrated_db)

    sales_mock, meta_mock, reviews_mock = _make_spy_mocks()
    copy_analysis, dossier_data = _make_llm_mocks()

    with (
        patch("mis.spy_orchestrator.SalesPageScraper", return_value=sales_mock),
        patch("mis.spy_orchestrator.MetaAdsScraper", return_value=meta_mock),
        patch("mis.spy_orchestrator.ReviewsScraper", return_value=reviews_mock),
        patch("mis.spy_orchestrator.analyze_copy", AsyncMock(return_value=copy_analysis)),
        patch("mis.spy_orchestrator.generate_dossier", AsyncMock(return_value=dossier_data)),
    ):
        from mis.spy_orchestrator import run_spy
        await run_spy(1)

    db = get_db(migrated_db)
    dossiers = list(db["dossiers"].rows_where("product_id = ?", [1]))
    assert len(dossiers) == 1
    d = dossiers[0]
    assert d["status"] == "done"
    assert d["dossier_json"] is not None
    parsed = json.loads(d["dossier_json"])
    assert "why_it_sells" in parsed
    assert d["confidence_score"] > 0


@pytest.mark.asyncio
async def test_run_spy_url_creates_product(tmp_path, monkeypatch):
    """run_spy_url() cria entrada na tabela dossiers e persiste dossier_json."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    db_path = str(tmp_path / "mis.db")
    run_migrations(db_path)
    monkeypatch.setenv("MIS_DB_PATH", db_path)

    sales_mock, meta_mock, reviews_mock = _make_spy_mocks()
    copy_analysis, dossier_data = _make_llm_mocks()

    with (
        patch("mis.spy_orchestrator.SalesPageScraper", return_value=sales_mock),
        patch("mis.spy_orchestrator.MetaAdsScraper", return_value=meta_mock),
        patch("mis.spy_orchestrator.ReviewsScraper", return_value=reviews_mock),
        patch("mis.spy_orchestrator.analyze_copy", AsyncMock(return_value=copy_analysis)),
        patch("mis.spy_orchestrator.generate_dossier", AsyncMock(return_value=dossier_data)),
    ):
        from mis.spy_orchestrator import run_spy_url
        await run_spy_url("https://hotmart.com/produto/xyz")

    db = get_db(db_path)
    dossiers = list(db["dossiers"].rows)
    assert len(dossiers) == 1
    assert dossiers[0]["status"] == "done"
    assert dossiers[0]["dossier_json"] is not None


@pytest.mark.asyncio
async def test_spy_failed_on_copy_error(migrated_db, monkeypatch):
    """Quando SalesPageScraper falha, status=failed e structlog tem alert='spy_failed'."""
    import structlog.testing

    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("MIS_DB_PATH", migrated_db)

    sales_mock = AsyncMock()
    sales_mock.__aenter__ = AsyncMock(return_value=sales_mock)
    sales_mock.__aexit__ = AsyncMock(return_value=False)
    sales_mock.extract = AsyncMock(side_effect=ValueError("fetch failed"))

    meta_mock = MagicMock()
    meta_mock.fetch_ads = AsyncMock(return_value=[])

    reviews_mock = AsyncMock()
    reviews_mock.__aenter__ = AsyncMock(return_value=reviews_mock)
    reviews_mock.__aexit__ = AsyncMock(return_value=False)
    reviews_mock.collect = AsyncMock(return_value=[])

    log_entries = []

    with (
        patch("mis.spy_orchestrator.SalesPageScraper", return_value=sales_mock),
        patch("mis.spy_orchestrator.MetaAdsScraper", return_value=meta_mock),
        patch("mis.spy_orchestrator.ReviewsScraper", return_value=reviews_mock),
        structlog.testing.capture_logs() as captured,
    ):
        from mis.spy_orchestrator import run_spy
        await run_spy(1)

    db = get_db(migrated_db)
    dossiers = list(db["dossiers"].rows_where("product_id = ?", [1]))
    assert len(dossiers) == 1
    assert dossiers[0]["status"] == "failed"

    # Verificar que alert='spy_failed' foi emitido
    spy_failed_logs = [e for e in captured if e.get("alert") == "spy_failed"]
    assert len(spy_failed_logs) > 0, f"Expected alert='spy_failed' in logs, got: {captured}"


@pytest.mark.asyncio
async def test_no_existing_dossier_required(migrated_db, monkeypatch):
    """Produto sem dossier existente é espionado normalmente (modo automático)."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("MIS_DB_PATH", migrated_db)

    sales_mock, meta_mock, reviews_mock = _make_spy_mocks()
    copy_analysis, dossier_data = _make_llm_mocks()

    with (
        patch("mis.spy_orchestrator.SalesPageScraper", return_value=sales_mock),
        patch("mis.spy_orchestrator.MetaAdsScraper", return_value=meta_mock),
        patch("mis.spy_orchestrator.ReviewsScraper", return_value=reviews_mock),
        patch("mis.spy_orchestrator.analyze_copy", AsyncMock(return_value=copy_analysis)),
        patch("mis.spy_orchestrator.generate_dossier", AsyncMock(return_value=dossier_data)),
    ):
        # Confirma que não há dossier antes
        db = get_db(migrated_db)
        assert list(db["dossiers"].rows) == []

        from mis.spy_orchestrator import run_spy
        await run_spy(1)

    db = get_db(migrated_db)
    dossiers = list(db["dossiers"].rows)
    assert len(dossiers) == 1
    assert dossiers[0]["status"] == "done"


@pytest.mark.asyncio
async def test_manual_forces_respy(migrated_db, monkeypatch):
    """Produto com dossier status='done' é re-espionado quando force=True."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("MIS_DB_PATH", migrated_db)

    # Pré-inserir dossier done
    db = get_db(migrated_db)
    now = datetime.utcnow().isoformat()
    db["dossiers"].insert({
        "product_id": 1,
        "status": "done",
        "dossier_json": json.dumps({"old": True}),
        "analysis": "{}",
        "opportunity_score": 0.5,
        "confidence_score": 70,
        "generated_at": now,
    })

    sales_mock, meta_mock, reviews_mock = _make_spy_mocks()
    copy_analysis, dossier_data = _make_llm_mocks()

    with (
        patch("mis.spy_orchestrator.SalesPageScraper", return_value=sales_mock),
        patch("mis.spy_orchestrator.MetaAdsScraper", return_value=meta_mock),
        patch("mis.spy_orchestrator.ReviewsScraper", return_value=reviews_mock),
        patch("mis.spy_orchestrator.analyze_copy", AsyncMock(return_value=copy_analysis)),
        patch("mis.spy_orchestrator.generate_dossier", AsyncMock(return_value=dossier_data)),
    ):
        from mis.spy_orchestrator import run_spy
        await run_spy(1, force=True)

    db = get_db(migrated_db)
    dossiers = list(db["dossiers"].rows_where("product_id = ?", [1]))
    # Deve ter re-espionado — dossier_json não é mais o antigo
    assert dossiers[0]["status"] == "done"
    parsed = json.loads(dossiers[0]["dossier_json"])
    assert "old" not in parsed


@pytest.mark.asyncio
async def test_semaphore_limits_concurrency(migrated_db, monkeypatch):
    """run_spy_batch() respeita max_concurrent_spy — semáforo limita execuções paralelas."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("MIS_DB_PATH", migrated_db)

    # Inserir produtos adicionais para o batch
    db = get_db(migrated_db)
    now = datetime.utcnow().isoformat()
    for i in range(2, 6):
        db["products"].insert({
            "id": i, "platform_id": 1, "niche_id": 1,
            "external_id": f"product-{i}", "title": f"Produto {i}",
            "url": f"https://hotmart.com/produto/test-{i}",
            "rank_score": 0.0, "price": 297.0, "currency": "BRL",
            "scraped_at": now, "raw_data": "{}",
        }, ignore=True)

    max_concurrent = 2
    active_count = 0
    max_active = 0
    call_count = 0
    import asyncio as _asyncio

    async def mock_run_spy(product_id, force=False):
        nonlocal active_count, max_active, call_count
        active_count += 1
        max_active = max(max_active, active_count)
        call_count += 1
        await _asyncio.sleep(0.01)
        active_count -= 1

    products = [{"id": i, "rank": i} for i in range(1, 6)]

    with patch("mis.spy_orchestrator.run_spy", mock_run_spy):
        from mis.spy_orchestrator import run_spy_batch
        await run_spy_batch(products, max_concurrent=max_concurrent)

    assert call_count == 5
    assert max_active <= max_concurrent, (
        f"Semaphore violated: max_active={max_active}, max_concurrent={max_concurrent}"
    )


@pytest.mark.asyncio
async def test_scheduler_triggers_spy_batch(monkeypatch):
    """Verifica que _scan_and_spy_job encadeia run_spy_batch após run_all_scanners."""
    spy_batch_calls = []

    product_mock = MagicMock()
    product_mock.external_id = "prod-1"
    product_mock.rank = 1

    scanner_result = {"hotmart.marketing-digital": [product_mock]}

    monkeypatch.setenv("MIS_DB_PATH", ":memory:")

    async def mock_run_all_scanners(config):
        return scanner_result

    async def mock_run_spy_batch(products, **kw):
        spy_batch_calls.extend(products)

    with (
        patch("mis.scheduler.run_all_scanners", mock_run_all_scanners),
        patch("mis.scheduler.run_spy_batch", mock_run_spy_batch),
    ):
        from mis.scheduler import _scan_and_spy_job
        await _scan_and_spy_job()

    assert len(spy_batch_calls) > 0, (
        "run_spy_batch deve ser chamado com produtos após run_all_scanners"
    )
