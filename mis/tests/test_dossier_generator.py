"""Tests for mis.intelligence.dossier_generator — TDD RED phase."""
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mis.db import run_migrations, get_db
from mis.spies.completeness_gate import SpyData

# Fixture path
FIXTURE_DIR = Path(__file__).parent / "fixtures" / "llm_responses"


def _load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def _make_mock_response(text: str, input_tokens: int = 1500, output_tokens: int = 800):
    """Build a mock Anthropic message response object with usage data."""
    content_block = MagicMock()
    content_block.text = text

    usage = MagicMock()
    usage.input_tokens = input_tokens
    usage.output_tokens = output_tokens

    response = MagicMock()
    response.content = [content_block]
    response.usage = usage
    return response


@pytest.fixture
def spy_data():
    """SpyData with full set of espionage data."""
    return SpyData(
        copy_text="Descubra o método definitivo para ganhar renda extra online. "
        "Mais de 50.000 alunos já transformaram suas finanças. "
        "Sem precisar largar seu emprego. Comece hoje mesmo.",
        offer_data={"price": 497.0, "installments": 12, "bonus_count": 7},
        reviews=[
            {"rating": 5, "text": "Triplicou minha renda em 3 meses"},
            {"rating": 4, "text": "Método funciona mesmo sendo iniciante"},
        ],
        ads=[
            {"creative_id": "ad_001", "headline": "De zero a 10k por mês"},
        ],
    )


@pytest.fixture
def copy_analysis():
    """Output típico do copy_analyzer passado para o dossier_generator."""
    return {
        "framework_type": "PAS",
        "emotional_triggers": ["medo de perder oportunidade", "desejo de liberdade financeira"],
        "narrative_structure": "Problema → Agitação → Solução → CTA urgente",
        "social_proof_elements": ["50.000 alunos", "resultados em números"],
    }


@pytest.fixture
def migrated_db(db_path):
    """DB with all migrations applied and seed data for FK constraints."""
    from datetime import datetime

    run_migrations(db_path)
    db = get_db(db_path)

    # Seed: platform → niche → product → dossier (needed for llm_calls FK)
    now = datetime.utcnow().isoformat()
    db["platforms"].insert(
        {"id": 1, "name": "Hotmart", "slug": "hotmart", "base_url": "https://hotmart.com", "created_at": now},
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
    db["dossiers"].insert(
        {"id": 1, "product_id": 1, "analysis": "{}", "opportunity_score": 0.0,
         "confidence_score": 0.0, "generated_at": now},
        ignore=True,
    )
    db["dossiers"].insert(
        {"id": 42, "product_id": 1, "analysis": "{}", "opportunity_score": 0.0,
         "confidence_score": 0.0, "generated_at": now},
        ignore=True,
    )
    return db_path


@pytest.mark.asyncio
async def test_pains_addressed(spy_data, copy_analysis, migrated_db, monkeypatch):
    """generate_dossier() returns dict with pains_addressed as list of dicts with pain and source."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    fixture_json = _load_fixture("dossier_generator_output.json")
    mock_response = _make_mock_response(fixture_json)

    with patch("mis.intelligence.dossier_generator.AsyncAnthropic") as mock_cls:
        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        mock_cls.return_value = mock_client

        from mis.intelligence.dossier_generator import generate_dossier

        result = await generate_dossier(
            data=spy_data,
            copy_analysis=copy_analysis,
            dossier_id=1,
            db_path=migrated_db,
        )

    assert "pains_addressed" in result
    assert isinstance(result["pains_addressed"], list)
    assert len(result["pains_addressed"]) > 0

    first_pain = result["pains_addressed"][0]
    assert "pain" in first_pain
    assert "source" in first_pain
    assert first_pain["source"] in ("copy", "review", "ad")


@pytest.mark.asyncio
async def test_modeling_template(spy_data, copy_analysis, migrated_db, monkeypatch):
    """Result contains modeling_template with sections, key_arguments, offer_structure (DOS-03)."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    fixture_json = _load_fixture("dossier_generator_output.json")
    mock_response = _make_mock_response(fixture_json)

    with patch("mis.intelligence.dossier_generator.AsyncAnthropic") as mock_cls:
        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        mock_cls.return_value = mock_client

        from mis.intelligence.dossier_generator import generate_dossier

        result = await generate_dossier(
            data=spy_data,
            copy_analysis=copy_analysis,
            dossier_id=1,
            db_path=migrated_db,
        )

    assert "modeling_template" in result
    template = result["modeling_template"]
    assert "sections" in template
    assert "key_arguments" in template
    assert "offer_structure" in template
    assert isinstance(template["sections"], list)
    assert len(template["sections"]) > 0


@pytest.mark.asyncio
async def test_opportunity_score(spy_data, copy_analysis, migrated_db, monkeypatch):
    """Result contains opportunity_score with score (int 0-100) and justification (str) (DOS-04)."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    fixture_json = _load_fixture("dossier_generator_output.json")
    mock_response = _make_mock_response(fixture_json)

    with patch("mis.intelligence.dossier_generator.AsyncAnthropic") as mock_cls:
        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        mock_cls.return_value = mock_client

        from mis.intelligence.dossier_generator import generate_dossier

        result = await generate_dossier(
            data=spy_data,
            copy_analysis=copy_analysis,
            dossier_id=1,
            db_path=migrated_db,
        )

    assert "opportunity_score" in result
    opp = result["opportunity_score"]
    assert "score" in opp
    assert "justification" in opp
    assert isinstance(opp["score"], int)
    assert 0 <= opp["score"] <= 100
    assert isinstance(opp["justification"], str)
    assert len(opp["justification"]) > 0


@pytest.mark.asyncio
async def test_why_it_sells(spy_data, copy_analysis, migrated_db, monkeypatch):
    """Result contains why_it_sells as non-empty list (DOS-01)."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    fixture_json = _load_fixture("dossier_generator_output.json")
    mock_response = _make_mock_response(fixture_json)

    with patch("mis.intelligence.dossier_generator.AsyncAnthropic") as mock_cls:
        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        mock_cls.return_value = mock_client

        from mis.intelligence.dossier_generator import generate_dossier

        result = await generate_dossier(
            data=spy_data,
            copy_analysis=copy_analysis,
            dossier_id=1,
            db_path=migrated_db,
        )

    assert "why_it_sells" in result
    assert isinstance(result["why_it_sells"], list)
    assert len(result["why_it_sells"]) > 0


@pytest.mark.asyncio
async def test_llm_call_recorded(spy_data, copy_analysis, migrated_db, monkeypatch):
    """After generate_dossier(), db['llm_calls'] has 1 record with correct fields."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    fixture_json = _load_fixture("dossier_generator_output.json")
    mock_response = _make_mock_response(
        fixture_json, input_tokens=2000, output_tokens=900
    )

    with patch("mis.intelligence.dossier_generator.AsyncAnthropic") as mock_cls:
        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        mock_cls.return_value = mock_client

        from mis.intelligence.dossier_generator import generate_dossier

        await generate_dossier(
            data=spy_data,
            copy_analysis=copy_analysis,
            dossier_id=42,
            db_path=migrated_db,
        )

    db = get_db(migrated_db)
    records = list(db["llm_calls"].rows)
    assert len(records) == 1

    rec = records[0]
    assert rec["dossier_id"] == 42
    assert rec["stage"] == "dossier_generator"
    assert rec["input_tokens"] == 2000
    assert rec["output_tokens"] == 900
    assert rec["cost_usd"] > 0
    assert "model" in rec
    assert "created_at" in rec


@pytest.mark.asyncio
async def test_json_decode_error_raises(spy_data, copy_analysis, migrated_db, monkeypatch):
    """When LLM returns free text, raises DossierGenerationError."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    mock_response = _make_mock_response(
        "Aqui está minha análise detalhada do produto..."
    )

    with patch("mis.intelligence.dossier_generator.AsyncAnthropic") as mock_cls:
        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        mock_cls.return_value = mock_client

        from mis.intelligence.dossier_generator import (
            generate_dossier,
            DossierGenerationError,
        )

        with pytest.raises(DossierGenerationError):
            await generate_dossier(
                data=spy_data,
                copy_analysis=copy_analysis,
                dossier_id=1,
                db_path=migrated_db,
            )
