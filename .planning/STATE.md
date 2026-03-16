# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-16)

**Core value:** Entregar o mapa completo do que está vendendo e por que está vendendo — sem esforço manual — para que o usuário possa modelar e lançar seus próprios produtos com máxima vantagem competitiva.
**Current focus:** Phase 13 — Infrastructure + Tech Debt

## Current Position

Phase: 13 of 17 (Infrastructure + Tech Debt)
Plan: 0 of TBD in current phase
Status: Ready to plan
Last activity: 2026-03-16 — Milestone v2.0 roadmap criado, 17 requisitos mapeados em 5 fases (13–17)

Progress: [░░░░░░░░░░] 0% (v2.0) | v1.0 completo (30/30 planos)

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

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting v2.0:

- [v2.0 Research]: rank_type metadata field necessário antes de qualquer scanner — percentile normalization requer semântica por plataforma
- [v2.0 Research]: Kajabi, Teachable, Stan Store, Skool excluídos — sem marketplace público confirmado
- [v2.0 Research]: platform_ids.py como fonte única de verdade para IDs — elimina risco de collision entre 16 scanner files
- [v2.0 Research]: PLAYWRIGHT_SEMAPHORE(3) necessário antes de Gumroad/AppSumo — OOM risk com AsyncIOScheduler e múltiplos contextos
- [v2.0 Research]: Udemy usa /api-2.0/courses/ (não HTML) — Cloudflare Enterprise bloqueia httpx em scraping direto

### Pending Todos

None yet.

### Blockers/Concerns

- [Pre-Phase 14]: Verificar URLs live de Eduzz, Monetizze, PerfectPay, Braip antes de escrever qualquer selector — plataformas BR podem ter migrado de domínio desde 2023
- [Pre-Phase 15]: Confirmar formato atual de /api-2.0/courses/ da Udemy (training data cutoff agosto 2025) e lifetime do token Product Hunt antes de implementar
- [Pre-Phase 16]: Inspecionar response headers do JVZoo para confirmar tipo de bot protection (Incapsula vs Cloudflare) antes de escolher estratégia de mitigação

## Session Continuity

Last session: 2026-03-16
Stopped at: v2.0 ROADMAP.md criado — 5 fases (13–17), 17 requisitos mapeados, coverage 100%
Resume file: None
