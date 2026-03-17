---
phase: 19-code-quality-cleanup
plan: 01
subsystem: infra
tags: [scanner, python, html, tailwind, documentation, tech-debt]

# Dependency graph
requires:
  - phase: 14-br-scanners
    provides: "EduzzScanner/MonetizzeScanner fallback pattern, mark_stale() wiring"
  - phase: 17-unified-cross-platform-ranking
    provides: "unified_table.html, unified ranking view"
provides:
  - "scanner.py com guard clause platform_slug is None no dispatch loop"
  - "scanner.py module docstring documentando o Fallback Scanner Pattern"
  - "unified_table.html com platform badges estilizados via span.platform-badge"
  - "REQUIREMENTS.md INFRA-03 corrigido: tabela platforms (nao products)"
affects: [v2.0-signoff, future-scanner-authors]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Null slug guard: platform_slug is None check antes de construir key no dispatch loop"
    - "Fallback Scanner Pattern: scan_niche() retorna [], emite marketplace_unavailable, run_all_scanners chama mark_stale()"
    - "Platform badge HTML: span.platform-badge com Tailwind utility classes"

key-files:
  created: []
  modified:
    - mis/scanner.py
    - mis/web/templates/unified_table.html
    - .planning/REQUIREMENTS.md

key-decisions:
  - "INFRA-03 referencia tabela `platforms` (confirmado via _006_v2_platforms.py linha 44: db['platforms'].add_column('rank_type', str))"
  - "Guard clause posicionado apos scanner_cls is None, antes de key = f'...' — ordem preserva short-circuit semantico"

patterns-established:
  - "Null slug guard pattern: sempre verificar platform_slug is None apos scanner_cls lookup em loops de dispatch"

requirements-completed: []

# Metrics
duration: 8min
completed: 2026-03-17
---

# Phase 19 Plan 01: Code Quality Cleanup Summary

**Null slug guard + Fallback Scanner Pattern docstring em scanner.py, platform badges Tailwind em unified_table.html, e correcao documental INFRA-03 de `products` para `platforms`**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-03-17T23:30:00Z
- **Completed:** 2026-03-17T23:38:44Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- Guard clause `if platform_slug is None: continue` inserida no dispatch loop de scanner.py, prevenindo que slugs nulos sejam passados para scan_niche()
- Module docstring de scanner.py expandida com secao "Fallback Scanner Pattern" documentando comportamento de Eduzz/Monetizze/PerfectPay com referencia a `marketplace_unavailable`
- Celula Plataforma em unified_table.html substituida por `<span class="platform-badge ...">` estilizado com Tailwind (bg-gray-700, text-gray-200, text-xs, rounded)
- INFRA-03 em REQUIREMENTS.md corrigido: "tabela `products`" -> "tabela `platforms`" (confirmado via migration _006_v2_platforms.py)
- Todos os 6 testes de regressao (test_scanner_niche_id + test_scanner_alerts) passando

## Task Commits

1. **Task 1: Null slug guard + Fallback Scanner Pattern docstring** - `1bd4aaa` (feat)
2. **Task 2: Platform badge estilizado + correcao INFRA-03** - `ae86c6f` (feat)

## Files Created/Modified

- `mis/scanner.py` - Guard clause no dispatch loop (linha 281) + module docstring expandida (linhas 1-19)
- `mis/web/templates/unified_table.html` - Celula Plataforma usa span.platform-badge estilizado
- `.planning/REQUIREMENTS.md` - INFRA-03 corrigido de `products` para `platforms`

## Decisions Made

- **INFRA-03 tabela correta:** Inspecao de `mis/migrations/_006_v2_platforms.py` linha 44 confirma `db["platforms"].add_column("rank_type", str)` — tabela e `platforms`, nao `products`. Correcao documental e factual.
- **Guard clause ordem:** Posicionada apos o bloco `scanner_cls is None` e antes de `key = f"..."` — preserva a logica de short-circuit existente e minimiza diff.

## Deviations from Plan

None - plano executado exatamente como escrito.

## Issues Encountered

None.

## Verification Output

```
=== 1. null slug guard ===
281:            if platform_slug is None:

=== 2. fallback pattern docstring ===
12:    log with alert='marketplace_unavailable'. run_all_scanners() detects the
17:        2. Remove the marketplace_unavailable log.warning() call.

=== 3. platform badge ===
24:        <span class="platform-badge bg-gray-700 text-gray-200 text-xs px-2 py-0.5 rounded">{{ product.platform_name }}</span>...

=== 4. INFRA-03 corrigido ===
- [x] **INFRA-03**: Campo `rank_type` adicionado à tabela `platforms` para identificar a semântica do rank por plataforma

=== 5. pytest ===
6 passed, 261 warnings in 4.46s
```

## User Setup Required

None - sem configuracao externa necessaria.

## Next Phase Readiness

- Tech debt cosmético/defensivo do audit v2.0 liquidado
- scanner.py robusto contra slugs nulos em producao
- Documentacao do Fallback Scanner Pattern preservada para futuros autores de scanners
- unified_table.html com badges HTML prontos para estilizacao futura
- REQUIREMENTS.md factualmente correto

---
*Phase: 19-code-quality-cleanup*
*Completed: 2026-03-17*
