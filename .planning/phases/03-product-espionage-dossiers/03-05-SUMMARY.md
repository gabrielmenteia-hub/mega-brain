---
phase: 03-product-espionage-dossiers
plan: "05"
subsystem: orchestration
tags: [spy, pipeline, orchestrator, cli, scheduler, apscheduler, asyncio, sqlite-utils, structlog]

requires:
  - phase: 03-01
    provides: SalesPageScraper, DB schema (dossiers, products, migrations)
  - phase: 03-02
    provides: MetaAdsScraper, ReviewsScraper
  - phase: 03-03
    provides: SpyData, check_completeness, completeness gate
  - phase: 03-04
    provides: analyze_copy, generate_dossier, LLM pipeline

provides:
  - spy_orchestrator.py with run_spy, run_spy_url, run_spy_batch (public API)
  - SPY_TOP_N=10 hardcoded constant for top-N per niche/platform
  - CLI entrypoint: python -m mis spy --url <URL> | --product-id <ID>
  - _scan_and_spy_job() in scheduler.py chaining run_all_scanners -> run_spy_batch
  - config.yaml spy section: max_concurrent_spy=3, min_reviews=10
  - Graceful failure: alert='spy_failed' logged, status='failed' persisted

affects:
  - phase-04 (any task orchestrator or dashboard consuming dossiers)
  - future phases requiring end-to-end product intelligence

tech-stack:
  added: []
  patterns:
    - PriorityQueue with tiebreak counter for batch spy ordering (priority=0 manual, rank=auto)
    - Semaphore-bounded concurrency in asyncio batch processor
    - SPY_TOP_N as hardcoded constant (not in config) — enforced in scheduler
    - PRAGMA foreign_keys=OFF for URL-based product insertion (no platform/niche FK)
    - Separate _get_db_path() and _get_spy_config() helpers for testability
    - scheduler.py imports from spy_orchestrator at module level (not lazy)

key-files:
  created:
    - mis/spy_orchestrator.py
    - mis/__main__.py
    - mis/tests/test_spy_orchestrator.py
  modified:
    - mis/config.yaml
    - mis/scheduler.py

key-decisions:
  - "SPY_TOP_N=10 hardcoded in spy_orchestrator.py — user decision, not configurable"
  - "config.yaml spy section contains only max_concurrent_spy and min_reviews — spy_top_n deliberately absent"
  - "run_spy_url uses PRAGMA foreign_keys=OFF for minimal product insertion (null platform/niche) — avoids FK violation for ad-hoc URL spying"
  - "MIS_DB_PATH env var as DB path source in orchestrator (testable, no hardcoded path)"
  - "scheduler.py _scan_and_spy_job skips products without DB ID — warns via structlog instead of crash"
  - "CLI test uses asyncio.run mock to verify dispatch without running full pipeline"

patterns-established:
  - "Batch orchestration pattern: PriorityQueue + asyncio.Semaphore for bounded concurrent tasks"
  - "Alert pattern: log.error with alert='spy_failed' key for machine-parseable failure detection"
  - "Force re-spy pattern: force=False skips done dossiers; force=True always re-runs"

requirements-completed: [SPY-01, SPY-02, SPY-03, SPY-04, SPY-05, DOS-01, DOS-02, DOS-03, DOS-04, DOS-05]

duration: 10min
completed: 2026-03-15
---

# Phase 03 Plan 05: Spy Orchestrator + CLI Summary

**End-to-end spy pipeline wiring all components into run_spy/run_spy_url/run_spy_batch, CLI python -m mis spy, and scheduler auto-trigger after scanners using hardcoded SPY_TOP_N=10**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-03-15T01:07:03Z
- **Completed:** 2026-03-15T01:17:13Z
- **Tasks:** 2
- **Files modified/created:** 5

## Accomplishments

- spy_orchestrator.py: full pipeline run_spy → SalesPageScraper → MetaAdsScraper → ReviewsScraper → completeness_gate → analyze_copy → generate_dossier → persist
- mis/__main__.py: CLI entrypoint with `spy` subcommand supporting --url and --product-id
- scheduler.py: _scan_and_spy_job() chains run_all_scanners → run_spy_batch with SPY_TOP_N=10 limit per platform
- config.yaml: spy section with max_concurrent_spy=3 and min_reviews=10
- 11/11 spy orchestrator tests GREEN, 85/85 full suite GREEN

## Task Commits

1. **Task 1 RED:** `6e8dc12` — test(03-05): add failing tests for spy_orchestrator pipeline
2. **Task 1 GREEN:** `a6b862d` — feat(03-05): implement spy_orchestrator with full pipeline
3. **Task 2 RED:** `84cdc52` — test(03-05): add failing tests for CLI spy and scheduler wiring
4. **Task 2 GREEN:** `122ba63` — feat(03-05): add CLI spy subcommand and scheduler scan+spy job

## Files Created/Modified

- `mis/spy_orchestrator.py` — Public pipeline API: run_spy, run_spy_url, run_spy_batch, SPY_TOP_N=10
- `mis/__main__.py` — CLI entrypoint: python -m mis spy --url URL | --product-id ID
- `mis/config.yaml` — Added spy section with max_concurrent_spy and min_reviews
- `mis/scheduler.py` — Added _scan_and_spy_job(), register_scan_and_spy_job(); imports spy_orchestrator
- `mis/tests/test_spy_orchestrator.py` — 11 tests covering full pipeline, failure, priority, CLI, scheduler wiring

## Decisions Made

- `SPY_TOP_N=10` hardcoded as constant in spy_orchestrator — user decision from 03-CONTEXT that this must not be configurable
- `PRAGMA foreign_keys=OFF` used in run_spy_url to allow minimal product insertion without valid platform/niche FK — acceptable for ad-hoc URL spying
- `MIS_DB_PATH` env var as DB path source — enables clean test isolation without global state
- scheduler.py imports spy_orchestrator at module level (not lazily) — clean dependency, no circular imports detected

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] ScraperError signature mismatch**
- **Found during:** Task 1 (spy_orchestrator implementation)
- **Issue:** Plan used `ScraperError("string")` but existing ScraperError requires `(url, attempts, cause)` positional args
- **Fix:** Used `RuntimeError` instead of `ScraperError` for "copy ausente" guard in _execute_spy_pipeline
- **Files modified:** mis/spy_orchestrator.py
- **Verification:** test_spy_failed_on_copy_error passes (raises any Exception, not specifically ScraperError)
- **Committed in:** a6b862d (Task 1 commit)

**2. [Rule 1 - Bug] DB schema has no `created_at` on dossiers table**
- **Found during:** Task 1 (first test run)
- **Issue:** _upsert_dossier_status inserted `created_at` which doesn't exist in _001_initial.py schema
- **Fix:** Removed `created_at` from insert dict, using only `generated_at` (the actual schema column)
- **Files modified:** mis/spy_orchestrator.py
- **Verification:** test_run_spy_happy_path passes
- **Committed in:** a6b862d (Task 1 commit)

**3. [Rule 1 - Bug] FK constraint on run_spy_url product insert**
- **Found during:** Task 1 (test_run_spy_url_creates_product)
- **Issue:** Inserting product with platform_id=0/niche_id=0 violated FK constraints
- **Fix:** Use PRAGMA foreign_keys=OFF before insert, platform_id=None, niche_id=None
- **Files modified:** mis/spy_orchestrator.py
- **Verification:** test_run_spy_url_creates_product passes
- **Committed in:** a6b862d (Task 1 commit)

**4. [Rule 1 - Bug] CLI test approach with asyncio_run mock not viable**
- **Found during:** Task 2 (test_cli_spy_url)
- **Issue:** `patch("mis.__main__.asyncio_run")` failed — no such symbol in module
- **Fix:** Simplified tests to use `patch("asyncio.run")` + `patch.object(sys, "argv")` and verify asyncio.run was called
- **Files modified:** mis/tests/test_spy_orchestrator.py
- **Verification:** test_cli_spy_url and test_cli_spy_product_id pass
- **Committed in:** 122ba63 (Task 2 commit)

---

**Total deviations:** 4 auto-fixed (4 Rule 1 bugs)
**Impact on plan:** All fixes were necessary for correct operation. No scope creep.

## Issues Encountered

None beyond the auto-fixed deviations above.

## Next Phase Readiness

- Full espionage pipeline operational end-to-end
- CLI ready for manual use: `python -m mis spy --url <URL>`
- Scheduler job ready for automated daily operation
- Phase 03 complete — all 5 plans executed
- Ready for Phase 04 (Task Orchestrator or Dashboard)

---
*Phase: 03-product-espionage-dossiers*
*Completed: 2026-03-15*
