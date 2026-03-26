"""Structural tests for all NEXUS review rubrics.

These tests verify:
- Required fields on all rubrics
- Numeric levels anchors on all criteria
- Criteria weights sum to 1.0
- Few-shot examples have required fields
- Coverage: at least 1 approved and 1 rejected per rubric
- Threshold consistency: expected_approved aligns with NexusConfig defaults
"""
import pytest
from nexus.rubrics import ALL_RUBRICS

# Thresholds from NexusConfig defaults
THRESHOLDS = {"copy": 7, "tech": 6, "compliance": 8, "performance": 6}


def test_all_rubrics_have_required_fields():
    """Each rubric must have dimension, criteria, and at least 2 few_shot_examples."""
    assert len(ALL_RUBRICS) == 4, f"Expected 4 rubrics, got {len(ALL_RUBRICS)}"
    for rubric in ALL_RUBRICS:
        assert "dimension" in rubric, f"Rubric missing 'dimension': {rubric}"
        assert "criteria" in rubric, f"Rubric missing 'criteria': {rubric}"
        assert "few_shot_examples" in rubric, f"Rubric missing 'few_shot_examples': {rubric}"
        assert len(rubric["few_shot_examples"]) >= 2, (
            f"Rubric '{rubric.get('dimension')}' has fewer than 2 few_shot_examples"
        )


def test_all_criteria_have_numeric_levels():
    """Each criterion must have name, weight, and levels with int keys including 10 and 2."""
    for rubric in ALL_RUBRICS:
        dim = rubric["dimension"]
        for criterion in rubric["criteria"]:
            assert "name" in criterion, f"Criterion in '{dim}' missing 'name': {criterion}"
            assert "weight" in criterion, f"Criterion in '{dim}' missing 'weight': {criterion}"
            assert "levels" in criterion, f"Criterion in '{dim}' missing 'levels': {criterion}"
            levels = criterion["levels"]
            assert 10 in levels, (
                f"Criterion '{criterion.get('name')}' in '{dim}' missing level 10"
            )
            assert 2 in levels, (
                f"Criterion '{criterion.get('name')}' in '{dim}' missing level 2"
            )


def test_criteria_weights_sum_to_one():
    """Criteria weights must sum to 1.0 (tolerance 0.01) for each rubric."""
    for rubric in ALL_RUBRICS:
        dim = rubric["dimension"]
        total = sum(c["weight"] for c in rubric["criteria"])
        assert abs(total - 1.0) <= 0.01, (
            f"Rubric '{dim}' weights sum to {total:.4f}, expected 1.0 (±0.01)"
        )


def test_few_shot_examples_have_expected_fields():
    """Each few-shot example must have input, expected_score, expected_total, expected_approved, reasoning."""
    required = {"input", "expected_score", "expected_total", "expected_approved", "reasoning"}
    for rubric in ALL_RUBRICS:
        dim = rubric["dimension"]
        for i, example in enumerate(rubric["few_shot_examples"]):
            for field in required:
                assert field in example, (
                    f"Rubric '{dim}' example #{i} missing field '{field}': {example}"
                )


def test_at_least_one_approved_and_one_rejected_per_rubric():
    """Each rubric must have at least 1 approved and 1 rejected few-shot example."""
    for rubric in ALL_RUBRICS:
        dim = rubric["dimension"]
        approved = [ex for ex in rubric["few_shot_examples"] if ex["expected_approved"] is True]
        rejected = [ex for ex in rubric["few_shot_examples"] if ex["expected_approved"] is False]
        assert len(approved) >= 1, (
            f"Rubric '{dim}' has no approved few-shot example"
        )
        assert len(rejected) >= 1, (
            f"Rubric '{dim}' has no rejected few-shot example"
        )


def test_expected_approved_consistent_with_threshold():
    """expected_approved must be consistent with expected_total vs NexusConfig thresholds."""
    for rubric in ALL_RUBRICS:
        dim = rubric["dimension"]
        threshold = THRESHOLDS[dim]
        for i, ex in enumerate(rubric["few_shot_examples"]):
            total = ex["expected_total"]
            approved = ex["expected_approved"]
            if total >= threshold:
                assert approved is True, (
                    f"Rubric '{dim}' example #{i}: expected_total={total} >= threshold={threshold} "
                    f"but expected_approved={approved} (should be True)"
                )
            else:
                assert approved is False, (
                    f"Rubric '{dim}' example #{i}: expected_total={total} < threshold={threshold} "
                    f"but expected_approved={approved} (should be False)"
                )
