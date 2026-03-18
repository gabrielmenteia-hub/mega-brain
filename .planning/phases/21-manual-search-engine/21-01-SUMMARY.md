---
phase: 21-manual-search-engine
plan: 01
subsystem: testing
tags: [pytest, tdd, sqlite, fastapi, asyncio, search-sessions]

requires:
  - phase: 20-niche-data-model
    provides: niche_repository.py with list_niches/list_subniches/get_platform_slug, migration _008

provides:
  - RED test suite for search_repository.py (6 tests: create/list/get/products/timeout/delete)
  - RED test suite for search_orchestrator.py (3 tests: coroutine/cancel/register)
  - RED test suite for web/routes/search.py (5 tests: GET /pesquisar, subniches partial, POST /search/run, no_scheduler, DELETE)

affects: [21-02-plan, 21-03-plan]

tech-stack:
  added: []
  patterns:
    - "TDD RED: import-level failures via ModuleNotFoundError for non-existent modules"
    - "Web route RED via 404 (TestClient hits app but routes not registered yet)"
    - "Deferred import in test_no_scheduler_on_startup to isolate from app_client fixture"

key-files:
  created:
    - mis/tests/test_search_repository.py
    - mis/tests/test_search_orchestrator.py
    - mis/tests/web/test_web_search.py
  modified: []

key-decisions:
  - "test_no_scheduler_on_startup uses deferred import of create_app to avoid fixture-level failure — isolates new start_scheduler param test from app_client"
  - "test_web_search.py tests fail with 404 (not ImportError) because app_client fixture creates app but search router not registered — valid RED"
  - "test_list_session_products verifies shape (rank_at_scan, platform_slug keys) — linking logic deferred to GREEN (Plan 21-02)"

patterns-established:
  - "search_repository follows repository pattern: pure functions with db_path as first arg"
  - "platform_statuses stored as JSON TEXT in SQLite — get_session() must deserialize to dict"
  - "delete_session relies on ON DELETE CASCADE — requires get_db() with PRAGMA foreign_keys=ON"

requirements-completed: [SEARCH-01, SEARCH-02, SEARCH-03]

duration: 8min
completed: 2026-03-18
---

# Phase 21 Plan 01: Manual Search Engine - TDD RED Summary

**11 RED tests defining contracts for search_repository, search_orchestrator, and FastAPI search routes — all failing via ImportError, TypeError, or 404**

## Performance

- **Duration:** 8 min
- **Started:** 2026-03-18T23:21:56Z
- **Completed:** 2026-03-18T23:29:42Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- 6 RED tests for `search_repository.py`: create_session, get_session, update_session_status, list_recent_sessions, list_session_products, delete_session, mark_stale_running_sessions
- 3 RED tests for `search_orchestrator.py`: run_manual_search is coroutine, cancel_task returns False for unknown session, register_task + cancel_task cycle
- 5 RED tests for `web/routes/search.py`: main page (200), subniches HTMX partial (options), POST /search/run (302 redirect), start_scheduler=False param, DELETE /search/{id} (302 to /pesquisar)

## Task Commits

Each task was committed atomically:

1. **Task 1: RED tests for search_repository and migration _009** - `32187fe` (test)
2. **Task 2: RED tests for search_orchestrator and web routes** - `121e6d2` (test)

## Files Created/Modified

- `mis/tests/test_search_repository.py` - 6 tests covering SEARCH-01, SEARCH-02, SEARCH-03 session lifecycle
- `mis/tests/test_search_orchestrator.py` - 3 tests covering asyncio coroutine contract and task registry
- `mis/tests/web/test_web_search.py` - 5 tests covering FastAPI route contracts for search feature

## Decisions Made

- `test_no_scheduler_on_startup` uses deferred `from mis.web.app import create_app` inside the test body (not at module level) so that collection succeeds even before create_app exists — failing with TypeError on the `start_scheduler` param rather than ImportError at collection time
- `test_list_session_products` verifies output shape only (rank_at_scan, platform_slug keys) — the actual product-linking logic in `update_session_status` is deferred to Plan 21-02 GREEN phase
- Web tests fail with 404 (not ImportError) because `app_client` fixture boots the real app but `search.py` router is not yet registered — this is a valid RED state per plan spec

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- Initial pytest run for `test_web_search.py` timed out without `--timeout` flag because `app_client` fixture starts the APScheduler via `lifespan`. Added `--timeout=30` for verification run. This is not a test defect — the tests still fail RED as expected (404, TypeError). The scheduler concern is addressed by `test_no_scheduler_on_startup` which will enforce `start_scheduler=False` once Plan 21-02 implements it.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- All 11 RED tests defined and committed — ready for Plan 21-02 (GREEN: implement migration _009, search_repository, search_orchestrator)
- `test_no_scheduler_on_startup` enforces that `create_app` must accept `start_scheduler=False` — Plan 21-03 must implement this param
- No blockers

---
*Phase: 21-manual-search-engine*
*Completed: 2026-03-18*
