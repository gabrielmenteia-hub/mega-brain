---
phase: 15-international-api-based
plan: "03"
subsystem: mis
tags: [scanner, wiring, config, phase-15, product-hunt, udemy]
dependency_graph:
  requires: [15-02]
  provides: [phase-15-complete, scanner-map-updated, config-yaml-updated]
  affects: [mis/scanner.py, mis/base_scraper.py, mis/config.yaml, bin/templates/env.example]
tech_stack:
  added: []
  patterns: [lazy-import-scanner-map, domain-delay-registry, env-example-documentation]
key_files:
  modified:
    - mis/scanner.py
    - mis/base_scraper.py
    - mis/config.yaml
    - bin/templates/env.example
decisions:
  - "product_hunt usa slug 'trending' em todos os nichos — scanner ignora slug, retorna trending geral (LOCKED no CONTEXT.md)"
  - "Udemy: Marketing Digital=Marketing, Emagrecimento=Health & Fitness, Financas=Finance & Accounting (categorias oficiais Affiliate API)"
  - "DOMAIN_DELAYS api.producthunt.com=1.0s, www.udemy.com=0.5s — reflete rate limits documentados das APIs oficiais"
metrics:
  duration_min: 10
  completed_date: "2026-03-17"
  tasks_completed: 2
  tasks_total: 2
  files_modified: 4
---

# Phase 15 Plan 03: Wiring Scanners Summary

**One-liner:** ProductHuntScanner e UdemyScanner conectados ao SCANNER_MAP + config.yaml + DOMAIN_DELAYS — Phase 15 operacionalmente completa com 12 testes GREEN.

## What Was Built

Plano de wiring final da Phase 15: conectou os scanners implementados em 15-02 ao pipeline de produção. Sem este plano, `ProductHuntScanner` e `UdemyScanner` existiam como código morto — invisíveis para `run_all_scanners()` e o scheduler.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | SCANNER_MAP + DOMAIN_DELAYS + config.yaml | cf95f46 | mis/scanner.py, mis/base_scraper.py, mis/config.yaml |
| 2 | env.example — documentar credenciais Phase 15 | 4a87dbf | bin/templates/env.example |

## Key Changes

### mis/scanner.py — run_all_scanners()

Adicionados lazy imports e entradas no SCANNER_MAP:

```python
from .scanners.product_hunt import ProductHuntScanner
from .scanners.udemy import UdemyScanner

SCANNER_MAP = {
    ...
    "product_hunt": ProductHuntScanner,
    "udemy": UdemyScanner,
}
```

### mis/base_scraper.py — DOMAIN_DELAYS

```python
DOMAIN_DELAYS = {
    ...
    "api.producthunt.com": 1.0,   # API oficial com rate limit documentado
    "www.udemy.com": 0.5,          # REST API com autenticacao
}
```

### mis/config.yaml — 3 nichos atualizados

| Niche | product_hunt | udemy |
|-------|-------------|-------|
| marketing-digital | trending | Marketing |
| emagrecimento | trending | Health & Fitness |
| financas-pessoais | trending | Finance & Accounting |

### bin/templates/env.example

Seção MIS adicionada com documentação de `PRODUCT_HUNT_API_TOKEN`, `UDEMY_CLIENT_ID`, `UDEMY_CLIENT_SECRET` — incluindo nota de deprecação da Udemy Affiliate API (2025-01-01) e URLs para obter credenciais.

## Verification

```
All imports OK
PH platform_id=8, Udemy platform_id=9
marketing-digital: product_hunt=trending, udemy=Marketing
emagrecimento: product_hunt=trending, udemy=Health & Fitness
financas-pessoais: product_hunt=trending, udemy=Finance & Accounting
12 passed, 556 warnings in 23.27s
```

## Deviations from Plan

None — plano executado exatamente como escrito.

## Phase 15 Completion

Phase 15 (International API-based) está operacionalmente completa:

- **15-01:** Infraestrutura — platform_ids.py, migrations, DB schema
- **15-02:** Implementação — ProductHuntScanner (GraphQL pagination) + UdemyScanner (Basic Auth REST + fallback)
- **15-03:** Wiring — SCANNER_MAP + config.yaml + DOMAIN_DELAYS + env.example

`python -m mis scan --platform product_hunt` e `--platform udemy` agora funcionam via `run_all_scanners()`.

## Self-Check: PASSED

- mis/scanner.py: FOUND
- mis/base_scraper.py: FOUND
- mis/config.yaml: FOUND
- bin/templates/env.example: FOUND
- 15-03-SUMMARY.md: FOUND
- Commit cf95f46: FOUND
- Commit 4a87dbf: FOUND
