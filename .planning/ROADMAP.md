# Roadmap: Market Intelligence System (MIS)

## Milestones

- ✅ **v1.0 MIS MVP** — Phases 1–12 (shipped 2026-03-16) — [Archive](.planning/milestones/v1.0-ROADMAP.md)
- ✅ **v2.0 Platform Expansion** — Phases 13–19 (shipped 2026-03-17) — [Archive](.planning/milestones/v2.0-ROADMAP.md)

## Phases

<details>
<summary>✅ v1.0 MIS MVP (Phases 1–12) — SHIPPED 2026-03-16</summary>

- [x] **Phase 1: Foundation** — Schema SQLite, BaseScraper, APScheduler, Health Monitor ✓ 2026-03-14
- [x] **Phase 2: Platform Scanners** — Hotmart, ClickBank, Kiwify scanners + ranking diário ✓ 2026-03-16
- [x] **Phase 3: Product Espionage + Dossiers** — SalesPageScraper, MetaAdsSpy, ReviewsScraper, pipeline LLM, dossiê IA ✓ 2026-03-16
- [x] **Phase 4: Pain Radar** — Trends, Reddit, Quora, YouTube, Meta Ads collectors + synthesizer horário ✓ 2026-03-15
- [x] **Phase 5: Dashboard** — FastAPI web, ranking, dossiê, feed de dores, alertas HTMX ✓ 2026-03-16
- [x] **Phase 6: MEGABRAIN Integration** — mis_agent.py bridge, skill /mis-briefing, CLI export ✓ 2026-03-15
- [x] **Phase 7: MIS Integration Bug Fixes** — export status filter, generated_at, scan→spy pipeline ✓ 2026-03-15
- [x] **Phase 8: Foundation Verification** — Proxy rotation, schema canary, VERIFICATION.md Phase 1 ✓ 2026-03-16
- [x] **Phase 9: Production Wiring & Proxy Fix** — FastAPI lifespan hook, proxy_list forwarding ✓ 2026-03-16
- [x] **Phase 10: Critical Runtime Fixes** — niche_id DB resolution, radar async wrappers ✓ 2026-03-16
- [x] **Phase 11: Health Monitor Wiring & Tech Debt** — schema integrity + platform canary em produção ✓ 2026-03-16
- [x] **Phase 12: Meta Ads Pain Radar** — MetaAdsRadarCollector, RADAR-04 fechado ✓ 2026-03-16

**31/31 requirements satisfied | 167 tests GREEN | 89 Python files, 11.393 LOC**

</details>

<details>
<summary>✅ v2.0 Platform Expansion (Phases 13–19) — SHIPPED 2026-03-17</summary>

- [x] **Phase 13: Infrastructure + Tech Debt** — Migração de plataformas, platform_ids.py, rank_type schema, DEBT v1.0 ✓ 2026-03-17
- [x] **Phase 14: BR Scanners** — Eduzz, Monetizze, PerfectPay, Braip (padrão SSR + fallback pattern) ✓ 2026-03-17
- [x] **Phase 15: International API-Based** — Product Hunt (GraphQL), Udemy (REST) com TDD RED/GREEN ✓ 2026-03-17
- [x] **Phase 16: International High-Friction** — JVZoo (Incapsula detection), Gumroad, AppSumo (PLAYWRIGHT_SEMAPHORE) ✓ 2026-03-17
- [x] **Phase 17: Unified Cross-Platform Ranking** — list_unified_ranking() percentile engine + /ranking/unified HTMX ✓ 2026-03-17
- [x] **Phase 18: Nyquist Sign-off** — VALIDATION.md retroativo phases 13, 15, 17 ✓ 2026-03-17
- [x] **Phase 19: Code Quality Cleanup** — null slug guard + fallback docstring + platform badges + INFRA-03 ✓ 2026-03-17

**17/17 requirements satisfied | 7 phases | 11 plans**

</details>

## Progress

| Milestone | Phases | Plans | Status | Shipped |
|-----------|--------|-------|--------|---------|
| v1.0 MIS MVP | 1–12 | 30/30 | ✅ Complete | 2026-03-16 |
| v2.0 Platform Expansion | 13–19 | 11/11 | ✅ Complete | 2026-03-17 |
