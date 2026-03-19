# Roadmap: Market Intelligence System (MIS)

## Milestones

- ✅ **v1.0 MIS MVP** — Phases 1–12 (shipped 2026-03-16) — [Archive](.planning/milestones/v1.0-ROADMAP.md)
- ✅ **v2.0 Platform Expansion** — Phases 13–19 (shipped 2026-03-17) — [Archive](.planning/milestones/v2.0-ROADMAP.md)
- 📋 **v3.0 Market Intelligence 2.0** — Phases 20–26 (planned)

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

### 📋 v3.0 Market Intelligence 2.0 (Planned)

**Milestone Goal:** Redesenhar a experiência de pesquisa com hierarquia nicho/subnicho, pesquisa manual sob demanda, espionagem automática dos top produtos, dossiê completo de estratégias de marketing, favoritos com histórico de posição, alertas de novos campeões e exportação em PDF.

- [x] **Phase 20: Niche Data Model** — Schema de nichos/subnichos com slug mappings por plataforma (completed 2026-03-18)
- [x] **Phase 21: Manual Search Engine** — Trigger de pesquisa, orquestração de scan, resultados persistidos (completed 2026-03-19)
- [ ] **Phase 22: Spy Wiring** — Espionagem automática dos top produtos + dossiê disponível por produto
- [ ] **Phase 23: Dashboard Redesign** — UI de pesquisa nicho/subnicho, grid de resultados por plataforma/país, página de dossiê
- [ ] **Phase 24: Favorites + Tracking** — Favoritar produtos, histórico de posição ao longo do tempo
- [ ] **Phase 25: Alerts** — Alerta visual quando novo produto entra no top de subnicho pesquisado anteriormente
- [ ] **Phase 26: PDF Export** — Exportar dossiê completo como PDF

## Phase Details

### Phase 20: Niche Data Model
**Goal**: Estrutura de dados para nichos e subnichos com mapeamento de slugs por plataforma está disponível e populada
**Depends on**: Phase 19 (v2.0 complete)
**Requirements**: NICHE-01, NICHE-02
**Success Criteria** (what must be TRUE):
  1. Banco de dados contém 4 nichos (Relacionamento, Saúde, Finanças, Renda Extra) com ~40 subnichos acessíveis via query
  2. Cada subnicho retorna slug específico por plataforma (ex: "weight-loss" para ClickBank, "emagrecimento" para Hotmart)
  3. Migration aplicável em banco existente sem destruir dados v1.0/v2.0
**Plans**: 2 plans
Plans:
- [ ] 20-01-PLAN.md — Testes RED para migration _008 e niche_repository (TDD)
- [ ] 20-02-PLAN.md — Implementar migration _008 + niche_repository.py + wiring db.py

### Phase 21: Manual Search Engine
**Goal**: Usuário pode disparar pesquisa por subnicho e obter resultados salvos no banco sem nenhuma automação de background
**Depends on**: Phase 20
**Requirements**: SEARCH-01, SEARCH-02, SEARCH-03
**Success Criteria** (what must be TRUE):
  1. Nenhum scan roda sem ação explícita do usuário — APScheduler não dispara scans de subnicho
  2. Após clicar "Pesquisar", resultados aparecem agrupados por plataforma e país (BR / US / Global)
  3. Resultados de uma pesquisa ficam persistidos no banco e podem ser consultados novamente sem re-scan
  4. Pesquisa em subnicho sem produtos retorna estado vazio legível, não erro
**Plans**: 3 plans
Plans:
- [ ] 21-01-PLAN.md — Testes RED para migration _009, search_repository e search_orchestrator (TDD)
- [ ] 21-02-PLAN.md — Implementar migration _009, search_repository, search_orchestrator + wiring app.py/db.py
- [ ] 21-03-PLAN.md — Rotas FastAPI + templates HTMX + wiring final + checkpoint visual

### Phase 22: Spy Wiring
**Goal**: Os top produtos de cada resultado de pesquisa são espionados automaticamente e o dossiê completo está disponível por produto
**Depends on**: Phase 21
**Requirements**: SPY-V3-01, SPY-V3-02, SPY-V3-03
**Success Criteria** (what must be TRUE):
  1. Após pesquisa concluída, os top produtos de cada plataforma têm pipeline de espionagem disparado automaticamente (sem clique adicional)
  2. Usuário clica em qualquer produto e abre dossiê com anúncios Meta Ads ativos exibidos
  3. Dossiê exibe página de venda, upsell/downsell mapeados, copy e gatilhos identificados e estrutura de oferta (preço, bônus, garantia)
  4. Produto sem espionagem concluída exibe estado "em processamento" em vez de erro
**Plans**: 3 plans
Plans:
- [ ] 22-01-PLAN.md — Testes RED para spy wiring (TDD scaffold)
- [ ] 22-02-PLAN.md — Backend wiring: SPY_V3_TOP_N, spy batch trigger, status transitions, list_session_products com dossier_status
- [ ] 22-03-PLAN.md — Rotas + templates: re-spy em /results, coluna Dossiê, banner, tab Oferta, Gatilhos

### Phase 23: Dashboard Redesign
**Goal**: Interface principal redesenhada com seletor nicho/subnicho, grid de resultados por plataforma/país e página de dossiê estruturada
**Depends on**: Phase 22
**Requirements**: DASH-V3-01, DASH-V3-02, DASH-V3-03
**Success Criteria** (what must be TRUE):
  1. Tela principal exibe seletor hierárquico nicho → subnicho e botão "Pesquisar" como ação primária
  2. Grid de resultados exibe produtos separados por plataforma e país com thumbnail, título, rank e comissão/preço visíveis
  3. Página de dossiê por produto exibe todas as estratégias de marketing em seções estruturadas e legíveis
  4. Navegação entre tela de pesquisa e página de dossiê funciona sem reload completo (HTMX)
**Plans**: TBD

### Phase 24: Favorites + Tracking
**Goal**: Usuário pode favoritar produtos e consultar histórico de variação de posição no ranking ao longo do tempo
**Depends on**: Phase 23
**Requirements**: TRACK-01, TRACK-02
**Success Criteria** (what must be TRUE):
  1. Usuário clica em ícone de favorito em qualquer produto e o produto aparece na lista de favoritos na próxima visita
  2. Página de produto favoritado exibe gráfico ou tabela com histórico de posição (subiu / caiu / manteve) ao longo do tempo
  3. Re-scan de subnicho atualiza a posição registrada para produtos favoritados daquele subnicho
**Plans**: TBD

### Phase 25: Alerts
**Goal**: Dashboard exibe alertas visuais quando novo produto entra no top de subnichos que o usuário pesquisou anteriormente
**Depends on**: Phase 24
**Requirements**: ALERT-V3-01
**Success Criteria** (what must be TRUE):
  1. Após re-scan de subnicho, dashboard mostra badge ou banner indicando novos produtos que apareceram no top desde a última pesquisa
  2. Alerta persiste até o usuário abrir a notificação ou realizar nova pesquisa no mesmo subnicho
  3. Subniche sem nova entrada no top não exibe alerta (zero falsos positivos)
**Plans**: TBD

### Phase 26: PDF Export
**Goal**: Usuário pode exportar o dossiê completo de qualquer produto como arquivo PDF pronto para uso
**Depends on**: Phase 25
**Requirements**: EXPORT-01
**Success Criteria** (what must be TRUE):
  1. Botão "Exportar PDF" na página de dossiê gera arquivo PDF para download em menos de 10 segundos
  2. PDF exportado contém todas as seções do dossiê: anúncios, página de venda, copy, gatilhos e estrutura de oferta
  3. PDF é legível sem acesso ao sistema — independente do dashboard
**Plans**: TBD

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Foundation | v1.0 | 3/3 | Complete | 2026-03-14 |
| 2. Platform Scanners | v1.0 | 3/3 | Complete | 2026-03-16 |
| 3. Product Espionage + Dossiers | v1.0 | 3/3 | Complete | 2026-03-16 |
| 4. Pain Radar | v1.0 | 3/3 | Complete | 2026-03-15 |
| 5. Dashboard | v1.0 | 3/3 | Complete | 2026-03-16 |
| 6. MEGABRAIN Integration | v1.0 | 3/3 | Complete | 2026-03-15 |
| 7. MIS Integration Bug Fixes | v1.0 | 3/3 | Complete | 2026-03-15 |
| 8. Foundation Verification | v1.0 | 3/3 | Complete | 2026-03-16 |
| 9. Production Wiring & Proxy Fix | v1.0 | 3/3 | Complete | 2026-03-16 |
| 10. Critical Runtime Fixes | v1.0 | 3/3 | Complete | 2026-03-16 |
| 11. Health Monitor Wiring & Tech Debt | v1.0 | 3/3 | Complete | 2026-03-16 |
| 12. Meta Ads Pain Radar | v1.0 | 3/3 | Complete | 2026-03-16 |
| 13. Infrastructure + Tech Debt | v2.0 | 1/1 | Complete | 2026-03-17 |
| 14. BR Scanners | v2.0 | 2/2 | Complete | 2026-03-17 |
| 15. International API-Based | v2.0 | 3/3 | Complete | 2026-03-17 |
| 16. International High-Friction | v2.0 | 2/2 | Complete | 2026-03-17 |
| 17. Unified Cross-Platform Ranking | v2.0 | 1/1 | Complete | 2026-03-17 |
| 18. Nyquist Sign-off | v2.0 | 1/1 | Complete | 2026-03-17 |
| 19. Code Quality Cleanup | v2.0 | 1/1 | Complete | 2026-03-17 |
| 20. Niche Data Model | v3.0 | 2/2 | Complete | 2026-03-18 |
| 21. Manual Search Engine | 3/3 | Complete    | 2026-03-19 | - |
| 22. Spy Wiring | v3.0 | 0/3 | Not started | - |
| 23. Dashboard Redesign | v3.0 | 0/TBD | Not started | - |
| 24. Favorites + Tracking | v3.0 | 0/TBD | Not started | - |
| 25. Alerts | v3.0 | 0/TBD | Not started | - |
| 26. PDF Export | v3.0 | 0/TBD | Not started | - |
