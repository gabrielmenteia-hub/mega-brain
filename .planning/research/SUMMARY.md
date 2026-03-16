# Project Research Summary

**Project:** Market Intelligence System (MIS) v2.0 — Platform Expansion
**Domain:** Multi-platform product intelligence scraping and unified cross-platform ranking
**Researched:** 2026-03-16
**Confidence:** MEDIUM

## Executive Summary

MIS v2.0 is a targeted expansion of an existing, well-structured scraping system — not a greenfield build. The v1.0 architecture was deliberately designed for this kind of expansion: the `PlatformScanner` ABC, `SCANNER_MAP` dict, and `Product` dataclass provide clean integration points that require no structural changes to accommodate 13 new platforms. The recommended approach is to add platforms incrementally in four groups — (1) a mandatory infrastructure setup phase, (2) BR infoproduct platforms using the established SSR/BeautifulSoup pattern, (3) international platforms with official APIs, and (4) SPA/high-friction platforms last — with the cross-platform unified ranking view as the capstone deliverable.

The central risk is not technical complexity but silent integration failures. Four of the 13 requested platforms (Kajabi, Teachable, Stan Store, and likely Skool) have no public marketplace to scan — implementing them as standard scanners produces scanners that permanently return empty data while health checks pass. Additionally, three platforms (Udemy, JVZoo, Gumroad) require non-obvious integration approaches: Udemy must use its undocumented JSON API to bypass Cloudflare Enterprise, JVZoo may use Incapsula bot protection requiring a different mitigation strategy, and Gumroad's discover page is React infinite scroll rather than SSR. The Brazil-based platforms (Eduzz, Monetizze, PerfectPay, Braip) carry platform verification risk due to potential rebranding and domain migrations between 2023-2025.

A critical pre-implementation decision is required before writing any scanner code: the `Product.rank` field maps incompatible metrics across platforms (positional rank on Hotmart, gravity score on ClickBank, enrollment count on Udemy, daily upvote count on Product Hunt). Without resolving this schema question first, the unified cross-platform ranking view will silently produce incoherent comparisons. The fix is a `rank_type` metadata field on the `platforms` table and percentile normalization at query time — both well-understood patterns with no new dependencies.

---

## Key Findings

### Recommended Stack

The existing v1.0 library stack is complete for all 13 new platforms. Zero new pip packages are required. `httpx` covers REST and GraphQL APIs, `playwright` + `playwright-stealth` covers React SPAs, and `beautifulsoup4` + `lxml` covers all SSR HTML platforms. The two API-based platforms (Udemy, Product Hunt) need free developer account registrations to obtain credentials, which must be treated as environment variables. The only infrastructure extension needed is appending 11 new entries to the `DOMAIN_DELAYS` dict in `base_scraper.py` and creating a `mis/platform_ids.py` as a single source of truth for all platform ID constants.

See `.planning/research/STACK.md` for full platform-by-platform integration analysis, code patterns, and verification checklist.

**Core technologies (existing, no changes):**
- `httpx[http2]` — SSR fetching, REST/GraphQL API calls — already handles Basic Auth (Udemy) and Bearer token (Product Hunt) patterns natively
- `playwright` + `playwright-stealth` — React SPA rendering — `fetch_spa()` already in `BaseScraper`; needed for Gumroad scroll loop and AppSumo fallback
- `beautifulsoup4` + `lxml` — HTML parsing — all BR platforms and SSR international platforms follow the exact Hotmart/Kiwify pattern
- `apscheduler` — scan scheduling — no changes needed; 16 platforms x 5 niches is trivial for `AsyncIOScheduler`
- `anthropic` (claude-sonnet-4-6) — enrichment — unchanged

**New env vars required:**
- `UDEMY_CLIENT_ID` + `UDEMY_CLIENT_SECRET` — free Udemy affiliate account at udemy.com/developers/affiliate/
- `PRODUCT_HUNT_API_TOKEN` — free developer token at producthunt.com/v2/oauth/applications
- `JVZOO_API_KEY` — optional; scanner degrades gracefully without it

### Expected Features

The domain has a clear dependency structure: all new scanners must be registered before the unified view has data, and the unified view is the headline v2.0 deliverable. The MVP order is BR platforms first (lowest friction, fastest to implement), official APIs second (cleanest data), SPA/rate-limited platforms third, then the unified ranking view as capstone.

See `.planning/research/FEATURES.md` for full platform-by-platform access analysis, unified ranking specification, and feature dependency map.

**Must have (table stakes for v2.0 milestone):**
- EduzzScanner — BR infoproduct, SSR HTML, same pattern as Hotmart
- MonetizzeScanner — BR infoproduct, SSR HTML
- JVZooScanner — affiliate marketplace, network-inspection for JSON API, fallback SSR HTML
- ProductHuntScanner — official GraphQL API, OAuth Bearer token, votesCount ranking
- UdemyScanner — undocumented REST API (`/api-2.0/courses/`), enrollment count ranking
- GumroadScanner — Playwright with scroll loop, discover page, positional ranking
- AppSumoScanner — SSR first (Next.js), Playwright fallback, serialized requests
- BraipScanner — BR infoproduct, SSR HTML (conditional on marketplace URL verification)
- PerfectPayScanner — BR infoproduct, SSR HTML (conditional on marketplace URL verification)
- `/ranking/unified` route — cross-platform view with percentile normalization via SQL window function

**Should have (differentiators):**
- Normalized cross-platform rank score (`percentile_rank = rank / COUNT` per platform-niche) — headline v2.0 value claim
- Multi-platform presence count per product — strongest buy signal in the system
- Platform health badges in unified view — surfaces existing health_monitor canary data in new template
- Alert taxonomy extension — `bot_detected`, `platform_down`, `auth_required`, `rate_limited` as distinct types vs. generic `schema_drift`

**Defer to v3.0+:**
- SkoolScanner — Playwright SPA, member count only (low intelligence value)
- KajabiScanner — no public marketplace, confirmed skip
- TeachableScanner — no public marketplace, confirmed skip
- Stan StoreScanner — no public marketplace, confirmed skip
- Currency normalization (BRL/USD) — show with `currency_code` tag, no conversion ever
- Redis, Celery, distributed workers — SQLite WAL + APScheduler sufficient at v2.0 scale

### Architecture Approach

The v1.0 architecture requires only additive changes for v2.0. Per new scanner, the integration points are: new scanner file, one-line `SCANNER_MAP` entry, one `VALID_PLATFORMS` entry, one `health_monitor` tuple, and one platform row in the seed migration. No existing infrastructure changes beyond adding a global `asyncio.Semaphore(3)` for Playwright concurrency control and one new `list_unified_ranking()` function in `dossier_repository.py`. The unified view adds one route and one Jinja2 template. No ALTER TABLE operations are needed — the `platforms` table already accepts any number of platform rows.

See `.planning/research/ARCHITECTURE.md` for full component boundary table, data flow, migration data, and build order.

**Major components:**
1. `mis/migrations/_006_v2_platforms.py` — seeds platform IDs 4-16 with `INSERT OR IGNORE`; hard blocker for all scanner work due to FK constraint on `products.platform_id`
2. `mis/platform_ids.py` (new) — single source of truth for all 16 platform ID constants; eliminates collision risk across scanner files, migration, and startup assertion
3. `mis/scanners/{platform}.py` (x11 new files) — one per implementable platform; each follows the existing `PlatformScanner` contract exactly
4. `mis/dossier_repository.py:list_unified_ranking()` — SQL window function query computing percentile_rank across all platforms per niche; SQLite 3.25+ confirmed safe
5. `mis/web/routes/ranking.py` + `templates/ranking_unified.html` — new `/ranking/unified` route; niche-first view with platform badges and multi-platform presence count

### Critical Pitfalls

1. **Rank field semantic collision across platforms** — `Product.rank` stores incompatible metrics (positional rank, gravity score, enrollment count, daily upvotes). Crossed wires in the unified view produce incoherent rankings users cannot trust. Fix: add `rank_type` metadata to `platforms` table before writing any scanner; use percentile normalization in unified view, never raw `rank` for cross-platform sorts. Must resolve before Phase 3.

2. **Four platforms have no public marketplace** — Kajabi, Teachable, Stan Store, and Skool are hosted content management tools, not open marketplaces. Building scanners produces permanent empty results with passing health checks. Fix: classify all 13 platforms before writing any code; skip confirmed Category D platforms entirely; document as "no public marketplace" in platform registry.

3. **Udemy requires undocumented API, not HTML scraping** — Cloudflare Enterprise blocks httpx; Playwright is detected from datacenter IPs even with stealth plugins. Fix: use `GET /api-2.0/courses/?ordering=enrollment` endpoint; verify endpoint before building; rate-limit to 1 req/10s with jitter.

4. **Platform ID collision with no central registry** — 13 new scanner files each needing a `PLATFORM_ID` constant that must match the DB seed exactly; SQLite does not enforce FK by default so orphaned IDs write silently. Fix: create `mis/platform_ids.py` as single source of truth; add startup assertion comparing constants against `SELECT id, slug FROM platforms`; add integration test asserting `SCANNER_MAP.keys() == expected_platform_slugs`.

5. **Playwright OOM with multiple concurrent SPA platforms** — `asyncio.gather()` running 15+ concurrent Playwright contexts consumes 2-4.5GB RAM on standard servers. Fix: add `PLAYWRIGHT_SEMAPHORE = asyncio.Semaphore(3)` in `scanner.py` before any Playwright-required scanner is registered; serialize AppSumo requests with `max_concurrent: 1`.

6. **Brazilian platform URL/structure verification** — Eduzz, Monetizze, PerfectPay, Braip may have migrated domains or changed rendering architecture post-2023. Fix: manual `View Page Source` test for all 4 before writing any selector code; document verified URL and date in scanner docstring.

---

## Implications for Roadmap

Based on combined research, the build order is driven by three hard constraints: (1) the platform seed migration is a FK blocker for all scanner code, (2) 4 of 13 platforms need pre-build classification to avoid permanently empty scanner slots, and (3) the unified ranking view requires multi-platform data to be meaningful. The suggested phase structure below reflects these constraints.

### Phase 1: Foundation, Classification, and Infrastructure
**Rationale:** Three blockers must be resolved before any scanner code is written. Without the seed migration, the FK constraint crashes every new scanner on first product save. Without platform classification, 4 scanner slots will be permanently empty and look like working scanners. Without the Playwright semaphore, adding Gumroad and AppSumo later causes OOM on the scan host.
**Delivers:** `mis/platform_ids.py`, `mis/migrations/_006_v2_platforms.py`, `mis/db.py` migration registration, SCANNER_MAP + VALID_PLATFORMS + health_monitor infrastructure entries for all 11 buildable platforms, `asyncio.Semaphore(3)` Playwright concurrency control, manual verification results for all 13 platforms (live URL fetch test), `rank_type` schema decision documented
**Addresses:** Pitfalls 2, 3, 4, 12 (all pre-empted before scanner code)
**Avoids:** FK integrity errors, silent empty scanners, platform ID collisions, OOM crashes

### Phase 2: BR Infoproduct Scanners (Eduzz, Monetizze, PerfectPay, Braip)
**Rationale:** These 4 platforms share the exact SSR + BeautifulSoup pattern as Hotmart and Kiwify — the lowest-friction, highest-confidence implementation path. They are also the highest-relevance platforms for the primary target audience. Doing these first establishes the implementation template and gives the team working scanners quickly. All 4 are conditional on Phase 1 URL verification passing.
**Delivers:** 4 new scanner files + 4 test files; first production data from new platforms in BR market
**Uses:** `httpx` + `beautifulsoup4` + `lxml` — no new patterns; identical to Hotmart/Kiwify
**Implements:** Pattern A (SSR HTML) expansion
**Avoids:** Pitfall 9 — Phase 1 URL verification results are the gate condition
**Research flag:** Standard pattern — skip research-phase; Phase 1 live verification is sufficient prep

### Phase 3: International API-Based Platforms (Product Hunt, Udemy)
**Rationale:** Both platforms have official or semi-official APIs with structured data and manageable auth. Product Hunt's GraphQL API is free and well-documented. Udemy's undocumented REST API bypasses Cloudflare and returns clean JSON. Doing these after the BR platforms means the scanner pattern is well-understood, reducing implementation errors on the more sensitive auth-based scanners. The `rank_type` schema decision from Phase 1 is required here — Product Hunt's daily-reset upvote count needs special handling.
**Delivers:** ProductHuntScanner + UdemyScanner + 2 test files; first international platform data
**Uses:** `httpx` Basic Auth (Udemy), `httpx` Bearer token POST (Product Hunt) — no new libraries
**Implements:** Pattern C (public API with auth key) — first production use of this pattern in the system
**Avoids:** Pitfall 4 (Udemy Cloudflare), Pitfall 6 (Product Hunt daily rank reset)
**Research flag:** Needs pre-build API verification — confirm Udemy `/api-2.0/courses/` endpoint format and response schema; confirm Product Hunt OAuth token lifetime and graceful 401 handling before implementation

### Phase 4: International SSR + High-Friction Platforms (JVZoo, AppSumo, Gumroad)
**Rationale:** These three require reconnaissance before implementation. JVZoo may have Incapsula protection (different from Cloudflare, needs different mitigation). AppSumo has aggressive per-endpoint rate limiting that requires per-platform concurrency controls. Gumroad requires a Playwright scroll loop. Doing these after Phases 2-3 means both the infrastructure (semaphore, per-platform concurrency) and Pattern D (SPA) are proven before tackling harder targets.
**Delivers:** JVZooScanner + AppSumoScanner + GumroadScanner + 3 test files
**Uses:** `playwright` + `beautifulsoup4` for Gumroad and AppSumo fallback; `httpx` + HTML for JVZoo
**Implements:** Pattern D (SPA with Playwright) first production use via Gumroad scroll loop
**Avoids:** Pitfall 5 (JVZoo Incapsula), Pitfall 7 (AppSumo parallel rate limiting), Pitfall 8 (Gumroad CSR infinite scroll)
**Research flag:** Needs pre-build reconnaissance — manually test JVZoo response headers for Incapsula markers; test AppSumo concurrent request behavior; inspect Gumroad discover page DOM structure for scroll loop implementation

### Phase 5: Cross-Platform Unified Ranking View
**Rationale:** The unified view is the headline v2.0 deliverable and depends on having multi-platform data from at least 5+ scanners to validate against. Building it last ensures the SQL window function query can be tested with real data. The percentile normalization formula requires accurate rank semantics, which are locked in Phase 1.
**Delivers:** `list_unified_ranking()` SQL window function query, `/ranking/unified` route, `ranking_unified.html` template, niche-first grouping with platform badges, multi-platform presence count, full test coverage
**Uses:** SQLite window functions (3.25+, confirmed safe), existing HTMX filter patterns from `ranking.html`
**Implements:** Percentile normalization formula; cross-platform view architecture
**Avoids:** Pitfall 1 (rank semantic collision resolved in Phase 1 with `rank_type` metadata)
**Research flag:** Standard SQL pattern — skip research-phase; window function syntax is well-documented (SQLite 3.25+)

### Phase Ordering Rationale

- Phase 1 is a hard dependency for all subsequent phases: FK constraint means platform rows must exist before any product upsert; platform classification prevents permanently empty scanner slots
- BR platforms (Phase 2) before international (Phases 3-4) because they use identical patterns to existing scanners — lower implementation risk, faster time to first data, establishes implementation template
- API platforms (Phase 3) before SPA/rate-limited platforms (Phase 4) because APIs are more stable than scraping targets and validate Pattern C before tackling harder platforms
- Unified view (Phase 5) last because it needs real multi-platform data for end-to-end validation and accurate rank semantics locked in Phase 1
- Kajabi, Teachable, Stan Store excluded entirely — no public marketplace confirmed with HIGH confidence; do not allocate implementation time

### Research Flags

Phases needing pre-build investigation or `/gsd:research-phase` during planning:
- **Phase 1:** Platform classification verification — manual URL fetch test for all 13 platforms before finalizing scope; no code research needed, just live URL tests (2 minutes per platform)
- **Phase 3:** Udemy `/api-2.0/courses/` endpoint format and current JSON response schema (training data cutoff August 2025 — must verify live); Product Hunt OAuth token lifetime and 401 graceful degradation pattern
- **Phase 4:** JVZoo bot protection type (Incapsula confirmation via live header inspection); AppSumo concurrent request behavior under 5-niche parallel load; Gumroad discover page current DOM structure for Playwright scroll loop

Phases with standard patterns (skip research-phase):
- **Phase 2:** SSR + BeautifulSoup — same pattern as Hotmart (production-validated since v1.0); only variable is URL structure which Phase 1 verifies
- **Phase 5:** SQL window functions — stable SQLite feature since 3.25 (2018); query pattern is straightforward and well-documented

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Existing codebase fully read (89 files, 11K LOC); zero new libraries confirmed; all integration patterns validated against working v1.0 scanners; no pypi.org verification needed since stack is unchanged |
| Features | MEDIUM | Table stakes features clearly defined; platform access methods for 8/13 platforms are MEDIUM/LOW confidence pending live URL and rendering verification; the 4 skipped platforms are HIGH confidence skips |
| Architecture | HIGH | Integration points derived from direct codebase read; SQL window functions confirmed safe on target SQLite version; migration pattern matches existing test fixtures; no assumptions required |
| Pitfalls | MEDIUM | Critical pitfalls grounded in v1.0 codebase patterns + known platform behaviors; platform-specific bot protection details (Udemy API, JVZoo Incapsula) require live confirmation before Phase 3/4 implementation |

**Overall confidence:** MEDIUM — architecture decisions are actionable and HIGH confidence; platform-specific implementation details for 8 of 11 buildable scanners require live verification before coding begins.

### Gaps to Address

- **Brazilian platform URL verification** — Eduzz, Monetizze, PerfectPay, Braip marketplace URLs must be confirmed live before Phase 2 begins. Resolution: 2-minute httpx fetch test per platform at Phase 1 kickoff.
- **Udemy `/api-2.0/courses/` endpoint** — endpoint path and JSON response schema based on training data (August 2025); must be manually verified before Phase 3. Resolution: single GET request verification before writing parser.
- **JVZoo bot protection type** — Incapsula vs. Cloudflare requires different mitigation strategies (residential proxy vs. stealth plugin tuning). Resolution: inspect response headers of `jvzoo.com/marketplace` before Phase 4 begins.
- **Product Hunt OAuth token lifetime** — whether tokens expire and how to handle graceful degradation on 401. Resolution: check token expiry policy during Phase 3 API setup.
- **`rank_type` schema decision** — whether to add a `rank_type` column to the `platforms` table or a `rank_raw_metric` column to `products`. This decision gates all scanner implementation. Resolution: Phase 1 planning decision; document in `mis/platform_ids.py` module docstring.
- **Gumroad CSR confirmation** — whether discover page requires Playwright scroll loop or if a direct JSON API endpoint exists for category browsing. Resolution: `fetch()` the URL and check for React hydration markers before Phase 4.

---

## Sources

### Primary (HIGH confidence)
- `mis/scanner.py`, `mis/base_scraper.py`, `mis/scanners/hotmart.py`, `mis/scanners/clickbank.py`, `mis/scanners/kiwify.py` — direct codebase read (2026-03-16); integration points, data contracts, existing patterns
- `mis/migrations/_001_initial.py` through `_005_alerts.py` — schema structure verified
- `mis/config.py`, `mis/health_monitor.py`, `mis/scheduler.py`, `mis/web/app.py` — registration points and dispatch logic read directly
- SQLite window functions — available since SQLite 3.25.0 (September 2018); Python 3.14 ships SQLite >= 3.39
- Kajabi/Teachable/Stan Store "no public marketplace" — well-established platform architecture, stable characteristic since 2020+
- Cloudflare Enterprise on Udemy — widely documented across community reports

### Secondary (MEDIUM confidence)
- Udemy Affiliate REST API (`/api-2.0/courses/`) — training data (August 2025); endpoint stable for years but requires live verification of current format
- Product Hunt GraphQL API v2 — publicly documented; OAuth token requirements need live verification
- Eduzz/Monetizze SSR rendering assumption — BR platforms of this generation typically SSR; must verify live
- Gumroad discover page React CSR — based on known Gumroad architecture; needs live confirmation
- AppSumo per-endpoint rate limiting — known patterns for high-scraping-incentive deal sites

### Tertiary (LOW confidence — verify before implementation)
- JVZoo Incapsula protection — based on Imperva deployment patterns for affiliate sites; unconfirmed until live header inspection
- PerfectPay/Braip marketplace discoverability — smaller platforms with less-documented structure
- Skool communities directory public pagination beyond page 1

---
*Research completed: 2026-03-16*
*Supersedes: v1.0 SUMMARY.md (dated 2026-03-14)*
*Ready for roadmap: yes*
