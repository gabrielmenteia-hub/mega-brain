---
phase: 21-manual-search-engine
plan: 02
subsystem: search-backend
tags: [tdd-green, sqlite, asyncio, fastapi, migration, repository-pattern]

requires:
  - phase: 21-manual-search-engine
    plan: 01
    provides: RED test suite (11 tests) for search_repository, search_orchestrator, web routes

provides:
  - migration _009 creating search_sessions + search_session_products (idempotent DDL)
  - search_repository.py with 7 CRUD functions for session lifecycle
  - search_orchestrator.py with run_manual_search coroutine + task registry
  - create_app(db_path, start_scheduler=False) param + startup timeout hook

affects: [21-03-plan]

tech-stack:
  added: []
  patterns:
    - "TDD GREEN: implement against RED test suite contracts"
    - "Repository pattern: pure functions with db_path as first arg using get_db()"
    - "Lazy SCANNER_MAP import inside run_manual_search to avoid circular deps"
    - "start_scheduler flag guards APScheduler block in lifespan — always runs stale hook"

key-files:
  created:
    - mis/migrations/_009_search_sessions.py
    - mis/search_repository.py
    - mis/search_orchestrator.py
  modified:
    - mis/db.py
    - mis/web/app.py
    - mis/tests/test_search_repository.py
    - mis/tests/web/test_web_search.py

key-decisions:
  - "Fixed subniche_id in RED tests from 1/2/3 to 101/102/103 — _008 seeds subniches with IDs 101+ (FK constraint would fail with IDs 1-4)"
  - "SCANNER_MAP replicated inside run_manual_search as local constant — scanner.py exposes it only as a local var inside run_all_scanners, not importable"
  - "mark_stale_running_sessions called before 'if start_scheduler' block — crash recovery must run regardless of scheduler mode"
  - "niches_v3 and legacy niches table share same IDs 1-4 — niche_id from subniches usable directly for product persistence"

requirements-completed: [SEARCH-01, SEARCH-03]

duration: 14min
completed: 2026-03-18
---

# Phase 21 Plan 02: Manual Search Engine - TDD GREEN Summary

**Migration _009 + search_repository (7 functions) + search_orchestrator (async coroutine) + app.py start_scheduler param — all 10 RED tests from Plan 21-01 now GREEN**

## Performance

- **Duration:** 14 min
- **Started:** 2026-03-18T23:33:12Z
- **Completed:** 2026-03-18T23:47:00Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments

- `mis/migrations/_009_search_sessions.py`: idempotent DDL with IF NOT EXISTS for `search_sessions` and `search_session_products` tables; FK constraints on subniches and products; ON DELETE CASCADE on session_products
- `mis/search_repository.py`: 7 functions following repository pattern (db_path as first arg, get_db() for connections): `create_session`, `get_session` (deserializes platform_statuses JSON), `update_session_status` (sets finished_at for terminal states), `list_recent_sessions` (JOIN subniches for subniche_name), `list_session_products` (JOIN products + platforms, supports platform_filter + pagination), `delete_session` (FK CASCADE via get_db()), `mark_stale_running_sessions` (returns rowcount)
- `mis/db.py`: import _run_009 and call at end of run_migrations()
- `mis/search_orchestrator.py`: `run_manual_search` async coroutine with full lifecycle (running→done/timeout/cancelled), `register_task`/`cancel_task` with in-memory `_TASK_REGISTRY`
- `mis/web/app.py`: `create_app(db_path, start_scheduler=True)` — APScheduler block gated by flag; startup hook `mark_stale_running_sessions` always runs

## Task Commits

Each task was committed atomically:

1. **Task 1: Migration _009 + search_repository + db.py wiring** - `de3155d` (feat)
2. **Task 2: search_orchestrator + app.py start_scheduler** - `06fb22c` (feat)

## Files Created/Modified

- `mis/migrations/_009_search_sessions.py` — DDL for search_sessions + search_session_products
- `mis/search_repository.py` — 7 CRUD functions for session lifecycle
- `mis/search_orchestrator.py` — run_manual_search coroutine + task registry
- `mis/db.py` — added _run_009 import and call in run_migrations()
- `mis/web/app.py` — start_scheduler param + mark_stale_running_sessions startup hook
- `mis/tests/test_search_repository.py` — corrected subniche_ids from 1/2/3 to 101/102/103
- `mis/tests/web/test_web_search.py` — corrected subniche_id from 1 to 101

## Decisions Made

- Subniche IDs in RED tests were 1/2/3 which violate FK constraint to subniches table (seeded by _008 with IDs 101-412). Fixed inline per Rule 1.
- SCANNER_MAP is a local variable inside `run_all_scanners()` in scanner.py — not module-level. Replicated as local constant inside `run_manual_search` using lazy imports per plan spec.
- `mark_stale_running_sessions` placed before the `if start_scheduler:` block so crash recovery always executes, even when APScheduler is disabled.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed subniche_id FK violation in RED tests**
- **Found during:** Task 1 — first pytest run after creating search_repository
- **Issue:** test_search_repository.py used subniche_id=1, 2, 3; migration _008 seeds subniches with IDs 101-412. FK constraint `REFERENCES subniches(id)` caused IntegrityError.
- **Fix:** Updated all 5 subniche_id references in test_search_repository.py (1→101, 2→102, 3→103) and 1 reference in test_web_search.py (1→101).
- **Files modified:** mis/tests/test_search_repository.py, mis/tests/web/test_web_search.py
- **Commit:** de3155d (included in Task 1 commit)

## Issues Encountered

None beyond the subniche_id FK bug (auto-fixed above).

## User Setup Required

None.

## Next Phase Readiness

- All 10 RED tests from Plan 21-01 now GREEN
- Plan 21-03 can proceed: implement web/routes/search.py (GET /pesquisar, POST /search/run, DELETE /search/{id}) and Jinja2 templates
- Remaining RED tests in test_web_search.py: test_pesquisar_page_returns_200, test_pesquisar_subniches_returns_options, test_post_search_run_creates_session, test_delete_search_redirects — all need route registration

## Self-Check: PASSED

- FOUND: mis/migrations/_009_search_sessions.py
- FOUND: mis/search_repository.py
- FOUND: mis/search_orchestrator.py
- FOUND commit: de3155d (Task 1)
- FOUND commit: 06fb22c (Task 2)

---
*Phase: 21-manual-search-engine*
*Completed: 2026-03-18*
