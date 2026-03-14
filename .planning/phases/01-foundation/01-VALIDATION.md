---
phase: 1
slug: foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-14
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.4.2 + pytest-asyncio 0.24.0 |
| **Config file** | `mis/pytest.ini` (Wave 0 gap — needs creation) |
| **Quick run command** | `pytest mis/tests/ -x -q --timeout=10` |
| **Full suite command** | `pytest mis/tests/ -v --timeout=30` |
| **Estimated runtime** | ~15 seconds (unit) / ~30 seconds (full with integration) |

---

## Sampling Rate

- **After every task commit:** Run `pytest mis/tests/ -x -q --timeout=10`
- **After every plan wave:** Run `pytest mis/tests/ -v --timeout=30`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01-01 | 1 | FOUND-01 | unit | `pytest mis/tests/test_db.py::test_all_tables_exist -x` | ❌ W0 | ⬜ pending |
| 1-01-02 | 01-01 | 1 | FOUND-01 | unit | `pytest mis/tests/test_db.py::test_migration_idempotent -x` | ❌ W0 | ⬜ pending |
| 1-01-03 | 01-01 | 1 | FOUND-01 | unit | `pytest mis/tests/test_db.py::test_foreign_key_constraint -x` | ❌ W0 | ⬜ pending |
| 1-02-01 | 01-02 | 1 | FOUND-02 | unit | `pytest mis/tests/test_base_scraper.py::test_fetch_success -x` | ❌ W0 | ⬜ pending |
| 1-02-02 | 01-02 | 1 | FOUND-02 | unit | `pytest mis/tests/test_base_scraper.py::test_fetch_retries_on_429 -x` | ❌ W0 | ⬜ pending |
| 1-02-03 | 01-02 | 1 | FOUND-02 | unit | `pytest mis/tests/test_base_scraper.py::test_rate_limiting -x` | ❌ W0 | ⬜ pending |
| 1-02-04 | 01-02 | 1 | FOUND-02 | unit | `pytest mis/tests/test_base_scraper.py::test_headers_not_default -x` | ❌ W0 | ⬜ pending |
| 1-02-05 | 01-02 | 1 | FOUND-02 | unit | `pytest mis/tests/test_base_scraper.py::test_scraper_error_raised -x` | ❌ W0 | ⬜ pending |
| 1-02-06 | 01-02 | 1 | FOUND-02 | unit | `pytest mis/tests/test_base_scraper.py::test_client_closed_on_exit -x` | ❌ W0 | ⬜ pending |
| 1-03-01 | 01-03 | 2 | FOUND-03 | unit | `pytest mis/tests/test_config.py::test_load_3_niches -x` | ❌ W0 | ⬜ pending |
| 1-03-02 | 01-03 | 2 | FOUND-03 | unit | `pytest mis/tests/test_config.py::test_too_many_niches -x` | ❌ W0 | ⬜ pending |
| 1-03-03 | 01-03 | 2 | FOUND-03 | unit | `pytest mis/tests/test_config.py::test_proxy_env_override -x` | ❌ W0 | ⬜ pending |
| 1-04-01 | 01-04 | 2 | FOUND-04 | unit | `pytest mis/tests/test_health_monitor.py::test_canary_empty_response -x` | ❌ W0 | ⬜ pending |
| 1-04-02 | 01-04 | 2 | FOUND-04 | unit | `pytest mis/tests/test_health_monitor.py::test_canary_scraper_error -x` | ❌ W0 | ⬜ pending |
| 1-04-03 | 01-04 | 2 | FOUND-04 | integration | `pytest mis/tests/test_health_monitor.py::test_canary_healthy -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `mis/pytest.ini` — configures `asyncio_mode = auto` and test path `testpaths = tests`
- [ ] `mis/tests/__init__.py` — empty, makes tests a package
- [ ] `mis/tests/conftest.py` — shared fixtures: in-memory SQLite DB, mock BaseScraper, temp config.yaml
- [ ] `mis/tests/test_db.py` — stub test functions for FOUND-01 (tables, idempotency, foreign keys)
- [ ] `mis/tests/test_base_scraper.py` — stub test functions for FOUND-02 (fetch, retry, rate limiting, headers, errors, cleanup)
- [ ] `mis/tests/test_config.py` — stub test functions for FOUND-03 (load, validation, env override)
- [ ] `mis/tests/test_health_monitor.py` — stub test functions for FOUND-04 (canary paths)
- [ ] `mis/requirements.txt` — MIS-specific production deps (httpx, playwright, playwright-stealth, tenacity, structlog, fake-useragent, sqlite-utils, apscheduler, PyYAML)
- [ ] `mis/requirements-dev.txt` — dev deps (`respx` for httpx mocking, `pytest`, `pytest-asyncio`)
- [ ] Install: `pip install respx` (httpx mock — needed for test_base_scraper.py)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `fetch_spa()` with stealth suppresses `navigator.webdriver` | FOUND-02 | Requires real browser; headless detection can't be unit-tested reliably | Run `python -c "import asyncio; from mis.base_scraper import BaseScraper; asyncio.run(test_stealth())"` against `https://bot.sannysoft.com/` and confirm `navigator.webdriver` is `false` in page output |
| APScheduler canary job fires every 15 minutes | FOUND-04 | Requires running scheduler for full interval | Start scheduler, wait 15 min, check structlog output for `health.canary.ok` event |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
