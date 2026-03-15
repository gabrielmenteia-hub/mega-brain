---
phase: 03-product-espionage-dossiers
plan: "03"
subsystem: data-quality
tags: [structlog, dataclass, gate, completeness, tdd, spy-pipeline]

# Dependency graph
requires:
  - phase: 03-product-espionage-dossiers/03-01
    provides: SalesPageScraper, reviews/llm_calls tables, SpyData output schema

provides:
  - SpyData dataclass: container for copy_text, offer_data, reviews, ads
  - check_completeness(): blocking gate with confidence scoring 0-100
  - structlog machine-readable log events (gate_passed, copy_ok, offer_ok, reviews_count, ads_ok)
  - Partial dossier logic: gate_passed=False but confidence>0 when copy present

affects:
  - 03-04: LLM pipeline only invokes if check_completeness() returns gate_passed=True
  - 03-05: SpyOrchestrator imports SpyData as unified data container across all spies

# Tech tracking
tech-stack:
  added: []
  patterns:
    - TDD RED→GREEN: failing tests committed before implementation, separate commits
    - Blocking gate pattern: critical fields fail fast (copy), non-critical fields reduce confidence only
    - Structlog machine-readable events: all gate decision fields emitted as individual log keys
    - Partial dossier support: two-tier response (gate_passed + confidence) enables graceful degradation

key-files:
  created:
    - mis/spies/completeness_gate.py
    - mis/tests/test_completeness_gate.py
  modified: []

key-decisions:
  - "copy is blocking at 100-char threshold — prevents LLM from running on empty or trivial pages"
  - "confidence_score independent of gate_passed — enables partial dossier generation when reviews < min_reviews but copy is present"
  - "min_reviews=10 as default parameter (configurable) — reviewed threshold based on statistical reliability"
  - "reviews score scales linearly 0-15 — no hard cutoff in confidence, smooth degradation"

patterns-established:
  - "Gate pattern: (gate_passed: bool, confidence: int) tuple — unambiguous machine-readable signal for downstream"
  - "structlog event 'completeness_gate' — standard event name for pipeline log parsing"

requirements-completed: [SPY-05, DOS-05]

# Metrics
duration: 5min
completed: 2026-03-14
---

# Phase 03 Plan 03: SpyData + Completeness Gate Summary

**SpyData dataclass + check_completeness() gate with blocking copy/reviews rules and weighted confidence score (0-100), structlog machine-readable events**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-03-14T23:46:02Z
- **Completed:** 2026-03-14T23:50:49Z
- **Tasks:** 1 (TDD: 2 commits)
- **Files modified:** 2

## Accomplishments

- SpyData dataclass with 4 fields (copy_text, offer_data, reviews, ads) — unified container for all spy outputs
- check_completeness() gate: copy is blocking (must be present AND >= 100 chars), reviews is blocking (must meet min_reviews threshold)
- Confidence score weights: copy=50, offer=15, ads=20, reviews=0-15 (scales linearly) — sums to 100 when all fields present
- structlog emits 6 machine-readable keys on every gate evaluation — parseable by log aggregators
- 9/9 TDD tests GREEN covering all boundary conditions

## Task Commits

Each task was committed atomically (TDD pattern: test then impl):

1. **Task 1 RED: Failing tests** - `03116c2` (test)
2. **Task 1 GREEN: Implementation** - `e18c4b8` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified

- `mis/spies/completeness_gate.py` - SpyData dataclass + check_completeness() with structlog
- `mis/tests/test_completeness_gate.py` - 9 tests: gate pass/block, confidence scores, structlog fields, partial dossier

## Decisions Made

- copy is blocking at >= 100 chars — prevents LLM from running on empty or trivial pages; confidence=0 when copy absent
- confidence_score is independent of gate_passed — allows partial dossier generation (confidence>0, gate=False) when copy present but reviews insufficient
- min_reviews=10 configurable parameter — default based on statistical reliability of review counts
- reviews score scales linearly 0-15 based on (count / min_reviews) — smooth degradation, no hard cutoff in confidence

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- `test_reviews_spy.py` collection error existed before this plan (missing `mis.spies.reviews` from plan 03-02) — pre-existing, out of scope per SCOPE BOUNDARY rule. Logged to deferred items.

## Next Phase Readiness

- SpyData and check_completeness() ready for import in plan 03-04 (LLM pipeline) and 03-05 (SpyOrchestrator)
- Gate contract established: `(gate_passed, confidence_score)` tuple — downstream can trust this interface

---
*Phase: 03-product-espionage-dossiers*
*Completed: 2026-03-14*
