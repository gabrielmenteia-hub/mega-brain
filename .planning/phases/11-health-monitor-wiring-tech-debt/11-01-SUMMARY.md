---
phase: 11-health-monitor-wiring-tech-debt
plan: 01
subsystem: health-monitoring
tags: [apscheduler, fastapi, lifespan, playwright, asyncio, datetime, mis]

# Dependency graph
requires:
  - phase: 08-foundation-verification
    provides: run_schema_integrity_check() and run_platform_canary() in health_monitor.py
  - phase: 09-production-wiring-proxy-fix
    provides: lifespan wiring pattern, register_canary_job in lifespan for-loop

provides:
  - register_platform_canary_jobs(db_path) — 3 APScheduler canary jobs (hotmart/clickbank/kiwify) at 25h interval
  - lifespan calls await run_schema_integrity_check(db_path) before job registrations (soft-fail)
  - fetch_spa() uses _select_proxy() for proxy rotation (equal to httpx fetch())
  - _compute_health() as async def with await run_canary_check() — no nested asyncio.run
  - Dead code removed: register_scanner_jobs(), run_hotmart_scan, run_clickbank_scan, run_kiwify_scan
  - datetime.utcnow() replaced by datetime.now(timezone.utc) across 7 MIS files

affects: [future health monitoring, platform canary jobs, scheduler jobs, proxy rotation for SPA scraping]

# Tech tracking
tech-stack:
  added: [playwright==1.58.0, playwright-stealth==2.0.2 (updated API: Stealth.apply_stealth_async)]
  patterns:
    - Soft-fail observability in lifespan — await check, log warning, continue startup
    - Platform canary jobs use interval=25h with replace_existing=True
    - _compute_health is async def, callers use one asyncio.run() at the boundary

key-files:
  created:
    - mis/tests/test_lifespan.py (updated with 2 new tests)
    - mis/tests/test_base_scraper.py (new test: test_fetch_spa_uses_select_proxy_not_self_proxy)
    - mis/tests/test_mis_agent.py (new test: test_compute_health_is_async_safe)
  modified:
    - mis/health_monitor.py — added register_platform_canary_jobs()
    - mis/web/app.py — lifespan wired with schema check + platform canary jobs
    - mis/base_scraper.py — fetch_spa uses _select_proxy(); playwright imports at module level; stealth API updated
    - mis/mis_agent.py — _compute_health converted to async def
    - mis/scheduler.py — docstring updated; register_scanner_jobs() removed
    - mis/scanners/hotmart.py — run_hotmart_scan() removed
    - mis/scanners/clickbank.py — run_clickbank_scan() removed
    - mis/scanners/kiwify.py — run_kiwify_scan() removed
    - mis/intelligence/dossier_generator.py — utcnow fix
    - mis/radar/quora_collector.py — utcnow fix
    - mis/radar/reddit_collector.py — utcnow fix
    - mis/radar/synthesizer.py — utcnow fix
    - mis/radar/trends_collector.py — utcnow fix
    - mis/radar/youtube_collector.py — utcnow fix (3 usages)
    - mis/radar/__init__.py — utcnow fix

key-decisions:
  - "register_platform_canary_jobs uses lazy import of get_scheduler (same pattern as register_canary_job)"
  - "stealth_async (playwright_stealth 1.x) replaced with Stealth().apply_stealth_async() — new 2.x API"
  - "async_playwright and Stealth imported at module level in base_scraper to enable test patching"
  - "test_scanner_jobs.py deleted entirely — tests 1 and 2 tested removed code; tests 3 and 4 (run_platform_canary, run_all_scanners) remain covered elsewhere"

patterns-established:
  - "Soft-fail lifespan observability: try/except around await check, log warning on fail"
  - "Async health compute with single asyncio.run() at sync/async boundary"

requirements-completed: [FOUND-02, FOUND-04]

# Metrics
duration: 24min
completed: 2026-03-16
---

# Phase 11 Plan 01: Health Monitor Wiring & Tech Debt Summary

**Health observability gaps closed — schema integrity + platform canary jobs wired into production lifespan, fetch_spa proxy rotation fixed, async _compute_health corrected, and 178 lines of dead code + 9 datetime.utcnow() usages removed**

## Performance

- **Duration:** ~24 min
- **Started:** 2026-03-16T06:56:46Z
- **Completed:** 2026-03-16T07:20:46Z
- **Tasks:** 3
- **Files modified:** 15

## Accomplishments
- Wired run_schema_integrity_check() and register_platform_canary_jobs() into the FastAPI lifespan — health monitoring now runs in production
- Fixed fetch_spa() proxy rotation bug: was using self._proxy (always None when proxy_list set) instead of _select_proxy()
- Fixed nested asyncio.run() bug in _compute_health() by converting it to async def with await
- Removed 178 lines of dead code (register_scanner_jobs + 3 run_*_scan helpers) and updated docstring
- Replaced datetime.utcnow() with datetime.now(timezone.utc) across all 7 affected MIS files

## Task Commits

Each task was committed atomically:

1. **Task 1: Wire observability into production (lifespan + APScheduler)** - `cce81f0` (feat)
2. **Task 2: Fix latent bugs (fetch_spa proxy + _compute_health async)** - `facb361` (fix)
3. **Task 3: Remove dead code and replace deprecated datetime** - `d42518d` (chore)

## Files Created/Modified
- `mis/health_monitor.py` — added register_platform_canary_jobs() function
- `mis/web/app.py` — lifespan updated: await schema check before jobs, platform canary in for-loop
- `mis/tests/test_lifespan.py` — updated existing test + new test_register_platform_canary_jobs_registers_3_jobs
- `mis/base_scraper.py` — fetch_spa uses _select_proxy(); playwright imports moved to module level; stealth API updated to 2.x
- `mis/tests/test_base_scraper.py` — new test_fetch_spa_uses_select_proxy_not_self_proxy
- `mis/mis_agent.py` — _compute_health() is now async def; get_briefing_data() uses asyncio.run(_compute_health(...))
- `mis/tests/test_mis_agent.py` — new test_compute_health_is_async_safe
- `mis/scheduler.py` — register_scanner_jobs() removed; docstring updated
- `mis/scanners/hotmart.py` — run_hotmart_scan() removed
- `mis/scanners/clickbank.py` — run_clickbank_scan() removed
- `mis/scanners/kiwify.py` — run_kiwify_scan() removed
- `mis/tests/test_scanner_jobs.py` — deleted (tested removed code)
- `mis/intelligence/dossier_generator.py` — utcnow fix + timezone import
- `mis/radar/quora_collector.py` — utcnow fix + timezone import
- `mis/radar/reddit_collector.py` — utcnow fix (timezone already imported)
- `mis/radar/synthesizer.py` — utcnow fix + timezone import
- `mis/radar/trends_collector.py` — utcnow fix + timezone import
- `mis/radar/youtube_collector.py` — utcnow fix (3 usages) + timezone import
- `mis/radar/__init__.py` — utcnow fix (timezone already imported)

## Decisions Made
- playwright_stealth 1.x exported `stealth_async(page)` (function); 2.x uses `Stealth().apply_stealth_async(page)` — updated accordingly during Task 2 execution
- async_playwright and _PlaywrightStealth moved to module-level imports in base_scraper.py to enable test patching via `mis.base_scraper.X` patch paths
- test_scanner_jobs.py deleted in full per plan — 2 of 4 tests referenced removed code; the remaining 2 (platform canary, run_all_scanners) remain covered by other test files

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] playwright and playwright-stealth not installed**
- **Found during:** Task 2 (fetch_spa proxy fix implementation)
- **Issue:** `from playwright.async_api import async_playwright` failed with ModuleNotFoundError
- **Fix:** `pip install playwright playwright-stealth`
- **Files modified:** None (environment only)
- **Verification:** Import succeeded, tests passed
- **Committed in:** facb361 (Task 2 commit)

**2. [Rule 1 - Bug] playwright_stealth 2.x broke stealth_async import**
- **Found during:** Task 2 after installing playwright_stealth 2.0.2
- **Issue:** `from playwright_stealth import stealth_async` fails — 2.x removed the function; new API is `Stealth().apply_stealth_async(page)`
- **Fix:** Changed base_scraper.py to import `Stealth as _PlaywrightStealth` and call `_PlaywrightStealth().apply_stealth_async(page)`; also moved imports to module-level for test patching
- **Files modified:** mis/base_scraper.py
- **Verification:** test_fetch_spa_uses_select_proxy_not_self_proxy passes; all 14 base_scraper tests pass
- **Committed in:** facb361 (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (1 blocking install, 1 API version bug)
**Impact on plan:** Both fixes necessary for tests to run. No scope creep.

## Issues Encountered
- `test_cli_spy_help` in test_spy_orchestrator.py was already failing before this phase (pre-existing: test runs `python -m mis spy --help` from wrong directory). Confirmed pre-existing by git stash verification. Deselected from final verification; not caused by this plan's changes.

## Next Phase Readiness
- All FOUND-02 and FOUND-04 requirements closed
- Health monitoring fully wired in production code path
- 161 tests green (1 pre-existing failure in test_spy_orchestrator.py excluded)

---
*Phase: 11-health-monitor-wiring-tech-debt*
*Completed: 2026-03-16*
