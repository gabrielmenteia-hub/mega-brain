"""Tests for mis.intelligence.copy_analyzer — TDD RED phase."""
import json
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mis.spies.completeness_gate import SpyData

# Fixture path
FIXTURE_DIR = Path(__file__).parent / "fixtures" / "llm_responses"


def _load_fixture(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def _make_mock_response(text: str):
    """Build a mock Anthropic message response object."""
    content_block = MagicMock()
    content_block.text = text

    usage = MagicMock()
    usage.input_tokens = 1234
    usage.output_tokens = 456

    response = MagicMock()
    response.content = [content_block]
    response.usage = usage
    return response


@pytest.fixture
def spy_data_with_copy():
    """SpyData with meaningful copy text."""
    return SpyData(
        copy_text="Descubra como ganhar renda extra trabalhando apenas 2 horas por dia "
        "com o método que já transformou a vida de mais de 50.000 alunos. "
        "Chega de depender do emprego CLT para pagar suas contas. "
        "Com nossa metodologia comprovada você pode dobrar sua renda em 90 dias. "
        "Garantia incondicional de 30 dias ou seu dinheiro de volta.",
        offer_data={"price": 297.0, "installments": 12, "bonus_count": 5},
        ads=[{"creative_id": "ad_001", "headline": "Liberdade financeira em 90 dias"}],
        reviews=[{"rating": 5, "text": "Mudou minha vida financeira completamente!"}],
    )


@pytest.mark.asyncio
async def test_happy_path(spy_data_with_copy, monkeypatch):
    """analyze_copy() returns dict with all required copy_analysis fields."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    fixture_json = _load_fixture("copy_analyzer_output.json")
    mock_response = _make_mock_response(fixture_json)

    with patch(
        "mis.intelligence.copy_analyzer.AsyncAnthropic"
    ) as mock_client_cls:
        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        from mis.intelligence.copy_analyzer import analyze_copy

        result = await analyze_copy(spy_data_with_copy)

    assert isinstance(result, dict)
    assert result["framework_type"]  # non-empty
    assert isinstance(result["emotional_triggers"], list)
    assert len(result["emotional_triggers"]) > 0
    assert result["narrative_structure"]  # non-empty string
    assert isinstance(result["social_proof_elements"], list)
    assert len(result["social_proof_elements"]) > 0


@pytest.mark.asyncio
async def test_returns_copy_analysis_section(spy_data_with_copy, monkeypatch):
    """All required keys from the copy_analysis schema are present."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    fixture_json = _load_fixture("copy_analyzer_output.json")
    mock_response = _make_mock_response(fixture_json)

    with patch(
        "mis.intelligence.copy_analyzer.AsyncAnthropic"
    ) as mock_client_cls:
        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        from mis.intelligence.copy_analyzer import analyze_copy

        result = await analyze_copy(spy_data_with_copy)

    required_keys = {
        "framework_type",
        "emotional_triggers",
        "narrative_structure",
        "social_proof_elements",
    }
    assert required_keys.issubset(result.keys()), (
        f"Missing keys: {required_keys - result.keys()}"
    )


@pytest.mark.asyncio
async def test_json_decode_error_raises_copy_analysis_error(spy_data_with_copy, monkeypatch):
    """When LLM returns free text (not JSON), raises CopyAnalysisError."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    mock_response = _make_mock_response("Desculpe, não consigo analisar isso agora.")

    with patch(
        "mis.intelligence.copy_analyzer.AsyncAnthropic"
    ) as mock_client_cls:
        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        from mis.intelligence.copy_analyzer import analyze_copy, CopyAnalysisError

        with pytest.raises(CopyAnalysisError):
            await analyze_copy(spy_data_with_copy)


@pytest.mark.asyncio
async def test_retry_on_rate_limit(spy_data_with_copy, monkeypatch):
    """When LLM raises RateLimitError once then succeeds, analyze_copy() returns result."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    from anthropic import RateLimitError

    fixture_json = _load_fixture("copy_analyzer_output.json")
    mock_response = _make_mock_response(fixture_json)

    # Build a mock RateLimitError — requires request and response args
    rate_limit_error = RateLimitError(
        message="Rate limit exceeded",
        response=MagicMock(status_code=429, headers={}),
        body={},
    )

    call_count = 0

    async def side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise rate_limit_error
        return mock_response

    with patch(
        "mis.intelligence.copy_analyzer.AsyncAnthropic"
    ) as mock_client_cls:
        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(side_effect=side_effect)
        mock_client_cls.return_value = mock_client

        # Patch tenacity wait to avoid actual sleeping in tests
        with patch(
            "mis.intelligence.copy_analyzer.wait_exponential",
            return_value=lambda retry_state: 0,
        ):
            from mis.intelligence.copy_analyzer import analyze_copy

            result = await analyze_copy(spy_data_with_copy)

    assert result["framework_type"] == "PAS"
    assert call_count == 2  # first failed, second succeeded


@pytest.mark.asyncio
async def test_no_copy_raises_copy_analysis_error(monkeypatch):
    """When SpyData.copy_text is None, raises CopyAnalysisError immediately (no LLM call)."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    data = SpyData(copy_text=None)

    with patch(
        "mis.intelligence.copy_analyzer.AsyncAnthropic"
    ) as mock_client_cls:
        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock()
        mock_client_cls.return_value = mock_client

        from mis.intelligence.copy_analyzer import analyze_copy, CopyAnalysisError

        with pytest.raises(CopyAnalysisError):
            await analyze_copy(data)

    # LLM should NOT be called when copy is absent
    mock_client.messages.create.assert_not_called()
