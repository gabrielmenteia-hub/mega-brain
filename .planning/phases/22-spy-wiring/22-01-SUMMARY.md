---
phase: 22-spy-wiring
plan: "01"
subsystem: mis/tests
tags: [tdd, red-tests, spy-wiring, search-orchestrator, dossier-routes]
dependency_graph:
  requires: []
  provides: [RED tests for Phase 22 spy wiring, SPY-V3-01, SPY-V3-02, SPY-V3-03]
  affects: [mis/tests/test_spy_wiring.py, mis/tests/test_search_repository.py, mis/tests/test_dossier_routes.py]
tech_stack:
  added: []
  patterns: [TDD RED, monkeypatch run_spy_batch, FastAPI TestClient, asyncio.create_task spy]
key_files:
  created:
    - mis/tests/test_spy_wiring.py
    - mis/tests/test_dossier_routes.py
  modified:
    - mis/tests/test_search_repository.py
decisions:
  - niches_v3 schema has no created_at column — seed uses (id, name, slug) only
  - subniche_platform_slugs uses platform_id INTEGER (not platform_slug TEXT) — FK to platforms.id
  - test_cancel_session_cancels_spy verifies _TASK_REGISTRY post-DELETE absence (not cancel callback) for clean RED assertion
  - test_results_page_triggers_respy patches asyncio.create_task to detect re-spy call from GET /results
metrics:
  duration: 8m
  completed_date: "2026-03-19"
  tasks_completed: 1
  files_changed: 3
---

# Phase 22 Plan 01: RED Tests — Spy Wiring Summary

TDD RED phase for Phase 22 spy wiring: 8 failing tests across 3 files that define the complete observable contract for automatic spy dispatch after manual search, status transitions, re-spy on results page, fallback platform exclusion, and dossier route extensions.

## What Was Built

Three test files with 8 RED tests that fail for the correct reason (missing functionality):

**`mis/tests/test_spy_wiring.py`** — 5 tests for SPY-V3-01:
- `test_spy_triggered_after_scan`: verifica que `run_spy_batch` é chamado após scan completar (falha: `AttributeError` — `run_spy_batch` não está em `search_orchestrator`)
- `test_session_status_transitions`: verifica que status passa por `'spying'` → `'spy_done'` (falha: mesma razão)
- `test_results_page_triggers_respy`: verifica que GET `/search/{id}/results` dispara `asyncio.create_task` (falha: `AssertionError` — rota não tem create_task)
- `test_fallback_platforms_excluded`: verifica que eduzz/monetizze/perfectpay ficam fora do spy batch (falha: mesma razão — `run_spy_batch` não existe em orchestrator)
- `test_cancel_session_cancels_spy`: verifica que DELETE cancela spy batch via `_TASK_REGISTRY` (falha: `AssertionError` — spy task nunca registrado)

**`mis/tests/test_search_repository.py`** — 1 teste adicionado para SPY-V3-02:
- `test_list_session_products_with_dossier`: verifica que `list_session_products` retorna `product_id` e `dossier_status` (falha: `AssertionError` — colunas ausentes no SELECT)

**`mis/tests/test_dossier_routes.py`** — 2 testes novos para SPY-V3-03:
- `test_from_search_param`: verifica que `?from_search=42` injeta `back_url` e `Voltar aos resultados` no HTML (falha: `AssertionError` — rota ignora o parâmetro)
- `test_oferta_tab_renders`: verifica que GET `/dossier/{id}/tab/oferta` retorna 200 (falha: `AssertionError` — `'oferta'` não está em `_VALID_TABS`)

## Verification

```
pytest mis/tests/test_spy_wiring.py \
       mis/tests/test_search_repository.py::test_list_session_products_with_dossier \
       mis/tests/test_dossier_routes.py::test_from_search_param \
       mis/tests/test_dossier_routes.py::test_oferta_tab_renders \
       -v --timeout=60
```

Result: **8 FAILED** (correct RED state)

Suite existente (excluindo novos testes): **208 passed** — sem regressão.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] niches_v3 schema mismatch in seed helper**
- **Found during:** Task 1 (first test run)
- **Issue:** `_seed_db` tentava inserir `niches_v3` com `created_at`, mas o schema real não tem essa coluna
- **Fix:** Reescrito para usar `SELECT id FROM subniches LIMIT 1` (migration _008 já semeia 44 subnichos) com fallback `INSERT (id, name, slug)` sem `created_at`
- **Files modified:** `mis/tests/test_spy_wiring.py`, `mis/tests/test_dossier_routes.py`

**2. [Rule 1 - Bug] subniche_platform_slugs FK mismatch**
- **Found during:** Task 1 (schema inspection)
- **Issue:** `_seed_db` usava `platform_slug TEXT` na tabela `subniche_platform_slugs`, mas o schema usa `platform_id INTEGER REFERENCES platforms(id)`
- **Fix:** Corrigido para `INSERT (subniche_id, platform_id, search_slug)` sem `created_at`
- **Files modified:** `mis/tests/test_spy_wiring.py`

## Commits

| Hash | Message |
|------|---------|
| 0642ede | test(22-01): add failing RED tests for spy wiring |

## Self-Check: PASSED

- FOUND: mis/tests/test_spy_wiring.py
- FOUND: mis/tests/test_dossier_routes.py
- FOUND: mis/tests/test_dossier_routes.py (extended)
- FOUND: commit 0642ede
- FOUND: .planning/phases/22-spy-wiring/22-01-SUMMARY.md
