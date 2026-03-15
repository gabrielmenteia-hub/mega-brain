"""Tests for mis.radar.synthesizer — LLM-based pain report synthesis."""
import json
import os
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import sqlite_utils

from mis.migrations._004_pain_radar import run_migration_004
from mis.radar.synthesizer import fetch_cycle_signals, synthesize_niche_pains


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_signal_counter = 0


def _make_signal(db, niche_slug, hours_ago, source="reddit", title="test signal"):
    """Insert a pain_signal with collected_at = now - hours_ago."""
    global _signal_counter
    _signal_counter += 1
    collected_at = (datetime.utcnow() - timedelta(hours=hours_ago)).isoformat()
    url = f"https://example.com/{source}/{hours_ago}/{title[:10]}/{_signal_counter}"
    import hashlib
    url_hash = hashlib.sha256(url.encode()).hexdigest()
    db["pain_signals"].insert(
        {
            "url_hash": url_hash,
            "url": url,
            "title": title,
            "source": source,
            "niche_slug": niche_slug,
            "score": 100,
            "extra_json": json.dumps({"top_comments": ["comment 1", "comment 2"]}),
            "collected_at": collected_at,
        }
    )


def _make_llm_response(pains=None):
    """Build a mock Anthropic messages.create() response."""
    if pains is None:
        pains = [
            {
                "description": f"Dor principal {i+1} do nicho",
                "evidence": f"Reddit: {i*5+3} posts com alto upvote",
                "interest_level": "Alto",
            }
            for i in range(5)
        ]
    payload = json.dumps({"pains": pains})
    content_block = MagicMock()
    content_block.text = payload
    usage = MagicMock()
    usage.input_tokens = 500
    usage.output_tokens = 200
    response = MagicMock()
    response.content = [content_block]
    response.usage = usage
    return response


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_synthesize_returns_report_with_top_pains(tmp_path, monkeypatch):
    """synthesize_niche_pains() returns a dict with 'pains' list of 5 items."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-abc123")
    db_path = str(tmp_path / "mis.db")
    db = sqlite_utils.Database(db_path)
    run_migration_004(db_path)

    # Insert a niches row so FK is satisfied
    db["niches"].insert({"id": 1, "name": "Emagrecimento", "slug": "emagrecimento"})

    # Populate 5 recent signals (within 2h cycle window)
    for i in range(5):
        _make_signal(db, "emagrecimento", hours_ago=1, title=f"Signal about weight loss {i}")

    mock_response = _make_llm_response()
    mock_create = AsyncMock(return_value=mock_response)

    with patch("mis.radar.synthesizer.anthropic.AsyncAnthropic") as MockClient:
        instance = MockClient.return_value
        instance.messages = MagicMock()
        instance.messages.create = mock_create

        cycle_at = datetime.utcnow().isoformat()
        report = await synthesize_niche_pains(
            niche_id=1,
            niche_name="Emagrecimento",
            niche_slug="emagrecimento",
            cycle_at=cycle_at,
            db_path=db_path,
        )

    assert report is not None
    assert "pains" in report
    assert len(report["pains"]) == 5
    for pain in report["pains"]:
        assert "description" in pain
        assert "evidence" in pain
        assert "interest_level" in pain
        assert pain["interest_level"] in ("Alto", "Médio", "Baixo")


@pytest.mark.asyncio
async def test_no_signals_skip_llm_call(tmp_path, monkeypatch):
    """When no signals exist, synthesizer skips LLM call and returns None."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-abc123")
    db_path = str(tmp_path / "mis.db")
    run_migration_004(db_path)

    mock_create = AsyncMock()

    with patch("mis.radar.synthesizer.anthropic.AsyncAnthropic") as MockClient:
        instance = MockClient.return_value
        instance.messages = MagicMock()
        instance.messages.create = mock_create

        cycle_at = datetime.utcnow().isoformat()
        result = await synthesize_niche_pains(
            niche_id=1,
            niche_name="Emagrecimento",
            niche_slug="emagrecimento",
            cycle_at=cycle_at,
            db_path=db_path,
        )

    assert result is None
    mock_create.assert_not_called()


@pytest.mark.asyncio
async def test_report_idempotent_upsert(tmp_path, monkeypatch):
    """Calling synthesize_niche_pains() twice for same niche/cycle results in 1 row."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-abc123")
    db_path = str(tmp_path / "mis.db")
    db = sqlite_utils.Database(db_path)
    run_migration_004(db_path)

    db["niches"].insert({"id": 1, "name": "Emagrecimento", "slug": "emagrecimento"})

    for i in range(3):
        _make_signal(db, "emagrecimento", hours_ago=1, title=f"Signal {i}")

    mock_response = _make_llm_response()
    mock_create = AsyncMock(return_value=mock_response)
    cycle_at = datetime.utcnow().isoformat()

    with patch("mis.radar.synthesizer.anthropic.AsyncAnthropic") as MockClient:
        instance = MockClient.return_value
        instance.messages = MagicMock()
        instance.messages.create = mock_create

        await synthesize_niche_pains(
            niche_id=1,
            niche_name="Emagrecimento",
            niche_slug="emagrecimento",
            cycle_at=cycle_at,
            db_path=db_path,
        )
        await synthesize_niche_pains(
            niche_id=1,
            niche_name="Emagrecimento",
            niche_slug="emagrecimento",
            cycle_at=cycle_at,
            db_path=db_path,
        )

    count = db.execute("SELECT COUNT(*) FROM pain_reports").fetchone()[0]
    assert count == 1


@pytest.mark.asyncio
async def test_report_has_evidence_fields(tmp_path, monkeypatch):
    """Report JSON contains required keys: pains, niche, cycle_at, sources_used."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-abc123")
    db_path = str(tmp_path / "mis.db")
    db = sqlite_utils.Database(db_path)
    run_migration_004(db_path)

    db["niches"].insert({"id": 1, "name": "Emagrecimento", "slug": "emagrecimento"})
    _make_signal(db, "emagrecimento", hours_ago=1)

    mock_response = _make_llm_response()
    mock_create = AsyncMock(return_value=mock_response)

    with patch("mis.radar.synthesizer.anthropic.AsyncAnthropic") as MockClient:
        instance = MockClient.return_value
        instance.messages = MagicMock()
        instance.messages.create = mock_create

        cycle_at = datetime.utcnow().isoformat()
        report = await synthesize_niche_pains(
            niche_id=1,
            niche_name="Emagrecimento",
            niche_slug="emagrecimento",
            cycle_at=cycle_at,
            db_path=db_path,
        )

    assert "pains" in report
    assert "niche" in report
    assert "cycle_at" in report
    assert "sources_used" in report
    assert report["niche"] == "emagrecimento"

    # Verify stored in DB as valid parseable JSON
    row = list(db["pain_reports"].rows)[0]
    parsed = json.loads(row["report_json"])
    assert "pains" in parsed
    assert "niche" in parsed


def test_fetch_cycle_signals_returns_recent_only(tmp_path):
    """fetch_cycle_signals returns only signals within the 2h window."""
    db_path = str(tmp_path / "mis.db")
    db = sqlite_utils.Database(db_path)
    run_migration_004(db_path)

    # Insert signal from 1h ago (should be returned — within 2h cycle)
    _make_signal(db, "emagrecimento", hours_ago=1, title="Recent signal")

    # Insert signal from 25h ago (should NOT be returned)
    _make_signal(db, "emagrecimento", hours_ago=25, title="Old signal")

    # cycle_start = 2 hours before now
    cycle_start = (datetime.utcnow() - timedelta(hours=2)).isoformat()
    signals = fetch_cycle_signals(db_path, "emagrecimento", cycle_start)

    assert len(signals) == 1
    assert signals[0]["title"] == "Recent signal"
