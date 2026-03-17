---
phase: 16-international-high-friction
plan: 01
subsystem: mis/scanners
tags: [scanner, jvzoo, tdd, playwright-semaphore, bot-detection, incapsula]
dependency_graph:
  requires:
    - mis/base_scraper.py (BaseScraper, PlatformScanner)
    - mis/platform_ids.py (JVZOO_PLATFORM_ID=10)
    - mis/scanner.py (Product, PlatformScanner)
    - mis/exceptions.py (ScraperError)
  provides:
    - mis/scanners/jvzoo.py (JVZooScanner)
    - mis/base_scraper.PLAYWRIGHT_SEMAPHORE (global Semaphore(3))
  affects:
    - mis/base_scraper.py (fetch_spa() order modified)
    - mis/scanner.py (run_all_scanners can now add jvzoo entry)
tech_stack:
  added:
    - BeautifulSoup (html.parser) para _parse_listings()
  patterns:
    - TDD Red/Green cycle (Wave 0 stub + Wave 1 implementation)
    - Incapsula bot detection via HTTP status + HTML body inspection
    - PLAYWRIGHT_SEMAPHORE(3) acquire-before-domain-semaphore (anti-deadlock)
key_files:
  created:
    - mis/scanners/jvzoo.py
    - mis/tests/test_jvzoo_scanner.py
    - mis/tests/fixtures/jvzoo/listings_category84.html
    - mis/tests/fixtures/jvzoo/incapsula_block.html
  modified:
    - mis/base_scraper.py (PLAYWRIGHT_SEMAPHORE + fetch_spa() + DOMAIN_DELAYS)
decisions:
  - "JVZoo usa fetch() SSR-only — sem Playwright — pois marketplace renderiza HTML no servidor"
  - "PLAYWRIGHT_SEMAPHORE adquirido ANTES do semaphore por dominio em fetch_spa() para prevenir deadlock"
  - "Deteccao Incapsula dupla: via ScraperError (403/503) e via corpo HTML ('incapsula' ou 'incident id')"
  - "rank_type = gravity (posicao 1-based por volume de vendas no JVZoo)"
metrics:
  duration_minutes: 11
  completed_date: "2026-03-17"
  tasks_completed: 2
  files_created: 4
  files_modified: 1
---

# Phase 16 Plan 01: PLAYWRIGHT_SEMAPHORE + JVZooScanner Summary

**One-liner:** JVZooScanner SSR-only com deteccao Incapsula dupla (HTTP status + HTML body) e PLAYWRIGHT_SEMAPHORE(3) global em base_scraper.py para prevencao de OOM.

## What Was Built

JVZooScanner implementado via TDD com 7 testes GREEN:

1. **PLAYWRIGHT_SEMAPHORE** adicionado a `mis/base_scraper.py` — semaforo global que limita Playwright a 3 contextos simultaneos, adquirido ANTES do semaforo por dominio em `fetch_spa()` para prevenir deadlock.

2. **JVZooScanner** em `mis/scanners/jvzoo.py` — scanner SSR-only que:
   - Usa `fetch()` HTTP simples (sem Playwright) — JVZoo renderiza no servidor
   - Detecta bloqueio via `ScraperError` (status 403/503 apos 3 tentativas) → retorna `[]` com `alert='bot_detected'`
   - Detecta soft-block Incapsula via corpo HTML (`'incapsula'` ou `'incident id'`) → retorna `[]` com `alert='bot_detected'`
   - `_parse_listings()` com BeautifulSoup parseia `div.product-listing`, extrai `pid=` via regex, `span.price` para preco, rank 1-based

3. **Fixtures HTML** sinteticas em `mis/tests/fixtures/jvzoo/` para mocking de resposta normal e pagina de bloqueio Incapsula.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Wave 0 — fixtures + stubs + testes RED/GREEN | 430b3fa | mis/scanners/jvzoo.py, mis/tests/test_jvzoo_scanner.py, fixtures/jvzoo/*.html |
| 2 | GREEN — PLAYWRIGHT_SEMAPHORE + JVZooScanner completo | 039d92b | mis/base_scraper.py, mis/scanners/jvzoo.py |

## Verification Results

```
mis/tests/test_jvzoo_scanner.py::test_happy_path PASSED
mis/tests/test_jvzoo_scanner.py::test_field_types PASSED
mis/tests/test_jvzoo_scanner.py::test_bot_detected_http_403 PASSED
mis/tests/test_jvzoo_scanner.py::test_bot_detected_incapsula_body PASSED
mis/tests/test_jvzoo_scanner.py::test_empty_results PASSED
mis/tests/test_jvzoo_scanner.py::test_upsert_no_duplicates PASSED
mis/tests/test_jvzoo_scanner.py::test_playwright_semaphore_exists PASSED

Full suite: 224 passed, 0 failed (320s)
```

## Decisions Made

1. **JVZoo SSR-only:** fetch() sem Playwright confirmado — marketplace renderiza HTML no servidor, sem necessidade de JS execution.

2. **PLAYWRIGHT_SEMAPHORE antes de _get_semaphore():** Ordem anti-deadlock conforme RESEARCH.md Pitfall 3. Se dominio-first, duas tasks concorrentes no mesmo dominio poderiam tentar adquirir PLAYWRIGHT_SEMAPHORE enquanto ja seguram o lock do dominio — deadlock garantido.

3. **Deteccao Incapsula dupla:** HTTP 403/503 + corpo HTML. JVZoo pode retornar 200 com pagina de desafio (soft-block), entao so verificar status code seria insuficiente.

4. **rank_type = gravity (positional):** Rank 1-based por posicao na lista `/listings?sort=sales`. Semantica gravity — produtos mais vendidos aparecem primeiro.

## Deviations from Plan

None — plan executed exactly as written.

## Success Criteria Met

- [x] PLAYWRIGHT_SEMAPHORE = asyncio.Semaphore(3) em mis/base_scraper.py, adquirido ANTES do semaphore por dominio em fetch_spa()
- [x] JVZooScanner em mis/scanners/jvzoo.py: fetch() SSR-only, deteccao Incapsula via status E corpo, _parse_listings() com BeautifulSoup
- [x] 7 testes em test_jvzoo_scanner.py todos GREEN
- [x] Suite completa (mis/tests/) sem regressoes (224 passed)
- [x] Requisito SCAN-INTL-03 coberto: scanner retorna produtos OU degrada com alert='bot_detected'

## Self-Check: PASSED

All created files confirmed on disk:
- FOUND: mis/scanners/jvzoo.py
- FOUND: mis/tests/test_jvzoo_scanner.py
- FOUND: mis/tests/fixtures/jvzoo/listings_category84.html
- FOUND: mis/tests/fixtures/jvzoo/incapsula_block.html

All commits confirmed in git history:
- FOUND: 430b3fa (test(16-01): Wave 0 stubs)
- FOUND: 039d92b (feat(16-01): GREEN implementation)
