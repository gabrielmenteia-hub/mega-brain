---
phase: 16-international-high-friction
plan: "02"
subsystem: mis-scanners
tags: [scanner, gumroad, appsumo, playwright, ssr, tdd, wiring]
dependency_graph:
  requires:
    - 16-01 (PLAYWRIGHT_SEMAPHORE, JVZooScanner base)
    - mis/base_scraper.py (PLAYWRIGHT_SEMAPHORE, fetch_spa, fetch)
    - mis/platform_ids.py (GUMROAD_PLATFORM_ID=11, APPSUMO_PLATFORM_ID=12)
  provides:
    - GumroadScanner (scan_niche, _scan_with_scroll, _parse_html)
    - AppSumoScanner (scan_niche SSR-first + fallback, _parse_html __NEXT_DATA__)
    - SCANNER_MAP updated: jvzoo + gumroad + appsumo
    - config.yaml slugs for all 3 niches
  affects:
    - mis/scanner.py (SCANNER_MAP, run_all_scanners)
    - mis/config.yaml (3 niches x 3 new scanners)
    - mis/base_scraper.py (DOMAIN_DELAYS)
tech_stack:
  added:
    - BeautifulSoup4 (HTML parsing for Gumroad + AppSumo)
    - json stdlib (__NEXT_DATA__ parsing for AppSumo)
  patterns:
    - TDD RED/GREEN (2 tasks: stubs RED -> implementations GREEN)
    - SSR-first with Playwright fallback (AppSumo)
    - Scroll loop with stability detection (Gumroad)
    - PLAYWRIGHT_SEMAPHORE direct acquisition (Gumroad scroll loop)
key_files:
  created:
    - mis/scanners/gumroad.py
    - mis/scanners/appsumo.py
    - mis/tests/test_gumroad_scanner.py
    - mis/tests/test_appsumo_scanner.py
    - mis/tests/fixtures/gumroad/discover_marketing.html
    - mis/tests/fixtures/appsumo/browse_software.html
  modified:
    - mis/base_scraper.py (DOMAIN_DELAYS: gumroad.com + appsumo.com added)
    - mis/scanner.py (SCANNER_MAP: jvzoo + gumroad + appsumo added)
    - mis/config.yaml (slugs for jvzoo/gumroad/appsumo in 3 niches)
decisions:
  - "GumroadScanner usa _scan_with_scroll() com Playwright direto (nao self.fetch_spa()) — scroll loop interativo precisa do objeto page; PLAYWRIGHT_SEMAPHORE adquirido explicitamente para protecao OOM identica"
  - "AppSumoScanner usa __NEXT_DATA__ JSON como path principal — Next.js SSR embute dados estruturados; CSS fallback com /products/ links para degradacao gracosa"
  - "AppSumo deal_price preferred over price — representa o preco real do deal no momento"
  - "JVZoo usa category ID 84 para todos os nichos — sem categoria especifica para saude/financas confirmada"
metrics:
  duration: "13 min"
  completed_date: "2026-03-17"
  tasks_completed: 2
  files_created: 6
  files_modified: 3
  tests_added: 12
  tests_total: 236
---

# Phase 16 Plan 02: GumroadScanner + AppSumoScanner + Wiring Summary

GumroadScanner com Playwright scroll loop (PLAYWRIGHT_SEMAPHORE direto) + AppSumoScanner com SSR-first __NEXT_DATA__ parsing + Playwright fallback, ambos wirados no SCANNER_MAP e config.yaml com slugs para 3 nichos.

## Tasks Completed

| Task | Description | Commit | Files |
|------|-------------|--------|-------|
| 1 | Wave 0 — fixtures + stubs + testes RED/GREEN | abb361a | 6 criados |
| 2 | GREEN — implementacoes completas + wiring | 061bf4b | 5 modificados |

## Verification Results

```
12 passed (test_gumroad_scanner.py + test_appsumo_scanner.py)
236 passed total (suite completa sem regressoes)
SCANNER_MAP: jvzoo, gumroad, appsumo OK
config.yaml: 3 niches x 3 scanners OK
PLAYWRIGHT_SEMAPHORE(3): intacto
```

## TDD Execution

### RED Phase (Task 1)

- 4 testes RED esperados: test_happy_path + test_field_types para Gumroad e AppSumo
- 8 testes GREEN imediatos: empty_results, marketplace_unavailable, upsert_no_duplicates, is_stale para ambos
- Stubs criados: _parse_html() retorna [], _scan_with_scroll() delega ao fetch_spa()

### GREEN Phase (Task 2)

- GumroadScanner._scan_with_scroll(): loop de scroll Playwright com estabilidade 2 rounds
- GumroadScanner._parse_html(): article.product-card -> gumroad.com/l/ -> BeautifulSoup
- AppSumoScanner._parse_html(): __NEXT_DATA__ JSON primary + CSS /products/ fallback
- DOMAIN_DELAYS: gumroad.com=2.0, appsumo.com=2.0 adicionados
- SCANNER_MAP + config.yaml atualizados

## Deviations from Plan

None — plan executed exactly as written.

The technical note about GumroadScanner using Playwright directly (not self.fetch_spa()) was pre-documented in the plan header and implemented as specified.

## Requirements Covered

- SCAN-INTL-04: GumroadScanner operacional (6 testes GREEN)
- SCAN-INTL-05: AppSumoScanner operacional (6 testes GREEN)

## Self-Check: PASSED

- mis/scanners/gumroad.py: FOUND
- mis/scanners/appsumo.py: FOUND
- mis/tests/test_gumroad_scanner.py: FOUND
- mis/tests/test_appsumo_scanner.py: FOUND
- mis/tests/fixtures/gumroad/discover_marketing.html: FOUND
- mis/tests/fixtures/appsumo/browse_software.html: FOUND
- Commit abb361a: FOUND (TDD RED)
- Commit 061bf4b: FOUND (GREEN + wiring)
