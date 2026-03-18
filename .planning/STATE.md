# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-17)

**Core value:** Entregar o mapa completo do que está vendendo e por que está vendendo — sem esforço manual — para que o usuário possa modelar e lançar seus próprios produtos com máxima vantagem competitiva.
**Current focus:** Phase 20 — Niche Data Model (v3.0 start)

## Current Position

Phase: 20 of 26 (Niche Data Model)
Plan: 0 of TBD in current phase
Status: Ready to plan
Last activity: 2026-03-17 — v3.0 roadmap criado (phases 20–26, 15 requirements, 100% coverage)

Progress: [░░░░░░░░░░] 0% (v3.0)

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

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions relevantes para v3.0:

- [v3.0 Design]: Pesquisa manual exclusiva — APScheduler não dispara scans de subnicho; zero automação de background
- [v3.0 Design]: Hierarquia nicho/subnicho substitui config.yaml de nichos livres — slugs por plataforma embutidos no schema
- [v3.0 Design]: SPY pipeline existente (SalesPageScraper, MetaAdsScraper, ReviewsScraper) reutilizado — não reconstruído
- [v3.0 Design]: Favoritos com histórico de posição exigem tabela de snapshots (product_id, subnicho, rank, timestamp)
- [v3.0 Design]: Alertas baseados em diff entre último scan e scan anterior por subnicho — sem infraestrutura externa

### Pending Todos

None yet.

### Blockers/Concerns

- [Pre-Phase 20]: Definir se nichos/subnichos ficam em tabela SQL ou em YAML/JSON seed — SQL facilita query, YAML facilita edição
- [Pre-Phase 21]: Confirmar se scan manual reutiliza run_all_scanners() com filtro de subnicho ou cria novo orchestrator dedicado
- [Pre-Phase 22]: Confirmar limite de produtos espionados por plataforma por pesquisa (ex: top 5) para controlar custo LLM

## Session Continuity

Last session: 2026-03-17
Stopped at: Roadmap v3.0 criado — phases 20–26 definidas, aguardando /gsd:plan-phase 20
Resume file: None
