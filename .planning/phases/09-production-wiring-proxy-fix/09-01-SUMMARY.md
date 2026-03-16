---
phase: 09-production-wiring-proxy-fix
plan: "01"
subsystem: mis
requirements_completed:
  - SCAN-04
  - FOUND-02
tags:
  - proxy-forwarding
  - lifespan
  - apscheduler
  - fastapi
  - wiring
dependency_graph:
  requires:
    - mis/base_scraper.py (proxy_list support — Phase 08)
    - mis/scheduler.py (register_scan_and_spy_job, get_scheduler)
    - mis/radar/__init__.py (register_radar_jobs)
    - mis/health_monitor.py (register_canary_job)
  provides:
    - PlatformScanner proxy_list forwarding chain
    - FastAPI lifespan hook with APScheduler startup
  affects:
    - mis/web/app.py (lifespan added)
    - mis/scanner.py (proxy_list accepted)
    - mis/scanners/hotmart.py, kiwify.py, clickbank.py (proxy_list forwarded)
tech_stack:
  added:
    - contextlib.asynccontextmanager (lifespan pattern)
  patterns:
    - TDD (RED → GREEN, 3 tasks)
    - Composition via PlatformScanner._base (proxy_list propagation)
    - Soft error logging in lifespan (warning, never hard fail)
key_files:
  created:
    - mis/tests/test_proxy_forwarding.py
    - mis/tests/test_lifespan.py
  modified:
    - mis/scanner.py
    - mis/scanners/hotmart.py
    - mis/scanners/kiwify.py
    - mis/scanners/clickbank.py
    - mis/web/app.py
decisions:
  - "Top-level imports preferred in app.py (no circular imports confirmed) — cleaner than lazy imports, enables mis.web.app.X patch paths in tests"
  - "register_scanner_jobs() NOT included in lifespan — would cause double-scan redundancy (locked decision from plan)"
  - "Config/register errors are soft-logged (warning) — server must never fail hard on scheduler setup"
metrics:
  duration_minutes: 14
  completed_date: "2026-03-16"
  tasks_completed: 3
  files_modified: 7
---

# Phase 09 Plan 01: Production Wiring & Proxy Fix Summary

**One-liner:** Wired APScheduler startup via FastAPI asynccontextmanager lifespan and propagated proxy_list through PlatformScanner -> BaseScraper chain — closing SCAN-04 and FOUND-02 gaps.

## What Was Built

### FOUND-02 — Proxy List Forwarding Fix

`PlatformScanner.__init__` previously only accepted `proxy_url`. The `run_all_scanners()` function was already passing `proxy_list=proxy_list` (line 206), but all three scanner subclasses rejected the kwarg with `TypeError` at runtime whenever `proxy_list` was non-empty in `config.yaml`.

Fix: added `proxy_list: Optional[list[str]] = None` to `PlatformScanner.__init__` and all three subclasses (`HotmartScanner`, `KiwifyScanner`, `ClickBankScanner`), forwarding the value via `super()` to `BaseScraper.__init__`, which already stores it in `self._proxy_list`.

### SCAN-04 — FastAPI Lifespan Hook

`create_app()` had no `lifespan` parameter — APScheduler never started when `python -m mis dashboard` ran. Jobs registered via `register_scan_and_spy_job`, `register_radar_jobs`, and `register_canary_job` never fired.

Fix: defined an `asynccontextmanager` lifespan closure inside `create_app()`. On startup it calls all three register functions with the loaded config and starts the scheduler. On teardown it calls `scheduler.shutdown(wait=False)`. Errors in any step are soft-logged as warnings — the server continues running.

## Test Results

| File | Tests | Status |
|------|-------|--------|
| mis/tests/test_proxy_forwarding.py | 5 | GREEN |
| mis/tests/test_lifespan.py | 3 | GREEN |
| **Total new** | **8** | **GREEN** |
| Full suite (mis/tests/) | 165 | GREEN (no regressions) |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed test_run_all_scanners config format**

- **Found during:** Task 2 (GREEN phase)
- **Issue:** Test used `"platforms": [{"name": "hotmart", "slug": "saude"}]` (list of dicts) but `run_all_scanners()` iterates `platforms.items()` (expects dict `{name: slug}`). Caused `AttributeError: 'list' object has no attribute 'items'`.
- **Fix:** Changed test config to `"platforms": {"hotmart": "saude"}` to match actual function contract.
- **Files modified:** mis/tests/test_proxy_forwarding.py
- **Commit:** eb4e0c1 (test file updated before final task commit)

**2. [Rule 3 - Blocking] Confirmed top-level imports before implementation**

- **Found during:** Task 3 planning
- **Issue:** Plan mentioned checking for circular imports before deciding on lazy vs top-level.
- **Fix:** Ran import smoke test first; confirmed no circular imports; used top-level imports in app.py for cleaner code and correct patch paths (`mis.web.app.X`).
- **Files modified:** None (decision only, test file already used correct paths)

## Self-Check

Files created:
- mis/tests/test_proxy_forwarding.py — FOUND
- mis/tests/test_lifespan.py — FOUND

Files modified:
- mis/scanner.py — FOUND
- mis/scanners/hotmart.py — FOUND
- mis/scanners/kiwify.py — FOUND
- mis/scanners/clickbank.py — FOUND
- mis/web/app.py — FOUND

Commits:
- eb4e0c1 — test(09-01): RED stubs
- 12db8be — feat(09-01): proxy forwarding fix
- fd73383 — feat(09-01): lifespan hook
