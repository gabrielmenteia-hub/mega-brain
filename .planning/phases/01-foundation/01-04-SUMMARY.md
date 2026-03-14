---
phase: 01-foundation
plan: "04"
subsystem: mis-health-monitor
tags: [health-monitor, canary, structlog, apscheduler, tdd, async]
dependency_graph:
  requires:
    - mis.exceptions.ScraperError (from plan 01-01)
    - mis.base_scraper.BaseScraper (from plan 01-02)
    - mis.scheduler.get_scheduler (from plan 01-03)
  provides:
    - mis.health_monitor.run_canary_check
    - mis.health_monitor.register_canary_job
    - mis.health_monitor.CANARY_URL
    - mis.health_monitor.CANARY_MIN_LENGTH
  affects:
    - Phase 2+ scrapers (canary job runs alongside scraper jobs in APScheduler)
tech_stack:
  added: []
  patterns:
    - TDD RED-GREEN: stubs replaced before implementation
    - "async with BaseScraper() as scraper: content = await scraper.fetch(url)"
    - structlog.testing.capture_logs() for log assertion in tests
    - APScheduler job registered with replace_existing=True
key_files:
  created:
    - mis/health_monitor.py
  modified:
    - mis/tests/test_health_monitor.py (stubs replaced with 3 real async tests)
decisions:
  - "run_canary_check() never propagates exceptions — catches ScraperError and Exception, always returns bool"
  - "alert field in structlog payloads is machine-readable key for external parsing (SCRAPER_RETURNING_EMPTY_RESPONSE, SCRAPER_BROKEN_CANARY_FAILED)"
  - "register_canary_job() uses replace_existing=True — safe to call at startup or on re-registration without duplicate job errors"
  - "CANARY_MIN_LENGTH=100 chosen to detect truly empty responses while allowing small valid JSON payloads"
metrics:
  duration: "~5 minutes"
  completed_date: "2026-03-14T17:55:00Z"
  tasks_completed: 2
  files_created: 1
  files_modified: 1
  test_results: "15 passed (3 db + 6 base_scraper + 3 config + 3 health_monitor)"
---

# Phase 1 Plan 04: Health Monitor Summary

Async canary health check using BaseScraper against httpbin.org/get, with structured alert logs via structlog and APScheduler job registration every 15 minutes.

## run_canary_check() — Signature and Behavior

```python
from mis.health_monitor import run_canary_check

async def run_canary_check() -> bool:
```

**Returns:** `True` if healthy, `False` if degraded. Never raises exceptions.

**Alert events emitted via structlog:**

| Condition | log level | event key | alert field |
|-----------|-----------|-----------|-------------|
| content < CANARY_MIN_LENGTH | warning | `health.canary.empty` | `SCRAPER_RETURNING_EMPTY_RESPONSE` |
| ScraperError raised | error | `health.canary.failed` | `SCRAPER_BROKEN_CANARY_FAILED` |
| Unexpected exception | error | `health.canary.unexpected_error` | `SCRAPER_BROKEN_CANARY_FAILED` |
| Healthy | info | `health.canary.ok` | (none) |

**Example structlog output on failure:**
```json
{"alert": "SCRAPER_BROKEN_CANARY_FAILED", "url": "https://httpbin.org/get", "attempts": 3, "cause": "timeout", "event": "health.canary.failed", "level": "error"}
```

## register_canary_job() — Signature and Behavior

```python
from mis.health_monitor import register_canary_job

def register_canary_job() -> None:
```

**What it does:** Calls `get_scheduler().add_job(run_canary_check, trigger="interval", minutes=15, id="health_canary", replace_existing=True)`

**Safe to call:** Multiple times — `replace_existing=True` prevents duplicate job errors on restart.

## Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `CANARY_URL` | `"https://httpbin.org/get"` | Known-good URL used for canary probe |
| `CANARY_MIN_LENGTH` | `100` | Minimum bytes in response to be considered healthy |

## How the Canary Job is Registered in APScheduler

```python
# At application startup (e.g., main.py or app init):
from mis.health_monitor import register_canary_job
from mis.scheduler import start_scheduler

register_canary_job()   # registers health_canary job
start_scheduler()       # starts the scheduler event loop
```

This pattern is how Phase 2 scraper jobs should also be added — each scraper module exports a `register_*_job()` function that calls `get_scheduler().add_job(...)` with its own `id` and `trigger`.

## How to Add More Jobs in Phase 2

```python
from mis.scheduler import get_scheduler

scheduler = get_scheduler()
scheduler.add_job(
    scrape_hotmart,         # async callable
    "interval",             # trigger
    hours=6,                # interval
    id="hotmart_scraper",   # unique ID
    replace_existing=True,  # safe on restart
)
```

## Test Results

| Test | Status | What it verifies |
|------|--------|-----------------|
| `test_canary_healthy` | PASSED | mock fetch 200+ chars → returns True, no error logs |
| `test_canary_empty_response` | PASSED | mock fetch 50 chars → returns False + SCRAPER_RETURNING_EMPTY_RESPONSE |
| `test_canary_scraper_error` | PASSED | mock raises ScraperError → returns False + SCRAPER_BROKEN_CANARY_FAILED |

**Full Phase 1 suite: 15/15 passed.**

| Test file | Count | Status |
|-----------|-------|--------|
| test_db.py | 3 | PASSED |
| test_base_scraper.py | 6 | PASSED |
| test_config.py | 3 | PASSED |
| test_health_monitor.py | 3 | PASSED |
| **Total** | **15** | **ALL GREEN** |

## Phase 1 Complete — Phase 2 Can Begin

All Phase 1 foundation components are implemented and tested:
- `mis/exceptions.py` — ScraperError
- `mis/db.py` — run_migrations(), get_db()
- `mis/base_scraper.py` — BaseScraper with fetch(), fetch_spa(), retry, rate limiting
- `mis/config.py` — load_config() with YAML niche validation
- `mis/scheduler.py` — APScheduler singleton with get_scheduler()
- `mis/health_monitor.py` — run_canary_check(), register_canary_job()

Phase 2 can implement real platform scrapers (Hotmart, Kiwify, etc.) using BaseScraper and register their jobs via the same APScheduler pattern.

## Deviations from Plan

None — plan executed exactly as written.

## Commits

| Hash | Message |
|------|---------|
| 41584cd | test(01-04): replace stubs with real tests for health monitor (RED) |
| bae29b4 | feat(01-04): implement health_monitor with run_canary_check and register_canary_job (GREEN) |

## Self-Check: PASSED
