---
phase: 03-product-espionage-dossiers
plan: "01"
subsystem: database
tags: [sqlite-utils, anthropic, markdownify, migration, scraper, llm]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: BaseScraper with fetch()/fetch_spa(), get_db(), run_migrations(), ScraperError, structlog, tenacity patterns
  - phase: 02-platform-scanners
    provides: dossiers table (from _001_initial), products table with platform FK

provides:
  - migration _003: dossiers expanded + reviews + llm_calls tables
  - SalesPageScraper: platform-agnostic copy + offer extractor (SPY-01 + SPY-03)
  - sales_page_extractor.md: zero-shot pt-BR LLM system prompt for JSON extraction
  - TDD test suite: 10 tests, all passing with committed fixtures (no real API needed)

affects:
  - 03-02: MetaAdsScraper and ReviewsScraper depend on reviews/llm_calls tables from _003
  - 03-03: DossierGenerator depends on SalesPageScraper output dict schema
  - 03-04: SpyOrchestrator wires all spies including SalesPageScraper

# Tech tracking
tech-stack:
  added:
    - anthropic>=0.79.0 (AsyncAnthropic LLM client)
    - markdownify>=0.12.0 (HTML → Markdown conversion)
  patterns:
    - TDD RED→GREEN: tests written before implementation, committed separately per phase
    - LLM-as-universal-parser: no platform-specific selectors, LLM extracts structured JSON
    - idempotent migration with add_column() + IF NOT EXISTS guards
    - AsyncAnthropic with tenacity retry (stop_after_attempt(3), wait_exponential)
    - Fixtures committed to repo: HTML fixture + JSON mock LLM response → tests run without real API

key-files:
  created:
    - mis/migrations/_003_spy_dossiers.py
    - mis/spies/__init__.py
    - mis/spies/sales_page.py
    - mis/prompts/sales_page_extractor.md
    - mis/tests/test_migration_003.py
    - mis/tests/test_sales_page_spy.py
    - mis/tests/fixtures/sales_page/hotmart_sample.html
    - mis/tests/fixtures/llm_responses/sales_page_extract.json
  modified:
    - mis/migrations/__init__.py (export run_migration_003)
    - mis/db.py (chain _001→_002→_003 in run_migrations())
    - mis/tests/test_db.py (expect 7 tables instead of 5)
    - mis/requirements.txt (add anthropic, markdownify)

key-decisions:
  - "ads_json stored as TEXT column in dossiers (not separate table) for MVP — avoids schema complexity for unstructured Meta Ad Library JSON"
  - "db.py run_migrations() chains all three migrations — callers get full schema with one call, no ordering burden on consumer"
  - "SalesPageScraper uses markdownify (not html2text) — strips irrelevant tags (nav, footer, script) before LLM call"
  - "LLM client instantiated per call in _call_llm() — avoids stale event loop issues with AsyncAnthropic in async context manager tests"
  - "ScraperError requires (url, attempts, cause) signature — test fixture corrected to match real interface"

patterns-established:
  - "LLM fixture pattern: record JSON response manually once, commit, mock AsyncAnthropic in tests — zero API cost in CI"
  - "Spy pattern: class Spy(BaseScraper) — inherits HTTP/Playwright/retry/semaphore; implements extract() → dict"
  - "Migration pattern: check existing_cols before add_column(), check table_names() before create() — full idempotency"

requirements-completed: [SPY-01, SPY-03]

# Metrics
duration: 7min
completed: 2026-03-15
---

# Phase 03 Plan 01: Migration _003 + SalesPageScraper Summary

**Migration _003 creates reviews/llm_calls tables and expands dossiers schema; SalesPageScraper extracts copy+offer from any URL using LLM as universal parser with Playwright SPA fallback**

## Performance

- **Duration:** 7 min
- **Started:** 2026-03-15T00:36:27Z
- **Completed:** 2026-03-15T00:43:34Z
- **Tasks:** 2
- **Files modified:** 12

## Accomplishments

- Migration _003 adds status/dossier_json/ads_json/incomplete/updated_at to dossiers, creates reviews and llm_calls tables — all idempotent via add_column() guards
- SalesPageScraper platform-agnostic: fetches any URL, converts HTML to clean text via markdownify, truncates at 50k chars, extracts full copy + offer in a single LLM call
- Full TDD test coverage: 10 tests (5 migration + 5 spy) passing with committed fixtures — no real API dependency

## Task Commits

Each task was committed atomically:

1. **Task 1: Migration _003** - `5e672ac` (feat)
2. **Task 2: SalesPageScraper** - `96b7201` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified

- `mis/migrations/_003_spy_dossiers.py` - Idempotent migration: expands dossiers, creates reviews + llm_calls
- `mis/spies/__init__.py` - Package init, exports SalesPageScraper
- `mis/spies/sales_page.py` - SalesPageScraper(BaseScraper) with extract() + _call_llm() + retry
- `mis/prompts/sales_page_extractor.md` - Zero-shot pt-BR system prompt for JSON extraction
- `mis/tests/test_migration_003.py` - 5 tests: new columns, legacy columns preserved, idempotent, reviews, llm_calls
- `mis/tests/test_sales_page_spy.py` - 5 tests: happy path, offer fields, SPA fallback, truncation, non-JSON error
- `mis/tests/fixtures/sales_page/hotmart_sample.html` - Realistic sales page fixture
- `mis/tests/fixtures/llm_responses/sales_page_extract.json` - Mock LLM response fixture
- `mis/migrations/__init__.py` - Exports all three migration functions
- `mis/db.py` - run_migrations() chains _001→_002→_003
- `mis/tests/test_db.py` - Updated to expect 7 tables (reviews + llm_calls added)
- `mis/requirements.txt` - Added anthropic>=0.79.0 and markdownify>=0.12.0

## Decisions Made

- LLM as universal parser: no platform-specific CSS/XPath selectors — works on any sales page URL from any platform
- `ads_json` as TEXT column in dossiers (MVP approach) — avoids over-engineering for Meta Ad Library JSON
- `run_migrations()` in db.py chains all migrations — single call gives full schema, no ordering burden on consumers

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] ScraperError fixture signature mismatch**
- **Found during:** Task 2 (test_spa_fallback)
- **Issue:** Test used `ScraperError("blocked")` but real interface requires `(url, attempts, cause)`
- **Fix:** Corrected fixture to `ScraperError("https://...", 3, ConnectionError("blocked"))`
- **Files modified:** mis/tests/test_sales_page_spy.py
- **Verification:** test_spa_fallback passes GREEN
- **Committed in:** 96b7201 (Task 2 commit)

**2. [Rule 1 - Bug] test_db.py expected 5 tables but migration chain now creates 7**
- **Found during:** Task 1 verification (test_db.py run after _003 changes)
- **Issue:** test_all_tables_exist and test_migration_idempotent expected {"platforms","niches","products","pains","dossiers"} but _003 adds reviews and llm_calls
- **Fix:** Updated both assertions to include "reviews" and "llm_calls"
- **Files modified:** mis/tests/test_db.py
- **Verification:** test_db.py 3/3 GREEN
- **Committed in:** 5e672ac (Task 1 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1 - Bug)
**Impact on plan:** Both fixes required for correctness. No scope creep.

## Issues Encountered

- `markdownify` was not installed in the environment — installed during Task 2 setup (pip install)
- `anthropic` 0.79.0 was already installed (plan spec'd >=0.84.0 but 0.79.0 has all required classes: AsyncAnthropic, APIConnectionError, RateLimitError)

## Next Phase Readiness

- migration _003 is prerequisite for all Phase 3 plans — now complete and idempotent
- SalesPageScraper ready for integration into SpyOrchestrator (Plan 03-04)
- reviews and llm_calls tables ready for ReviewsScraper (Plan 03-02) and DossierGenerator (Plan 03-03)

---
*Phase: 03-product-espionage-dossiers*
*Completed: 2026-03-15*
