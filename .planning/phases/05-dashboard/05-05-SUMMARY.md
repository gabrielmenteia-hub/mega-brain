---
phase: 05-dashboard
plan: "05"
subsystem: alerts
tags: [alerts, htmx, scanner, top20, badge]
dependency_graph:
  requires: [05-04, alert_repository, scanner]
  provides: [GET /alerts, GET /alerts/badge, POST /alerts/{id}/mark-seen, save_batch_with_alerts]
  affects: [mis/web/app.py, mis/scanner.py, mis/scanners/hotmart.py, mis/scanners/clickbank.py, mis/scanners/kiwify.py]
tech_stack:
  added: []
  patterns: [TDD red-green, HTMX outerHTML swap, FastAPI APIRouter, sqlite3 direct writes]
key_files:
  created:
    - mis/web/routes/alerts.py
    - mis/web/templates/alerts.html
    - mis/web/templates/alerts_badge.html
    - mis/tests/test_scanner_alerts.py
  modified:
    - mis/web/app.py
    - mis/scanner.py
    - mis/scanners/hotmart.py
    - mis/scanners/clickbank.py
    - mis/scanners/kiwify.py
decisions:
  - alerts router registered in app.py between feed and health routers
  - alerts_badge.html is a partial fragment (no extends base.html) — required for HTMX outerHTML swap
  - save_batch_with_alerts captures pre-upsert ranks to detect genuine new top-20 entries (not re-entries)
  - Brand-new products (old_rank=None) with rank<=20 also trigger alert — first appearance counts as entry
metrics:
  duration: 6m
  completed_date: "2026-03-15"
  tasks: 2
  files: 9
---

# Phase 05 Plan 05: Alerts System Summary

**One-liner:** FastAPI alerts routes + HTMX badge polling + save_batch_with_alerts() auto-trigger for top-20 entrants across 3 scanners.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 (RED) | Existing test file confirmed RED (404 before router) | pre-existing | tests/web/test_web_alerts.py |
| 1 (GREEN) | Alerts routes, templates, app.py wiring | bea020c | alerts.py, alerts.html, alerts_badge.html, app.py |
| 2 (RED) | Failing tests for save_batch_with_alerts | bea55ad | tests/test_scanner_alerts.py |
| 2 (GREEN) | save_batch_with_alerts + 3 scanner updates | 4a48571 | scanner.py, hotmart.py, clickbank.py, kiwify.py |

## What Was Built

**Task 1 — Alerts Routes & Templates:**
- `GET /alerts`: expires stale alerts first, queries `alerts JOIN products`, renders `alerts.html` with seen/unseen list and unseen count badge
- `GET /alerts/badge`: returns HTMX partial fragment `alerts_badge.html` (no base.html extension) — compatible with outerHTML swap
- `POST /alerts/{id}/mark-seen`: calls `mark_seen()`, returns 404 if not found, 303 redirect to /alerts on success
- `alerts_badge.html`: outer `<span id="alerts-badge">` preserved so HTMX `hx-swap="outerHTML"` replaces the whole span correctly
- `app.py`: all 5 routers registered (ranking, dossier, feed, alerts, health)

**Task 2 — save_batch_with_alerts & Scanner Wiring:**
- `save_batch_with_alerts(db, db_path, products)` in `mis/scanner.py`: captures pre-upsert ranks, calls `save_batch()`, then calls `create_alert()` for each product that newly entered the top 20
- Top-20 detection: `old_rank is None` (brand new) OR `old_rank > 20` (was outside) → alert created
- Already in top 20 (`old_rank <= 20`) → skipped, no duplicate alert
- Three scanners updated: hotmart.py, clickbank.py, kiwify.py now call `save_batch_with_alerts` instead of `save_batch` from product_repository

## Verification Results

- `tests/web/test_web_alerts.py`: 3/3 GREEN (GET /alerts 200, GET /alerts/badge 200, POST mark-seen 200/404)
- `tests/test_scanner_alerts.py`: 4/4 GREEN (entry from rank>20, already top20 skip, new product, outside top20)
- `tests/web/` full suite: 21/21 GREEN
- Combined alerts suite: 29/29 GREEN
- Scanner grep check: `from mis.product_repository import save_batch` not found in any scanner

## Deviations from Plan

None — plan executed exactly as written. The TemplateResponse deprecation warning (positional `name` vs `request`) is a pre-existing condition affecting all routes, not introduced by this plan.

## Pre-Existing Issues (Out of Scope)

- `test_cli_spy_help` fails with `No module named mis` in system Python (C:\Python314) — mis package not installed there. Pre-existing, unrelated to this plan.

## Self-Check: PASSED
