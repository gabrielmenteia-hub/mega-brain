---
phase: 06-megabrain-integration
plan: "01"
subsystem: mis-bridge
tags: [mis, megabrain, bridge, integration, tdd]
dependency_graph:
  requires: []
  provides: [mis_agent.get_briefing_data, mis_agent.export_to_megabrain]
  affects: [06-02-PLAN.md, mis-briefing-skill, cli-export]
tech_stack:
  added: []
  patterns: [TDD-RED-GREEN, idempotent-export-md5, asyncio-run-canary]
key_files:
  created:
    - mis/mis_agent.py
    - mis/tests/test_mis_agent.py
  modified: []
decisions:
  - "order_by='opportunity_score' rejected — list_dossiers_by_rank uses p.{order_by} prefix (products table only); sorted in Python after fetching top-100"
  - "asyncio.run() wraps run_canary_check() — health score computed synchronously inside get_briefing_data()"
  - "MD5 of rendered Markdown content used for idempotency in export_to_megabrain() — avoids mtime drift on re-export"
metrics:
  duration: 4m
  completed_date: "2026-03-15"
  tasks: 1
  files: 2
---

# Phase 06 Plan 01: MIS/MEGABRAIN Bridge Summary

**One-liner:** MIS/MEGABRAIN bridge with get_briefing_data() aggregating top-10 products + pain reports + health score, and export_to_megabrain() exporting Markdown files via MD5-idempotent writes.

## What Was Built

`mis/mis_agent.py` — the single file that crosses the MIS/MEGABRAIN boundary. Exposes two public functions:

- **`get_briefing_data()`** — aggregates: top-10 products by opportunity_score (Python sort after DB fetch), top-5 pains per niche from latest pain_report, unseen alert count, 0-100 health score (scraper canary 40pts + cycle freshness 30pts + dossiers-today 20pts + alerts-ok 10pts), last_cycle ISO timestamp, data_stale flag.
- **`export_to_megabrain(dest)`** — exports all `status='complete'` dossiers and pain_reports from the last 7 days as Markdown files with YAML frontmatter. Idempotent: computes MD5 of rendered content, skips unchanged files. Generates/updates `README.md` with export metrics.
- **`_init_db()`** called at module import — runs all migrations idempotently, swallows exceptions.

`mis/tests/test_mis_agent.py` — 3 scenarios:
- `test_empty_db` — empty migrated DB returns correct structure (status='ok', products=[], etc.)
- `test_with_data` — seeded DB (12 products, 5 dossiers, 1 pain_report) returns list ≤10 products
- `test_incremental_export` — second identical export call yields exported=0, skipped=N

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] order_by='opportunity_score' causes SQL error**
- **Found during:** Task 1 (GREEN phase)
- **Issue:** `list_dossiers_by_rank()` builds `ORDER BY p.{order_by}` — the `p.` prefix scopes to the `products` table, but `opportunity_score` is a column on `dossiers`. SQL error: `no such column: p.opportunity_score`.
- **Fix:** Fetch top-100 by `rank ASC` (native products column), then sort in Python by `opportunity_score DESC`, slice `[:10]`.
- **Files modified:** `mis/mis_agent.py`
- **Commit:** caaa754

## Verification Results

```
mis/tests/test_mis_agent.py::test_empty_db PASSED
mis/tests/test_mis_agent.py::test_with_data PASSED
mis/tests/test_mis_agent.py::test_incremental_export PASSED
3 passed in 12.03s
```

## Self-Check: PASSED

- `mis/mis_agent.py` — EXISTS
- `mis/tests/test_mis_agent.py` — EXISTS
- Commit `daa723f` (RED tests) — EXISTS
- Commit `caaa754` (GREEN implementation) — EXISTS
