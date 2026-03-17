# Roadmap: Market Intelligence System (MIS)

## Milestones

- ✅ **v1.0 MIS MVP** — Phases 1–12 (shipped 2026-03-16) — [Archive](.planning/milestones/v1.0-ROADMAP.md)
- 🚧 **v2.0 Platform Expansion** — Phases 13–17 (in progress)

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

### 🚧 v2.0 Platform Expansion (In Progress)

**Milestone Goal:** Expandir cobertura para 9 novas plataformas globais e BR, unificar o ranking cross-platform no dashboard, e liquidar o tech debt remanescente do v1.0.

- [ ] **Phase 13: Infrastructure + Tech Debt** — Migração de plataformas, platform_ids.py, rank_type schema, DEBT v1.0
- [ ] **Phase 14: BR Scanners** — Eduzz, Monetizze, PerfectPay, Braip (padrão SSR idêntico ao v1.0)
- [ ] **Phase 15: International API-Based** — Product Hunt (GraphQL), Udemy (REST) — APIs oficiais/semi-oficiais
- [ ] **Phase 16: International High-Friction** — JVZoo, Gumroad, AppSumo — bot detection + SPA rendering
- [ ] **Phase 17: Unified Cross-Platform Ranking** — View consolidada por nicho com percentile normalization

## Phase Details

### Phase 13: Infrastructure + Tech Debt
**Goal**: Pré-condições técnicas resolvidas e tech debt v1.0 liquidado — nenhum scanner pode ser escrito sem estes bloqueios eliminados
**Depends on**: Phase 12 (v1.0 complete)
**Requirements**: INFRA-01, INFRA-02, INFRA-03, DEBT-01, DEBT-02
**Success Criteria** (what must be TRUE):
  1. `python -m mis` inicia sem FK constraint violation ao criar produto em qualquer das 16 plataformas
  2. Todo scanner novo pode importar `from mis.platform_ids import EDUZZ_PLATFORM_ID` (e equivalentes) sem hardcode local
  3. Cada plataforma no DB tem campo `rank_type` preenchido descrevendo a semântica do rank (positional, gravity, enrollment, upvotes)
  4. `grep -r "nyquist_compliant: false"` retorna zero resultados em todos os VALIDATION.md
  5. Docstring `radar/__init__.py:141` lê "6 jobs" (não "5 jobs")
**Plans**: 1 plan

Plans:
- [ ] 13-01-PLAN.md — Migration _006 + platform_ids.py + rank_type + nyquist sign-off + DEBT-02

### Phase 14: BR Scanners
**Goal**: Quatro plataformas brasileiras de infoprodutos produzindo dados reais de ranking no sistema — usando o padrão SSR estabelecido pelo v1.0
**Depends on**: Phase 13
**Requirements**: SCAN-BR-01, SCAN-BR-02, SCAN-BR-03, SCAN-BR-04
**Success Criteria** (what must be TRUE):
  1. `python -m mis scan --platform eduzz` retorna produtos rankeados por nicho sem erro
  2. `python -m mis scan --platform monetizze` retorna produtos rankeados por nicho sem erro
  3. Dashboard `/ranking` exibe produtos das plataformas BR (Eduzz, Monetizze, PerfectPay, Braip) com filtro por plataforma funcional
  4. Cada novo scanner tem suite de testes GREEN com mocks SSR que cobrem o caminho de parsing principal
**Plans**: TBD

Plans:
- [ ] 14-01: EduzzScanner + MonetizzeScanner
- [ ] 14-02: PerfectPayScanner + BraipScanner

### Phase 15: International API-Based
**Goal**: Duas plataformas internacionais com APIs oficiais integradas, trazendo dados de mercado global para o sistema
**Depends on**: Phase 13
**Requirements**: SCAN-INTL-01, SCAN-INTL-02
**Success Criteria** (what must be TRUE):
  1. `python -m mis scan --platform product_hunt` retorna trending products com votesCount como rank sem erro
  2. `python -m mis scan --platform udemy` retorna top cursos por nicho via REST API sem erro
  3. Scanner Product Hunt degrada graciosamente quando `PRODUCT_HUNT_API_TOKEN` está ausente (retorna lista vazia, sem exception)
  4. Scanner Udemy degrada graciosamente quando `UDEMY_CLIENT_ID`/`UDEMY_CLIENT_SECRET` estão ausentes
**Plans**: TBD

Plans:
- [ ] 15-01: ProductHuntScanner + UdemyScanner

### Phase 16: International High-Friction
**Goal**: Três plataformas internacionais de alta fricção (bot detection / SPA rendering) integradas com estratégias de mitigação documentadas
**Depends on**: Phase 13
**Requirements**: SCAN-INTL-03, SCAN-INTL-04, SCAN-INTL-05
**Success Criteria** (what must be TRUE):
  1. `python -m mis scan --platform jvzoo` retorna produtos sem ser bloqueado por bot detection (ou falha graciosamente com alert `bot_detected`)
  2. `python -m mis scan --platform gumroad` navega o discover page via Playwright scroll loop e persiste produtos por nicho
  3. `python -m mis scan --platform appsumo` retorna produtos sem OOM — `PLAYWRIGHT_SEMAPHORE` limita concorrência a 3 contextos
  4. Nenhum dos três scanners causa crash de memória em scan de 5 nichos simultâneos
**Plans**: TBD

Plans:
- [ ] 16-01: JVZooScanner (reconhecimento + implementação)
- [ ] 16-02: GumroadScanner + AppSumoScanner

### Phase 17: Unified Cross-Platform Ranking
**Goal**: Dashboard exibe ranking consolidado cross-platform com percentile normalization — entrega principal do v2.0
**Depends on**: Phases 14, 15, 16
**Requirements**: DASH-V2-01, DASH-V2-02, DASH-V2-03
**Success Criteria** (what must be TRUE):
  1. Usuário acessa `/ranking/unified` e vê produtos de múltiplas plataformas ordenados por unified score (percentile normalizado)
  2. Filtro por nicho em `/ranking/unified` funciona — exibe apenas produtos do nicho selecionado de todas as plataformas
  3. Toggle "multi-platform only" filtra para produtos presentes em 2+ plataformas simultaneamente
  4. Cada produto na view exibe badge de plataforma, unified score e rank bruto da plataforma original
**Plans**: TBD

Plans:
- [ ] 17-01: list_unified_ranking() + rota /ranking/unified + template

## Progress

**Execution Order:**
Phases execute in numeric order: 13 → 14 → 15 → 16 → 17
Note: Phases 14 and 15 can execute in parallel (both depend only on Phase 13).

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1–12 (Foundation → Meta Ads) | v1.0 | 30/30 | ✅ Complete | 2026-03-16 |
| 13. Infrastructure + Tech Debt | v2.0 | 0/1 | Not started | - |
| 14. BR Scanners | v2.0 | 0/TBD | Not started | - |
| 15. International API-Based | v2.0 | 0/TBD | Not started | - |
| 16. International High-Friction | v2.0 | 0/TBD | Not started | - |
| 17. Unified Cross-Platform Ranking | v2.0 | 0/TBD | Not started | - |
