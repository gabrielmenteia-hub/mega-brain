"""
Tests for SpyData dataclass and check_completeness() gate.
Requirements: SPY-05, DOS-05
"""
import pytest
import structlog
from structlog.testing import capture_logs

from mis.spies.completeness_gate import SpyData, check_completeness


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_copy(length: int = 150) -> str:
    """Return a copy string of the specified length."""
    return "a" * length


def make_reviews(count: int) -> list[dict]:
    return [{"text": f"review {i}"} for i in range(count)]


def make_ads(count: int = 3) -> list[dict]:
    return [{"id": f"ad-{i}"} for i in range(count)]


def make_offer() -> dict:
    return {"price": 197.0, "currency": "BRL"}


# ---------------------------------------------------------------------------
# Gate pass / block tests
# ---------------------------------------------------------------------------

def test_gate_passes():
    """copy present (>100 chars) + 10 reviews => gate_passed=True, confidence >= 65"""
    data = SpyData(
        copy_text=make_copy(150),
        reviews=make_reviews(10),
    )
    gate_passed, confidence = check_completeness(data)
    assert gate_passed is True
    assert confidence >= 65


def test_copy_missing_blocks():
    """copy_text=None => gate_passed=False, confidence=0"""
    data = SpyData(
        copy_text=None,
        reviews=make_reviews(10),
    )
    gate_passed, confidence = check_completeness(data)
    assert gate_passed is False
    assert confidence == 0


def test_copy_too_short_blocks():
    """copy_text with 50 chars => gate_passed=False, confidence=0"""
    data = SpyData(
        copy_text=make_copy(50),
        reviews=make_reviews(10),
    )
    gate_passed, confidence = check_completeness(data)
    assert gate_passed is False
    assert confidence == 0


def test_reviews_below_threshold():
    """copy ok but reviews_count=5 => gate_passed=False, confidence > 0 (copy counts)"""
    data = SpyData(
        copy_text=make_copy(150),
        reviews=make_reviews(5),
    )
    gate_passed, confidence = check_completeness(data)
    assert gate_passed is False
    assert confidence > 0


# ---------------------------------------------------------------------------
# Confidence score calculation tests
# ---------------------------------------------------------------------------

def test_confidence_full():
    """copy + offer + ads + 10 reviews => confidence=100"""
    data = SpyData(
        copy_text=make_copy(150),
        offer_data=make_offer(),
        reviews=make_reviews(10),
        ads=make_ads(3),
    )
    gate_passed, confidence = check_completeness(data)
    assert gate_passed is True
    assert confidence == 100


def test_confidence_no_ads():
    """copy + offer + 0 ads + 10 reviews => confidence=80 (missing 20 pts from ads)"""
    data = SpyData(
        copy_text=make_copy(150),
        offer_data=make_offer(),
        reviews=make_reviews(10),
        ads=[],
    )
    gate_passed, confidence = check_completeness(data)
    assert gate_passed is True
    assert confidence == 80


def test_confidence_no_offer():
    """copy + no offer + ads + 10 reviews => confidence=85 (missing 15 pts from offer)"""
    data = SpyData(
        copy_text=make_copy(150),
        offer_data=None,
        reviews=make_reviews(10),
        ads=make_ads(3),
    )
    gate_passed, confidence = check_completeness(data)
    assert gate_passed is True
    assert confidence == 85


# ---------------------------------------------------------------------------
# structlog machine-readable fields
# ---------------------------------------------------------------------------

def test_structlog_fields_emitted():
    """structlog event must have copy_ok, offer_ok, reviews_count, ads_ok, gate_passed fields"""
    data = SpyData(
        copy_text=make_copy(150),
        offer_data=make_offer(),
        reviews=make_reviews(10),
        ads=make_ads(3),
    )
    with capture_logs() as logs:
        check_completeness(data)

    assert len(logs) >= 1
    entry = logs[0]
    assert "copy_ok" in entry
    assert "offer_ok" in entry
    assert "reviews_count" in entry
    assert "ads_ok" in entry
    assert "gate_passed" in entry


# ---------------------------------------------------------------------------
# Partial dossier (incomplete) allowed
# ---------------------------------------------------------------------------

def test_partial_dossier_allowed():
    """copy ok + 5 reviews => gate_passed=False but confidence > 0 (partial dossier possible)"""
    data = SpyData(
        copy_text=make_copy(150),
        reviews=make_reviews(5),
    )
    gate_passed, confidence = check_completeness(data)
    assert gate_passed is False
    # copy present => confidence > 0 even though gate blocked
    assert confidence > 0
