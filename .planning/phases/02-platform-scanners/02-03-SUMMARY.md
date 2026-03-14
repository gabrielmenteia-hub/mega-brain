---
phase: 02-platform-scanners
plan: "03"
subsystem: mis/scanners
tags: [hotmart, scanner, ssr, apscheduler, health-monitor, tdd]
dependency_graph:
  requires: [02-01, 02-02]
  provides: [HotmartScanner, register_scanner_jobs, run_platform_canary]
  affects: [mis/scanner.py, mis/scheduler.py, mis/health_monitor.py]
tech_stack:
  added: []
  patterns: [SSR HTML parsing, CSS selector fallback chain, APScheduler CronTrigger, DB-based canary]
key_files:
  created:
    - mis/scanners/hotmart.py
    - mis/tests/test_hotmart_scanner.py
    - mis/tests/test_scanner_jobs.py
  modified:
    - mis/scanners/clickbank.py
    - mis/scanners/kiwify.py
    - mis/scheduler.py
    - mis/health_monitor.py
    - mis/scanner.py
decisions:
  - "HOTMART_PLATFORM_ID=1 (convention: 1=Hotmart, 2=ClickBank, 3=Kiwify — consistent with prior plans)"
  - "Hotmart marketplace is SSR (confirmed live 2026-03-14) — httpx sufficient, Playwright not needed"
  - "run_platform_canary() uses sqlite3 directly (not sqlite_utils) for simplicity of MAX(updated_at) query"
  - "register_scanner_jobs() uses CronTrigger.from_crontab() — reads scan_schedule from config.settings"
  - "test_partial_failure patches scanner classes at mis.scanners.*.ClassName — not mis.scanner.ClassName"
metrics:
  duration_seconds: 635
  completed_date: "2026-03-14"
  tasks_completed: 2
  files_created: 3
  files_modified: 6
---

# Phase 02 Plan 03: HotmartScanner + Scanner Jobs Summary

HotmartScanner via httpx SSR with 3-selector fallback chain, APScheduler CronTrigger jobs for all 3 platforms, and DB-based platform canary with 25h staleness threshold.

## What Was Built

### HotmartScanner (mis/scanners/hotmart.py)

- **Protocol:** SSR HTML via httpx (confirmed by live inspection 2026-03-14 — no Playwright needed)
- **URL:** `https://hotmart.com/pt-br/marketplace/produtos?category={category_slug}`
- **Primary selector:** `a.product-link` — confirmed 24 products in fixture
- **Fallback selectors:** `.product-card-alt a[aria-label]` → `[class*='product'] a[href*='/produtos/']`
- **external_id:** Alphanumeric code from URL path (regex: `r'/([A-Z][0-9A-Z]{6,10})\?'`)
  - Example: `E45853768C`, `A1412453A`
- **title:** `aria-label` attribute, text before ` - ` separator
- **price:** `None` (not available in SSR HTML)
- **rank:** 1-based positional
- **HOTMART_PLATFORM_ID:** 1 (convention matching prior phases)
- **Schema drift:** Logs `alert='schema_drift'` via structlog when all selectors fail, returns `[]`

### register_scanner_jobs (mis/scheduler.py extension)

- Registers 3 jobs: `scanner_hotmart`, `scanner_clickbank`, `scanner_kiwify`
- Trigger: `CronTrigger.from_crontab(scan_schedule)` — default `"0 3 * * *"` (3 AM daily)
- `replace_existing=True` — safe to call at startup or on re-registration
- Each job receives `config` dict as argument
- `run_hotmart_scan`, `run_clickbank_scan`, `run_kiwify_scan` added to respective scanner files

### run_platform_canary (mis/health_monitor.py extension)

- Query: `SELECT MAX(updated_at) FROM products WHERE platform_id = ?`
- Threshold: 25 hours (configurable via `threshold_hours` parameter)
- Alert: `alert='platform_data_stale'` via structlog when stale or no data
- Uses `sqlite3` directly (no `sqlite_utils` overhead)
- Never raises exceptions — always returns `bool`

### run_all_scanners update (mis/scanner.py)

- SCANNER_MAP extended to include `HotmartScanner` and `ClickBankScanner`
- All 3 platforms now participate in parallel scan with `asyncio.gather(return_exceptions=True)`

## Test Results

**Total: 34/34 GREEN** (no regressions)

| Module | Tests | Result |
|--------|-------|--------|
| Phase 1 (foundation) | 15 | GREEN |
| KiwifyScanner | 5 | GREEN |
| ClickBankScanner | 5 | GREEN |
| HotmartScanner | 5 | GREEN |
| Scanner jobs + canary | 4 | GREEN |

Suite execution time: ~80 seconds

## Hotmart SSR Structure (Confirmed)

| Field | Source | Example |
|-------|--------|---------|
| `external_id` | URL path regex `[A-Z][0-9A-Z]{6,10}` before `?` | `E45853768C` |
| `title` | `aria-label` attr, before ` - ` | `Curso de Cutilagem para Manicures com Faby Cardoso` |
| `url` | `href` attribute (absolute URL) | `https://hotmart.com/pt-br/marketplace/produtos/...` |
| `price` | N/A — not in SSR HTML | `None` |
| `rank` | Positional (1-based) | `1`, `2`, `3`... |

No Cloudflare/anti-bot blockers encountered — SSR page accessible with standard httpx.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] temp_config_with_schedule fixture had only 1 niche but load_config() requires 3-5**
- **Found during:** Task 2 — test_jobs_registered and test_cron_trigger
- **Issue:** Tests called `load_config()` with a 1-niche config, which raises `ValueError`. The scheduler's `register_scanner_jobs()` accepts any dict — no need for `load_config()` validation in these tests.
- **Fix:** Removed `load_config()` from test_jobs_registered and test_cron_trigger — pass config dict directly
- **Files modified:** `mis/tests/test_scanner_jobs.py`

**2. [Rule 2 - Missing] run_clickbank_scan and run_kiwify_scan functions missing from scanner files**
- **Found during:** Task 2 — register_scanner_jobs() imports these functions
- **Issue:** scheduler.py imports `run_hotmart_scan`, `run_clickbank_scan`, `run_kiwify_scan` — only hotmart had this function
- **Fix:** Added `run_clickbank_scan()` to `clickbank.py` and `run_kiwify_scan()` to `kiwify.py`
- **Files modified:** `mis/scanners/clickbank.py`, `mis/scanners/kiwify.py`

**3. [Rule 2 - Missing] run_all_scanners() SCANNER_MAP only had Kiwify**
- **Found during:** Task 2 — test_partial_failure testing multi-platform behavior
- **Issue:** `run_all_scanners()` in `scanner.py` only imported `KiwifyScanner` in its SCANNER_MAP
- **Fix:** Added `HotmartScanner` and `ClickBankScanner` to the SCANNER_MAP
- **Files modified:** `mis/scanner.py`

**4. [Rule 1 - Bug] test_partial_failure was patching mis.scanner.KiwifyScanner (wrong path)**
- **Found during:** Task 2 — test failed with AttributeError
- **Issue:** `run_all_scanners()` imports scanners via lazy imports inside the function — patching `mis.scanner.XScanner` patches a non-existent attribute
- **Fix:** Updated patch targets to `mis.scanners.kiwify.KiwifyScanner` and `mis.scanners.hotmart.HotmartScanner`
- **Files modified:** `mis/tests/test_scanner_jobs.py`

## Commits

| Hash | Description |
|------|-------------|
| `18684ae` | test(02-03): add failing tests for HotmartScanner and scanner jobs (RED) |
| `ab18494` | feat(02-03): implement HotmartScanner, register_scanner_jobs, run_platform_canary (GREEN) |

## Self-Check: PASSED

- mis/scanners/hotmart.py: FOUND
- mis/tests/test_hotmart_scanner.py: FOUND
- mis/tests/test_scanner_jobs.py: FOUND
- Commit 18684ae: FOUND
- Commit ab18494: FOUND
