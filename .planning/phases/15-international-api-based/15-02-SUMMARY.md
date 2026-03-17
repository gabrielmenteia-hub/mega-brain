---
phase: 15-international-api-based
plan: "02"
subsystem: mis/scanners
tags: [tdd, green-cycle, product-hunt, udemy, graphql, basic-auth, cursor-pagination]
dependency_graph:
  requires:
    - 15-01 (stubs + fixtures + test scaffolds RED)
  provides:
    - mis/scanners/product_hunt.py (ProductHuntScanner completo — GraphQL cursor pagination)
    - mis/scanners/udemy.py (UdemyScanner completo — Basic Auth REST + fallback api_discontinued)
  affects:
    - mis/tests/ (12 testes agora GREEN)
tech_stack:
  added: []
  patterns:
    - TDD GREEN cycle — implementacao completa sobre stubs RED existentes
    - GraphQL cursor pagination com 2 requisicoes (after=None / after=endCursor)
    - Basic Auth via base64.b64encode para Udemy REST API
    - _parse_post() / _parse_course() como funcoes auxiliares puras (nao metodos)
    - Graceful degradation: missing_credentials + api_discontinued + schema_drift
key_files:
  created: []
  modified:
    - mis/scanners/product_hunt.py
    - mis/scanners/udemy.py
decisions:
  - "rank calculado globalmente na lista concatenada (pagina1 + pagina2) — nao reinicia em cada pagina"
  - "test_cli_spy_help falha pre-existente de ambiente (subprocess usa Python 3.14 sem mis instalado) — out of scope"
  - "hasNextPage verificado antes da segunda requisicao — evita chamada desnecessaria quando < 20 trending"
metrics:
  duration_minutes: 12
  completed_date: "2026-03-17"
  tasks_completed: 2
  files_created: 0
  files_modified: 2
---

# Phase 15 Plan 02: GREEN Cycle — ProductHuntScanner + UdemyScanner Summary

**One-liner:** Ciclo GREEN completo — ProductHuntScanner com cursor pagination GraphQL (2 paginas, rank ordinal, thumbnail.url) e UdemyScanner com Basic Auth REST + fallback api_discontinued para HTTP 401/403/404, todos os 12 testes passando.

## What Was Built

### ProductHuntScanner (completo)

`mis/scanners/product_hunt.py` — reescrito do stub RED para implementacao plena:

- **`_parse_post(node, rank, niche_id) -> Product | None`** — funcao auxiliar pura que parseia `edges[].node` do GraphQL. Extrai `slug` como `external_id`, calcula `rank` ordinal (1-based), `price=None` sempre, `thumbnail_url=thumbnail['url']` (schema Media.url — nao imageUrl).
- **`scan_niche()`** — realiza 2 requisicoes GraphQL se `hasNextPage=True`: pagina 1 com `after=None`, pagina 2 com `after=endCursor`. Rank global continua incrementando atraves das paginas. Excecoes retornam `[]` com `alert=schema_drift`.
- **`_post_graphql()`** — mantido da estrutura do stub, sem alteracoes.

### UdemyScanner (completo)

`mis/scanners/udemy.py` — reescrito do stub RED para implementacao plena:

- **`_parse_course(course, rank, niche_id) -> Product | None`** — funcao auxiliar pura. `external_id=str(course['id'])`, `url='https://www.udemy.com'+course['url']`, `price=float(price_detail.amount)` ou None, `rating=float(avg_rating)` ou None, `thumbnail_url=image_480x270`.
- **`scan_niche()`** — Basic Auth via `base64.b64encode(client_id:client_secret)`, GET para `/api-2.0/courses/` com `category=platform_slug`. HTTP 401/403/404 retorna `[]` com `alert=api_discontinued`. Excecoes gerais retornam `[]` com `alert=schema_drift`.

## Verification Run

```
cd mis && python -m pytest tests/test_product_hunt_scanner.py tests/test_udemy_scanner.py -v
# 12 passed

cd mis && python -m pytest tests/ --tb=short -q
# 216 passed, 1 failed (pre-existing: test_cli_spy_help — subprocess environment issue)
```

## Deviations from Plan

None — plano executado exatamente como escrito.

### Pre-existing Issue (out of scope)

**test_cli_spy_help** em `tests/test_spy_orchestrator.py` falha porque usa `subprocess` com `sys.executable` (Python 3.14 system-level sem `mis` instalado). Nao relacionado a esta execucao. Registrado em deferred-items.

## Self-Check

Files modified:
- [x] mis/scanners/product_hunt.py — FOUND
- [x] mis/scanners/udemy.py — FOUND

Commits verified:
- 47911e4 — feat(15-02): implement ProductHuntScanner — GraphQL cursor pagination GREEN
- c766ee1 — feat(15-02): implement UdemyScanner — Basic Auth REST + graceful fallback GREEN

## Self-Check: PASSED
