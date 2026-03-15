---
phase: 04-pain-radar
plan: "03"
subsystem: api-integration
tags: [youtube, google-api-python-client, sqlite-utils, quota-management, async, tdd]

# Dependency graph
requires:
  - phase: 04-pain-radar
    plan: "01"
    provides: "Migration _004 with youtube_quota_log and pain_signals tables, config.yaml youtube_quota_daily_limit"

provides:
  - "mis/radar/youtube_collector.py — collect_youtube_signals(), get_quota_used_today(), log_quota_usage()"
  - "Persistent quota guard: checks and logs units in youtube_quota_log, survives process restarts"
  - "Daily reset at 07:00 UTC (midnight PT) via get_quota_used_today(reset_hour_utc=7)"
  - "Async entry point wrapping synchronous googleapiclient in run_in_executor"
  - "view_count via videos().list(part='statistics') — not search.list"
  - "mis/radar/__init__.py — package created"

affects:
  - 04-04-scheduler
  - 04-05-integration

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Quota guard pattern: check DB before API call, log after, re-check mid-loop"
    - "Sync API wrapped in run_in_executor for async compatibility (googleapiclient is blocking)"
    - "INSERT OR IGNORE via sqlite-utils ignore=True for pain_signals idempotent upsert"
    - "Daily reset: reset_dt = today.replace(hour=7) adjusted back 1 day if current hour < 7"

key-files:
  created:
    - mis/radar/__init__.py
    - mis/radar/youtube_collector.py
  modified:
    - mis/tests/test_youtube_collector.py

key-decisions:
  - "asyncio.get_event_loop().run_in_executor() wraps googleapiclient — it is inherently synchronous; no async wrapper available"
  - "Quota re-checked before each keyword iteration — prevents mid-niche overage when multiple keywords are processed"
  - "youtube_quota_log persists in DB not a module variable — critical for correctness across process restarts"
  - "commentThreads.list wrapped in try/except — disabled comments on some videos should not abort the whole collection"

patterns-established:
  - "External API quota guard: pre-check → call → log → re-check loop pattern"
  - "Sync blocking API in run_in_executor with (signals, units_used) return tuple for clean caller interface"

requirements-completed:
  - RADAR-03
  - RADAR-05

# Metrics
duration: 10min
completed: 2026-03-15
---

# Phase 4 Plan 03: YouTube Collector Summary

**YouTube Data API v3 collector with DB-persisted quota guard — collect_youtube_signals() checks/logs units in youtube_quota_log, resets at 07:00 UTC, wraps blocking googleapiclient in run_in_executor**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-03-15T15:05:00Z
- **Completed:** 2026-03-15T15:15:34Z
- **Tasks:** 1 (TDD: RED commit + GREEN commit)
- **Files modified:** 3 (2 created, 1 modified)

## Accomplishments
- YouTubeCollector implemented with quota guard persisted in youtube_quota_log table
- Quota resets daily at 07:00 UTC via get_quota_used_today(reset_hour_utc=7) with correct day-boundary logic
- Statistics (view_count, like_count) fetched via videos().list — not search.list — 1 unit for batch of IDs
- comment threads fetched per-video with graceful fallback (try/except) when comments disabled
- 5/5 tests GREEN covering happy path, quota guard, persistence, reset logic, required fields

## Task Commits

Each task was committed atomically:

1. **RED: Failing tests for YouTube collector** - `48543b3` (test)
2. **GREEN: YouTubeCollector implementation** - `320885e` (feat)

**Plan metadata:** (pending final docs commit)

## Files Created/Modified
- `mis/radar/__init__.py` — Package init for mis.radar collectors
- `mis/radar/youtube_collector.py` — Full implementation: collect_youtube_signals(), get_quota_used_today(), log_quota_usage(), _sync_collect_youtube()
- `mis/tests/test_youtube_collector.py` — 5 real tests replacing Wave 0 RED stubs

## Decisions Made
- `asyncio.get_event_loop().run_in_executor()` wraps googleapiclient — it is a blocking synchronous library; no async wrapper exists
- Quota re-checked before each keyword iteration — prevents mid-niche quota overage when processing multiple keywords
- youtube_quota_log persists in SQLite DB not module variable — critical for correctness across process restarts
- commentThreads.list wrapped in try/except — videos with disabled comments should not abort the whole niche collection

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- None — implementation matched plan specification precisely. Wave 0 RED scaffolds for other collectors (trends, reddit, quora, synthesizer, radar_jobs) remain RED as expected — they are not in scope for this plan.

## Next Phase Readiness
- YouTube collector fully functional with quota guard
- collect_youtube_signals() ready to be called by radar scheduler (Plan 04-04)
- mis/radar/ package created — other collectors (reddit, trends, quora) can be added in their respective plans
- youtube_quota_log in DB ready for multi-process safe quota tracking

---
*Phase: 04-pain-radar*
*Completed: 2026-03-15*

## Self-Check: PASSED

- mis/radar/youtube_collector.py: FOUND
- mis/radar/__init__.py: FOUND
- 04-03-SUMMARY.md: FOUND
- RED commit 48543b3: FOUND
- GREEN commit 320885e: FOUND
