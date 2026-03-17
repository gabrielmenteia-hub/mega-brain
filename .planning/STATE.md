---
gsd_state_version: 1.0
milestone: v2.0
milestone_name: Platform Expansion
status: in-progress
stopped_at: Completed 14-br-scanners/14-01-PLAN.md
last_updated: "2026-03-17T03:50:08Z"
last_activity: 2026-03-17 — Phase 14 Plan 01 concluido: EduzzScanner + MonetizzeScanner fallback + is_stale migration + mark_stale wiring
progress:
  total_phases: 5
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

### Pending Todos

None yet.

### Blockers/Concerns

- [Pre-Phase 14]: Verificar URLs live de Eduzz, Monetizze, PerfectPay, Braip antes de escrever qualquer selector — plataformas BR podem ter migrado de domínio desde 2023
- [Pre-Phase 15]: Confirmar formato atual de /api-2.0/courses/ da Udemy (training data cutoff agosto 2025) e lifetime do token Product Hunt antes de implementar
- [Pre-Phase 16]: Inspecionar response headers do JVZoo para confirmar tipo de bot protection (Incapsula vs Cloudflare) antes de escolher estratégia de mitigação

## Session Continuity

Last session: 2026-03-17T03:50:08Z
Stopped at: Completed 14-br-scanners/14-01-PLAN.md
Resume file: .planning/phases/14-br-scanners/14-01-SUMMARY.md
