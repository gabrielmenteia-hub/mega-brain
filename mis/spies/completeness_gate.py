"""
SpyData dataclass and data completeness gate.

The gate is the critical boundary between data collection and AI analysis.
It ensures the LLM pipeline only receives data sufficient to generate a
reliable dossier.

Requirements: SPY-05, DOS-05
"""
from dataclasses import dataclass, field
from typing import Optional

import structlog

log = structlog.get_logger()


@dataclass
class SpyData:
    """Container for all data collected by product espionage spies."""

    copy_text: Optional[str] = None
    offer_data: Optional[dict] = None
    reviews: list[dict] = field(default_factory=list)
    ads: list[dict] = field(default_factory=list)


def check_completeness(data: SpyData, min_reviews: int = 10) -> tuple[bool, int]:
    """
    Evaluate completeness of espionage data.

    Returns:
        (gate_passed, confidence_score 0-100)

    Rules:
    - copy is BLOCKING: absent or < 100 chars => (False, 0)
    - reviews < min_reviews => gate_passed=False (but confidence > 0 if copy ok)
    - offer and ads: non-blocking — only affect confidence score

    Confidence weights (sum to 100):
    - copy present: +50
    - offer present: +15
    - ads present: +20
    - reviews: scales 0–15 based on (reviews_count / min_reviews) * 15
    """
    copy_ok = bool(data.copy_text and len(data.copy_text) >= 100)
    offer_ok = bool(data.offer_data)
    reviews_count = len(data.reviews)
    ads_ok = bool(data.ads)

    gate_passed = copy_ok and reviews_count >= min_reviews

    # Confidence score
    if not copy_ok:
        confidence = 0
    else:
        confidence = 50  # copy present
        if offer_ok:
            confidence += 15
        if ads_ok:
            confidence += 20
        # reviews: scale 0–15 based on 0–min_reviews
        reviews_score = min(15, int((reviews_count / min_reviews) * 15))
        confidence += reviews_score

    log.info(
        "completeness_gate",
        copy_ok=copy_ok,
        offer_ok=offer_ok,
        reviews_count=reviews_count,
        ads_ok=ads_ok,
        gate_passed=gate_passed,
        confidence_score=confidence,
    )

    return gate_passed, confidence
