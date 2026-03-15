---
phase: 03-product-espionage-dossiers
verified: 2026-03-14T12:00:00Z
status: passed
score: 10/10 must-haves verified
re_verification: false
gaps: []
human_verification:
  - test: "Executar python -m mis spy --url https://hotmart.com/produto-real e verificar saída JSON no terminal"
    expected: "Pipeline completo executa, dossier_json persistido no banco, structlog emite spy.done com confidence > 0"
    why_human: "Requer URL real com página de vendas ativa e ANTHROPIC_API_KEY configurada no .env"
  - test: "Verificar que dossier gerado está realmente em pt-BR"
    expected: "Campos why_it_sells, pains_addressed e modeling_template contêm texto em português"
    why_human: "Comportamento do LLM em produção depende de API real — prompts instruem pt-BR mas saída real não foi testada"
---

# Phase 03: Product Espionage + Dossiers — Verification Report

**Phase Goal:** Implementar sistema de espionagem competitiva que coleta dados de produtos concorrentes (copy, ads, reviews) e gera dossiês estruturados com inteligência LLM sobre por que vendem e como modelar.
**Verified:** 2026-03-14T12:00:00Z
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SPY-01: Sistema extrai copy completa da página de vendas (headlines, sub-headlines, argumentos, CTA, estrutura narrativa) | VERIFIED | `mis/spies/sales_page.py` — `SalesPageScraper.extract()` implementada, retorna dict com headlines/sub_headlines/arguments/ctas/narrative_structure via LLM parser; 5/5 testes GREEN |
| 2 | SPY-02: Sistema coleta anúncios ativos via Meta Ad Library (criativos e copy) | VERIFIED | `mis/spies/meta_ads.py` — `MetaAdsScraper.fetch_ads()` chama `graph.facebook.com/v25.0/ads_archive` com `ad_reached_countries=BR`; retorna [] graciosamente sem token; 5/5 testes GREEN |
| 3 | SPY-03: Sistema extrai estrutura da oferta (preço, bônus, garantias, upsells, downsells) | VERIFIED | Mesma chamada de `SalesPageScraper.extract()` do SPY-01 retorna price/bonuses/guarantees/upsells/downsells; `test_extract_offer_fields` GREEN |
| 4 | SPY-04: Sistema coleta e classifica reviews separando positivos (4-5★) e negativos (1-3★) | VERIFIED | `mis/spies/reviews.py` — `ReviewsScraper.collect()` com plataformas nativas + Google fallback; valência calculada por threshold 4.0; 5/5 testes GREEN |
| 5 | SPY-05: Dados só são processados pelo LLM quando completude mínima é atingida | VERIFIED | `mis/spies/completeness_gate.py` — `check_completeness()` bloqueia quando copy < 100 chars ou reviews < min_reviews; 9/9 testes GREEN |
| 6 | DOS-01: IA gera análise explicando por que o produto está vendendo | VERIFIED | `mis/intelligence/copy_analyzer.py` — `analyze_copy()` retorna framework_type, emotional_triggers, narrative_structure, social_proof_elements; wired em `spy_orchestrator._execute_spy_pipeline()`; 5/5 testes GREEN |
| 7 | DOS-02: IA mapeia dores endereçadas com base na copy e reviews | VERIFIED | `mis/intelligence/dossier_generator.py` — `generate_dossier()` retorna pains_addressed como lista de dicts com pain+source; prompt instrui citação de fonte (copy/review/ad); 6/6 testes GREEN |
| 8 | DOS-03: IA gera template de modelagem com estrutura para criar produto próprio | VERIFIED | `generate_dossier()` retorna modeling_template com sections/key_arguments/offer_structure; `test_modeling_template` GREEN |
| 9 | DOS-04: IA atribui score de oportunidade por nicho | VERIFIED | `generate_dossier()` retorna opportunity_score com score (int 0-100) e justification (str); `test_opportunity_score` GREEN |
| 10 | DOS-05: Dossiê exibe confidence score indicando qualidade/completude dos dados | VERIFIED | `check_completeness()` retorna confidence 0-100 com pesos definidos; confidence persistido em dossiers.confidence_score e dentro de dossier_json; `test_confidence_full` e variantes GREEN |

**Score:** 10/10 truths verified

---

## Required Artifacts

| Artifact | Purpose | Status | Details |
|----------|---------|--------|---------|
| `mis/migrations/_003_spy_dossiers.py` | Migration aditiva para espionagem | VERIFIED | 88 linhas; `run_migration_003()` com add_column() idempotente; cria reviews e llm_calls; contém `add_column` |
| `mis/spies/sales_page.py` | SalesPageScraper platform-agnostic | VERIFIED | 114 linhas; exporta `SalesPageScraper`; herda `BaseScraper`; usa `AsyncAnthropic` |
| `mis/spies/meta_ads.py` | MetaAdsScraper — Meta Ad Library API | VERIFIED | 76 linhas; exporta `MetaAdsScraper`; usa httpx + `ads_archive`; `ad_reached_countries` presente |
| `mis/spies/reviews.py` | ReviewsScraper — plataformas nativas + Google fallback | VERIFIED | 152 linhas; exporta `ReviewsScraper`; herda `BaseScraper`; NATIVE_REVIEW_PLATFORMS definido |
| `mis/spies/completeness_gate.py` | SpyData + check_completeness() | VERIFIED | 77 linhas; exporta `SpyData`, `check_completeness`; structlog com campos machine-readable |
| `mis/intelligence/copy_analyzer.py` | Etapa 1 do pipeline LLM | VERIFIED | 109 linhas; exporta `analyze_copy`, `CopyAnalysisError`; retry tenacity 3x |
| `mis/intelligence/dossier_generator.py` | Etapa 2 do pipeline LLM | VERIFIED | 141 linhas; exporta `generate_dossier`; registra `llm_calls` no banco; retry tenacity 3x |
| `mis/prompts/sales_page_extractor.md` | System prompt para extração de copy+oferta | VERIFIED | 40 linhas; contém JSON schema e instrução sem fencing |
| `mis/prompts/copy_analyzer.md` | System prompt para análise de copy | VERIFIED | 34 linhas; contém JSON schema |
| `mis/prompts/dossier_generator.md` | System prompt para dossiê em pt-BR | VERIFIED | 70 linhas; contém pt-BR e JSON schema completo |
| `mis/spy_orchestrator.py` | Ponto de entrada público da espionagem | VERIFIED | 300 linhas; exporta `run_spy`, `run_spy_url`, `run_spy_batch`; `SPY_TOP_N = 10` |
| `mis/__main__.py` | CLI entrypoint | VERIFIED | 67 linhas; subcomando `spy` com `--url` e `--product-id` mutuamente exclusivos |
| `mis/config.yaml` | Configuração spy | VERIFIED | Contém seção `spy` com `max_concurrent_spy: 3` e `min_reviews: 10` |
| `mis/tests/test_migration_003.py` | Testes da migration | VERIFIED | 5 testes GREEN |
| `mis/tests/test_sales_page_spy.py` | Testes SPY-01 e SPY-03 | VERIFIED | 5 testes GREEN; fixtures commitadas |
| `mis/tests/test_meta_ads_spy.py` | Testes SPY-02 | VERIFIED | 5 testes GREEN |
| `mis/tests/test_reviews_spy.py` | Testes SPY-04 | VERIFIED | 5 testes GREEN |
| `mis/tests/test_completeness_gate.py` | Testes SPY-05 e DOS-05 | VERIFIED | 161 linhas; 9 testes GREEN |
| `mis/tests/test_copy_analyzer.py` | Testes DOS-01 | VERIFIED | 188 linhas; 5 testes GREEN |
| `mis/tests/test_dossier_generator.py` | Testes DOS-02/03/04 | VERIFIED | 6 testes GREEN |
| `mis/tests/test_spy_orchestrator.py` | Testes integração + CLI + scheduler | VERIFIED | 11 testes GREEN |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `mis/spies/sales_page.py` | `mis/base_scraper.py` | `class SalesPageScraper(BaseScraper)` | VERIFIED | Herança confirmada na linha 37 |
| `mis/spies/sales_page.py` | Anthropic API | `AsyncAnthropic` + `messages.create()` | VERIFIED | Linhas 25-27 e 107-113; retry tenacity presente |
| `mis/spies/meta_ads.py` | `graph.facebook.com/v25.0/ads_archive` | `httpx.AsyncClient GET` | VERIFIED | Linha 61; `ads_archive` na META_API_URL; `ad_reached_countries` sempre presente |
| `mis/spies/reviews.py` | `mis/base_scraper.py` | `class ReviewsScraper(BaseScraper)` | VERIFIED | Herança confirmada na linha 32 |
| `mis/intelligence/copy_analyzer.py` | Anthropic API | `AsyncAnthropic` + retry | VERIFIED | Linhas 14-20 e 80-87 |
| `mis/intelligence/dossier_generator.py` | `copy_analyzer.py` | `copy_analysis: dict` como parâmetro | VERIFIED | Parâmetro em `generate_dossier(data, copy_analysis, ...)` |
| `mis/intelligence/dossier_generator.py` | tabela `llm_calls` | `db["llm_calls"].insert(...)` | VERIFIED | Linhas 75-84; stage, tokens, cost_usd registrados |
| `mis/spy_orchestrator.py` | todos os 3 spies | `SalesPageScraper`, `MetaAdsScraper`, `ReviewsScraper` instanciados | VERIFIED | Linhas 201-212 em `_execute_spy_pipeline()` |
| `mis/spy_orchestrator.py` | `completeness_gate.py` | `check_completeness()` chamado antes do LLM | VERIFIED | Linha 234 |
| `mis/spy_orchestrator.py` | `copy_analyzer.py` e `dossier_generator.py` | pipeline sequencial | VERIFIED | Linhas 240-241 |
| `mis/scheduler.py` | `spy_orchestrator.run_spy_batch()` | `_scan_and_spy_job()` encadeia após `run_all_scanners()` | VERIFIED | Linha 18 importa `run_spy_batch, SPY_TOP_N`; linha 109 chama `run_spy_batch()` |

---

## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| SPY-01 | 03-01, 03-05 | Extração de copy completa da página de vendas | SATISFIED | `SalesPageScraper.extract()` retorna headlines/sub_headlines/arguments/ctas/narrative_structure; testes com fixture commitada |
| SPY-02 | 03-02, 03-05 | Coleta de anúncios Meta Ad Library | SATISFIED | `MetaAdsScraper.fetch_ads()` com API oficial; ad_reached_countries=BR; graceful fallback sem token |
| SPY-03 | 03-01, 03-05 | Extração da estrutura da oferta | SATISFIED | Mesma chamada LLM do SPY-01; retorna price/bonuses/guarantees/upsells/downsells |
| SPY-04 | 03-02, 03-05 | Coleta e classificação de reviews | SATISFIED | `ReviewsScraper.collect()` com plataformas nativas + Google fallback; valência por threshold 4.0 |
| SPY-05 | 03-03, 03-05 | Data completeness gate | SATISFIED | `check_completeness()` bloqueia copy ausente/curta e reviews insuficientes; confidence_score 0-100 |
| DOS-01 | 03-04, 03-05 | Análise LLM de por que o produto vende | SATISFIED | `analyze_copy()` retorna framework_type, emotional_triggers, narrative_structure, social_proof_elements |
| DOS-02 | 03-04, 03-05 | Mapeamento de dores com fonte | SATISFIED | `generate_dossier()` retorna pains_addressed como `[{"pain": "...", "source": "copy|review|ad"}]` |
| DOS-03 | 03-04, 03-05 | Template de modelagem | SATISFIED | `generate_dossier()` retorna modeling_template com sections/key_arguments/offer_structure |
| DOS-04 | 03-04, 03-05 | Score de oportunidade | SATISFIED | `generate_dossier()` retorna opportunity_score com score (0-100) e justification |
| DOS-05 | 03-03, 03-05 | Confidence score no dossiê | SATISFIED | `check_completeness()` calcula confidence 0-100; persistido em dossiers.confidence_score e dossier_json |

**Todos os 10 requisitos da Fase 3 verificados e satisfeitos.** Nenhum requisito órfão detectado. REQUIREMENTS.md marca todos como `[x] Complete`.

---

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `mis/spy_orchestrator.py` | 274, 255, 115 | `datetime.utcnow()` deprecated no Python 3.12+ | Info | Deprecation warning em testes; funciona corretamente hoje |
| `mis/intelligence/dossier_generator.py` | 83 | `datetime.utcnow()` deprecated | Info | Mesma situação — warnings, sem impacto funcional |
| `mis/tests/test_dossier_generator.py` | 72 | `datetime.utcnow()` deprecated | Info | Código de teste apenas |

Nenhum anti-padrão bloqueante encontrado. Nenhum placeholder, stub, `return null` ou handler vazio. Os warnings de `utcnow()` são informativos e não afetam a corretude do pipeline.

---

## Human Verification Required

### 1. Pipeline End-to-End com API Real

**Test:** Executar `python -m mis spy --url <URL_DE_PAGINA_DE_VENDAS_REAL>` com `ANTHROPIC_API_KEY` configurada no `.env`
**Expected:** Pipeline executa completo: fetch da página, extração de copy, gate passa, copy_analyzer e dossier_generator chamados, dossier_json persistido no banco com status='done'
**Why human:** Requer URL real ativa (Hotmart/ClickBank/Kiwify) e API key válida — não pode ser verificado por mock

### 2. Output em pt-BR

**Test:** Após execução com produto brasileiro real, verificar dossier_json no banco SQLite
**Expected:** Campos `why_it_sells`, `pains_addressed`, `modeling_template` contêm texto em português
**Why human:** Prompts instruem pt-BR mas o comportamento real do LLM depende da chamada de API — só verificável em produção

### 3. Meta Ads com Token Válido

**Test:** Configurar `META_ACCESS_TOKEN` no `.env` e executar `MetaAdsScraper.fetch_ads("produto real")`
**Expected:** Lista de anúncios ativos retornada com campos page_name, ad_snapshot_url, ad_creative_bodies
**Why human:** API Meta requer token OAuth válido com permissões de Ad Library — não testável em CI

---

## Gaps Summary

Nenhum gap identificado. Todos os 10 requisitos (SPY-01 a SPY-05, DOS-01 a DOS-05) estão implementados com código substantivo, testado com fixtures commitadas (sem dependência de API real), e corretamente conectados no pipeline.

**Suite de testes:** 51/51 testes passando (includes todos os 8 arquivos de teste da Fase 3).

**Destaques da implementação:**
- Migration _003 é totalmente idempotente — não destrói dados legados
- SalesPageScraper usa LLM como parser universal — zero seletores CSS por plataforma
- MetaAdsScraper tem degradação graciosa sem token — nunca bloqueia o pipeline
- ReviewsScraper captura ScraperError internamente — falha silenciosa por design
- Completeness gate retorna dossier parcial quando copy ok mas reviews insuficientes
- SPY_TOP_N = 10 hardcoded no spy_orchestrator por decisão do usuário — não está no config.yaml
- CLI funcional: `python -m mis spy --url URL` e `--product-id ID`

---

_Verified: 2026-03-14T12:00:00Z_
_Verifier: Claude (gsd-verifier)_
