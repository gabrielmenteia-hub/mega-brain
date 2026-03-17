---
phase: 17-unified-cross-platform-ranking
plan: "01"
subsystem: mis-dashboard
tags: [ranking, unified, percentile, htmx, fastapi, tdd]
dependency_graph:
  requires: []
  provides: [list_unified_ranking, GET /ranking/unified, GET /ranking/unified/table]
  affects: [mis/product_repository.py, mis/web/routes/ranking.py, mis/web/templates/]
tech_stack:
  added: [unicodedata.normalize, collections.defaultdict]
  patterns: [percentile-normalization, htmx-partial, tab-navigation, python-pagination]
key_files:
  created:
    - mis/tests/test_unified_ranking.py
    - mis/web/templates/ranking_tabs.html
    - mis/web/templates/unified.html
    - mis/web/templates/unified_table.html
  modified:
    - mis/product_repository.py
    - mis/web/routes/ranking.py
    - mis/web/templates/ranking.html
decisions:
  - "Paginação feita em Python (não SQL) para garantir que threshold filter e multi-platform filter operem sobre o conjunto completo antes de paginar"
  - "MIN_PRODUCTS_PER_PLATFORM=5 como constante de módulo — limiar configurável sem migração"
  - "multi_platform_only recebe int=0 na rota (não bool) porque checkbox HTML unchecked não envia o campo; FastAPI recebe ausência como 0"
  - "_normalize_title() via NFKD+ascii+lower para comparação cross-platform sem dependências externas"
metrics:
  duration: "9m 18s"
  completed_date: "2026-03-17T22:34:50Z"
  tasks_completed: 3
  files_created: 4
  files_modified: 3
  tests_added: 12
  tests_green: 12
---

# Phase 17 Plan 01: Unified Cross-Platform Ranking Summary

**One-liner:** Percentile normalization cross-platform ranking via `list_unified_ranking()` + FastAPI routes + HTMX templates with niche filter, multi-platform toggle, and tab navigation.

## Tasks Completed

| Task | Name | Commit | Type |
|------|------|--------|------|
| 1 | RED — 12 test stubs para list_unified_ranking() | 7852327 | test (TDD RED) |
| 2 | GREEN — list_unified_ranking() em product_repository.py | 43deece | feat (TDD GREEN) |
| 3 | Rotas FastAPI + Templates HTMX + Tabs de Navegação | acea00e | feat |

## Artifacts Criados

### mis/tests/test_unified_ranking.py
12 testes cobrindo DASH-V2-01/02/03:
- `test_unified_score_order` — ordenação por unified_score DESC
- `test_percentile_positional` — rank #1/total=5 → 80.0
- `test_percentile_gravity` — gravity max/max → 100.0
- `test_null_rank_excluded` — produtos com rank=NULL excluídos
- `test_min_products_threshold` — plataforma com <5 produtos excluída
- `test_niche_filter` — filtro de nicho correto
- `test_multi_platform_filter` — toggle multi-plataforma funciona
- `test_title_normalization` — "Café Marketing" == "cafe marketing"
- `test_result_fields` — todos os campos obrigatórios presentes
- `test_stale_included` — produtos stale aparecem com is_stale=True
- `test_single_platform_warning` — warning quando 1 plataforma
- `test_pagination` — page=2, per_page=5 → slice correto

### mis/product_repository.py (modificado)
Adicionadas:
- Constante `MIN_PRODUCTS_PER_PLATFORM = 5`
- `_normalize_title(title)` — NFKD + ascii + lower + strip
- `_compute_unified_scores(rows)` — score por rank_type
- `list_unified_ranking(db_path, niche, multi_platform_only, per_page, page)` — algoritmo de 11 steps

### mis/web/routes/ranking.py (modificado)
Adicionadas:
- `_get_unified_context()` — helper de contexto
- `GET /ranking/unified` — página completa ou partial HTMX
- `GET /ranking/unified/table` — partial HTMX sempre

### mis/web/templates/ranking_tabs.html (novo)
Partial compartilhado com tabs "Por Plataforma | Unificado".

### mis/web/templates/unified.html (novo)
Página completa com filtros (nicho, per_page, multi-platform checkbox) e banner de warning single-platform.

### mis/web/templates/unified_table.html (novo)
Partial HTMX com tabela de 5 colunas: posição, produto, plataforma, score, rank original. Stale products aparecem em text-gray-500.

### mis/web/templates/ranking.html (modificado)
`{% include "ranking_tabs.html" %}` inserido antes do h1.

## Resultado dos Testes

```
12 passed in 2.91s
```

Todos os critérios de sucesso satisfeitos:
- [x] 12 testes GREEN
- [x] list_unified_ranking() retorna products ordenados por unified_score DESC
- [x] Percentile positional: rank #1 / total=5 → 80.0
- [x] Percentile gravity: valor/max * 100
- [x] Plataformas com < 5 produtos excluídas silenciosamente
- [x] rank=NULL excluídos do resultado
- [x] Toggle multi_platform_only filtra por título normalizado em 2+ plataformas
- [x] warning_single_platform=True quando nicho tem dados de 1 plataforma
- [x] Paginação correta (page=2 retorna slice correto)
- [x] GET /ranking/unified responde com template unified.html
- [x] GET /ranking/unified/table responde com partial unified_table.html
- [x] Tabs visíveis em /ranking e /ranking/unified
- [x] pytest mis/tests/ tests_unified_ranking.py: 12 passed

## Decisões Tomadas

1. **Paginação em Python (nunca no SQL):** O threshold filter (MIN_PRODUCTS_PER_PLATFORM) e o multi-platform filter precisam operar sobre o conjunto completo de dados antes de paginar. Colocar LIMIT no SQL tornaria esses filtros incorretos.

2. **MIN_PRODUCTS_PER_PLATFORM=5 como constante de módulo:** Valor limiar configurável sem requerer migração de schema. Padrão escolhido conforme DASH-V2-03.

3. **multi_platform_only como int=0 na rota:** Checkbox HTML não envia campo quando desmarcado — FastAPI recebe ausência como 0 e presença como 1. A função `list_unified_ranking` converte internamente com `bool()`.

4. **_normalize_title via NFKD+ascii+lower:** Comparação cross-platform sem dependências externas (unicodedata é stdlib Python). "Café Marketing" e "cafe marketing" normalizam para "cafe marketing".

## Deviations from Plan

None — plano executado exatamente como escrito.

## Self-Check: PASSED
