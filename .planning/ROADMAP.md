# Roadmap: Market Intelligence System (MIS)

## Milestones

- ✅ **v1.0 MIS MVP** — Phases 1–12 (shipped 2026-03-16) — [Archive](.planning/milestones/v1.0-ROADMAP.md)
- 📋 **v2.0** — Platform Expansion + Advanced Features (planned)

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

### 📋 v2.0 (Planned)

- [ ] **Phase 13: Platform Expansion** — Gumroad, Kajabi, Teachable, JVZoo, Digistore24, Stan Store, Skool (15+ plataformas)
- [ ] **Phase 14: Advanced Features** — Export PDF, comparação side-by-side, histórico de evolução de produto
- [ ] **Phase 15: Notifications** — WhatsApp/Telegram além do dashboard

## Progress

| Phase | Milestone | Plans | Status | Completed |
|-------|-----------|-------|--------|-----------|
| 1–12 (Foundation → Meta Ads) | v1.0 | 30/30 | ✅ Complete | 2026-03-16 |
| 13. Platform Expansion | v2.0 | 0/TBD | 📋 Planned | - |
| 14. Advanced Features | v2.0 | 0/TBD | 📋 Planned | - |
| 15. Notifications | v2.0 | 0/TBD | 📋 Planned | - |
