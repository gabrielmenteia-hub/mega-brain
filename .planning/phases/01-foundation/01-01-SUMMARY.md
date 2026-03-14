---
phase: 01-foundation
plan: "01"
subsystem: mis-data-foundation
tags: [sqlite, migrations, tdd, test-infrastructure, schema]
dependency_graph:
  requires: []
  provides:
    - mis.db.get_db
    - mis.db.run_migrations
    - mis.exceptions.ScraperError
    - mis/pytest.ini
    - mis/tests/conftest.py
    - stub-tests-for-01-02-01-03-01-04
  affects:
    - mis/tests/test_base_scraper.py (stubs — consumed by plan 01-02)
    - mis/tests/test_config.py (stubs — consumed by plan 01-03)
    - mis/tests/test_health_monitor.py (stubs — consumed by plan 01-04)
tech_stack:
  added:
    - sqlite-utils 3.39 (installed during execution — was missing from env)
  patterns:
    - idempotent migrations via `if "table_name" not in db.table_names()`
    - PRAGMA WAL + foreign_keys applied on every get_db() call
    - TDD RED-GREEN cycle: stub files first, real tests before implementation
key_files:
  created:
    - mis/__init__.py
    - mis/exceptions.py
    - mis/db.py
    - mis/migrations/__init__.py
    - mis/migrations/_001_initial.py
    - mis/pytest.ini
    - mis/requirements.txt
    - mis/requirements-dev.txt
    - mis/tests/__init__.py
    - mis/tests/conftest.py
    - mis/tests/test_db.py
    - mis/tests/test_base_scraper.py
    - mis/tests/test_config.py
    - mis/tests/test_health_monitor.py
  modified: []
decisions:
  - "Migration filename: _001_initial.py (underscore prefix) — Python cannot import modules starting with a digit; underscore prefix is the cleanest solution without importlib hacks"
  - "Migration location: mis/migrations/_001_initial.py — sub-package follows research recommendation; file naming deviation from plan documented"
  - "DB path in tests: tmp_path/mis.db (real file) — used instead of :memory: to allow get_db() PRAGMA calls to work correctly; :memory: also works but file path is clearer"
  - "sqlite-utils installed during execution: was not present in global Python env; pip install sqlite-utils added during Rule 3 auto-fix"
metrics:
  duration: "~8 minutes"
  completed_date: "2026-03-14T17:29:24Z"
  tasks_completed: 2
  files_created: 14
  files_modified: 1
  test_results: "3 passed, 12 FAILED (stubs)"
---

# Phase 1 Plan 01: Data Foundation Summary

MIS data foundation with 5-table SQLite schema, idempotent migrations via sqlite-utils, ScraperError custom exception, and full test infrastructure (pytest.ini, conftest, 15 stub tests across 4 modules).

## Files Created

| File | Purpose | Key Exports |
|------|---------|-------------|
| `mis/__init__.py` | Module marker | — |
| `mis/exceptions.py` | Custom exceptions | `ScraperError(url, attempts, cause)` |
| `mis/db.py` | DB connection + migration | `get_db(db_path)`, `run_migrations(db_path)` |
| `mis/migrations/__init__.py` | Sub-package marker | — |
| `mis/migrations/_001_initial.py` | Idempotent initial schema | `run_migrations(db_path)` |
| `mis/pytest.ini` | Pytest config | `asyncio_mode=auto`, `testpaths=tests`, `timeout=10` |
| `mis/requirements.txt` | Runtime deps | 10 packages pinned with `>=` |
| `mis/requirements-dev.txt` | Dev/test deps | pytest, pytest-asyncio, respx, pytest-timeout |
| `mis/tests/__init__.py` | Test package marker | — |
| `mis/tests/conftest.py` | Shared fixtures | `db_path`, `temp_config_yaml` |
| `mis/tests/test_db.py` | DB tests (GREEN) | 3 passing tests |
| `mis/tests/test_base_scraper.py` | BaseScraper stubs | 6 RED stubs |
| `mis/tests/test_config.py` | Config loader stubs | 3 RED stubs |
| `mis/tests/test_health_monitor.py` | Health monitor stubs | 3 RED stubs |

## Database Schema (5 Tables)

### `platforms`
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| name | TEXT | NOT NULL |
| slug | TEXT | NOT NULL, UNIQUE INDEX |
| base_url | TEXT | — |
| created_at | TEXT | — |

### `niches`
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| name | TEXT | NOT NULL |
| slug | TEXT | NOT NULL, UNIQUE INDEX |
| created_at | TEXT | — |

### `products`
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| platform_id | INTEGER | FK -> platforms(id) |
| niche_id | INTEGER | FK -> niches(id) |
| external_id | TEXT | — |
| title | TEXT | — |
| url | TEXT | — |
| rank_score | REAL | — |
| price | REAL | — |
| currency | TEXT | — |
| scraped_at | TEXT | — |
| raw_data | TEXT | JSON blob |

Index: `(platform_id, niche_id, scraped_at)`

### `pains`
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| niche_id | INTEGER | FK -> niches(id) |
| source | TEXT | reddit / quora / youtube / trends |
| content | TEXT | — |
| sentiment | TEXT | positive / negative / neutral |
| detected_at | TEXT | — |

### `dossiers`
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| product_id | INTEGER | FK -> products(id) |
| analysis | TEXT | JSON: factors, pains, template |
| opportunity_score | REAL | — |
| confidence_score | REAL | — |
| generated_at | TEXT | — |

## Decisions Made

1. **Migration file named `_001_initial.py`** (not `001_initial.py` as in plan): Python module names cannot start with a digit. Underscore prefix `_001_initial.py` is the standard convention and avoids `importlib` indirection. Plan acknowledged this issue in its own notes.

2. **DB path in tests uses `tmp_path / "mis.db"`** (real file, not `:memory:`): `get_db()` applies `PRAGMA journal_mode=WAL` which returns a result row — both approaches work. Using a real tmp file makes the FK test more realistic (WAL mode is file-based).

3. **sqlite-utils installed on the fly** (Rule 3 auto-fix): Package was in `requirements.txt` but not installed in the global Python environment. Installed during execution: `pip install sqlite-utils`. No architectural change.

## Test Stub Status

| File | Tests | Status | Consumed by |
|------|-------|--------|-------------|
| `test_db.py` | 3 | GREEN (passing) | — (complete) |
| `test_base_scraper.py` | 6 | RED (stubs) | Plan 01-02 |
| `test_config.py` | 3 | RED (stubs) | Plan 01-03 |
| `test_health_monitor.py` | 3 | RED (stubs) | Plan 01-04 |

**Total stubs awaiting implementation:** 12 (across 3 files)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] sqlite-utils not installed in Python environment**
- **Found during:** Task 1 GREEN phase
- **Issue:** `ModuleNotFoundError: No module named 'sqlite_utils'` when running test_db.py
- **Fix:** `pip install sqlite-utils` (3.39 installed successfully)
- **Files modified:** none (runtime dependency install)
- **Commit:** 3c79345

**2. [Rule 1 - Bug] Migration filename changed from `001_initial.py` to `_001_initial.py`**
- **Found during:** Task 1 implementation planning
- **Issue:** Python cannot import modules whose names begin with a digit — `from .migrations.001_initial import ...` is a SyntaxError
- **Fix:** Named file `_001_initial.py`; `mis/db.py` imports as `from .migrations._001_initial import run_migrations`
- **Files modified:** `mis/db.py`, `mis/migrations/_001_initial.py`
- **Commit:** 3c79345

## Verification Results

```
pytest mis/tests/test_db.py -v
3 passed, 113 warnings in 2.88s

pytest mis/tests/ -q
3 passed, 12 failed, 584 warnings in 1.42s
(12 failures are all pytest.fail("not implemented") stubs — expected RED state)
```

## Commits

| Hash | Message |
|------|---------|
| 5452d6f | test(01-01): add test infrastructure and stub files (RED) |
| 3c79345 | feat(01-01): implement ScraperError, DB schema, and migration (GREEN) |

## Self-Check: PASSED
