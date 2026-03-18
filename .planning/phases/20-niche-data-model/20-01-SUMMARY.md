---
phase: 20-niche-data-model
plan: "01"
subsystem: mis/tests
tags: [tdd, migration, niche, repository, red-tests]
dependency_graph:
  requires: []
  provides:
    - mis/tests/test_migration_008.py
    - mis/tests/test_niche_repository.py
  affects:
    - mis/migrations/_008_niche_v3.py  # Plan 02 must make these GREEN
    - mis/niche_repository.py          # Plan 02 must make these GREEN
tech_stack:
  added: []
  patterns:
    - TDD RED-first (migration test pattern from test_migration_006.py)
    - db_path fixture via tmp_path (conftest.py standard)
key_files:
  created:
    - mis/tests/test_migration_008.py
    - mis/tests/test_niche_repository.py
  modified: []
decisions:
  - "subniche_id=201 (Emagrecimento) used as canonical test anchor for slug assertions"
  - "PerfectPay chosen as unmapped platform sentinel (no marketplace search slugs)"
  - "test_existing_products_preserved uses raw INSERT INTO products to simulate v1/v2 legacy data"
metrics:
  duration: "4 minutes"
  completed: "2026-03-18"
  tasks_completed: 2
  files_created: 2
  files_modified: 0
---

# Phase 20 Plan 01: TDD RED Tests for Migration _008 and Niche Repository Summary

**One-liner:** RED test suite defining migration _008 contract (3 tables, 4 niches, 40+ subniches, platform slug lookups) and niche_repository interface before implementation exists.

## What Was Built

Two test files that define the exact contract Plan 02 must implement:

- `mis/tests/test_migration_008.py` — 7 tests covering: table creation (`niches_v3`, `subniches`, `subniche_platform_slugs`), niche count (4), subniche count (>=40), platform slug lookups (clickbank returns `"health"`, hotmart returns `"saude-e-fitness"` for emagrecimento), idempotency, and backward-compatibility (legacy products preserved).
- `mis/tests/test_niche_repository.py` — 8 tests covering: `list_niches()` returns 4 items with `{id, name, slug}` structure, `list_subniches("saude")` returns >=10 items, `list_subniches("nicho-inexistente")` returns `[]`, `get_platform_slug(201, "hotmart")` returns `"saude-e-fitness"`, `get_platform_slug(201, "clickbank")` returns `"health"`, unmapped platform returns `None`, unknown subniche_id returns `None`.

All 15 tests fail with `ModuleNotFoundError` (state RED) — no implementation files were created.

## Task Commits

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | RED — testes da migration _008 | 30760ac | mis/tests/test_migration_008.py |
| 2 | RED — testes do niche_repository | ec8e1ea | mis/tests/test_niche_repository.py |

## Verification Results

- `python -c "import ast; ast.parse(...)"` on both files: SyntaxOK
- `python -m pytest mis/tests/test_migration_008.py -x -q`: fails with `ModuleNotFoundError: No module named 'mis.migrations._008_niche_v3'` (correct RED state)
- `python -m pytest mis/tests/test_niche_repository.py -x -q`: fails with `ModuleNotFoundError: No module named 'mis.niche_repository'` (correct RED state)
- No implementation files created — Plan 02 responsibility

## Deviations from Plan

None — plan executed exactly as written.

## Key Decisions

1. **subniche_id=201 as test anchor:** Emagrecimento (id=201) has well-defined platform slugs in the research document, making it the safest anchor for slug assertions in both test files.

2. **PerfectPay as unmapped sentinel:** PerfectPay has no marketplace search interface (documented in research), so `get_platform_slug(201, "perfectpay")` correctly tests the None-return path without risk of a future slug mapping invalidating the test.

3. **test_existing_products_preserved uses raw SQL INSERT:** Rather than depending on any product factory or fixture, the test inserts directly into `products` via `db.execute()` to simulate legacy v1/v2 data — matching the exact pattern of the existing migration tests and avoiding coupling to higher-level APIs.

## Next Steps

Plan 02 (`20-02-PLAN.md`) will turn these RED tests GREEN by creating:
- `mis/migrations/_008_niche_v3.py` with `run_migration_008()` + seed data (4 niches, 42 subniches, platform slug mappings)
- `mis/niche_repository.py` with `list_niches()`, `list_subniches()`, `get_platform_slug()`
- Updating `mis/db.py` to register `_008` in the migration chain
