---
phase: 05-dashboard
plan: "04"
subsystem: web-dashboard
tags: [dossier, feed, htmx, pain-radar, routes, templates]
dependency_graph:
  requires: [05-03, mis/dossier_repository.py, mis/pain_repository.py]
  provides: [GET /dossier/{id}, GET /dossier/{id}/tab/{tab}, GET /feed, GET /feed/niche/{slug}]
  affects: [mis/web/app.py]
tech_stack:
  added: []
  patterns: [HTMX tab fragments, sqlite3 niche_id lookup adapter, time_ago helper]
key_files:
  created:
    - mis/web/routes/dossier.py
    - mis/web/routes/feed.py
    - mis/web/templates/dossier.html
    - mis/web/templates/dossier_tab_visao_geral.html
    - mis/web/templates/dossier_tab_copy.html
    - mis/web/templates/dossier_tab_anuncios.html
    - mis/web/templates/dossier_tab_reviews.html
    - mis/web/templates/dossier_tab_template.html
    - mis/web/templates/feed.html
    - mis/web/templates/feed_report.html
  modified:
    - mis/web/app.py
decisions:
  - "pain_repository uses niche_id not niche_slug — feed route resolves ID via sqlite3 lookup before calling repository"
  - "dossier tab route returns 200 even when product has no dossier — empty state shown in partial"
  - "feed_report.html interest level badge handles pt and en strings (alto/high, médio/medium, baixo/low)"
metrics:
  duration: "5m"
  completed_date: "2026-03-15"
  tasks: 2
  files: 11
---

# Phase 05 Plan 04: Dossier Detail Page + Pain Feed Summary

Dossier page with 5 HTMX-navigable tabs and feed page with niche selector, history dropdown, and graceful empty states.

## What Was Built

### Task 1: Dossier Detail Page with HTMX Tabs

`GET /dossier/{product_id}` renders a full dossier page with:
- Product header: title, platform, niche, rank position
- Opportunity and confidence scores (badges when present, "Análise em andamento" when not)
- Prev/next navigation by rank
- 5 tabs loaded via `hx-get` targeting `#tab-content`

`GET /dossier/{product_id}/tab/{tab_name}` returns HTMX fragments:
- Valid tabs: `visao-geral`, `copy`, `anuncios`, `reviews`, `template`
- Returns 400 for invalid tab names
- Returns 200 even without dossier (empty state shown in partial)

5 tab templates (all partial — no `{% extends "base.html" %}`):
- `dossier_tab_visao_geral.html`: analysis, pains list, success_factors
- `dossier_tab_copy.html`: headlines, arguments, CTAs, narrative
- `dossier_tab_anuncios.html`: ad cards with copy, date, platform
- `dossier_tab_reviews.html`: IA synthesis, positive/negative lists
- `dossier_tab_template.html`: formatted template text + clipboard copy button

### Task 2: Pain Feed with Niche Tabs and Report History

`GET /feed` renders full page with:
- Niche tabs (hx-get to swap `#feed-report-wrapper`)
- Initial report for first niche loaded inline via `{% include "feed_report.html" %}`
- Empty state when no niches configured

`GET /feed/niche/{slug}` with `HX-Request: true` returns `feed_report.html` partial:
- Signal count, timestamp, time_ago string
- History selector dropdown (hx-get + hx-include for historical report loading)
- Search input with 300ms debounce
- Pains list with interest level badges (alto=red, médio=yellow, baixo=gray)
- Source links (max 3 per pain)
- Empty state when no reports exist

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing critical functionality] pain_repository.get_latest_report uses niche_id not niche_slug**
- **Found during:** Task 2 implementation
- **Issue:** The plan interface contract shows `get_latest_report(db_path, niche_slug: str)` but the actual implementation at `mis/pain_repository.py:20` uses `niche_id: int`. The feed route would fail at runtime with a type mismatch.
- **Fix:** Added `_niche_id_for_slug()` helper in `feed.py` that resolves `slug → niche_id` via sqlite3 before calling the repository. Same pattern applied to `get_historical_reports`.
- **Files modified:** mis/web/routes/feed.py
- **Commit:** 78a2ab4

## Verification Results

```
5 passed (test_web_dossier.py 3/3, test_web_feed.py 2/2)
```

All routers registered in app.py: ranking, dossier, feed, health.

All partial templates (dossier_tab_*.html, feed_report.html) confirmed to NOT contain `{% extends "base.html" %}`.

## Self-Check

Files created:
- mis/web/routes/dossier.py ✓
- mis/web/routes/feed.py ✓
- mis/web/templates/dossier.html ✓
- mis/web/templates/dossier_tab_visao_geral.html ✓
- mis/web/templates/dossier_tab_copy.html ✓
- mis/web/templates/dossier_tab_anuncios.html ✓
- mis/web/templates/dossier_tab_reviews.html ✓
- mis/web/templates/dossier_tab_template.html ✓
- mis/web/templates/feed.html ✓
- mis/web/templates/feed_report.html ✓

Commits:
- 0b698ea feat(05-04): dossier detail page with HTMX tabs
- 78a2ab4 feat(05-04): feed page with niche tabs and pain report history
