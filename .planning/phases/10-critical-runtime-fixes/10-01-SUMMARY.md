---
phase: 10-critical-runtime-fixes
plan: 01
subsystem: database
tags: [sqlite3, apscheduler, asyncio, scanner, radar, niche_id, tdd]

requires:
  - phase: 09-production-wiring-proxy-fix
    provides: lifespan hook wiring APScheduler at startup, production-ready web server

provides:
  - run_all_scanners() with bulk niche_id lookup via sqlite3 before gather
  - 5 radar job wrappers converted from sync+asyncio.run() to async def+await
  - test_scanner_niche_id.py covering DEFECT-1 RED->GREEN
  - test_radar_async_jobs.py covering DEFECT-3 RED->GREEN

affects: [dashboard niche filter, radar job execution, mis.scanner, mis.radar]

tech-stack:
  added: []
  patterns:
    - "niche_id_map: bulk sqlite3 SELECT id, slug FROM niches before coroutine dispatch"
    - "async def job wrappers inside register_radar_jobs for AsyncIOScheduler compatibility"
    - "DB unavailable graceful fallback: try/except on sqlite3.connect with niche_id_map=None"

key-files:
  created:
    - mis/tests/test_scanner_niche_id.py
    - mis/tests/test_radar_async_jobs.py
  modified:
    - mis/scanner.py
    - mis/radar/__init__.py

key-decisions:
  - "niche_id_map lookup uses sqlite3 directly (not sqlite_utils) — consistent with existing pattern in radar/__init__.py"
  - "niche_id_map=None fallback when DB unavailable — preserves old behavior in test environments without MIS_DB_PATH"
  - "niche_id_map check runs BEFORE platform check — unknown slugs are skipped early with log.warning"
  - "asyncio.to_thread(_run_cleanup) for cleanup job — _run_cleanup is sync, must not block the event loop"
  - "DEFECT-3 test uses asyncio.iscoroutinefunction() to verify fix without needing a live scheduler dispatch"

patterns-established:
  - "Bulk lookup before gather: resolve DB IDs for all entities before asyncio.gather() to avoid per-item DB calls inside coroutines"
  - "Graceful DB fallback: wrap infrastructure lookups in try/except so test environments without MIS_DB_PATH do not fail"

requirements-completed: [SCAN-01, SCAN-02, SCAN-03, DASH-01, RADAR-01, RADAR-02, RADAR-03, RADAR-05, RADAR-06]

duration: 25min
completed: 2026-03-16
---

# Phase 10 Plan 01: Critical Runtime Fixes Summary

**sqlite3 bulk niche_id lookup injected post-gather in run_all_scanners(), and 5 radar job wrappers converted from sync+asyncio.run() to async def+await — eliminating niche_id=0 defect and AsyncIOScheduler RuntimeError**

## Performance

- **Duration:** 25 min
- **Started:** 2026-03-16T04:41:03Z
- **Completed:** 2026-03-16T05:06:00Z
- **Tasks:** 4 (0: RED scaffolds, 1: DEFECT-1 fix, 2: DEFECT-3 fix, 3: regression)
- **Files modified:** 4

## Accomplishments

- Fixed DEFECT-1: products saved by run_all_scanners() now have niche_id matching the niches table (not always 0), making the dashboard niche filter fully operational
- Fixed DEFECT-3: all 5 radar job wrappers are now async def — AsyncIOScheduler dispatches them via create_task() instead of run_in_executor(), eliminating RuntimeError in production
- Full suite 163/163 GREEN after both fixes, including pre-existing test_proxy_forwarding regression

## Task Commits

1. **Task 0: RED test scaffolds** - `a5c1795` (test)
2. **Task 1: Fix DEFECT-1** - `64eeb9f` (feat)
3. **Task 2: Fix DEFECT-3** - `3dec845` (feat)
4. **Task 3: Regression fix** - `db5f710` (fix)

**Plan metadata:** (docs commit — see below)

## Files Created/Modified

- `mis/scanner.py` - Added niche_id_map bulk lookup before asyncio.gather(), slug-not-in-db skip with log.warning, niche_id injection post-gather, graceful DB fallback when MIS_DB_PATH unavailable
- `mis/radar/__init__.py` - Converted 5 internal job wrappers (_trends_job, _reddit_quora_job, _youtube_job, _synthesizer_job, _cleanup_job) from sync def to async def
- `mis/tests/test_scanner_niche_id.py` - Created: 2 TDD tests for DEFECT-1 (test_niche_id_resolved_correctly, test_unknown_slug_skipped)
- `mis/tests/test_radar_async_jobs.py` - Created: 1 TDD test for DEFECT-3 (test_async_radar_jobs_no_runtime_error)

## Decisions Made

- Used `niche_id_map=None` as fallback sentinel (not empty dict) so test environments without `MIS_DB_PATH` still invoke scanners correctly — `niche_id_map is not None` guard distinguishes "DB available, slug not found" from "DB unavailable"
- Used `asyncio.to_thread(_run_cleanup, db_path)` for the cleanup job because `_run_cleanup` is sync — wrapping it in `await asyncio.to_thread()` prevents it from blocking the event loop while maintaining the async def contract
- DEFECT-3 test avoids starting scheduler; verifies `asyncio.iscoroutinefunction(job.func)` instead — more reliable for unit test isolation than actually dispatching jobs in a running loop

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] test_proxy_forwarding broke after DEFECT-1 fix**
- **Found during:** Task 3 (regression suite)
- **Issue:** `run_all_scanners()` now calls `sqlite3.connect(MIS_DB_PATH)` — the proxy forwarding test doesn't set `MIS_DB_PATH` so it got `OperationalError: unable to open database file`
- **Fix:** Wrapped the DB lookup in try/except; `niche_id_map=None` when DB unavailable; all `niche_id_map` checks gated on `niche_id_map is not None`
- **Files modified:** `mis/scanner.py`
- **Verification:** `test_proxy_forwarding` GREEN; `test_scanner_niche_id` still GREEN; 163/163 total
- **Committed in:** `db5f710` (Task 3 fix commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 — bug introduced by DEFECT-1 fix)
**Impact on plan:** Necessary correctness fix. No scope creep.

## Issues Encountered

None beyond the auto-fixed regression above.

## Next Phase Readiness

- Both critical defects closed — dashboard niche filter and radar jobs fully operational
- 9 requirements closed: SCAN-01, SCAN-02, SCAN-03, DASH-01, RADAR-01, RADAR-02, RADAR-03, RADAR-05, RADAR-06
- Suite 163/163 GREEN — no technical debt introduced

---
*Phase: 10-critical-runtime-fixes*
*Completed: 2026-03-16*
