# Roadmap: Market Intelligence System (MIS)

## Milestones

- ✅ **v1.0 MIS MVP** — Phases 1–12 (shipped 2026-03-16) — [Archive](.planning/milestones/v1.0-ROADMAP.md)
- 🚧 **v2.0 Platform Expansion** — Phases 13–19 (in progress)

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

- [x] **Phase 13: Infrastructure + Tech Debt** — Migração de plataformas, platform_ids.py, rank_type schema, DEBT v1.0 (completed 2026-03-17)
- [x] **Phase 14: BR Scanners** — Eduzz, Monetizze, PerfectPay, Braip (padrão SSR idêntico ao v1.0) (completed 2026-03-17)
- [x] **Phase 15: International API-Based** — Product Hunt (GraphQL), Udemy (REST) — APIs oficiais/semi-oficiais (completed 2026-03-17)
- [x] **Phase 16: International High-Friction** — JVZoo, Gumroad, AppSumo — bot detection + SPA rendering (completed 2026-03-17)
- [x] **Phase 17: Unified Cross-Platform Ranking** — View consolidada por nicho com percentile normalization (completed 2026-03-17)

## Phase Details

### Phase 13: Infrastructure + Tech Debt
**Goal**: Pré-condições técnicas resolvidas e tech debt v1.0 liquidado — nenhum scanner pode ser escrito sem estes bloqueios eliminados
**Depends on**: Phase 12 (v1.0 complete)
**Requirements**: INFRA-01, INFRA-02, INFRA-03, DEBT-01, DEBT-02
**Success Criteria** (what must be TRUE):
  1. `python -m mis` inicia sem FK constraint violation ao criar produto em qualquer das 12 plataformas
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
**Plans**: 2 plans

Plans:
- [ ] 14-01-PLAN.md — Migration _007_is_stale + upsert/mark_stale + EduzzScanner + MonetizzeScanner
- [ ] 14-02-PLAN.md — PerfectPayScanner + BraipScanner (window.__NUXT__) + config.yaml slugs

### Phase 15: International API-Based
**Goal**: Duas plataformas internacionais com APIs oficiais integradas, trazendo dados de mercado global para o sistema
**Depends on**: Phase 13
**Requirements**: SCAN-INTL-01, SCAN-INTL-02
**Success Criteria** (what must be TRUE):
  1. `python -m mis scan --platform product_hunt` retorna trending products com rank posicional sem erro
  2. `python -m mis scan --platform udemy` retorna top cursos por nicho via REST API sem erro (ou degrada com api_discontinued)
  3. Scanner Product Hunt degrada graciosamente quando `PRODUCT_HUNT_API_TOKEN` está ausente (retorna lista vazia, sem exception)
  4. Scanner Udemy degrada graciosamente quando `UDEMY_CLIENT_ID`/`UDEMY_CLIENT_SECRET` estão ausentes
**Plans**: 3 plans

Plans:
- [ ] 15-01-PLAN.md — Wave 0 TDD: fixtures JSON + stubs ProductHuntScanner + UdemyScanner (RED cycle)
- [ ] 15-02-PLAN.md — Implementacao completa ProductHuntScanner + UdemyScanner (GREEN cycle)
- [ ] 15-03-PLAN.md — Wiring: SCANNER_MAP + config.yaml slugs + DOMAIN_DELAYS + env.example

### Phase 16: International High-Friction
**Goal**: Três plataformas internacionais de alta fricção (bot detection / SPA rendering) integradas com estratégias de mitigação documentadas
**Depends on**: Phase 13
**Requirements**: SCAN-INTL-03, SCAN-INTL-04, SCAN-INTL-05
**Success Criteria** (what must be TRUE):
  1. `python -m mis scan --platform jvzoo` retorna produtos sem ser bloqueado por bot detection (ou falha graciosamente com alert `bot_detected`)
  2. `python -m mis scan --platform gumroad` navega o discover page via Playwright scroll loop e persiste produtos por nicho
  3. `python -m mis scan --platform appsumo` retorna produtos sem OOM — `PLAYWRIGHT_SEMAPHORE` limita concorrência a 3 contextos
  4. Nenhum dos três scanners causa crash de memória em scan de 5 nichos simultâneos
**Plans**: 2 plans

Plans:
- [ ] 16-01-PLAN.md — PLAYWRIGHT_SEMAPHORE em base_scraper.py + JVZooScanner TDD (fetch-only, detecção Incapsula)
- [ ] 16-02-PLAN.md — GumroadScanner (fetch_spa + scroll loop) + AppSumoScanner (SSR-first) + wiring SCANNER_MAP + config.yaml

### Phase 17: Unified Cross-Platform Ranking
**Goal**: Dashboard exibe ranking consolidado cross-platform com percentile normalization — entrega principal do v2.0
**Depends on**: Phases 14, 15, 16
**Requirements**: DASH-V2-01, DASH-V2-02, DASH-V2-03
**Success Criteria** (what must be TRUE):
  1. Usuário acessa `/ranking/unified` e vê produtos de múltiplas plataformas ordenados por unified score (percentile normalizado)
  2. Filtro por nicho em `/ranking/unified` funciona — exibe apenas produtos do nicho selecionado de todas as plataformas
  3. Toggle "multi-platform only" filtra para produtos presentes em 2+ plataformas simultaneamente
  4. Cada produto na view exibe badge de plataforma, unified score e rank bruto da plataforma original
**Plans**: 1 plan

Plans:
- [ ] 17-01-PLAN.md — list_unified_ranking() + percentile engine (TDD) + rotas /ranking/unified + templates + tabs

### Phase 18: Nyquist Sign-off
**Goal**: Assinar os VALIDATION.md das novas phases v2.0 (13, 15, 17) que ficaram com `nyquist_compliant: false` após execução — completando a cobertura de validação do milestone
**Depends on**: Phase 17
**Requirements**: (tech debt cleanup — sem REQ-ID novo)
**Gap Closure**: Closes tech debt items from v2.0 audit (phases 13, 15, 17 VALIDATION.md unsigned)
**Success Criteria** (what must be TRUE):
  1. `grep -r "nyquist_compliant: false" .planning/phases/` retorna zero resultados em todas as phases v2.0
  2. VALIDATION.md de phases 13, 15, 17 assinados com `nyquist_compliant: true` e data de aprovação
**Plans**: 1 plan

Plans:
- [ ] 18-01-PLAN.md — Sign off VALIDATION.md phases 13, 15, 17

### Phase 19: Code Quality Cleanup
**Goal**: Fechar os 4 itens de qualidade de código acumulados no audit v2.0 — null slug guard, styled platform badges, documentação de fallback scanners, e correção de REQUIREMENTS.md INFRA-03
**Depends on**: Phase 18
**Requirements**: (tech debt cleanup — sem REQ-ID novo)
**Gap Closure**: Closes code quality tech debt items from v2.0 audit
**Success Criteria** (what must be TRUE):
  1. `scanner.py` tem guard `if platform_slug is None: continue` no loop de despacho (com comentário)
  2. `unified_table.html` exibe platform badges como elementos HTML estilizados (`<span>` com classe CSS)
  3. `REQUIREMENTS.md` descreve INFRA-03 como "tabela platforms" (não "tabela products")
  4. Comportamento fallback dos scanners BR documentado em scanner.py ou README
**Plans**: 1 plan

Plans:
- [ ] 19-01-PLAN.md — null slug guard + styled badges + REQUIREMENTS.md correction + fallback docs

## Progress

**Execution Order:**
Phases execute in numeric order: 13 → 14 → 15 → 16 → 17
Note: Phases 14 and 15 can execute in parallel (both depend only on Phase 13).

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1–12 (Foundation → Meta Ads) | v1.0 | 30/30 | ✅ Complete | 2026-03-16 |
| 13. Infrastructure + Tech Debt | 1/1 | Complete    | 2026-03-17 | - |
| 14. BR Scanners | 2/2 | Complete    | 2026-03-17 | - |
| 15. International API-Based | 3/3 | Complete    | 2026-03-17 | - |
| 16. International High-Friction | 2/2 | Complete    | 2026-03-17 | - |
| 17. Unified Cross-Platform Ranking | 1/1 | Complete    | 2026-03-17 | - |
| 18. Nyquist Sign-off | v2.0 | 0/1 | Not started | - |
| 19. Code Quality Cleanup | v2.0 | 0/1 | Not started | - |
