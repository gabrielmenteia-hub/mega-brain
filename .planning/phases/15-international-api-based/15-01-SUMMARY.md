---
phase: 15-international-api-based
plan: "01"
subsystem: mis/scanners
tags: [tdd, product-hunt, udemy, fixtures, red-cycle, international-scanners]
dependency_graph:
  requires: []
  provides:
    - mis/scanners/product_hunt.py (ProductHuntScanner stub — importável, verifica credenciais)
    - mis/scanners/udemy.py (UdemyScanner stub — importável, verifica credenciais + HTTP 401)
    - mis/tests/fixtures/product_hunt/trending_today.json (3 produtos: jarvis-ai-assistant, notion-ai-plus, cursor-ide)
    - mis/tests/fixtures/udemy/courses_marketing.json (3 cursos: Digital Marketing, Marketing Masterclass, Email Marketing)
    - mis/tests/test_product_hunt_scanner.py (6 testes — ciclo RED)
    - mis/tests/test_udemy_scanner.py (6 testes — ciclo RED)
  affects:
    - mis/tests/ (12 novos testes adicionados ao suite)
    - Plano 15-02 (ciclo GREEN: implementar parse completo nos stubs)
tech_stack:
  added: []
  patterns:
    - TDD RED cycle com stubs intencionais (retornam [] sem parse)
    - capsys para verificação de logs JSON quando structlog usa PrintLoggerFactory
    - respx.mock para POST GraphQL (ProductHunt) e GET REST (Udemy)
    - Bearer token auth (ProductHunt) e Basic Auth via base64 (Udemy)
key_files:
  created:
    - mis/scanners/product_hunt.py
    - mis/scanners/udemy.py
    - mis/tests/fixtures/product_hunt/trending_today.json
    - mis/tests/fixtures/udemy/courses_marketing.json
    - mis/tests/test_product_hunt_scanner.py
    - mis/tests/test_udemy_scanner.py
  modified: []
decisions:
  - "thumbnail usa thumbnail['url'] e não thumbnail['imageUrl'] — schema Media oficial do Product Hunt define url: String!, não imageUrl"
  - "capsys em vez de structlog.testing.capture_logs() para testes de credenciais — base_scraper.py configura structlog com PrintLoggerFactory+JSONRenderer no nível de módulo antes dos testes"
  - "UdemyScanner stub tenta GET real e captura HTTP 401/403/404 como api_discontinued — preserva arquitetura para credenciais legadas que ainda funcionem"
metrics:
  duration_minutes: 8
  completed_date: "2026-03-17"
  tasks_completed: 2
  files_created: 6
  files_modified: 0
---

# Phase 15 Plan 01: Wave 0 — TDD RED Fixtures + Stubs Summary

**One-liner:** TDD RED cycle completo — fixtures JSON (PH + Udemy), stubs de scanner que verificam credenciais/HTTP errors, e 12 testes escritos (8 GREEN / 4 RED conforme esperado).

## What Was Built

### Fixtures JSON
- `mis/tests/fixtures/product_hunt/trending_today.json` — estrutura GraphQL real com 3 produtos (jarvis-ai-assistant, notion-ai-plus, cursor-ide), `hasNextPage=true`, `thumbnail.url` (não `imageUrl`)
- `mis/tests/fixtures/udemy/courses_marketing.json` — estrutura REST com 3 cursos (IDs: 1234567, 7654321, 9876543), `price_detail.amount`, `avg_rating`, `image_480x270`

### Scanner Stubs (RED — retornam [] intencionalmente)
- `ProductHuntScanner`: verifica `PRODUCT_HUNT_API_TOKEN`; se ausente `return []` + `alert='missing_credentials'`; se presente faz POST GraphQL mas retorna `[]` sem parse
- `UdemyScanner`: verifica `UDEMY_CLIENT_ID` + `UDEMY_CLIENT_SECRET`; captura `HTTPStatusError` 401/403/404 como `alert='api_discontinued'`; retorna `[]` sem parse

### Test Scaffolds (12 testes)
**ProductHuntScanner (6):**
- `test_happy_path` — RED (stub retorna [])
- `test_field_types` — RED (stub retorna [])
- `test_missing_credentials` — GREEN (stub implementa credential check)
- `test_empty_results` — GREEN (stub retorna [] em qualquer caso)
- `test_upsert_no_duplicates` — GREEN (testa product_repository, não o scanner)
- `test_is_stale` — GREEN (testa mark_stale em product_repository)

**UdemyScanner (6):**
- `test_happy_path` — RED (stub retorna [])
- `test_field_types` — RED (stub retorna [])
- `test_missing_credentials` — GREEN (stub implementa credential check)
- `test_empty_results` — GREEN (stub retorna [] em qualquer caso)
- `test_api_discontinued_fallback` — GREEN (stub captura HTTP 401)
- `test_upsert_no_duplicates` — GREEN (testa product_repository)

**Estado final:** 4 FAILED (RED) + 8 PASSED (GREEN) — ciclo TDD RED correto.

## Verification Run

```
cd mis && python -m pytest tests/test_product_hunt_scanner.py tests/test_udemy_scanner.py -v
# 4 failed (RED: happy_path + field_types x2), 8 passed
```

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] structlog.testing.capture_logs() não captura logs do scanner**
- **Found during:** Task 2 — ao rodar test_missing_credentials
- **Issue:** `base_scraper.py` configura structlog com `PrintLoggerFactory + JSONRenderer` no nível de módulo. Quando o scanner é importado antes dos testes, `capture_logs()` não consegue interceptar os logs (estrutlog já configurado). O mesmo bug afeta `test_braip_scanner::test_drift_alert` e `test_eduzz_scanner::test_drift_alert` (pré-existente).
- **Fix:** Substituiu `capture_logs()` por `capsys.readouterr()` para verificar a string `"missing_credentials"` no stdout JSON. Comportamento verificado correto: os logs são emitidos e contêm o campo `alert`.
- **Files modified:** `mis/tests/test_product_hunt_scanner.py`, `mis/tests/test_udemy_scanner.py`
- **Commit:** b99a672

## Next Steps (Plan 15-02)

1. **Implementar `_parse_post()` em `ProductHuntScanner`** — parsear `edges[].node` do GraphQL, rank por posição, `thumbnail.url`
2. **Implementar `_parse_course()` em `UdemyScanner`** — parsear `results[]`, prefixar URL com `https://www.udemy.com`, `price_detail.amount`, `avg_rating`
3. **Ciclo GREEN:** 4 testes RED devem passar após implementação

## Self-Check

Files created:
- [x] mis/tests/fixtures/product_hunt/trending_today.json — FOUND
- [x] mis/tests/fixtures/udemy/courses_marketing.json — FOUND
- [x] mis/scanners/product_hunt.py — FOUND
- [x] mis/scanners/udemy.py — FOUND
- [x] mis/tests/test_product_hunt_scanner.py — FOUND
- [x] mis/tests/test_udemy_scanner.py — FOUND

Commits verified:
- 5b6136c — feat(15-01): create fixtures JSON + scanner stubs
- 9bc5d64 — test(15-01): add failing test scaffolds (RED cycle)
- b99a672 — fix(15-01): use capsys for structlog assertion

## Self-Check: PASSED
