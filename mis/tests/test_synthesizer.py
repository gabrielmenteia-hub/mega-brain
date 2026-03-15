"""Tests for mis.radar.synthesizer — LLM-based pain report synthesis.

RED scaffolds: these tests fail with ImportError because mis.radar.synthesizer
does not exist yet. This is intentional — Wave 2 will implement the module.
"""
from mis.radar.synthesizer import synthesize_niche_pains, fetch_cycle_signals
import pytest


@pytest.mark.asyncio
async def test_synthesize_returns_report_with_top_pains(tmp_path):
    """synthesize_niche_pains() returns a pain_reports row with top pain list."""
    pytest.skip("RED: module not implemented yet")


@pytest.mark.asyncio
async def test_no_signals_skip_llm_call(tmp_path):
    """When no signals collected for niche, synthesizer skips LLM call and returns None."""
    pytest.skip("RED: module not implemented yet")


@pytest.mark.asyncio
async def test_report_idempotent_upsert(tmp_path):
    """Calling synthesize_niche_pains() twice for same niche/cycle results in 1 report row."""
    pytest.skip("RED: module not implemented yet")


@pytest.mark.asyncio
async def test_report_has_evidence_fields():
    """Report JSON contains top_pains list, each with evidence (sources, urls, scores)."""
    pytest.skip("RED: module not implemented yet")
