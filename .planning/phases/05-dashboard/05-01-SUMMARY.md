---
phase: 05-dashboard
plan: "01"
subsystem: testing
tags: [pytest, fastapi, tdd, wave-0, test-scaffold, red-phase]

# Dependency graph
requires:
  - phase: 04-pain-radar
    provides: pain_reports table + run_migrations() chaining all 4 migrations
  - phase: 03-product-espionage-dossiers
    provides: dossiers table + product_repository pattern
provides:
  - 21 RED tests in mis/tests/web/ defining contracts for all 5 dashboard requirements
  - conftest.py with deferred create_app import + db_path/app_client fixtures
  - test_alert_repository.py (4 tests), test_dossier_repository.py (2), test_pain_repository.py (2)
  - test_web_ranking.py (5), test_web_dossier.py (3), test_web_feed.py (2), test_web_alerts.py (3)
affects: [05-02-web-layer, 05-03-repositories, 05-04-alerts, 05-05-integration]

# Tech tracking
tech-stack:
  added: [fastapi[standard], uvicorn, jinja2, aiofiles]
  patterns: [wave-0-tdd-scaffold, deferred-import-red-pattern, fixture-lazy-import]

key-files:
  created:
    - mis/tests/web/__init__.py
    - mis/tests/web/conftest.py
    - mis/tests/web/test_alert_repository.py
    - mis/tests/web/test_dossier_repository.py
    - mis/tests/web/test_pain_repository.py
    - mis/tests/web/test_web_ranking.py
    - mis/tests/web/test_web_dossier.py
    - mis/tests/web/test_web_feed.py
    - mis/tests/web/test_web_alerts.py
  modified: []

key-decisions:
  - "Deferred imports inside test functions (not module level) for repository tests — allows pytest collection even before modules exist, while still failing RED at runtime"
  - "Deferred create_app import inside app_client fixture — conftest.py collectible without mis.web existing; only route tests that use app_client fail at setup"
  - "fastapi[standard] + uvicorn + jinja2 + aiofiles installed as web layer dependencies during Wave 0"

patterns-established:
  - "Wave 0 TDD: test files define contracts before any implementation exists"
  - "Deferred import pattern: imports inside function bodies for RED-but-collectible tests"
  - "conftest.py lazy fixture: create_app import deferred to fixture body, not module top"

requirements-completed: [DASH-01, DASH-02, DASH-03, DASH-04, SCAN-05]

# Metrics
duration: 12min
completed: 2026-03-15
---

# Phase 5 Plan 01: Dashboard Test Scaffold Summary

**21 RED test stubs across 9 files in mis/tests/web/ defining contracts for FastAPI dashboard routes and repository layers (DASH-01..DASH-04, SCAN-05)**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-03-15T00:00:00Z
- **Completed:** 2026-03-15T00:12:00Z
- **Tasks:** 2
- **Files modified:** 9 created

## Accomplishments
- Installed web stack dependencies (fastapi[standard], uvicorn, jinja2, aiofiles)
- Created mis/tests/web/ package with conftest.py using deferred fixture imports
- 8 repository contract tests (alert, dossier, pain repositories) — RED via ImportError at runtime
- 13 route contract tests (ranking, dossier, feed, alerts) — RED via ModuleNotFoundError at fixture setup
- 21 total tests collected by pytest, zero SyntaxErrors

## Task Commits

Each task was committed atomically:

1. **Task 1: conftest + repository stubs** - `15eb079` (test)
2. **Task 2: route stubs (ranking, dossier, feed, alerts)** - `7358da4` (test)

## Files Created/Modified
- `mis/tests/web/__init__.py` - package marker
- `mis/tests/web/conftest.py` - db_path + app_client fixtures with deferred create_app import
- `mis/tests/web/test_alert_repository.py` - 4 RED tests for create_alert, get_unseen_count, mark_seen, expire_old_alerts
- `mis/tests/web/test_dossier_repository.py` - 2 RED tests for get_dossier_by_product_id, list_dossiers_by_rank
- `mis/tests/web/test_pain_repository.py` - 2 RED tests for get_latest_report, get_historical_reports
- `mis/tests/web/test_web_ranking.py` - 5 RED tests for DASH-01/SCAN-05 routes
- `mis/tests/web/test_web_dossier.py` - 3 RED tests for DASH-02 dossier detail
- `mis/tests/web/test_web_feed.py` - 2 RED tests for DASH-03 pain feed
- `mis/tests/web/test_web_alerts.py` - 3 RED tests for DASH-04 alerts

## Decisions Made
- Deferred imports inside test function bodies for repository tests — module-level imports blocked collection with ImportError before pytest could even list test IDs; deferring enables collection while still failing RED at execution time
- create_app import deferred to app_client fixture body — conftest.py itself stays importable, only tests that USE the fixture fail at fixture setup (ModuleNotFoundError on mis.web)
- fastapi[standard] installed at Wave 0 — web layer needs TestClient from fastapi.testclient which is part of fastapi[standard]

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Moved repository test imports from module level to function body**
- **Found during:** Task 1 (repository test stubs)
- **Issue:** Module-level imports of mis.alert_repository/mis.dossier_repository/mis.pain_repository caused ImportError during collection, preventing pytest from listing the 8 test IDs — criteria required 21 tests "collected"
- **Fix:** Moved all repository module imports inside each test function body; conftest.py create_app import moved inside app_client fixture
- **Files modified:** test_alert_repository.py, test_dossier_repository.py, test_pain_repository.py, conftest.py
- **Verification:** `pytest tests/web/ --co -q` shows 21 tests collected in 0.50s
- **Committed in:** 15eb079 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 — import collection bug)
**Impact on plan:** Fix was necessary to meet the "21 tests collected" success criteria. No scope creep — RED behavior preserved at runtime.

## Issues Encountered
- Plan specified "import at module level to enforce ImportError as RED failure mode" (Phase 04-01 decision), but this conflicts with the success criterion "21+ tests collected". Resolved by using deferred imports inside function bodies — tests still fail RED at execution (ImportError), but pytest can list them during collection phase.

## Next Phase Readiness
- All 21 test contracts defined and RED — ready for 05-02 to implement FastAPI app, repositories (dossier, pain), and migrations _005 (alerts table)
- conftest.py wired correctly with `create_app(db_path=...)` signature
- Repository test fixture uses `db_path` from parent conftest (mis/tests/conftest.py) as intended

---
*Phase: 05-dashboard*
*Completed: 2026-03-15*
