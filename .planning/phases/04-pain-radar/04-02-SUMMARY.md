---
phase: 04-pain-radar
plan: "02"
subsystem: radar-collectors
tags: [google-trends, reddit, quora, pytrends, praw, playwright, tdd, pain-radar]

# Dependency graph
requires:
  - phase: 04-pain-radar
    plan: "01"
    provides: migration _004 pain_signals table, config.yaml radar block, Wave 0 RED scaffolds

provides:
  - "mis/radar/trends_collector.py — collect_trends_signal() returns peak_index (int 0-100) relative to anchor_term"
  - "mis/radar/reddit_collector.py — collect_reddit_signals() wraps PRAW in run_in_executor, filters >24h posts"
  - "mis/radar/quora_collector.py — collect_quora_signals() uses fetch_spa(), returns [] gracefully on any failure"
  - "mis/radar/__init__.py — package entrypoint with docstring"

affects:
  - 04-03-synthesizer
  - 04-04-scheduler
  - 04-05-integration

# Tech tracking
tech-stack:
  added:
    - pytrends==4.9.2 (Google Trends via TrendReq)
    - praw==7.8.1 (Reddit PRAW synchronous API)
  patterns:
    - "asyncio.sleep mock in TDD tests to prevent real rate-limit delays during test runs"
    - "run_in_executor pattern for PRAW (synchronous library wrapped for async event loop)"
    - "Graceful degradation: all collectors return [] on any exception without propagating"
    - "INSERT OR IGNORE on UNIQUE url_hash for idempotent persistence"

key-files:
  created:
    - mis/radar/trends_collector.py
    - mis/radar/reddit_collector.py
    - mis/radar/quora_collector.py
  modified:
    - mis/radar/__init__.py
    - mis/tests/test_trends_collector.py
    - mis/tests/test_reddit_collector.py
    - mis/tests/test_quora_collector.py

key-decisions:
  - "asyncio.sleep must be patched in TDD tests for TrendsCollector — 5-10s real sleep would make test suite impractically slow"
  - "PRAW wrapped in run_in_executor — PRAW is a synchronous library; executor prevents blocking async event loop"
  - "QuoraCollector uses len(html)<5000 threshold for empty SPA shell detection — React app shell is ~2-4KB without content"
  - "Quora CAPTCHA/403 treated as non-blocking — collector returns [] without error propagation (MVP design decision)"

requirements-completed:
  - RADAR-01
  - RADAR-02
  - RADAR-05

# Metrics
duration: 13min
completed: 2026-03-15
---

# Phase 4 Plan 02: Pain Radar Collectors Summary

**Three signal collectors implemented (Google Trends, Reddit, Quora) with 12 GREEN tests — each collector persists to pain_signals via url_hash upsert and degrades gracefully to [] on any failure**

## Performance

- **Duration:** ~13 min
- **Started:** 2026-03-15T15:09:02Z
- **Completed:** 2026-03-15T15:22:00Z
- **Tasks:** 2
- **Files modified:** 7 (3 new collectors, 1 updated __init__, 3 updated test files)

## Accomplishments
- `mis/radar/trends_collector.py`: collect_trends_signal() returns peak_index (int 0-100) normalized relative to anchor_term; collect_niche_trends() iterates all keywords and persists to pain_signals
- `mis/radar/reddit_collector.py`: collect_reddit_signals() wraps synchronous PRAW in asyncio run_in_executor; filters posts older than 24h; returns [] on any PRAW exception
- `mis/radar/quora_collector.py`: collect_quora_signals() uses BaseScraper.fetch_spa() for React SPA rendering; detects empty shell via len(html)<5000; returns [] on CAPTCHA/403/error
- 12 total tests GREEN (4 trends + 4 reddit + 4 quora)
- All collectors use INSERT OR IGNORE on url_hash UNIQUE constraint for idempotent persistence

## Task Commits

Each task was committed atomically:

1. **Task 1: TrendsCollector + RedditCollector + 8 tests** - `ed8dc31` (feat)
2. **Task 2: QuoraCollector + 4 tests** - `912778b` (feat)

## Files Created/Modified
- `mis/radar/__init__.py` — updated with package docstring
- `mis/radar/trends_collector.py` — Google Trends collector via pytrends; collect_trends_signal() + collect_niche_trends()
- `mis/radar/reddit_collector.py` — Reddit collector via PRAW in executor; _sync_collect_reddit() + collect_reddit_signals()
- `mis/radar/quora_collector.py` — Quora scraper via Playwright fetch_spa(); _extract_questions() + collect_quora_signals()
- `mis/tests/test_trends_collector.py` — 4 tests replacing RED scaffolds
- `mis/tests/test_reddit_collector.py` — 4 tests replacing RED scaffolds
- `mis/tests/test_quora_collector.py` — 4 tests replacing RED scaffolds

## Decisions Made
- asyncio.sleep patched in TDD test fixtures for TrendsCollector — the 5-10s rate-limit delay is production behavior but must be bypassed in unit tests to avoid 40+ seconds per test run
- PRAW in run_in_executor pattern — PRAW blocks the thread with network I/O; wrapping in executor keeps the asyncio event loop unblocked
- len(html) < 5000 as Quora empty shell threshold — React SPA shell is typically 2-4KB without content; 5000 is a safe detection margin
- Quora returns [] non-blockingly on all failure modes — Quora is NOT a required data source for MVP; any failure is acceptable behavior

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] asyncio.sleep mock required in TrendsCollector tests**
- **Found during:** Task 1 (TDD GREEN — tests hung for >120s)
- **Issue:** `collect_trends_signal()` calls `asyncio.sleep(random.uniform(5, 10))` after each keyword for rate limiting. Without mocking, each test would sleep 5-10s, causing 2-minute timeout.
- **Fix:** Added `with patch("mis.radar.trends_collector.asyncio.sleep")` in all three trends tests that call `collect_trends_signal()`
- **Files modified:** mis/tests/test_trends_collector.py
- **Commit:** ed8dc31

**2. [Rule 1 - Bug] QUORA_HTML_WITH_QUESTIONS fixture size**
- **Found during:** Task 2 (TDD GREEN — test_collect_quora_signals_returns_list failed)
- **Issue:** HTML fixture repeated 10x was only 4010 bytes — below the 5000-byte threshold used to detect empty SPA shell. Triggered `quora_empty_response` alert instead of parsing questions.
- **Fix:** Increased repetition from `* 10` to `* 20` to ensure HTML > 5000 bytes
- **Files modified:** mis/tests/test_quora_collector.py
- **Commit:** 912778b

---

**Total deviations:** 2 auto-fixed (Rule 1 - Bug)
**Impact on plan:** Both fixes were necessary for tests to pass. No scope change.

## Verification Results
- `python -m pytest tests/test_trends_collector.py tests/test_reddit_collector.py tests/test_quora_collector.py -v -q` → 12 passed
- `python -c "from mis.radar.trends_collector import collect_trends_signal; from mis.radar.reddit_collector import collect_reddit_signals; from mis.radar.quora_collector import collect_quora_signals; print('OK')"` → OK
- Full suite (excluding Wave 3/4 RED scaffolds): 101 passed, 1 pre-existing failure (test_cli_spy_help — PYTHONPATH issue, documented in deferred-items.md)

## Next Phase Readiness
- 3 collectors ready to be called by synthesizer (Wave 3 — Plan 04-03)
- All collectors return consistent signal shape: {url_hash, url, title, source, niche_slug, score, extra_json, collected_at}
- pain_signals table populated idempotently; synthesizer can query by niche_slug + collected_at range
- Wave 0 RED scaffolds for test_synthesizer.py and test_radar_jobs.py still pending (Wave 3/4 implementation)

---
*Phase: 04-pain-radar*
*Completed: 2026-03-15*
