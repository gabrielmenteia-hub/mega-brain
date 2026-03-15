---
phase: 04-pain-radar
plan: "01"
subsystem: database
tags: [sqlite, sqlite-utils, migration, pain-radar, tdd, scaffolding]

# Dependency graph
requires:
  - phase: 03-product-espionage-dossiers
    provides: run_migrations() chain _001→_002→_003, db.py helpers, conftest.py fixtures

provides:
  - "Migration _004 with pain_signals, pain_reports, youtube_quota_log tables"
  - "UNIQUE indexes on url_hash and (niche_id, cycle_at)"
  - "config.yaml radar block per niche (anchor_term, subreddits, relevance_language)"
  - "config.yaml settings: youtube_quota_daily_limit=9000, radar_synthesizer_offset_min=30"
  - "Wave 0 RED scaffolds: 6 test files for all radar collector/synthesizer/job modules"
  - "Fixtures: reddit_response.json, youtube_search_response.json"

affects:
  - 04-02-collectors
  - 04-03-synthesizer
  - 04-04-scheduler
  - 04-05-integration

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "INSERT OR IGNORE idempotent upsert pattern via url_hash UNIQUE constraint"
    - "Wave 0 RED scaffolds: import-level fail ensures test collection is verified before implementation"
    - "IF NOT EXISTS guard on all table and index creation for idempotent migrations"

key-files:
  created:
    - mis/migrations/_004_pain_radar.py
    - mis/tests/test_migration_004.py
    - mis/tests/test_trends_collector.py
    - mis/tests/test_reddit_collector.py
    - mis/tests/test_quora_collector.py
    - mis/tests/test_youtube_collector.py
    - mis/tests/test_synthesizer.py
    - mis/tests/test_radar_jobs.py
    - mis/tests/fixtures/reddit_response.json
    - mis/tests/fixtures/youtube_search_response.json
  modified:
    - mis/db.py
    - mis/config.yaml
    - mis/tests/test_db.py

key-decisions:
  - "INSERT OR IGNORE as upsert pattern for pain_signals — pain_signals has no sqlite-utils pk for upsert(), UNIQUE index on url_hash is sufficient for idempotency"
  - "Wave 0 test scaffolds import at module level to fail with ImportError — this ensures pytest collection works once modules exist, no pytest.skip needed at collection time"
  - "config.yaml radar block uses pt as relevance_language for all niches — project targets BR market"
  - "test_db.py updated from 7 to 10 tables — adding _004 was an anticipated change, test update is correctness not scope creep"

patterns-established:
  - "Pain signal idempotency: url_hash UNIQUE + INSERT OR IGNORE pattern"
  - "Red scaffold pattern: import at top of file (not inside test function) to enforce ImportError as failure mode"

requirements-completed:
  - RADAR-01
  - RADAR-02
  - RADAR-03
  - RADAR-05
  - RADAR-06

# Metrics
duration: 10min
completed: 2026-03-15
---

# Phase 4 Plan 01: Pain Radar Foundation Summary

**SQLite _004 migration with pain_signals/pain_reports/youtube_quota_log tables, config.yaml radar fields per niche, and 6 Wave 0 RED test scaffolds for all Pain Radar modules**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-03-15T14:55:24Z
- **Completed:** 2026-03-15T15:05:40Z
- **Tasks:** 2
- **Files modified:** 10 (5 created migrations+tests, 3 modified, 2 fixtures)

## Accomplishments
- Migration _004 creates pain_signals (UNIQUE url_hash), pain_reports (UNIQUE niche+cycle), youtube_quota_log with proper indexes
- db.py run_migrations() now chains _001→_002→_003→_004 — callers get full Pain Radar schema with one call
- config.yaml extended with radar block per niche (anchor_term, subreddits, relevance_language) and quota settings
- 6 Wave 0 RED scaffold files created — all fail with ImportError (mis.radar.* not yet implemented)
- 2 fixture JSON files created for Reddit PRAW mock and YouTube API v3 search.list mock

## Task Commits

Each task was committed atomically:

1. **Task 1: Migration _004 + config.yaml radar fields** - `7c09546` (feat)
2. **Task 2: Wave 0 RED scaffolds + fixtures** - `4821300` (test)

**Plan metadata:** (pending final docs commit)

## Files Created/Modified
- `mis/migrations/_004_pain_radar.py` — 3 new tables with IF NOT EXISTS guards and UNIQUE indexes
- `mis/db.py` — added _004 import and call in run_migrations() chain
- `mis/config.yaml` — radar block per niche + youtube_quota_daily_limit + radar_synthesizer_offset_min
- `mis/tests/test_migration_004.py` — 5 tests GREEN (tables, unique indexes, upsert idempotency, migration idempotency)
- `mis/tests/test_db.py` — updated expected table count from 7 to 10
- `mis/tests/test_trends_collector.py` — RED scaffold (ImportError)
- `mis/tests/test_reddit_collector.py` — RED scaffold (ImportError)
- `mis/tests/test_quora_collector.py` — RED scaffold (ImportError)
- `mis/tests/test_youtube_collector.py` — RED scaffold (ImportError)
- `mis/tests/test_synthesizer.py` — RED scaffold (ImportError)
- `mis/tests/test_radar_jobs.py` — RED scaffold (ImportError)
- `mis/tests/fixtures/reddit_response.json` — 3 mock PRAW posts
- `mis/tests/fixtures/youtube_search_response.json` — YouTube API v3 search.list mock (2 items)

## Decisions Made
- INSERT OR IGNORE as upsert pattern for pain_signals — UNIQUE index on url_hash is sufficient for idempotency without needing sqlite-utils pk-based upsert
- Wave 0 test scaffolds import at module level (not inside test) — ensures ImportError on collection attempt, correct RED state
- config.yaml relevance_language="pt" for all niches — project targets BR market exclusively
- test_db.py updated to expect 10 tables — adding _004 is the expected chain extension, updating the count is correctness not scope creep

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed test_upsert_idempotent to use INSERT OR IGNORE instead of hash_id**
- **Found during:** Task 1 (TDD GREEN — test_migration_004.py)
- **Issue:** Plan specified `upsert(signal, hash_id="url_hash")` — but `hash_id` in sqlite-utils generates a new hash column, not uses the existing url_hash column. Test resulted in count=0.
- **Fix:** Rewrote test to use raw SQL `INSERT OR IGNORE` which directly tests the UNIQUE constraint behavior
- **Files modified:** mis/tests/test_migration_004.py
- **Verification:** test_upsert_idempotent passes (count==1)
- **Committed in:** 7c09546 (Task 1 commit)

**2. [Rule 1 - Bug] Updated test_db.py table count from 7 to 10**
- **Found during:** Task 1 post-commit verification (full suite run)
- **Issue:** test_db.py hardcoded `== {7 tables}` — after _004 adds 3 tables, test fails with extra items pain_signals, pain_reports, youtube_quota_log
- **Fix:** Updated expected set to include all 10 tables
- **Files modified:** mis/tests/test_db.py
- **Verification:** test_all_tables_exist and test_migration_idempotent pass
- **Committed in:** 7c09546 (Task 1 commit)

---

**Total deviations:** 2 auto-fixed (Rule 1 - Bug)
**Impact on plan:** Both fixes necessary for correctness. No scope creep.

## Issues Encountered
- Pre-existing failure `test_spy_orchestrator.py::test_cli_spy_help` confirmed via git stash test — subprocess `python -m mis` missing PYTHONPATH. Documented in deferred-items.md. Not introduced by this plan.

## Next Phase Readiness
- Schema foundation complete: pain_signals, pain_reports, youtube_quota_log tables ready
- config.yaml radar fields ready for collectors to read anchor_term, subreddits, quota limits
- 6 Wave 0 RED scaffolds ready for Wave 2 GREEN implementation in Plan 04-02
- Fixtures ready for mocking in collector tests

---
*Phase: 04-pain-radar*
*Completed: 2026-03-15*
