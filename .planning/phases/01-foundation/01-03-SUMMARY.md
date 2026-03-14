---
phase: 01-foundation
plan: "03"
subsystem: mis-config-scheduler
tags: [yaml, config, apscheduler, tdd, async, dotenv]
dependency_graph:
  requires:
    - mis.exceptions.ScraperError (from plan 01-01)
    - mis.base_scraper.BaseScraper (from plan 01-02)
  provides:
    - mis.config.load_config
    - mis/config.yaml
    - mis.scheduler.get_scheduler
    - mis.scheduler.start_scheduler
    - mis.scheduler.stop_scheduler
  affects:
    - mis/tests/test_health_monitor.py (health monitor uses scheduler — plan 01-04)
    - All Phase 2+ scrapers (read request_delay_s, max_retries from load_config())
tech_stack:
  added:
    - apscheduler 3.11.2 (installed during execution — was missing from env)
  patterns:
    - TDD RED-GREEN: stubs replaced before implementation
    - CONFIG_PATH = Path(__file__).parent / "config.yaml" — relative to module
    - .env override via os.getenv("PROXY_URL") — never hardcoded in yaml
    - APScheduler singleton via module-level _scheduler global + get_scheduler()
key_files:
  created:
    - mis/config.yaml
    - mis/config.py
    - mis/scheduler.py
  modified:
    - mis/tests/test_config.py (stubs replaced with 3 real tests)
decisions:
  - "config.yaml path relative to mis/config.py via Path(__file__).parent — portable across environments without needing CWD assumptions"
  - "load_config() accepts optional config_path parameter — avoids mock patching in tests, aligns with plan spec"
  - "APScheduler singleton pattern with _scheduler global — health monitor and scrapers share one scheduler instance"
  - "apscheduler installed as Rule 3 auto-fix — was in requirements.txt but not in the Python environment"
metrics:
  duration: "~4 minutes"
  completed_date: "2026-03-14T17:46:27Z"
  tasks_completed: 2
  files_created: 3
  files_modified: 1
  test_results: "3 passed"
---

# Phase 1 Plan 03: Config System and APScheduler Skeleton Summary

YAML niche config loader with 3-5 niche validation and .env PROXY_URL override, plus APScheduler AsyncIOScheduler singleton skeleton with structlog event logging ready for Phase 2 scraper jobs.

## load_config() — Signature and Validation

```python
from mis.config import load_config

def load_config(config_path: Path | None = None) -> dict:
```

**What it validates:**
1. Niche count must be 3-5 — raises `ValueError("config.yaml must define 3-5 niches, got N")`
2. Each niche must have a `slug` field — raises `ValueError("Each niche must have a 'slug' field. Missing in: {...}")`
3. Reads `PROXY_URL` from environment (`.env` via python-dotenv) — if set, overrides `cfg["settings"]["proxy_url"]`

**Default path:** `mis/config.yaml` (relative to `mis/config.py` via `Path(__file__).parent`)

**Returns:** `dict` with structure:
```python
{
    "niches": [{"name": str, "slug": str, "keywords": list[str]}, ...],
    "settings": {"proxy_url": str, "request_delay_s": float, "max_retries": int}
}
```

## config.yaml Structure

Required fields per niche:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Display name (e.g. "Marketing Digital") |
| `slug` | string | yes | URL-safe identifier (e.g. "marketing-digital") |
| `keywords` | list[str] | no | Search keywords for this niche |

Settings fields:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `proxy_url` | string | `""` | Proxy URL — override via `PROXY_URL` env var |
| `request_delay_s` | float | `2.0` | Delay between requests in seconds |
| `max_retries` | int | `3` | Max retry attempts per request |

## Scheduler Interface (3 Exported Functions)

```python
from mis.scheduler import get_scheduler, start_scheduler, stop_scheduler
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `get_scheduler` | `() -> AsyncIOScheduler` | Returns singleton; creates on first call with job event listener |
| `start_scheduler` | `() -> None` | Idempotent start; logs `scheduler.started` via structlog |
| `stop_scheduler` | `() -> None` | Graceful shutdown with `wait=False`; resets singleton to None; logs `scheduler.stopped` |

**Internal:** `_on_job_event(event)` listener logs `scheduler.job.error` (with exception) or `scheduler.job.executed` for each job.

## How to Add Jobs in Phase 2

```python
from mis.scheduler import get_scheduler

scheduler = get_scheduler()

# Register a scraper job — runs every 6 hours
scheduler.add_job(
    scrape_hotmart,           # async callable
    "interval",               # trigger type
    hours=6,                  # interval
    id="hotmart_scraper",     # unique job ID
    replace_existing=True,    # safe to call on re-registration
)

# Start (idempotent — safe to call at app startup)
start_scheduler()
```

APScheduler 3.x job kwargs reference: `seconds`, `minutes`, `hours`, `days`, `weeks`. Use `replace_existing=True` to avoid duplicate job errors on restart.

## Test Status

| Test | Status | What it verifies |
|------|--------|-----------------|
| `test_load_3_niches` | PASSED | load_config() with temp yaml returns 3 niches |
| `test_too_many_niches` | PASSED | 6-niche yaml raises ValueError matching "3-5" |
| `test_proxy_env_override` | PASSED | PROXY_URL env var overrides settings.proxy_url |

**Result: 3/3 passed.**

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] apscheduler not installed in Python environment**
- **Found during:** Task 2 implementation
- **Issue:** `ModuleNotFoundError: No module named 'apscheduler'` — package in requirements.txt but not installed
- **Fix:** `pip install apscheduler` (3.11.2 installed)
- **Files modified:** none (runtime dependency install)
- **Commit:** 712e95e

## Verification Results

```
pytest mis/tests/test_config.py -v
3 passed, 115 warnings in 0.22s

python -c "from mis.config import load_config; cfg = load_config(); print('nichos:', [n['slug'] for n in cfg['niches']])"
nichos: ['marketing-digital', 'emagrecimento', 'financas-pessoais']

python -c "from mis.scheduler import get_scheduler, start_scheduler, stop_scheduler; s = get_scheduler(); print('OK:', type(s).__name__)"
OK: AsyncIOScheduler

asyncio.run(test()) — start_scheduler() + stop_scheduler()
scheduler.started / started: OK / scheduler.stopped / stopped: OK
```

## Commits

| Hash | Message |
|------|---------|
| 4cbf04d | test(01-03): replace stubs with real tests for config loader (RED) |
| 73be48d | feat(01-03): implement config.yaml and load_config() with niche validation (GREEN) |
| 712e95e | feat(01-03): implement APScheduler AsyncIOScheduler skeleton |

## Self-Check: PASSED
