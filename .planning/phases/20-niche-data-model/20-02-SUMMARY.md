---
phase: 20-niche-data-model
plan: "02"
subsystem: mis/migrations + mis/niche_repository
tags: [tdd, migration, niche, repository, green-tests, seed-data]
dependency_graph:
  requires:
    - 20-01  # RED tests created in Plan 01
  provides:
    - mis/migrations/_008_niche_v3.py
    - mis/niche_repository.py
    - mis/db.py (updated)
  affects:
    - mis/db.py
    - Phase 21 (Manual Search Engine) — consumes list_subniches, get_platform_slug
tech_stack:
  added: []
  patterns:
    - TDD GREEN (turning RED tests from Plan 01 to GREEN)
    - SQLite idempotent migration with fast-path COUNT check
    - sqlite_utils for DDL + DML in migrations
    - Pure function repository pattern (db_path in, list[dict] out)
key_files:
  created:
    - mis/migrations/_008_niche_v3.py
    - mis/niche_repository.py
  modified:
    - mis/db.py
decisions:
  - "Idempotent fast-path via COUNT check instead of INSERT OR IGNORE only — avoids write lock when another connection has a pending transaction on same db file"
  - "44 subniches (10+12+10+12) seeded — plan description said 42 but task action listed 44; the explicit list is the authoritative contract"
  - "396 platform slug mappings (44 × 9 platforms with public marketplace) — consistent with actual subniche count"
metrics:
  duration: "22 minutes"
  completed: "2026-03-18"
  tasks_completed: 2
  files_created: 2
  files_modified: 1
---

# Phase 20 Plan 02: Migration _008 + niche_repository Implementation Summary

**One-liner:** Migration _008 seeds 4 niches, 44 subniches and 396 platform slug mappings into SQLite; niche_repository provides 3 pure query functions — all 15 RED tests from Plan 01 are now GREEN.

## What Was Built

### mis/migrations/_008_niche_v3.py

Migration function `run_migration_008(db_path)` that:
- Creates `niches_v3` table (id PK, name, slug with unique index)
- Creates `subniches` table (id PK, niche_id FK, name, slug with composite unique index)
- Creates `subniche_platform_slugs` table (subniche_id + platform_id composite PK, search_slug)
- Seeds 4 niches with fixed IDs 1-4 (Relacionamento, Saúde, Finanças, Renda Extra)
- Seeds 44 subniches with fixed IDs (101-110, 201-212, 301-310, 401-412)
- Seeds 396 platform slug mappings (44 subniches × 9 platforms: hotmart, clickbank, kiwify, braip, udemy, gumroad, appsumo, product_hunt, jvzoo)
- PerfectPay (id=6), Eduzz (id=4) and Monetizze (id=5) have no mappings (checkout-only/403)

### mis/niche_repository.py

Three pure query functions:
- `list_niches(db_path)` — returns all 4 niches as `[{"id": int, "name": str, "slug": str}]`
- `list_subniches(db_path, niche_slug)` — returns subniches for a niche or `[]` if not found
- `get_platform_slug(db_path, subniche_id, platform_slug)` — returns `str | None`

### mis/db.py

Added import and call for `_run_008` at end of `run_migrations()` chain after `_run_007`.

## Task Commits

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Migration _008 com seed data completo | c8401f0 | mis/migrations/_008_niche_v3.py, mis/db.py |
| 2 | niche_repository.py + wiring em db.py | 98ec965 | mis/niche_repository.py |

## Verification Results

- `python -m pytest mis/tests/test_migration_008.py mis/tests/test_niche_repository.py -q`: **15 passed**
- `python -m pytest mis/tests/ -q`: **263 passed, 0 failed** (full suite, zero regressions)
- Banco: nichos=4, subnichos=44, slugs mapeados=396

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Write lock deadlock on idempotent migration call**
- **Found during:** Task 1 — `test_existing_products_preserved` timeout
- **Issue:** `test_existing_products_preserved` opens a `sqlite_utils.Database` connection, executes INSERT without commit (creating a pending write transaction), then calls `run_migration_008()` which opens a second connection and tries to execute `INSERT OR IGNORE`. SQLite does not allow two simultaneous writers — second connection blocks indefinitely.
- **Fix:** Added a COUNT-based fast-path: check `SELECT COUNT(*) FROM niches_v3` before attempting any INSERT loop. If data is already fully populated, skip all DML writes entirely. On the second (idempotent) call, only SELECTs are executed — no write lock needed.
- **Files modified:** `mis/migrations/_008_niche_v3.py`
- **Commit:** c8401f0

### Seed Data Count Discrepancy (not a bug)

The plan description said "42 subnichos" but the explicit `_SUBNICHES` list in the task action contains 44 entries (10 Relacionamento + 12 Saúde + 10 Finanças + 12 Renda Extra = 44). The tests only require `>= 40`, which passes. The explicit list is authoritative — 44 subnichos and 396 slug mappings were seeded.

## Key Decisions

1. **Idempotent fast-path via COUNT:** Using `SELECT COUNT(*) FROM niches_v3` to detect already-seeded data avoids acquiring a write lock on repeated calls. This is safer than relying on `INSERT OR IGNORE` alone, which still needs a RESERVED lock even when ignoring all rows.

2. **44 subniches, not 42:** The plan narrative mentioned 42 but the task action's explicit `_SUBNICHES` list contained 44 entries. The explicit list is the authoritative contract — it was seeded as specified.

3. **9 platform mappings per subniche:** hotmart, clickbank, kiwify, braip, udemy, gumroad, appsumo, product_hunt (always "trending"), jvzoo (always "84") — 396 total rows.

## Next Steps

Phase 21 (Manual Search Engine) can now consume:
- `list_subniches(db_path, niche_slug)` to populate subniche selector UI
- `get_platform_slug(db_path, subniche_id, platform_slug)` to build platform-specific search URLs
