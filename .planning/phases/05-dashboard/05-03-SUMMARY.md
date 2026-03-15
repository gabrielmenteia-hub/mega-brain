---
phase: 05-dashboard
plan: "03"
subsystem: ui
tags: [fastapi, jinja2, htmx, tailwind, uvicorn, dashboard]

requires:
  - phase: 05-02
    provides: dossier_repository.list_dossiers_by_rank(), alert_repository, pain_repository, _005 migration

provides:
  - FastAPI app factory create_app(db_path) in mis/web/app.py
  - GET /ranking with platform/niche/per_page/page query filters
  - GET /ranking/table HTMX partial (no base layout)
  - GET /health endpoint with scheduler job listing
  - Jinja2 templates: base.html (Tailwind + HTMX CDN, dark mode), ranking.html, ranking_table.html, health.html
  - mis/__main__.py dashboard subcommand (uvicorn runner, --host/--port)

affects: [05-04, 05-05, web routes, templates]

tech-stack:
  added: [fastapi[standard], uvicorn, jinja2, aiofiles]
  patterns:
    - FastAPI app factory with app.state for db_path and templates injection
    - HTMX partial via is_htmx() helper checking HX-Request header
    - TemplateResponse(request=request, name=..., context=...) new-style API
    - db_path != ':memory:' guard to skip migrations when using in-memory test DB

key-files:
  created:
    - mis/web/__init__.py
    - mis/web/app.py
    - mis/web/routes/__init__.py
    - mis/web/routes/ranking.py
    - mis/web/routes/health.py
    - mis/web/templates/base.html
    - mis/web/templates/ranking.html
    - mis/web/templates/ranking_table.html
    - mis/web/templates/health.html
    - mis/web/static/app.js
  modified:
    - mis/__main__.py

key-decisions:
  - "db_path != ':memory:' guard in create_app skips run_migrations — each migration creates a separate sqlite_utils.Database(:memory:) connection, making in-memory chaining impossible; test conftest uses real tmp file"
  - "app.state injection for db_path and templates — avoids global state and enables clean TestClient testing"
  - "ranking_table.html has no {% extends %} — pure HTMX fragment returned by both /ranking (HTMX) and /ranking/table (always)"

patterns-established:
  - "is_htmx(request): return request.headers.get('HX-Request') == 'true' — shared helper across all route modules"
  - "Jinja2Templates stored in app.state.templates — accessible in every route via request.app.state.templates"

requirements-completed: [DASH-01, SCAN-05]

duration: 18min
completed: 2026-03-15
---

# Phase 05 Plan 03: Dashboard Web Layer Summary

**FastAPI app factory with Jinja2/HTMX ranking dashboard, platform/niche filters, and `python -m mis dashboard` CLI subcommand**

## Performance

- **Duration:** 18 min
- **Started:** 2026-03-15T18:25:00Z
- **Completed:** 2026-03-15T18:43:00Z
- **Tasks:** 1
- **Files modified:** 11

## Accomplishments

- FastAPI `create_app(db_path)` factory with StaticFiles, Jinja2Templates, and route inclusion
- `/ranking` page with platform/niche/per_page/page filters, HTMX-driven table swap
- `/ranking/table` dedicated partial endpoint (always returns fragment without navbar)
- Dark-mode base layout with Tailwind CDN, HTMX CDN, navbar with 3 links + alerts badge polling
- CLI `dashboard` subcommand wires uvicorn to the app factory
- 5/5 test_web_ranking.py GREEN, 13/13 full web suite GREEN

## Task Commits

1. **Task 1: FastAPI app factory + ranking page + dashboard CLI** - `6f4acb2` (feat)

## Files Created/Modified

- `mis/web/__init__.py` - Package marker
- `mis/web/app.py` - create_app() factory; mounts /static, includes routers, redirects / -> /ranking
- `mis/web/routes/__init__.py` - Package marker
- `mis/web/routes/ranking.py` - GET /ranking and GET /ranking/table with HTMX detection
- `mis/web/routes/health.py` - GET /health with optional scheduler job listing
- `mis/web/templates/base.html` - Dark layout: Tailwind CDN, HTMX CDN, navbar, footer /health link
- `mis/web/templates/ranking.html` - Extends base; platform/niche/per_page selectors + HTMX table swap
- `mis/web/templates/ranking_table.html` - HTMX fragment: table with rank/title/platform/niche/score + Pendente badge
- `mis/web/templates/health.html` - Extends base; sistema operacional + scheduler jobs list
- `mis/web/static/app.js` - Clipboard copy handler
- `mis/__main__.py` - Added dashboard subparser (--host, --port) and _handle_dashboard()

## Decisions Made

- `db_path != ':memory:'` guard in `create_app` skips `run_migrations` — sqlite_utils opens a fresh in-memory DB per call, so chaining _001 through _005 would produce 5 separate empty DBs. Test conftest uses real `tmp_path` files.
- `app.state` for `db_path` and `templates` — clean injection without globals; TestClient sets state at construction time.
- `ranking_table.html` has no `{% extends %}` — pure Jinja2 fragment for HTMX. Both `GET /ranking` (when HTMX) and `GET /ranking/table` (always) render this template directly.

## Deviations from Plan

None — plan executed exactly as written, with one minor Rule 1 fix:

### Auto-fixed Issues

**1. [Rule 1 - Bug] :memory: multi-connection guard in create_app**
- **Found during:** Task 1 (verification step)
- **Issue:** `create_app(':memory:')` raised RuntimeError because `run_migrations` chains 5 separate `sqlite_utils.Database(':memory:')` calls — each gets an isolated in-memory DB
- **Fix:** Added `if db_path != ':memory:': run_migrations(db_path)` guard; callers must pre-migrate real DB paths
- **Files modified:** mis/web/app.py
- **Verification:** `python -c "from mis.web.app import create_app; app = create_app(':memory:'); print('OK')"` returns OK
- **Committed in:** 6f4acb2 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - bug)
**Impact on plan:** Fix necessary for verification criterion `create_app(':memory:')`. No scope creep.

## Issues Encountered

None beyond the :memory: guard above.

## Next Phase Readiness

- `GET /ranking` functional with HTMX partial swap — 05-04 (Feed de Dores) and 05-05 (Alertas) can build on `base.html` and `create_app` pattern
- `/dossier/{id}` route referenced in `ranking_table.html` links — needs 05-04 or 05-05 to implement
- `/alerts/badge` HTMX polling endpoint referenced in navbar — unimplemented until alerts plan

---
*Phase: 05-dashboard*
*Completed: 2026-03-15*
