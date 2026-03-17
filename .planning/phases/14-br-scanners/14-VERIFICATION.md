---
phase: 14-br-scanners
verified: 2026-03-17T04:30:00Z
status: passed
score: 14/14 must-haves verified
re_verification: false
---

# Phase 14: BR Scanners Verification Report

**Phase Goal:** Implementar scanners para as 4 plataformas de afiliados BR (Eduzz, Monetizze, PerfectPay, Braip) com suporte a is_stale, migration _007, e integração completa no pipeline de scan.
**Verified:** 2026-03-17T04:30:00Z
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| #  | Truth | Status | Evidence |
|----|-------|--------|----------|
| 1  | EduzzScanner.scan_niche() retorna [] e emite alert='marketplace_unavailable' sem lançar exceção | VERIFIED | mis/scanners/eduzz.py L42-52: log.warning com alert='marketplace_unavailable', return []. 6 testes GREEN. |
| 2  | MonetizzeScanner.scan_niche() retorna [] e emite alert='marketplace_unavailable' sem lançar exceção | VERIFIED | mis/scanners/monetizze.py L42-52: idêntico ao Eduzz. 6 testes GREEN. |
| 3  | Coluna is_stale existe na tabela products após run_migrations() | VERIFIED | mis/migrations/_007_is_stale.py: add_column is_stale BOOLEAN DEFAULT FALSE. test_is_stale_column_added GREEN. |
| 4  | upsert_product() seta is_stale=False em cada produto persistido | VERIFIED | mis/product_repository.py L54: is_stale=0 no UPDATE; L88: is_stale=0 no INSERT. test_is_stale_default_false e test_upsert_resets_stale GREEN. |
| 5  | mark_stale() seta is_stale=True em batch por (platform_id, niche_id) | VERIFIED | mis/product_repository.py L118-137: UPDATE products SET is_stale=1. test_mark_stale_sets_true GREEN. |
| 6  | EduzzScanner e MonetizzeScanner registrados em SCANNER_MAP em scanner.py | VERIFIED | mis/scanner.py L186-198: ambos importados e registrados em SCANNER_MAP. |
| 7  | run_all_scanners() chama mark_stale() quando scan_niche() retorna [] | VERIFIED | mis/scanner.py L302-312: if not products → mark_stale(db, resolved_platform_id, resolved_niche_id). |
| 8  | PerfectPayScanner.scan_niche() retorna [] e emite alert='marketplace_unavailable' sem exceção | VERIFIED | mis/scanners/perfectpay.py L42-52: idêntico ao padrão fallback. 6 testes GREEN. |
| 9  | BraipScanner.scan_niche() retorna lista de produtos com external_id=hash, price=float (centavos/100), rank=int | VERIFIED | mis/scanners/braip.py: _build_products() usa hash_id, price_cents/100.0, enumerate(start=1). test_happy_path e test_field_types GREEN. |
| 10 | BraipScanner emite alert='schema_drift' quando window.__NUXT__ não é encontrado no HTML | VERIFIED | mis/scanners/braip.py L199-207: log.warning com alert='schema_drift'. test_drift_alert GREEN. |
| 11 | BraipScanner e PerfectPayScanner registrados em SCANNER_MAP | VERIFIED | mis/scanner.py L188-198: ambos importados e registrados. |
| 12 | config.yaml tem entradas para braip nos 3 nichos | VERIFIED | mis/config.yaml: marketing-digital→cursos-online, emagrecimento→encapsulados, financas-pessoais→cursos-online. |
| 13 | config.yaml tem entradas explícitas eduzz: null, monetizze: null, perfectpay: null nos 3 nichos | VERIFIED | mis/config.yaml: todos os 3 nichos têm as 3 entradas null explícitas com comentário de razão. |
| 14 | Suite completa 29 testes GREEN sem skips ou xfails | VERIFIED | pytest output: 29 passed, 0 skips, 0 xfails — executado em 46.32s. |

**Score:** 14/14 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `mis/migrations/_007_is_stale.py` | Migration idempotente que adiciona is_stale BOOLEAN DEFAULT FALSE | VERIFIED | 31 linhas. run_migration_007() com verificação de coluna existente + db.conn.commit(). |
| `mis/scanners/eduzz.py` | EduzzScanner subclass de PlatformScanner | VERIFIED | 53 linhas. Exporta EduzzScanner. Herda PlatformScanner. |
| `mis/scanners/monetizze.py` | MonetizzeScanner subclass de PlatformScanner | VERIFIED | 53 linhas. Exporta MonetizzeScanner. Herda PlatformScanner. |
| `mis/scanners/perfectpay.py` | PerfectPayScanner subclass de PlatformScanner (fallback-only) | VERIFIED | 53 linhas. Exporta PerfectPayScanner. Herda PlatformScanner. |
| `mis/scanners/braip.py` | BraipScanner com parsing window.__NUXT__ | VERIFIED | 216 linhas. Exporta BraipScanner, _parse_nuxt_products. IIFE parser completo. |
| `mis/product_repository.py` | upsert_product() + mark_stale() com is_stale support | VERIFIED | is_stale=0 em UPDATE e INSERT. mark_stale() implementada. |
| `mis/tests/test_migration_007.py` | 5 testes de migration _007 | VERIFIED | 118 linhas, 5 funções de teste. |
| `mis/tests/test_eduzz_scanner.py` | 6 testes SCAN-BR-01 | VERIFIED | 143 linhas, 6 funções de teste. |
| `mis/tests/test_monetizze_scanner.py` | 6 testes SCAN-BR-02 | VERIFIED | 143 linhas, 6 funções de teste. |
| `mis/tests/test_perfectpay_scanner.py` | 6 testes SCAN-BR-03 | VERIFIED | 143 linhas, 6 funções de teste. |
| `mis/tests/test_braip_scanner.py` | 6 testes SCAN-BR-04 | VERIFIED | 216 linhas, 6 funções de teste. |
| `mis/tests/fixtures/braip/catalog_cursos-online.html` | Fixture HTML real com window.__NUXT__ | VERIFIED | 152 linhas, 60KB. Contém window.__NUXT__ (grep count=1). |
| `mis/tests/fixtures/eduzz/.gitkeep` | Diretório de fixtures (fallback scanner) | VERIFIED | Diretório existe. |
| `mis/tests/fixtures/monetizze/.gitkeep` | Diretório de fixtures (fallback scanner) | VERIFIED | Diretório existe. |
| `mis/tests/fixtures/perfectpay/.gitkeep` | Diretório de fixtures (fallback scanner) | VERIFIED | Diretório existe. |
| `mis/config.yaml` | Entradas braip + null para 3 plataformas em 3 nichos | VERIFIED | 79 linhas. Todos os 3 nichos atualizados. |
| `mis/base_scraper.py` | DOMAIN_DELAYS: marketplace.braip.com: 2.0 | VERIFIED | L41: "marketplace.braip.com": 2.0 adicionado. |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| mis/db.py | mis/migrations/_007_is_stale.py | import + _run_007(db_path) em run_migrations() | WIRED | L23: from .migrations._007_is_stale import run_migration_007 as _run_007. L43: _run_007(db_path). |
| mis/scanner.py SCANNER_MAP | mis/scanners/eduzz.py + monetizze.py + perfectpay.py + braip.py | import + registro no dict SCANNER_MAP | WIRED | L186-198: todos 4 importados e registrados. |
| mis/scanners/eduzz.py | mis/platform_ids.py | from mis.platform_ids import EDUZZ_PLATFORM_ID | WIRED | L14: import presente. EDUZZ_PLATFORM_ID=4. |
| mis/scanners/braip.py | mis/platform_ids.py | from mis.platform_ids import BRAIP_PLATFORM_ID | WIRED | L28: import presente. BRAIP_PLATFORM_ID=7. |
| mis/scanner.py run_all_scanners() | mis/product_repository.mark_stale() | chamada após scan_niche() retornar [] | WIRED | L305: from .product_repository import mark_stale. L307: mark_stale(_stale_db, resolved_platform_id, resolved_niche_id). |
| mis/scanners/braip.py _parse_nuxt_products() | window.__NUXT__ JSON blob | re.search + IIFE resolver + json.loads | WIRED | L83-128: idx=html.find("window.__NUXT__") + _resolve_iife_vars() + produtos extraídos. |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| SCAN-BR-01 | 14-01-PLAN.md | EduzzScanner varre marketplace Eduzz por nicho e persiste top produtos | SATISFIED | EduzzScanner implementado como fallback (marketplace indisponível sem auth). Pesquisa confirmou ausência de marketplace público. Padrão correto: retorna [] + alert + mark_stale via pipeline. |
| SCAN-BR-02 | 14-01-PLAN.md | MonetizzeScanner varre marketplace Monetizze por nicho | SATISFIED | MonetizzeScanner implementado como fallback (403 sem login). Mesmo padrão SCAN-BR-01. 6 testes GREEN. |
| SCAN-BR-03 | 14-02-PLAN.md | PerfectPayScanner varre marketplace PerfectPay por nicho | SATISFIED | PerfectPayScanner implementado como fallback (checkout-only sem marketplace público). 6 testes GREEN. |
| SCAN-BR-04 | 14-02-PLAN.md | BraipScanner varre marketplace Braip por nicho | SATISFIED | BraipScanner implementado com parsing SSR real (window.__NUXT__ IIFE). Fixture ao vivo capturada. 6 testes GREEN incluindo test_happy_path com produto real. |

Nota: REQUIREMENTS.md lista SCAN-BR-01 a SCAN-BR-04 como mapeados para Phase 14 e marcados como Complete. Traceability confirmada.

Nenhum requirement ID adicional mapeado para Phase 14 em REQUIREMENTS.md que não esteja coberto pelos planos.

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| mis/scanners/braip.py | 61 | "# {} placeholders are valid JSON objects" | Info | Comentário de código explicativo — não é placeholder de implementação. Sem impacto. |

Nenhum blocker ou warning encontrado. Todos os arquivos da fase foram inspecionados.

---

### Human Verification Required

Nenhum item requer verificação humana. Todos os comportamentos observáveis da fase são verificáveis programaticamente:

- Fallback scanners: comportamento determinístico (sempre retorna [] + emite log) — coberto por testes.
- BraipScanner: parsing SSR verificado via fixture real — testes passam com produto real (price=29.90).
- is_stale pipeline: verificado por testes de banco em memória (tmp_path).
- Todos os 29 testes passam em ambiente real.

---

### Commit Verification

Todos os 6 commits de task documentados nos SUMMARYs verificados em git log:

| Commit | Tipo | Descrição |
|--------|------|-----------|
| 7e5b95c | feat | migration _007 + is_stale em product_repository + wiring em db.py |
| 2dbca07 | feat | EduzzScanner + MonetizzeScanner fallback + SCANNER_MAP + mark_stale wiring |
| 11d52a8 | test | failing tests para PerfectPayScanner SCAN-BR-03 (RED) |
| a0587fc | feat | PerfectPayScanner fallback-only + registro em SCANNER_MAP (GREEN) |
| f96e0cf | test | failing tests para BraipScanner SCAN-BR-04 + live fixture (RED) |
| 5e6ef18 | feat | BraipScanner SSR implementation + config.yaml atualizado (GREEN) |

---

## Summary

Phase 14 alcançou seu objetivo integralmente. Os 4 scanners BR foram implementados com arquitetura correta:

- Eduzz, Monetizze e PerfectPay: fallback-only (marketplaces requerem autenticação — confirmado por pesquisa no CONTEXT.md e RESEARCH.md). Implementam o padrão estabelecido: retornam [] + emitem alert='marketplace_unavailable' + pipeline chama mark_stale().

- Braip: scanner SSR funcional. Fixture ao vivo capturada. Parser IIFE correto para Nuxt 2 (desvio documentado no SUMMARY: o plano assumia JSON puro, a fixture revelou formato IIFE com variable binding — corrigido com _resolve_iife_vars()). Retorna produtos reais com hash como external_id.

- Migration _007: adiciona coluna is_stale BOOLEAN DEFAULT FALSE de forma idempotente. Wired em db.py.

- product_repository: mark_stale() implementada. upsert_product() reseta is_stale=0. Pipeline (run_all_scanners) chama mark_stale() quando scan retorna [] — is_stale funciona em produção, não apenas em testes.

- config.yaml: todas as 4 plataformas BR configuradas em todos os 3 nichos (braip com slugs reais, demais com null explícito + comentário de razão).

- 29/29 testes GREEN. Sem skips, xfails ou warnings que indiquem problemas de implementação.

---

_Verified: 2026-03-17T04:30:00Z_
_Verifier: Claude (gsd-verifier)_
