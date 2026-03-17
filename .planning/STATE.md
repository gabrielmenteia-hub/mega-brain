---
gsd_state_version: 1.0
milestone: v2.0
milestone_name: Platform Expansion
status: in-progress
stopped_at: Completed 17-unified-cross-platform-ranking/17-01-PLAN.md
last_updated: "2026-03-17T22:48:34.188Z"
last_activity: "2026-03-17 — Phase 14 Plan 01: EduzzScanner + MonetizzeScanner fallback-only, migration _007 is_stale, mark_stale() wiring em run_all_scanners()"
progress:
  total_phases: 5
  completed_phases: 5
  total_plans: 9
  completed_plans: 9
  percent: 100
---

---
gsd_state_version: 1.0
milestone: v2.0
milestone_name: Platform Expansion
status: in-progress
stopped_at: Completed 14-br-scanners/14-01-PLAN.md
last_updated: "2026-03-17T03:50:08Z"
last_activity: 2026-03-17 — Phase 14 Plan 01 concluido: EduzzScanner + MonetizzeScanner fallback + is_stale migration + mark_stale wiring
progress:
  [██████████] 100%
  completed_phases: 1
  total_plans: 2
  completed_plans: 2
  percent: 40
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-16)

**Core value:** Entregar o mapa completo do que está vendendo e por que está vendendo — sem esforço manual — para que o usuário possa modelar e lançar seus próprios produtos com máxima vantagem competitiva.
**Current focus:** Phase 14 — BR Scanners (Eduzz, Monetizze, PerfectPay, Braip)

## Current Position

Phase: 14 of 17 (BR Scanners)
Plan: 1 of TBD in current phase (14-01 COMPLETE)
Status: In progress — ready for 14-02 (PerfectPay + Braip)
Last activity: 2026-03-17 — Phase 14 Plan 01: EduzzScanner + MonetizzeScanner fallback-only, migration _007 is_stale, mark_stale() wiring em run_all_scanners()

Progress: [██████████] 100%

## Performance Metrics

**Velocity (v1.0 reference):**
- Total plans completed: 30 (v1.0)
- Average duration: ~12 min/plan
- Total execution time: ~6h (v1.0)

**By Phase (v1.0 summary):**

| Phase | Plans | Avg/Plan |
|-------|-------|----------|
| 01–12 | 30 | ~12m |

**Recent Trend:**
- v2.0: Not started
- v1.0 final trend: Stable (~10–25m/plan for complex phases)

*Updated after each plan completion*
| Phase 13 P01 | 12 | 3 tasks | 17 files |
| Phase 14 P01 | 8 | 2 tasks (TDD) | 11 files |
| Phase 14-br-scanners P02 | 10 | 2 tasks | 9 files |
| Phase 15 P01 | 9 | 2 tasks | 6 files |
| Phase 15-international-api-based P02 | 12 | 2 tasks | 2 files |
| Phase 15-international-api-based P03 | 10 | 2 tasks | 4 files |
| Phase 16-international-high-friction P01 | 11 | 2 tasks | 5 files |
| Phase 16-international-high-friction P02 | 13 | 2 tasks | 9 files |
| Phase 17-unified-cross-platform-ranking P01 | 9 | 3 tasks | 7 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting v2.0:

- [v2.0 Research]: rank_type metadata field necessário antes de qualquer scanner — percentile normalization requer semântica por plataforma
- [v2.0 Research]: Kajabi, Teachable, Stan Store, Skool excluídos — sem marketplace público confirmado
- [v2.0 Research]: platform_ids.py como fonte única de verdade para IDs — elimina risco de collision entre 16 scanner files
- [v2.0 Research]: PLAYWRIGHT_SEMAPHORE(3) necessário antes de Gumroad/AppSumo — OOM risk com AsyncIOScheduler e múltiplos contextos
- [v2.0 Research]: Udemy usa /api-2.0/courses/ (não HTML) — Cloudflare Enterprise bloqueia httpx em scraping direto
- [Phase 13]: db.conn.commit() required after INSERT OR IGNORE in sqlite_utils — implicit transactions not auto-committed on GC
- [Phase 13]: rank_type semantics per platform: positional (BR+Gumroad/AppSumo), gravity (ClickBank/JVZoo), upvotes (Product Hunt), enrollment (Udemy)
- [Phase 14-01]: EduzzScanner e MonetizzeScanner sao fallback-only — marketplaces exigem autenticacao, sem vitrine publica confirmada
- [Phase 14-01]: mark_stale() wiring em run_all_scanners() quando scan retorna [] — is_stale funciona em producao, nao apenas em testes
- [Phase 14-01]: Fallback scanner pattern estabelecido — reutilizavel para PerfectPay e Braip em 14-02
- [Phase 14-02]: Braip window.__NUXT__ is Nuxt 2 IIFE — parse with variable binding resolution (params+args->var_map), not raw JSON
- [Phase 14-02]: config.yaml null entries for perfectpay/eduzz/monetizze are explicit opt-in — absence would mean scanner ignored by scheduler
- [Phase 15]: thumbnail usa thumbnail['url'] (não 'imageUrl') — schema Media oficial Product Hunt define url:String!
- [Phase 15]: capsys em vez de capture_logs() para testes de log — base_scraper configura structlog com PrintLoggerFactory+JSONRenderer antes dos testes
- [Phase 15-02]: rank calculado globalmente na lista concatenada (pagina1 + pagina2) — nao reinicia em cada pagina
- [Phase 15-03]: product_hunt usa slug trending em todos os nichos — scanner ignora slug, retorna trending geral (LOCKED no CONTEXT.md)
- [Phase 15-03]: Udemy categories por niche: Marketing/Health & Fitness/Finance & Accounting — categorias oficiais Affiliate API
- [Phase 15-03]: DOMAIN_DELAYS api.producthunt.com=1.0s www.udemy.com=0.5s — reflete rate limits documentados das APIs oficiais
- [Phase 16-01]: JVZooScanner SSR-only sem Playwright — JVZoo renderiza no servidor, sem JS execution necessario
- [Phase 16-01]: PLAYWRIGHT_SEMAPHORE adquirido antes de _get_semaphore(domain) em fetch_spa() — previne deadlock (Pitfall 3)
- [Phase 16-01]: Deteccao Incapsula dupla: ScraperError (403/503) + corpo HTML ('incapsula'/'incident id') — soft-block retorna 200 com HTML de desafio
- [Phase 16-02]: GumroadScanner usa Playwright direto (nao fetch_spa) para scroll loop interativo — PLAYWRIGHT_SEMAPHORE adquirido explicitamente
- [Phase 16-02]: AppSumoScanner usa __NEXT_DATA__ JSON (Next.js SSR) como path principal com CSS fallback /products/ links
- [Phase 17-01]: Paginacao em Python (nao SQL): threshold e multi-platform filters operam sobre conjunto completo antes de paginar
- [Phase 17-01]: MIN_PRODUCTS_PER_PLATFORM=5 como constante de modulo — limiar configuravel sem migracao de schema
- [Phase 17-01]: multi_platform_only como int=0 na rota FastAPI — checkbox HTML unchecked nao envia campo

### Pending Todos

None yet.

### Blockers/Concerns

- [Pre-Phase 14]: Verificar URLs live de Eduzz, Monetizze, PerfectPay, Braip antes de escrever qualquer selector — plataformas BR podem ter migrado de domínio desde 2023
- [Pre-Phase 15]: Confirmar formato atual de /api-2.0/courses/ da Udemy (training data cutoff agosto 2025) e lifetime do token Product Hunt antes de implementar
- [Pre-Phase 16]: Inspecionar response headers do JVZoo para confirmar tipo de bot protection (Incapsula vs Cloudflare) antes de escolher estratégia de mitigação

## Session Continuity

Last session: 2026-03-17T22:36:02.411Z
Stopped at: Completed 17-unified-cross-platform-ranking/17-01-PLAN.md
Resume file: None
