"""Tests for mis.radar.meta_ads_collector — Meta Ads Pain Radar (RADAR-04).

Coverage:
- test_happy_path_inserts_3_signals: fixture with 3 ads + token → returns 3 signals, COUNT=3 in pain_signals
- test_no_token_returns_empty: no META_ACCESS_TOKEN → returns [], no exception, COUNT=0
- test_idempotency_url_hash: running collect twice with same fixture → COUNT does not increase
- test_ad_without_creative_body_skipped: ad_creative_bodies=[] → returns [], COUNT=0
"""
import json
import sqlite3
from pathlib import Path
from unittest.mock import AsyncMock

import httpx
import pytest
import respx

from mis.radar.meta_ads_collector import collect_ad_comments, META_API_URL
from mis.db import run_migrations

_FIXTURE = (
    Path(__file__).parent / "fixtures" / "meta_ads" / "ads_archive_radar_response.json"
)


@pytest.fixture
def radar_fixture() -> dict:
    """Load the radar Meta Ads fixture with 3 ads."""
    return json.loads(_FIXTURE.read_text(encoding="utf-8"))


def _make_niche(keywords=None):
    """Return a minimal niche dict for radar tests."""
    return {
        "slug": "emagrecimento",
        "name": "Emagrecimento",
        "keywords": keywords or ["emagrecer rapido"],
        "ad_countries": ["BR"],
    }


@pytest.mark.asyncio
async def test_happy_path_inserts_3_signals(tmp_path, monkeypatch, radar_fixture):
    """Com token e fixture de 3 anuncios, retorna 3 signals e COUNT=3 em pain_signals."""
    monkeypatch.setenv("META_ACCESS_TOKEN", "fake_radar_token")
    monkeypatch.setattr("asyncio.sleep", AsyncMock())

    db_path = str(tmp_path / "mis.db")
    run_migrations(db_path)

    niche = _make_niche()

    with respx.mock:
        respx.get(META_API_URL).mock(
            return_value=httpx.Response(200, json=radar_fixture)
        )
        signals = await collect_ad_comments(niche, db_path)

    assert len(signals) == 3

    conn = sqlite3.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM pain_signals WHERE source='meta_ads'").fetchone()[0]
    conn.close()
    assert count == 3

    # Verify source field
    for sig in signals:
        assert sig["source"] == "meta_ads"
        assert sig["niche_slug"] == "emagrecimento"


@pytest.mark.asyncio
async def test_no_token_returns_empty(tmp_path, monkeypatch):
    """Sem META_ACCESS_TOKEN, retorna [] graciosamente sem propagar excecao. COUNT=0."""
    monkeypatch.delenv("META_ACCESS_TOKEN", raising=False)
    monkeypatch.setattr("asyncio.sleep", AsyncMock())

    db_path = str(tmp_path / "mis.db")
    run_migrations(db_path)

    niche = _make_niche()

    # No respx.mock needed — should return before making HTTP calls
    signals = await collect_ad_comments(niche, db_path)

    assert signals == []

    conn = sqlite3.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM pain_signals").fetchone()[0]
    conn.close()
    assert count == 0


@pytest.mark.asyncio
async def test_idempotency_url_hash(tmp_path, monkeypatch, radar_fixture):
    """Segunda execucao com mesma fixture nao aumenta o COUNT em pain_signals (INSERT OR IGNORE)."""
    monkeypatch.setenv("META_ACCESS_TOKEN", "fake_radar_token_idem")
    monkeypatch.setattr("asyncio.sleep", AsyncMock())

    db_path = str(tmp_path / "mis.db")
    run_migrations(db_path)

    niche = _make_niche()

    with respx.mock:
        respx.get(META_API_URL).mock(
            return_value=httpx.Response(200, json=radar_fixture)
        )
        # First run
        await collect_ad_comments(niche, db_path)

    conn = sqlite3.connect(db_path)
    count_after_first = conn.execute("SELECT COUNT(*) FROM pain_signals").fetchone()[0]
    conn.close()

    with respx.mock:
        respx.get(META_API_URL).mock(
            return_value=httpx.Response(200, json=radar_fixture)
        )
        # Second run with same fixture
        await collect_ad_comments(niche, db_path)

    conn = sqlite3.connect(db_path)
    count_after_second = conn.execute("SELECT COUNT(*) FROM pain_signals").fetchone()[0]
    conn.close()

    assert count_after_first == count_after_second, (
        f"INSERT OR IGNORE should prevent duplicates: "
        f"first={count_after_first}, second={count_after_second}"
    )


@pytest.mark.asyncio
async def test_ad_without_creative_body_skipped(tmp_path, monkeypatch):
    """Anuncio com ad_creative_bodies=[] e silenciosamente ignorado. Retorna [], COUNT=0."""
    monkeypatch.setenv("META_ACCESS_TOKEN", "fake_radar_token_empty")
    monkeypatch.setattr("asyncio.sleep", AsyncMock())

    db_path = str(tmp_path / "mis.db")
    run_migrations(db_path)

    niche = _make_niche()

    empty_fixture = {
        "data": [
            {
                "page_name": "Anuncio Sem Copy",
                "ad_snapshot_url": "https://www.facebook.com/ads/archive/render_ad/?id=empty001",
                "ad_creative_bodies": [],
                "ad_delivery_start_time": "2026-03-01",
            }
        ]
    }

    with respx.mock:
        respx.get(META_API_URL).mock(
            return_value=httpx.Response(200, json=empty_fixture)
        )
        signals = await collect_ad_comments(niche, db_path)

    assert signals == []

    conn = sqlite3.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM pain_signals").fetchone()[0]
    conn.close()
    assert count == 0
