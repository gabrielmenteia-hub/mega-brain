---
phase: 05-dashboard
plan: "02"
subsystem: data-layer
tags: [sqlite, migrations, repositories, alerts, dossiers, pain-radar, dashboard]
dependency_graph:
  requires: [05-01]
  provides: [alerts-table, alert-repository, dossier-repository, pain-repository]
  affects: [05-03, 05-05]
tech_stack:
  added: []
  patterns: [sqlite3-autocommit, repository-pattern, 24h-idempotency, left-join-pagination]
key_files:
  created:
    - mis/migrations/_005_alerts.py
    - mis/alert_repository.py
    - mis/dossier_repository.py
    - mis/pain_repository.py
  modified:
    - mis/db.py
    - mis/tests/test_db.py
decisions:
  - "[05-02]: get_db() changed to use isolation_level=None (autocommit) — multi-connection pattern in web repositories requires writes to be immediately visible without explicit commit calls"
  - "[05-02]: alert_repository uses sqlite3.connect directly (not get_db/sqlite_utils) — avoids WAL write-lock conflicts when tests use uncommitted get_db connections"
  - "[05-02]: created_at column added to dossiers in _005 migration — was missing from _003 which only added status, dossier_json, ads_json, incomplete, updated_at"
  - "[05-02]: create_alert idempotency uses 24h window on (product_id, position) — prevents alert spam on repeated radar cycles"
  - "[05-02]: test_db.py uses issubset instead of == for table name check — sqlite_sequence appears as system table when AUTOINCREMENT is used"
metrics:
  duration: "15m"
  completed_date: "2026-03-15"
  tasks_completed: 2
  files_created: 4
  files_modified: 2
---

# Phase 05 Plan 02: Dashboard Data Layer Summary

**One-liner:** Migration _005 (alerts table), 3 web repositories (alert/dossier/pain), and get_db autocommit fix for multi-connection correctness.

## What Was Built

### Task 1: Migration _005 + db.py chain

`mis/migrations/_005_alerts.py` creates the `alerts` table idempotently with `CREATE TABLE IF NOT EXISTS`. Schema: `id PK AUTOINCREMENT, product_id NOT NULL, platform_slug, niche_slug, position NOT NULL, seen DEFAULT 0, created_at NOT NULL, expires_at NOT NULL`. Two indexes: `idx_alerts_created(created_at)` and `idx_alerts_seen(seen, expires_at)`.

Also adds `created_at` column to `dossiers` if absent — this column was missing from migration _003 but is referenced in test fixtures.

`mis/db.py` updated to import and call `_run_005(db_path)` at the end of `run_migrations()`. The chain is now `_001 → _002 → _003 → _004 → _005`.

`get_db()` was updated to use `isolation_level=None` (autocommit) by passing a `sqlite3.connect(..., isolation_level=None)` connection to `sqlite_utils.Database`. This enables multi-connection patterns where repository reads must see data inserted by the caller's connection.

### Task 2: 3 Web Repositories

**`mis/alert_repository.py`** — uses `sqlite3.connect` directly (not `get_db`) to avoid WAL write-lock conflicts.
- `create_alert(db_path, product_id, position, platform_slug=None, niche_slug=None)` — 24h idempotency on `(product_id, position)`, expires_at = now + 7 days
- `get_unseen_count(db_path)` — COUNT(*) WHERE seen=0 AND expires_at > now
- `mark_seen(db_path, alert_id)` — UPDATE seen=1, returns bool
- `expire_old_alerts(db_path)` — DELETE WHERE expires_at < now, returns count deleted

**`mis/dossier_repository.py`** — uses `get_db` (sqlite_utils).
- `get_dossier_by_product_id(db_path, product_id)` — returns None or dict with dossier_json/ads_json/copy_json/reviews_json parsed
- `list_dossiers_by_rank(db_path, platform=None, niche=None, order_by="rank", order_dir="asc", per_page=20, page=1)` — LEFT JOIN products+dossiers+platforms+niches, returns `has_dossier` bool

**`mis/pain_repository.py`** — uses `get_db` (sqlite_utils).
- `get_latest_report(db_path, niche_id)` — most recent pain_report by niche_id, includes parsed `report` and `signal_count`
- `get_historical_reports(db_path, niche_id, limit=48)` — list of `{id, cycle_at}` dicts, no report_json

## Test Results

8 repository tests GREEN (4 alert + 2 dossier + 2 pain) + 3 db tests GREEN = 11 total.

```
tests/web/test_alert_repository.py      4/4 PASS
tests/web/test_dossier_repository.py    2/2 PASS
tests/web/test_pain_repository.py       2/2 PASS
tests/test_db.py                        3/3 PASS
```

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] get_db() lacked autocommit — multi-connection visibility broken**
- **Found during:** Task 2 — alert repository tests failing with empty SELECT after INSERT
- **Issue:** `sqlite_utils.Database(db_path)` opens a connection that begins transactions implicitly. When the test inserted via `get_db()` without commit, a second `get_db()` (or `sqlite3.connect`) opened in the repository could not see the uncommitted data.
- **Fix:** Changed `get_db()` to create a `sqlite3.connect(db_path, isolation_level=None)` connection (autocommit) and wrap it in `sqlite_utils.Database(conn)`. FK enforcement verified to still work.
- **Files modified:** `mis/db.py`
- **Commit:** 636fb1c

**2. [Rule 2 - Missing Functionality] dossiers table missing `created_at` column**
- **Found during:** Task 2 — test fixture `INSERT INTO dossiers (product_id, status, created_at)` failing with `OperationalError: table dossiers has no column named created_at`
- **Issue:** Migration _003 added `status, dossier_json, ads_json, incomplete, updated_at` but not `created_at`. The test contracts (written in 05-01) expected this column to exist.
- **Fix:** Added `created_at` column to `dossiers` in migration _005 via `add_column()` if absent.
- **Files modified:** `mis/migrations/_005_alerts.py`
- **Commit:** 636fb1c

**3. [Rule 1 - Bug] test_db.py table set comparison too strict**
- **Found during:** Task 1 verification — `test_all_tables_exist` asserting `set(tables) == expected` but `sqlite_sequence` system table appeared due to AUTOINCREMENT.
- **Fix:** Changed assertion to `expected.issubset(set(db.table_names()))`. Updated table count from 10 to 11 (adding `alerts`).
- **Files modified:** `mis/tests/test_db.py`
- **Commit:** 636fb1c

**4. [Rule 1 - Bug] alert_repository contract assinatura diferente do plano**
- **Found during:** Task 2 — testes usam `create_alert(db_path, product_id=1, position=5)` (sem platform_slug/niche_slug obrigatórios) mas o plano especificava assinatura com todos os campos obrigatórios.
- **Fix:** `platform_slug` e `niche_slug` tornados opcionais com default `None`. Assinatura compatível com testes e plano.
- **Files modified:** `mis/alert_repository.py`
- **Commit:** 636fb1c

**5. [Rule 1 - Bug] pain_repository assinatura usa niche_id (não niche_slug)**
- **Found during:** Task 2 — testes usam `get_latest_report(db_path, niche_id=1)` mas o plano especificava `niche_slug`.
- **Fix:** Implementado com `niche_id` conforme contrato dos testes. Para `signal_count`, o niche_slug é resolvido via JOIN interno.
- **Files modified:** `mis/pain_repository.py`
- **Commit:** 636fb1c

## Self-Check: PASSED

| Item | Status |
|------|--------|
| mis/migrations/_005_alerts.py | FOUND |
| mis/alert_repository.py | FOUND |
| mis/dossier_repository.py | FOUND |
| mis/pain_repository.py | FOUND |
| Commit be4c57c (Task 1) | FOUND |
| Commit 636fb1c (Task 2) | FOUND |
| 11 tests GREEN | VERIFIED |
