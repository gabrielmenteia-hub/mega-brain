---
gsd_state_version: 1.0
milestone: v3.0
milestone_name: Market Intelligence 2.0
status: executing
stopped_at: Completed 21-02-PLAN.md
last_updated: "2026-03-18T23:48:45.603Z"
last_activity: "2026-03-18 — Plan 20-01 complete: TDD RED tests for migration _008 and niche_repository"
progress:
  total_phases: 7
  completed_phases: 1
  total_plans: 5
  completed_plans: 4
  percent: 100
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-17)

**Core value:** Entregar o mapa completo do que está vendendo e por que está vendendo — sem esforço manual — para que o usuário possa modelar e lançar seus próprios produtos com máxima vantagem competitiva.
**Current focus:** Phase 20 — Niche Data Model (v3.0 start)

## Current Position

Phase: 20 of 26 (Niche Data Model)
Plan: 1 of 2 in current phase
Status: In progress
Last activity: 2026-03-18 — Plan 20-01 complete: TDD RED tests for migration _008 and niche_repository

Progress: [██████████] 100%

## Performance Metrics

**Velocity (v1.0+v2.0 reference):**
- Total plans completed: 41 (v1.0: 30 + v2.0: 11)
- Average duration: ~10 min/plan
- Total execution time: ~8h

**Recent Trend (v2.0):**

| Phase | Plans | Avg/Plan |
|-------|-------|----------|
| 13–19 | 11 | ~10m |

*Updated after each plan completion*
| Phase 20 P02 | 22 | 2 tasks | 3 files |
| Phase 21-manual-search-engine P01 | 8 | 2 tasks | 3 files |
| Phase 21-manual-search-engine P02 | 14 | 2 tasks | 7 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions relevantes para v3.0:

- [v3.0 Design]: Pesquisa manual exclusiva — APScheduler não dispara scans de subnicho; zero automação de background
- [v3.0 Design]: Hierarquia nicho/subnicho substitui config.yaml de nichos livres — slugs por plataforma embutidos no schema
- [v3.0 Design]: SPY pipeline existente (SalesPageScraper, MetaAdsScraper, ReviewsScraper) reutilizado — não reconstruído
- [v3.0 Design]: Favoritos com histórico de posição exigem tabela de snapshots (product_id, subnicho, rank, timestamp)
- [v3.0 Design]: Alertas baseados em diff entre último scan e scan anterior por subnicho — sem infraestrutura externa
- [Phase 20]: Idempotent migration fast-path via COUNT check to avoid write lock when another connection has pending transaction
- [Phase 20]: 44 subniches seeded (not 42 as plan text stated) — explicit _SUBNICHES list in task action is authoritative
- [Phase 21-manual-search-engine]: test_no_scheduler_on_startup uses deferred import to test start_scheduler=False param — isolates new contract from existing app_client fixture
- [Phase 21-manual-search-engine]: Web search tests fail with 404 (not ImportError) in RED — valid because app starts but router not registered yet
- [Phase 21-manual-search-engine]: subniche_ids in RED tests fixed 1/2/3→101/102/103 — FK targets _008 seed IDs
- [Phase 21-manual-search-engine]: SCANNER_MAP replicated as local constant in run_manual_search — not module-level in scanner.py
- [Phase 21-manual-search-engine]: mark_stale_running_sessions runs before if start_scheduler block — crash recovery always executes

### Pending Todos

- Plan 20-02: implement _008_niche_v3.py migration + niche_repository.py (turns RED tests GREEN)

### Blockers/Concerns

- [RESOLVED - Phase 20]: Nichos/subnichos ficam em tabela SQL (niches_v3, subniches) seed via migration _008 — banco é fonte de verdade
- [Pre-Phase 21]: Confirmar se scan manual reutiliza run_all_scanners() com filtro de subnicho ou cria novo orchestrator dedicado
- [Pre-Phase 22]: Confirmar limite de produtos espionados por plataforma por pesquisa (ex: top 5) para controlar custo LLM

## Session Continuity

Last session: 2026-03-18T23:48:45.591Z
Stopped at: Completed 21-02-PLAN.md
Resume file: None
