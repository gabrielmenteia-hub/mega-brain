---
phase: 07-mis-integration-bugfixes
plan: "01"
subsystem: mis-bridge
requirements_completed: [INT-01, INT-02]
tags: [bugfix, mis, integration, tdd]
dependency_graph:
  requires: [06-megabrain-integration]
  provides: [mis-export-working, mis-health-score-correct, mis-scan-spy-pipeline]
  affects: [mis/mis_agent.py, mis/scheduler.py, mis/tests/]
tech_stack:
  added: []
  patterns: [tdd-red-green, surgical-string-fix, mock-patching]
key_files:
  created:
    - mis/tests/test_scan_and_spy_job.py
  modified:
    - mis/mis_agent.py
    - mis/scheduler.py
    - mis/tests/test_mis_agent.py
    - mis/tests/test_spy_orchestrator.py
decisions:
  - "test_health_with_dossier_today mocks run_canary_check to avoid network timeout — health score test must be deterministic"
  - "BUG-03 fix adds get_db + save_batch_with_alerts imports at module level in scheduler.py — avoids repeated lazy imports per job run"
  - "Existing test_spy_orchestrator.py tests updated to mock new scheduler deps — correct fix, not regression"
metrics:
  duration: 12m
  completed: "2026-03-15"
  tasks_completed: 3
  files_modified: 4
  files_created: 1
---

# Phase 07 Plan 01: MIS Integration Bugfixes Summary

**One-liner:** Three surgical string/call fixes restore export_to_megabrain (status='done'), health score accuracy (generated_at), and scan→spy pipeline (save_batch_with_alerts before spy loop).

## What Was Fixed

### BUG-01: export_to_megabrain() exported 0 dossiers silently

**Root cause:** SQL query filtered `WHERE d.status = 'complete'` but dossiers table uses `status = 'done'`.

**Fix:** Changed string literal `'complete'` to `'done'` in export SQL query in `mis/mis_agent.py:308`.

**Verification:** `test_incremental_export` now asserts `exported > 0` and passes GREEN.

### BUG-02: get_briefing_data() computed incorrect health score

**Root cause:** Two queries used `created_at` column (added in migration _005) instead of `generated_at` (original column from migration _001). When dossiers were seeded with `generated_at` only, `created_at` was NULL — causing `last_cycle = None` and `dossiers_today = False`.

**Fix (3 changes in mis/mis_agent.py):**
- `SELECT MAX(generated_at) FROM dossiers` for `last_cycle` (line 149)
- `WHERE generated_at >= ?` for `dossiers_today` count (line 229)
- `_render_dossier_markdown`: `row.get("generated_at") or row.get("created_at")` fallback (line 446)
- Added `d.generated_at` to export SQL SELECT for rendering

**Verification:** `test_health_with_dossier_today` asserts `last_cycle is not None` and `dossiers_today is True` — passes GREEN.

### BUG-03: _scan_and_spy_job() never persisted products — all spy attempts skipped

**Root cause:** `_scan_and_spy_job()` called `run_all_scanners()` but never called `save_batch_with_alerts()`. Products had no DB IDs (`product.id` attribute didn't exist on the dataclass), so every product was skipped with a warning. The spy pipeline never ran.

**Fix (mis/scheduler.py):**
- Added imports: `import os`, `from .db import get_db`, `from .scanner import save_batch_with_alerts`
- After `run_all_scanners()`: opens DB with `get_db(db_path)`, calls `save_batch_with_alerts(db, db_path, platform_products)` per platform
- Resolves real DB IDs via `SELECT id FROM products WHERE platform_id=? AND external_id=?` after save
- Products with no DB ID are skipped with warning log (same behavior, but now only genuinely missing products)

**Verification:** `test_scan_and_spy_saves_products` and `test_scan_and_spy_triggers_spy_pipeline` pass GREEN.

## Test Results

```
148 passed, 0 failed
```

New tests added:
- `test_mis_agent.py::test_health_with_dossier_today` — new
- `test_scan_and_spy_job.py::test_scan_and_spy_saves_products` — new
- `test_scan_and_spy_job.py::test_scan_and_spy_triggers_spy_pipeline` — new

Existing tests updated:
- `test_mis_agent.py::_seed_db` — seed fixed to use `status='done'` and `generated_at` column
- `test_mis_agent.py::test_incremental_export` — assertion changed from `>= 0` to `> 0`
- `test_spy_orchestrator.py::test_scheduler_calls_run_spy_batch_after_scanners` — added mock for `save_batch_with_alerts` and `get_db`
- `test_spy_orchestrator.py::test_scheduler_triggers_spy_batch` — added mock for `save_batch_with_alerts` and `get_db`

## Commits

| Hash | Task | Description |
|------|------|-------------|
| f186161 | Task 1 (TDD RED) | Add failing tests for BUG-01/02/03 — seed fixed, new health/scheduler tests |
| c1c620d | Task 2 (TDD GREEN) | Fix BUG-01 and BUG-02 in mis_agent.py — status and generated_at queries |
| 8436464 | Task 3 (TDD GREEN) | Fix BUG-03 in scheduler.py — save_batch_with_alerts before spy loop |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] test_health_with_dossier_today: run_canary_check network timeout**
- **Found during:** Task 1 (RED phase)
- **Issue:** First version of the test called `get_briefing_data()` without mocking `run_canary_check()`, causing a network call that timed out in test environment
- **Fix:** Added `patch("mis.health_monitor.run_canary_check", new=AsyncMock(return_value=False))` in the test
- **Files modified:** `mis/tests/test_mis_agent.py`
- **Commit:** f186161

**2. [Rule 1 - Bug] test_spy_orchestrator.py: existing tests broke after BUG-03 fix**
- **Found during:** Task 3 full suite run
- **Issue:** `test_scheduler_calls_run_spy_batch_after_scanners` and `test_scheduler_triggers_spy_batch` only mocked `run_all_scanners` + `run_spy_batch`. After BUG-03 fix added `save_batch_with_alerts()` + `get_db()` calls, those tests hit `sqlite3.OperationalError: no such table: products` on the `:memory:` DB.
- **Fix:** Added `patch("mis.scheduler.save_batch_with_alerts")` and `patch("mis.scheduler.get_db", return_value=mock_db)` to both tests
- **Files modified:** `mis/tests/test_spy_orchestrator.py`
- **Commit:** 8436464

## Self-Check: PASSED

| Check | Result |
|-------|--------|
| mis/mis_agent.py | FOUND |
| mis/scheduler.py | FOUND |
| mis/tests/test_mis_agent.py | FOUND |
| mis/tests/test_scan_and_spy_job.py | FOUND |
| 07-01-SUMMARY.md | FOUND |
| Commit f186161 | FOUND |
| Commit c1c620d | FOUND |
| Commit 8436464 | FOUND |
| Full test suite (148 tests) | 148 passed, 0 failed |
