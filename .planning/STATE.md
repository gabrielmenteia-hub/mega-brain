---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: executing
stopped_at: Completed 08-foundation-verification/08-01-PLAN.md
last_updated: "2026-03-16T00:30:19.857Z"
last_activity: "2026-03-14 — Plan 02-02 complete: ClickBankScanner via GraphQL API, gravity scores without auth, 5/5 tests GREEN, 25/25 full suite GREEN."
progress:
  total_phases: 9
  completed_phases: 8
  total_plans: 26
  completed_plans: 26
---

---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: executing
stopped_at: Completed 02-platform-scanners/02-01-PLAN.md
last_updated: "2026-03-14T21:54:37.566Z"
last_activity: "2026-03-14 — Plan 01-04 complete: health_monitor with run_canary_check(), register_canary_job(), 15/15 tests GREEN. Phase 1 complete."
progress:
  total_phases: 6
  completed_phases: 1
  total_plans: 7
  completed_plans: 5
  percent: 71
---

---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: executing
stopped_at: Completed 01-foundation/01-03-PLAN.md
last_updated: "2026-03-14T17:49:22.628Z"
last_activity: "2026-03-14 — Plan 01-02 complete: BaseScraper with httpx async, tenacity retry, Semaphore rate limiting, stealth Playwright"
progress:
  [███████░░░] 71%
  completed_phases: 0
  total_plans: 4
  completed_plans: 3
  percent: 75
---

---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: executing
stopped_at: "Completed 01-foundation/01-02-PLAN.md"
last_updated: "2026-03-14T17:39:06Z"
last_activity: "2026-03-14 — Plan 01-02 complete: BaseScraper with httpx async, tenacity retry, Semaphore rate limiting, stealth Playwright"
progress:
  [████████░░] 75%
  completed_phases: 0
  total_plans: 4
  completed_plans: 2
  percent: 8
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-14)

**Core value:** Entregar o mapa completo do que está vendendo e por que está vendendo — sem esforço manual — para que o usuário possa modelar e lançar seus próprios produtos com máxima vantagem competitiva.
**Current focus:** Phase 2 — Platform Scanners

## Current Position

Phase: 2 of 6 (Platform Scanners)
Plan: 2 of 3 in current phase — IN PROGRESS
Status: Executing
Last activity: 2026-03-14 — Plan 02-02 complete: ClickBankScanner via GraphQL API, gravity scores without auth, 5/5 tests GREEN, 25/25 full suite GREEN.

Progress: [████████░░░░░░░░░░░░] 40% (2/6 phases, 7/7 plans complete in P1+P2 so far)

## Performance Metrics

**Velocity:**
- Total plans completed: 1
- Average duration: ~8 minutes
- Total execution time: 0.13h

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01-foundation | 2/4 | ~18m | ~9m |

**Recent Trend:**
- Last 5 plans: 01-01 (~8m), 01-02 (~10m)
- Trend: baseline

*Updated after each plan completion*
| Phase 01-foundation P03 | 4m | 2 tasks | 4 files |
| Phase 01-foundation P04 | 5m | 2 tasks | 2 files |
| Phase 02-platform-scanners P01 | 17 | 2 tasks | 11 files |
| Phase 02-platform-scanners P02 | 28m | 2 tasks | 6 files |
| Phase 02-platform-scanners P03 | 635 | 2 tasks | 9 files |
| Phase 03-product-espionage-dossiers P01 | 7 | 2 tasks | 12 files |
| Phase 03-product-espionage-dossiers P02 | 12 | 2 tasks | 6 files |
| Phase 03-product-espionage-dossiers P03 | 5 | 1 tasks | 2 files |
| Phase 03-product-espionage-dossiers P04 | 10 | 2 tasks | 9 files |
| Phase 03-product-espionage-dossiers P05 | 10 | 2 tasks | 5 files |
| Phase 04-pain-radar P01 | 10 | 2 tasks | 12 files |
| Phase 04-pain-radar P03 | 10 | 1 tasks | 3 files |
| Phase 04-pain-radar P02 | 13 | 2 tasks | 7 files |
| Phase 04-pain-radar P04 | 14 | 1 tasks | 3 files |
| Phase 04-pain-radar P05 | 7 | 2 tasks | 3 files |
| Phase 05-dashboard P01 | 12 | 2 tasks | 9 files |
| Phase 05-dashboard P02 | 15 | 2 tasks | 6 files |
| Phase 05-dashboard P03 | 18 | 1 tasks | 11 files |
| Phase 05-dashboard P04 | 5 | 2 tasks | 11 files |
| Phase 05-dashboard P05 | 6m | 2 tasks | 9 files |
| Phase 06-megabrain-integration P01 | 4m | 1 tasks | 2 files |
| Phase 06-megabrain-integration P02 | 8 | 2 tasks | 3 files |
| Phase 07-mis-integration-bugfixes P01 | 12 | 3 tasks | 5 files |
| Phase 08-foundation-verification P01 | 13 | 3 tasks | 7 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Init]: Dashboard web separado do MEGABRAIN CLI — UX para consumo rápido de dados visuais requer interface dedicada (Pending)
- [Init]: Scraping vs APIs oficiais para plataformas BR — APIs inexistentes, scraping é o caminho viável (Pending)
- [Init]: Ciclo horário para radar de dores — frequência suficiente sem sobrecarregar APIs (Pending)
- [01-01]: Migration file named _001_initial.py (underscore prefix) — Python cannot import modules starting with a digit
- [01-01]: DB path in tests uses tmp_path/mis.db (real file) — cleaner than :memory: for FK PRAGMA tests
- [01-01]: sqlite-utils installed during execution (was missing from global Python env)
- [01-02]: Tenacity @retry as nested inner function inside fetch() — cleaner ScraperError wrapping after reraise=True
- [01-02]: h2 package installed (httpx[http2]) — required for HTTP/2 support, was missing from environment
- [Phase 01-foundation]: config.yaml path relative to mis/config.py via Path(__file__).parent — portable without CWD assumptions
- [Phase 01-foundation]: APScheduler singleton via _scheduler global + get_scheduler() — health monitor and scrapers share one scheduler instance
- [01-04]: run_canary_check() never propagates exceptions — always returns bool; alert field in structlog payloads is machine-readable key for external parsing
- [01-04]: register_canary_job() uses replace_existing=True — safe to call at startup or on re-registration without duplicate job errors
- [Phase 02-platform-scanners]: KIWIFY_PLATFORM_ID=3 (convention: 1=Hotmart, 2=ClickBank, 3=Kiwify — no seed data in DB schema)
- [Phase 02-platform-scanners]: UPDATE-then-INSERT upsert pattern for products table — autoincrement id PK from _001 prevents sqlite-utils composite-pk upsert
- [Phase 02-platform-scanners]: Kiwify fixtures are synthetic HTML — marketplace has no public URL (404), API requires auth token
- [02-02]: ClickBank marketplace is React SPA with GraphQL API (not SSR) — gravity available without auth via POST /graphql
- [02-02]: CLICKBANK_PLATFORM_ID=2 (convention: 1=Hotmart, 2=ClickBank, 3=Kiwify)
- [02-02]: external_id for ClickBank = 'site' field (vendor ID, e.g. BRAINSONGX) — stable and unique
- [02-02]: rank = int(gravity) — ClickBank gravity float score stored as int; positional fallback when None
- [Phase 02-platform-scanners]: HOTMART_PLATFORM_ID=1 (convention: 1=Hotmart, 2=ClickBank, 3=Kiwify)
- [Phase 02-platform-scanners]: Hotmart marketplace confirmed SSR — httpx sufficient, Playwright not needed (live inspection 2026-03-14)
- [Phase 02-platform-scanners]: register_scanner_jobs() uses CronTrigger.from_crontab() reading scan_schedule from config.settings
- [Phase 03-01]: ads_json stored as TEXT column in dossiers (not separate table) for MVP — avoids schema complexity for unstructured Meta Ad Library JSON
- [Phase 03-01]: db.py run_migrations() chains _001→_002→_003 — callers get full schema with one call
- [Phase 03-01]: SalesPageScraper uses LLM-as-universal-parser — no platform-specific selectors, works with any sales page URL
- [Phase 03-02]: MetaAdsScraper nao herda BaseScraper — usa httpx.AsyncClient direto (API REST vs scraping)
- [Phase 03-02]: ad_reached_countries=BR hardcoded obrigatorio — sem ele Meta API retorna 400
- [Phase 03-02]: ReviewsScraper retorna [] em ScraperError — reviews nao e gate bloqueante no pipeline
- [Phase 03-03]: copy is blocking at 100-char threshold — prevents LLM from running on empty or trivial pages
- [Phase 03-03]: confidence_score independent of gate_passed — enables partial dossier generation (confidence>0, gate=False) when copy present but reviews insufficient
- [Phase 03-03]: min_reviews=10 configurable default — gate contract is (gate_passed, confidence_score) tuple for downstream LLM pipeline
- [Phase 03-product-espionage-dossiers]: Env var ANTHROPIC_API_KEY injetada via monkeypatch nos testes — evita dependência de credenciais reais
- [Phase 03-product-espionage-dossiers]: cost_usd calculado com preços claude-sonnet-4-6 (input 0.000003/token, output 0.000015/token)
- [Phase 03-product-espionage-dossiers]: SPY_TOP_N=10 hardcoded in spy_orchestrator — not configurable by user decision
- [Phase 03-product-espionage-dossiers]: MIS_DB_PATH env var as DB path source in orchestrator — enables clean test isolation
- [Phase 03-product-espionage-dossiers]: run_spy_url uses PRAGMA foreign_keys=OFF for null platform/niche product insertion
- [Phase 04-01]: INSERT OR IGNORE as upsert pattern for pain_signals — UNIQUE index on url_hash sufficient for idempotency without sqlite-utils pk-based upsert
- [Phase 04-01]: Wave 0 test scaffolds import at module level to enforce ImportError as RED failure mode — ensures pytest collection validates when modules exist
- [Phase 04-01]: config.yaml radar block uses relevance_language=pt for all niches — project targets BR market
- [Phase 04-pain-radar]: asyncio.get_event_loop().run_in_executor() wraps googleapiclient — blocking sync library; no async wrapper available
- [Phase 04-pain-radar]: youtube_quota_log persists in SQLite DB not module variable — critical for correctness across process restarts
- [Phase 04-pain-radar]: Quota re-checked before each keyword iteration in collect_youtube_signals — prevents mid-niche overage when multiple keywords processed
- [Phase 04-02]: asyncio.sleep must be patched in TDD tests for TrendsCollector — 5-10s real sleep would make test suite impractically slow
- [Phase 04-02]: PRAW wrapped in run_in_executor — synchronous library; executor prevents blocking async event loop
- [Phase 04-02]: QuoraCollector uses len(html)<5000 threshold for empty SPA shell detection — React app shell is 2-4KB without content
- [Phase 04-pain-radar]: sqlite3 direct connection used for upsert instead of sqlite_utils.Database — context manager protocol not supported in installed version
- [Phase 04-pain-radar]: pain_synthesis_prompt.txt uses double braces {{}} for JSON literal in format string to avoid KeyError in Python str.format()
- [Phase 04-pain-radar]: Explicit remove-before-add in register_radar_jobs — APScheduler 3.x replace_existing only works on running scheduler, not paused
- [Phase 04-pain-radar]: db_path from MIS_DB_PATH env var in register_radar_jobs — consistent with spy_orchestrator pattern
- [Phase 05-dashboard]: Deferred imports inside test functions (not module level) for repository tests — allows pytest collection while still failing RED at runtime
- [Phase 05-dashboard]: fastapi[standard] + uvicorn + jinja2 + aiofiles installed as web layer dependencies during Wave 0 test scaffold
- [Phase 05-02]: get_db() changed to use isolation_level=None (autocommit) — multi-connection pattern in web repositories requires writes to be immediately visible
- [Phase 05-02]: alert_repository uses sqlite3.connect directly — avoids WAL write-lock conflicts when tests use uncommitted get_db connections
- [Phase 05-02]: created_at column added to dossiers in _005 migration — was missing from _003 (status+dossier_json only)
- [Phase 05-dashboard]: db_path != ':memory:' guard in create_app — sqlite_utils creates isolated in-memory DB per call; test conftest uses real tmp file
- [Phase 05-dashboard]: app.state injection for db_path and templates — avoids global state, enables clean TestClient testing
- [Phase 05-dashboard]: pain_repository uses niche_id not niche_slug — feed route resolves ID via sqlite3 lookup before calling repository
- [Phase 05-dashboard]: alerts_badge.html is a partial fragment (no extends base.html) — required for HTMX outerHTML swap to replace span correctly
- [Phase 05-dashboard]: save_batch_with_alerts captures pre-upsert ranks to detect genuine new top-20 entries; brand-new products with rank<=20 also trigger alerts
- [Phase 06-01]: order_by='opportunity_score' rejected — list_dossiers_by_rank uses p.{order_by} prefix (products table only); sorted in Python after fetching top-100
- [Phase 06-01]: MD5 of rendered Markdown content used for idempotency in export_to_megabrain() — avoids mtime drift on re-export
- [Phase 06-02]: SKILL.md uses execution-script pattern (Claude runs Bash) not agent pattern for MIS data fetch
- [Phase 06-02]: export --dest defaults to None, resolved inside export_to_megabrain() — clean CLI/logic separation
- [Phase 07-mis-integration-bugfixes]: export_to_megabrain uses WHERE status='done' — matches dossier lifecycle value set by spy_orchestrator
- [Phase 07-mis-integration-bugfixes]: generated_at is canonical timestamp for dossier age queries — created_at (migration _005) is for created_at backfill only
- [Phase 08-01]: Temporary httpx.AsyncClient per-request for proxy rotation in BaseScraper — ensures each request uses a fresh connection with the selected proxy, no state leakage
- [Phase 08-01]: proxy_list takes precedence over proxy_url; proxy_url auto-wrapped in list for backward compat
- [Phase 08-01]: run_schema_integrity_check uses sqlite_master SELECT + never-propagate-exceptions contract consistent with run_platform_canary pattern

### Pending Todos

None yet.

### Blockers/Concerns

- [Pre-Phase 2]: Hotmart SPA structure requer inspeção live antes de implementar scraper — agendar fase de research antes de Phase 2
- [Pre-Phase 3]: Cloudflare stealth config e seleção de proxy residencial precisam de decisão antes de Phase 3
- [Pre-Phase 4]: Solicitar aumento de quota YouTube Data API antes de Phase 4 (aprovação leva 1-2 semanas)
- [Pre-Phase 4]: Verificar status de manutenção do pytrends antes de Phase 4

## Session Continuity

Last session: 2026-03-16T00:19:15.605Z
Stopped at: Completed 08-foundation-verification/08-01-PLAN.md
Resume file: None
