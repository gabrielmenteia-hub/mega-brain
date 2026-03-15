---
phase: 04-pain-radar
plan: "04"
subsystem: mis/radar
tags: [synthesizer, llm, pain-reports, idempotency, tdd]
dependency_graph:
  requires:
    - 04-02  # collectors (Reddit, Quora, Trends)
    - 04-03  # YouTube collector + quota guard
  provides:
    - synthesize_niche_pains()
    - fetch_cycle_signals()
    - pain_reports upsert contract
  affects:
    - 04-05  # radar orchestrator/scheduler
tech_stack:
  added:
    - anthropic.AsyncAnthropic (LLM client, claude-sonnet-4-6)
    - mis/prompts/pain_synthesis_prompt.txt (pt-BR synthesis template)
  patterns:
    - TDD (RED -> GREEN -> verify)
    - ON CONFLICT upsert for idempotent reports
    - sqlite3 direct connection to avoid sqlite_utils context manager issue
key_files:
  created:
    - mis/radar/synthesizer.py
    - mis/prompts/pain_synthesis_prompt.txt
  modified:
    - mis/tests/test_synthesizer.py
decisions:
  - "sqlite3 direct connection used for upsert instead of sqlite_utils.Database — sqlite_utils does not support context manager protocol in this version, leading to database locked errors"
  - "_signal_counter global used in test helper _make_signal to ensure unique url_hash per signal — loop with same title[:10] would collide on UNIQUE constraint"
metrics:
  duration: 14m
  tasks_completed: 1
  files_created: 2
  files_modified: 1
  tests_added: 5
  completed_date: "2026-03-15"
---

# Phase 04 Plan 04: Synthesizer LLM with Idempotent Pain Reports Summary

LLM synthesizer that consolidates raw market signals into hourly pain reports per niche — claude-sonnet-4-6 with ON CONFLICT upsert for idempotent re-execution.

## What Was Built

`mis/radar/synthesizer.py` — the final output layer of the Pain Radar pipeline. Takes raw signals from `pain_signals` table (collected by Reddit, Quora, YouTube, and Trends collectors), formats them into a structured prompt, calls the Anthropic LLM, and stores a JSON pain report in `pain_reports` with idempotency via `ON CONFLICT(niche_id, cycle_at)`.

`mis/prompts/pain_synthesis_prompt.txt` — pt-BR prompt template that instructs the LLM to identify the top 5 pains/desires from collected signals, each with a clear description, specific evidence (sources and engagement numbers), and an interest level classification (Alto/Médio/Baixo).

## Tasks Completed

| Task | Description | Commit | Files |
|------|-------------|--------|-------|
| 1 | Prompt + Synthesizer LLM with idempotency (TDD) | 7681219 | mis/radar/synthesizer.py, mis/prompts/pain_synthesis_prompt.txt, mis/tests/test_synthesizer.py |

## Tests (5/5 GREEN)

- `test_synthesize_returns_report_with_top_pains` — happy path: 5 signals -> LLM called -> dict with pains[] returned
- `test_no_signals_skip_llm_call` — no signals -> LLM never called, returns None, structlog alert emitted
- `test_report_idempotent_upsert` — same (niche_id, cycle_at) called twice -> COUNT(*) == 1
- `test_report_has_evidence_fields` — report has pains, niche, cycle_at, sources_used; DB row parseable as JSON
- `test_fetch_cycle_signals_returns_recent_only` — 1h ago signal returned, 25h ago signal excluded from 2h window

## Key Contracts

```python
# Fetch signals for a cycle window
signals = fetch_cycle_signals(db_path, niche_slug, cycle_start_iso)

# Synthesize to pain report (idempotent)
report = await synthesize_niche_pains(
    niche_id=1,
    niche_name="Emagrecimento",
    niche_slug="emagrecimento",
    cycle_at="2026-03-15T14:00:00",
    db_path=db_path,
)
# Returns dict with: pains[], niche, cycle_at, sources_used, cost_usd, signals_count
# Returns None if no signals in cycle window (no LLM call made)
```

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed UNIQUE constraint collision in test helper**
- **Found during:** Task 1 (GREEN phase)
- **Issue:** `_make_signal` helper used `title[:10]` in URL construction causing duplicate url_hash when inserting multiple signals with similar titles in a loop
- **Fix:** Added `_signal_counter` global to guarantee unique URL per signal insert
- **Files modified:** mis/tests/test_synthesizer.py
- **Commit:** 7681219

**2. [Rule 1 - Bug] Replaced sqlite_utils.Database context manager with sqlite3 direct connection**
- **Found during:** Task 1 (GREEN phase)
- **Issue:** `sqlite_utils.Database` does not support context manager protocol (`__exit__` missing) in the installed version — `with sqlite_utils.Database(db_path) as db:` raised `TypeError`
- **Fix:** Extracted `_upsert_report()` helper using `sqlite3.connect()` directly with explicit `conn.close()` in finally block
- **Files modified:** mis/radar/synthesizer.py
- **Commit:** 7681219

## Self-Check: PASSED

- mis/radar/synthesizer.py: FOUND
- mis/prompts/pain_synthesis_prompt.txt: FOUND
- mis/tests/test_synthesizer.py: FOUND
- Commit 7681219: FOUND
- 5 tests GREEN: VERIFIED
