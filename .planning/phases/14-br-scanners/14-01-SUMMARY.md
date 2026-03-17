---
phase: 14-br-scanners
plan: 01
subsystem: database, scanners
tags: [sqlite, sqlite_utils, structlog, migration, is_stale, fallback-scanner, eduzz, monetizze, mark_stale]

# Dependency graph
requires:
  - phase: 13-infrastructure
    provides: run_migrations() chain, PlatformScanner ABC, product_repository.upsert_product(), SCANNER_MAP

provides:
  - migration _007 que adiciona is_stale BOOLEAN DEFAULT FALSE em products
  - mark_stale(db, platform_id, niche_id) para marcar produtos desatualizados
  - EduzzScanner fallback-only com alert='marketplace_unavailable'
  - MonetizzeScanner fallback-only com alert='marketplace_unavailable'
  - Wiring mark_stale() em run_all_scanners() quando scan retorna []

affects:
  - 14-02-perfectpay (mesmo padrao de fallback-only scanner)
  - 14-03-braip (mesmo padrao de fallback-only scanner)
  - 15-intl-scanners (mark_stale disponivel para qualquer scanner que retorne [])
  - mis/scanner.py run_all_scanners (agora chama mark_stale em producao)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Fallback scanner pattern: scan_niche() retorna [] + emite alert='marketplace_unavailable' sem levantar excecao"
    - "mark_stale() chamado pelo pipeline run_all_scanners() quando scan retorna [] — is_stale funciona em producao"
    - "Migration pattern: verificar coluna existe antes de add_column (idempotente) + db.conn.commit() obrigatorio"

key-files:
  created:
    - mis/migrations/_007_is_stale.py
    - mis/scanners/eduzz.py
    - mis/scanners/monetizze.py
    - mis/tests/test_migration_007.py
    - mis/tests/test_eduzz_scanner.py
    - mis/tests/test_monetizze_scanner.py
    - mis/tests/fixtures/eduzz/.gitkeep
    - mis/tests/fixtures/monetizze/.gitkeep
  modified:
    - mis/db.py (adicionado import + _run_007 em run_migrations)
    - mis/product_repository.py (is_stale=0 em upsert, nova funcao mark_stale)
    - mis/scanner.py (SCANNER_MAP + wiring mark_stale em run_all_scanners)

key-decisions:
  - "EduzzScanner e MonetizzeScanner sao fallback-only — nao ha marketplace publico acessivel sem autenticacao em ambas plataformas"
  - "mark_stale() chamada em run_all_scanners() apos scan_niche() retornar [] — necessario para is_stale funcionar em producao, nao apenas em testes unitarios"
  - "is_stale=0 setado explicitamente em upsert_product() UPDATE e INSERT — garante reset automatico quando produto e re-escaneado"
  - "platform_id_map carregado via segundo SELECT em run_all_scanners() para resolver platform_id a partir do nome do scanner no config"

patterns-established:
  - "Fallback scanner: herdar PlatformScanner, implementar scan_niche() retornando [] + log.warning com alert='marketplace_unavailable'"
  - "TDD pattern: RED (ImportError esperado) -> GREEN (implementacao minima) -> sem refactor necessario"

requirements-completed:
  - SCAN-BR-01
  - SCAN-BR-02

# Metrics
duration: 8min
completed: 2026-03-17
---

# Phase 14 Plan 01: BR Scanners (Eduzz + Monetizze) Summary

**EduzzScanner e MonetizzeScanner implementados como fallback-only com is_stale pipeline completo: migration _007, mark_stale(), e wiring em run_all_scanners()**

## Performance

- **Duration:** 8 min
- **Started:** 2026-03-17T03:42:03Z
- **Completed:** 2026-03-17T03:50:08Z
- **Tasks:** 2 (TDD)
- **Files modified:** 11 (3 modificados, 8 criados)

## Accomplishments
- Migration _007 idempotente adicionando is_stale BOOLEAN DEFAULT FALSE na tabela products
- upsert_product() atualizado para setar is_stale=0 explicitamente (reset automatico)
- mark_stale(db, platform_id, niche_id) criada em product_repository.py
- EduzzScanner e MonetizzeScanner fallback-only com alert='marketplace_unavailable' estruturado
- EduzzScanner e MonetizzeScanner registrados no SCANNER_MAP em scanner.py
- Wiring mark_stale() em run_all_scanners() quando scan_niche() retorna [] — is_stale funciona em producao
- 17 testes GREEN: 5 migration + 6 eduzz + 6 monetizze (sem skips ou xfails)

## Task Commits

Cada task foi commitada atomicamente:

1. **Task 1: Migration _007 + is_stale em product_repository + wiring em db.py** - `7e5b95c` (feat)
2. **Task 2: EduzzScanner + MonetizzeScanner fallback + SCANNER_MAP + mark_stale wiring** - `2dbca07` (feat)

**Plan metadata:** (docs commit abaixo)

_TDD: ambas tasks seguiram RED → GREEN sem fase refactor necessaria_

## Files Created/Modified

- `mis/migrations/_007_is_stale.py` - Migration idempotente que adiciona is_stale BOOLEAN DEFAULT FALSE
- `mis/db.py` - Adicionado import _run_007 e chamada em run_migrations()
- `mis/product_repository.py` - is_stale=0 em upsert UPDATE/INSERT + nova funcao mark_stale()
- `mis/scanners/eduzz.py` - EduzzScanner fallback-only (marketplace requer autenticacao)
- `mis/scanners/monetizze.py` - MonetizzeScanner fallback-only (403 sem login)
- `mis/scanner.py` - EduzzScanner/MonetizzeScanner em SCANNER_MAP + wiring mark_stale
- `mis/tests/test_migration_007.py` - 5 testes de migration _007
- `mis/tests/test_eduzz_scanner.py` - 6 testes SCAN-BR-01
- `mis/tests/test_monetizze_scanner.py` - 6 testes SCAN-BR-02
- `mis/tests/fixtures/eduzz/.gitkeep` - Diretorio de fixtures (scanner e fallback)
- `mis/tests/fixtures/monetizze/.gitkeep` - Diretorio de fixtures (scanner e fallback)

## Decisions Made

- Fallback-only pattern: Eduzz orbita.eduzz.com e Monetizze app.monetizze.com.br exigem autenticacao sem excecao — sem marketplace publico confirmado pela pesquisa de fase 14
- mark_stale() wiring em run_all_scanners(): necessario para is_stale funcionar em producao — sem isso a coluna existia apenas nos testes unitarios
- platform_id_map resolvido via segundo SELECT no mesmo _db_path da run_all_scanners() — sem alterar a assinatura da funcao
- is_stale=0 setado explicitamente no UPDATE (nao apenas no INSERT) para garantir reset automatico

## Deviations from Plan

None — plano executado exatamente como escrito.

## Issues Encountered

None — todos os 17 testes passaram na primeira tentativa do passo GREEN.

## User Setup Required

None — nenhuma configuracao externa necessaria. Scanners de fallback nao requerem credenciais ou servicos externos.

## Next Phase Readiness

- Padrao de fallback scanner estabelecido para os proximos scanners BR (PerfectPay, Braip) em 14-02 e 14-03
- mark_stale() disponivel para qualquer scanner futuro que retorne []
- is_stale coluna no schema — pronto para consultas de "quais produtos estao desatualizados"

---
*Phase: 14-br-scanners*
*Completed: 2026-03-17*
