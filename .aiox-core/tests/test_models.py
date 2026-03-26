"""Unit tests for nexus.models — AgentScore and CreativeBundle."""
import pytest
from pydantic import ValidationError

from nexus.models import AgentScore, CreativeBundle


# ─── AgentScore tests ────────────────────────────────────────────────────────

def test_valid_score():
    score = AgentScore(
        dimension="copy",
        score=8,
        approved=True,
        feedback="Hook forte com urgencia. CTA claro e direto.",
        strengths=["Hook urgente"],
        issues=[],
    )
    assert score.score == 8
    assert score.approved is True
    assert score.dimension == "copy"


def test_score_below_minimum():
    with pytest.raises(ValidationError) as exc_info:
        AgentScore(
            dimension="copy",
            score=0,
            approved=False,
            feedback="Too low score value here",
            strengths=[],
            issues=[],
        )
    assert "greater than or equal to 1" in str(exc_info.value)


def test_score_above_maximum():
    with pytest.raises(ValidationError) as exc_info:
        AgentScore(
            dimension="copy",
            score=11,
            approved=True,
            feedback="Too high score value given",
            strengths=[],
            issues=[],
        )
    assert "less than or equal to 10" in str(exc_info.value)


def test_feedback_too_short():
    with pytest.raises(ValidationError) as exc_info:
        AgentScore(
            dimension="copy",
            score=5,
            approved=False,
            feedback="short",
            strengths=[],
            issues=[],
        )
    error_text = str(exc_info.value).lower()
    assert "min_length" in error_text or "at least" in error_text or "string should have at least" in error_text


# ─── CreativeBundle tests ─────────────────────────────────────────────────────

def test_valid_creative_bundle():
    bundle = CreativeBundle(
        niche="emagrecimento",
        script_text="Voce sabia que 73% dos brasileiros nao conseguem perder peso? Este produto resolve em 30 dias.",
        status="pending",
    )
    assert bundle.niche == "emagrecimento"
    assert bundle.status == "pending"
    assert bundle.id is not None  # auto-generated UUID


def test_creative_bundle_missing_required():
    with pytest.raises(ValidationError):
        CreativeBundle(
            script_text="Some script text here",
            status="pending",
        )  # niche is required and missing
