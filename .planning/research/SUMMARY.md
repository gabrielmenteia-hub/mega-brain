# Project Research Summary

**Project:** Market Intelligence System (MIS) — MEGABRAIN Module
**Domain:** Web scraping pipeline + AI analysis + competitive intelligence dashboard (infoproducts)
**Researched:** 2026-03-14
**Confidence:** MEDIUM (core architecture HIGH; scraping library versions and platform ToS details need live verification)

## Executive Summary

The Market Intelligence System is a Python-first data pipeline that continuously monitors infoproduct marketplaces (Hotmart, Kiwify, Eduzz, ClickBank), extracts competitive signals, and synthesizes them into AI-generated product dossiers and pain/desire reports. The domain is mature — ETL pipelines, scraper architecture, and LLM analysis workflows are well-understood — but the execution is high-risk due to three platform-level dependencies: anti-bot detection, API quotas, and HTML structure instability. The recommended approach is a layered, dependency-ordered build: Foundation → Platform Scrapers → Social/Trend Scrapers → AI Analysis → Dashboard → MEGABRAIN integration. The entire system lives as a sibling module (`mis/`) inside MEGABRAIN, sharing `.env` credentials and writing outputs that feed back into the existing DNA pipeline.

The defensible value proposition rests on three differentiators that no existing tool offers simultaneously: Brazilian platform coverage (Hotmart/Kiwify/Eduzz), AI-generated structured dossiers optimized for product modeling, and an hourly voice-of-customer radar across Reddit/YouTube/Quora. The MVP should validate the core loop first — Hotmart + ClickBank scanning, copy extraction, and dossier generation — before investing in the hourly radar, which has the highest complexity and the highest API risk surface. Shipping a reliable 2-platform loop with clean dossiers in weeks is worth more than a fragile 8-platform system that breaks weekly.

The primary risks are operational, not architectural: IP bans from aggressive scraping, quota exhaustion on YouTube/Google Trends, and HTML structure drift on platforms that frequently update their frontends. These risks are manageable with defensive patterns built in from Phase 1 (rate limiting, fallback selectors, idempotent upserts, schema drift detection), but they cannot be retrofitted. The legal risk from ToS violations also demands a platform-by-platform review before any production scraping begins.

---

## Key Findings

### Recommended Stack

The stack is Python-first throughout, consistent with MEGABRAIN's existing codebase. FastAPI serves as the API and dashboard backend (with Jinja2 + HTMX for server-rendered UI — no Node.js build pipeline needed). SQLite handles persistence for single-user local deployment, with a clear migration path to PostgreSQL when scale demands it. The scraping layer uses httpx for static/API sources and Playwright for JS-rendered platforms (Hotmart's SPA requires it). APScheduler handles cron scheduling in-process — Celery is explicitly not recommended at MVP scale. OpenAI SDK (`gpt-4o-mini` for bulk analysis, `gpt-4o` for final dossiers) handles AI synthesis, with Anthropic as an alternative for long-context product page analysis.

See `.planning/research/STACK.md` for full rationale, alternatives considered, and version verification checklist.

**Core technologies:**
- Python 3.11 + FastAPI 0.111+: Runtime and API layer — already used by MEGABRAIN, async-native, auto-generates OpenAPI docs
- Playwright 1.40+: JS-rendered platform scraping (Hotmart, Kiwify, Eduzz) — handles SPAs and anti-bot challenges
- httpx 0.27+: Static/API scraping (YouTube, Reddit, static HTML pages) — async, faster than Playwright for non-JS targets
- SQLAlchemy 2.0+ / SQLite: Storage with async support — zero-config for local dev, migration path to PostgreSQL
- APScheduler 3.10+: In-process cron scheduling — sufficient for single-machine hourly pipeline without Celery overhead
- openai SDK 1.x: Dossier generation and copy analysis — structured JSON outputs via `response_format`
- FastAPI + Jinja2 + HTMX: Dashboard — SSR avoids Node.js build pipeline, HTMX handles dynamic updates
- tenacity + fake-useragent: Retry logic and bot detection evasion — mandatory from day one

**Critical version notes:**
- APScheduler v4 (AsyncIO-native) may be stable by now — verify before building scheduler
- Avoid Python 3.12 for now due to minor scraping library ecosystem gaps
- SQLite requires WAL mode (`PRAGMA journal_mode=WAL`) if any concurrent writes occur

### Expected Features

The domain has a clear feature dependency tree: product ranking data gates everything downstream (copy extraction, dossier generation, trajectory tracking all require products to be identified first). The MVP prioritizes the core intelligence loop over breadth of platform coverage or dashboard polish.

See `.planning/research/FEATURES.md` for full feature dependency map, competitive positioning, and anti-features.

**Must have (table stakes):**
- Product ranking scanner (Hotmart + ClickBank for MVP) — core output; missing = no product
- Niche/category filtering — without this, rankings are noise
- Sales page / copy extraction — highest-signal competitive intelligence
- Pricing and offer structure extraction — feeds dossier quality
- Review aggregation — voice of customer mining, feeds AI analysis
- AI-generated product dossier — the differentiating output that justifies building vs. using SEMrush
- Basic web dashboard (table view + dossier detail page) — raw data without UI limits users to engineers

**Should have (competitive differentiators):**
- Hourly pain/desire radar (Reddit + YouTube + Google Trends synthesis) — genuinely novel, no existing tool does this
- Brazilian platform coverage beyond Hotmart (Kiwify, Eduzz) — defensible moat, no English tool covers this well
- Ad intelligence via Meta Ad Library — high value but TOS-sensitive
- Competitor trajectory tracking (rising vs. declining products) — requires historical data from v1 running for weeks
- Alert on new top product — depends on scheduler reliability

**Defer (v2+):**
- Full multi-platform coverage (JVZoo, Udemy, Teachable, Product Hunt, AppSumo)
- Cross-platform product matching (needs multi-platform data first)
- LLM "model this" brief (enhancement on top of dossier)
- Ad comment sentiment mining (TOS risk + high complexity)
- White-label / multi-tenant SaaS (premature)

**Explicit anti-features (never build):**
- Full SEO intelligence (keyword rankings, backlinks) — SimilarWeb/SEMrush territory, not replicable
- Buyer PII collection — illegal under LGPD
- Real-time sub-minute monitoring — engineering cost disproportionate to intelligence value

### Architecture Approach

The system follows a strict layered pipeline pattern: Ingestion (scrapers) → Queue/Scheduler → Storage → AI Analysis → Serving. Scrapers and AI analysis are explicitly decoupled — scrapers write raw data to a status column queue (`status: raw → processing → processed → failed`), and the analysis pipeline reads from that queue independently. This separation is critical: LLM API calls and HTTP scraping have different failure modes, costs, and retry semantics. The entire MIS module has a single integration boundary with MEGABRAIN via `mis_agent.py`, preventing tight coupling.

See `.planning/research/ARCHITECTURE.md` for full component map, data flow diagrams, and anti-patterns.

**Major components:**
1. Platform Scrapers (httpx + Playwright) — fetch product listings from each marketplace, write raw to DB
2. Trend/Social Scrapers (PRAW + YouTube API + pytrends) — hourly VOC signal collection across Reddit/YouTube/Trends
3. APScheduler — wires all scraper jobs to cron schedules, manages rate limits
4. Storage Layer (SQLite/PostgreSQL + filesystem) — DB for structured data, `/artifacts/mis/` for HTML blobs and PDFs
5. Analysis Pipeline (copy_analyzer, pain_synthesizer, dossier_generator, trend_reporter) — LLM-powered transformation
6. FastAPI Server — REST endpoints consumed by dashboard and MEGABRAIN bridge
7. Web Dashboard (Jinja2 + HTMX) — product rankings, pain cards, dossier viewer
8. MEGABRAIN Bridge (mis_agent.py) — only file that crosses MIS/MEGABRAIN boundary

**Key patterns to follow:**
- Collector/Processor Separation: scrapers only collect, AI runs separately from queue
- Idempotent Upserts: every scrape operation uses `INSERT OR REPLACE` keyed on URL hash
- Rate Limit Budget per Source: configurable per-domain delays from day one
- Status-Driven Processing Queue: DB status column replaces need for Redis/Celery at this scale

### Critical Pitfalls

1. **HTML structure drift (Pitfall 1)** — Platforms update markup weekly; scrapers silently return empty data. Prevention: multiple fallback selectors per field, schema integrity checks after every scrape, automated canary checks on known products, version-pinned selector configs.

2. **IP bans from aggressive scraping (Pitfall 2)** — Hotmart runs Cloudflare Enterprise; a single-IP aggressive scraper gets permanently blocked. Prevention: `RateLimitedSession` with 3-8s jitter from day one, residential proxy rotation for Cloudflare-protected platforms, Playwright stealth mode, exponential backoff on 429/503.

3. **ToS legal exposure (Pitfall 3)** — Scraping authenticated dashboards or storing user PII creates LGPD/GDPR liability. Prevention: per-platform legal review checklist before any production scraping, respect `robots.txt`, strip reviewer PII from stored review content, 90-day max retention for raw data.

4. **Hourly pipeline idempotency failures (Pitfall 4)** — Failed mid-run pipelines create duplicate records on retry, corrupting trend frequency counts. Prevention: composite key deduplication `(source, timestamp_bucket, query)`, `pipeline_runs` checkpoint table with `STARTED/PARTIAL/COMPLETED/FAILED` states.

5. **AI hallucinations from incomplete data (Pitfall 11)** — LLM fills null fields with plausible-sounding fabrications; user makes product decisions on phantom signals. Prevention: data completeness gate before any AI analysis, `data_confidence_score` on every dossier output, explicit LLM instruction to say "data unavailable" rather than infer.

**Additional pitfalls worth noting:**
- Google Trends returns relative (0-100) index, not absolute search volume — misuse produces wrong trend conclusions (Pitfall 5)
- JS-heavy sites (Hotmart SPA) return empty `<div id="app">` to HTTP-only scrapers (Pitfall 6)
- YouTube Data API exhausts 10,000 unit/day quota in ~4 hours at hourly niche scanning — request quota increase before building (Pitfall 8)
- Dashboard built before pipeline stabilizes creates schema churn pressure (Pitfall 9)

---

## Implications for Roadmap

Research reveals a strict dependency chain that dictates phase order. No AI analysis is possible without scraped data. No dashboard is meaningful without reliable AI analysis. No alerts work without a stable scheduler. The build order is non-negotiable.

### Phase 1: Foundation + Legal Clearance

**Rationale:** Infrastructure that every other phase depends on. Database schema, base scraper class, scheduler skeleton, and rate limiting must exist before any scraper can be written. Legal review must happen before any production scraping begins — this is Phase 0 work but blocks Phase 1 production use.
**Delivers:** `mis.db` schema (all tables), `BaseScraper` class with rate limiting + retry + logging, APScheduler setup with test job, per-platform legal risk matrix in `docs/legal/platform_review.md`
**Addresses features:** Data model for product ranking, retention policy, currency normalization
**Avoids pitfalls:** Pitfall 3 (ToS legal exposure), Pitfall 4 (idempotency), Pitfall 10 (retention strategy), Pitfall 12 (currency normalization), Pitfall 2 (rate limiting infrastructure)
**Research flag:** Standard patterns — no additional research needed

### Phase 2: Platform Scanners (Product Discovery)

**Rationale:** The first user-facing value and the upstream dependency for all downstream features. Start with Hotmart (BR) + ClickBank (international) only — two platforms validates the architecture before scaling to 8+. JS rendering audit must happen before coding each scraper.
**Delivers:** Daily/6h product ranking refresh for Hotmart + ClickBank, niche filtering, structured `raw_products` records
**Uses:** Playwright (Hotmart SPA), httpx (ClickBank if SSR), BaseScraper, APScheduler
**Implements:** Platform Scrapers component, Storage Layer
**Avoids pitfalls:** Pitfall 1 (fallback selectors + schema drift alerts), Pitfall 2 (IP ban prevention), Pitfall 6 (JS rendering audit before coding)
**Research flag:** Needs phase research — Hotmart's current anti-bot posture and exact HTML structure need live verification before scraper implementation

### Phase 3: Product Espionage + Dossier Generation

**Rationale:** Once products are identified, deep-scrape their sales pages and generate dossiers. This is the core differentiating output. Requires Phase 2 data to be flowing reliably for 48+ hours before starting.
**Delivers:** Sales page copy extraction, pricing/offer structure, review aggregation, AI-generated product dossiers (JSON + PDF), `data_confidence_score` on each dossier
**Uses:** Playwright (landing pages behind Cloudflare), OpenAI SDK (gpt-4o-mini for analysis, gpt-4o for final dossier), WeasyPrint (PDF export)
**Implements:** Analysis Pipeline (copy_analyzer, dossier_generator), product_spy_job queue
**Avoids pitfalls:** Pitfall 11 (data completeness gate before AI), Pitfall 2 (residential proxy for landing pages), Pitfall 9 (pipeline validated before dashboard work begins)
**Research flag:** Needs phase research — Cloudflare stealth configuration for Playwright, current Hotmart landing page structure

### Phase 4: Trend/Social Radar (Hourly VOC)

**Rationale:** The highest-complexity module, built after the core product intelligence loop is validated. Highest API risk surface (YouTube quota, Google Trends rate limits, Reddit OAuth). Idempotency design is critical here.
**Delivers:** Hourly pain/desire reports per niche (Reddit + YouTube + Google Trends signals, LLM-synthesized), `pain_reports` table
**Uses:** PRAW (Reddit), YouTube Data API v3, pytrends, OpenAI (pain_synthesizer + trend_reporter)
**Implements:** Trend/Social Scrapers component, hourly APScheduler jobs
**Avoids pitfalls:** Pitfall 4 (idempotency + checkpoint store), Pitfall 5 (anchor terms for Trends normalization), Pitfall 7 (Reddit rate limits + Quora graceful degradation), Pitfall 8 (YouTube quota architecture), Pitfall 13 (singleton lock on hourly jobs), Pitfall 14 (geo=BR + UTC timestamps)
**Research flag:** Needs phase research — YouTube quota increase request lead time (1-2 weeks), current Reddit API free tier limits, pytrends maintenance status

### Phase 5: Dashboard + Serving Layer

**Rationale:** Only built after Phase 3 has been producing reliable dossiers for multiple days. Dashboard adapts to the schema, not the reverse. FastAPI + Jinja2 + HTMX avoids Node.js build pipeline complexity.
**Delivers:** Product ranking table view, dossier detail pages, pain report cards, niche filtering UI
**Uses:** FastAPI, Jinja2, HTMX, Tailwind CSS (CDN), Chart.js (CDN)
**Implements:** FastAPI Server, Web Dashboard components
**Avoids pitfalls:** Pitfall 9 (pipeline must be stable before dashboard), Pitfall 5 (display "relative interest score" not "search volume")
**Research flag:** Standard patterns — FastAPI + HTMX is well-documented

### Phase 6: MEGABRAIN Integration + Alerts

**Rationale:** Final phase — MIS as a first-class MEGABRAIN module. The integration boundary is exactly one file (`mis_agent.py`) to prevent tight coupling. Alerts depend on scheduler reliability established in Phase 4.
**Delivers:** `/mis-briefing` slash command, new dossier alerts, dossier YAML/JSON export to MEGABRAIN knowledge pipeline, `mis_agent.py` bridge
**Uses:** MEGABRAIN skill router, existing `.env` config, FastAPI endpoints
**Implements:** MEGABRAIN Bridge component
**Avoids pitfalls:** Anti-Pattern 4 (tight coupling via single integration file only)
**Research flag:** Standard patterns — integration boundary is clear from architecture research

### Phase Ordering Rationale

- Phases 1-2 unblock everything: no scraper can run without DB schema and rate limiting infrastructure
- Phase 3 precedes Phase 4: product intelligence (lower API risk) validates architecture before the higher-risk hourly radar is built
- Phase 5 is explicitly last among data phases: dashboard pressure during pipeline development causes schema churn
- Phase 6 is final: integration is a wrapper around a working system, not a foundation

### Research Flags

Phases needing `/gsd:research-phase` during planning:
- **Phase 2 (Platform Scanners):** Hotmart's current Cloudflare configuration and SPA structure need live verification — architecture decisions (which pages are SSR vs CSR, which selectors are stable) cannot be made from training data alone
- **Phase 3 (Espionagem):** Landing page Cloudflare stealth requirements need live testing; residential proxy provider selection needed
- **Phase 4 (Radar):** YouTube quota increase approval, current Reddit API tier limits, and pytrends maintenance status need live verification before design decisions

Phases with well-documented patterns (skip research-phase):
- **Phase 1 (Foundation):** SQLite schema design, APScheduler setup, BaseScraper patterns — all well-established
- **Phase 5 (Dashboard):** FastAPI + HTMX + Jinja2 — official docs are comprehensive
- **Phase 6 (Integration):** MEGABRAIN bridge pattern is already established in `core/intelligence/`

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | Core choices (FastAPI, SQLite, APScheduler) verified via official docs. Library versions for Playwright, APScheduler, pytrends need live pypi.org verification before implementation. |
| Features | MEDIUM | Stable domain — competitive intelligence feature sets have been consistent since 2022. No live verification of SimilarWeb/SEMrush feature pages possible in research session. Core feature dependency tree is reliable. |
| Architecture | HIGH | ETL/ELT pipeline patterns are mature and well-documented. Layered architecture with collector/processor separation is established best practice. Component boundaries are clear. |
| Pitfalls | MEDIUM | Platform-specific behavior (Hotmart anti-bot, current API quotas) based on training data — may have changed since August 2025 cutoff. General scraping pitfalls (HTML drift, IP bans, idempotency) are high-confidence regardless of date. |

**Overall confidence:** MEDIUM — architecture is solid and actionable; implementation details for specific platforms need live verification during Phase 2-4 planning.

### Gaps to Address

- **Hotmart SPA structure:** Requires live browser inspection to determine which pages are CSR vs SSR before scraper design. Do this during Phase 2 research.
- **APScheduler v4 status:** If v4 is now stable (AsyncIO-native), prefer it over v3 API. Verify at pypi.org/project/apscheduler before writing scheduler code.
- **YouTube quota increase lead time:** Request Google Cloud quota increase before Phase 4 begins — approval takes 1-2 weeks. Do not wait until Phase 4 is ready to build.
- **Per-platform legal review:** Create `docs/legal/platform_review.md` during Phase 1, before any production scraping. Each platform needs explicit ToS review for: public rankings scraping, review content storage, pricing data use.
- **pytrends maintenance status:** Unofficial library; verify it's still actively maintained and confirm current version before Phase 4 implementation.
- **Residential proxy provider:** Required for Hotmart and likely ClickBank landing pages. Selection and budget should happen during Phase 3 planning, not during implementation.

---

## Sources

### Primary (HIGH confidence)
- https://fastapi.tiangolo.com/ — FastAPI framework, verified 2026-03-14
- https://www.postgresql.org/about/ — PostgreSQL capabilities, verified 2026-03-14
- https://www.sqlite.org/about.html — SQLite limits and ACID compliance, verified 2026-03-14
- https://redis.io/docs/latest/get-started/ — Redis use cases, verified 2026-03-14

### Secondary (MEDIUM confidence)
- Training data (cutoff August 2025): Playwright, httpx, APScheduler, PRAW, YouTube Data API quotas, BeautifulSoup4, SQLAlchemy 2.0, openai SDK patterns
- Training data: Competitive intelligence tool feature sets (SimilarWeb, SEMrush, AdSpy, BigSpy) — stable domain, unlikely to have changed materially
- Training data: Reddit API 2023 restrictions — widely documented, HIGH confidence despite training data source
- Training data: LGPD general principles for scraped data — stable legal framework

### Tertiary (LOW confidence — verify before using)
- pytrends version and maintenance status — unofficial library, check pypi.org/project/pytrends
- APScheduler v4 release status — may now be stable; check pypi.org/project/apscheduler
- Playwright 1.40+ version confirmation — check pypi.org/project/playwright
- Current Hotmart/Kiwify anti-bot configuration — requires live testing
- Current YouTube Data API v3 quota defaults — check developers.google.com/youtube/v3/getting-started#quota

---
*Research completed: 2026-03-14*
*Ready for roadmap: yes*
