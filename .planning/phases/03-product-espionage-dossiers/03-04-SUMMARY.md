---
phase: 03-product-espionage-dossiers
plan: "04"
subsystem: intelligence
tags: [anthropic, llm, copy-analysis, dossier, tenacity, sqlite-utils, pt-BR]

# Dependency graph
requires:
  - phase: 03-03
    provides: SpyData dataclass e completeness_gate (gate bloqueante para o pipeline LLM)
  - phase: 03-01
    provides: DB schema com tabela llm_calls (migration 003)
provides:
  - "copy_analyzer.py: analyze_copy() — Etapa 1, identifica framework PAS/AIDA/Story/Híbrido, gatilhos emocionais, estrutura narrativa, prova social"
  - "dossier_generator.py: generate_dossier() — Etapa 2, gera dossiê completo em pt-BR com why_it_sells, pains_addressed (com fonte), modeling_template, opportunity_score"
  - "Rastreamento de custo LLM via tabela llm_calls (tokens input/output, cost_usd)"
  - "System prompts em markdown que instruem saída exclusivamente em JSON pt-BR"
affects: [04-orchestrator, 05-api, dashboard]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Pipeline LLM 2-etapas: copy_analyzer (análise estrutural) → dossier_generator (dossiê completo)"
    - "Retry tenacity 3x com backoff exponencial para RateLimitError/APIConnectionError — consistente com BaseScraper"
    - "AsyncAnthropic com model='claude-sonnet-4-6', sem prefill (deprecated)"
    - "System prompt MD externo carregado via Path(__file__).parent.parent / 'prompts' / arquivo.md"
    - "Tracking de tokens e custo após cada chamada LLM via sqlite-utils insert em llm_calls"
    - "Anti-JSON-injection: instrução explícita no prompt 'sem marcadores de código' em vez de prefill"

key-files:
  created:
    - mis/intelligence/__init__.py
    - mis/intelligence/copy_analyzer.py
    - mis/intelligence/dossier_generator.py
    - mis/prompts/copy_analyzer.md
    - mis/prompts/dossier_generator.md
    - mis/tests/test_copy_analyzer.py
    - mis/tests/test_dossier_generator.py
    - mis/tests/fixtures/llm_responses/copy_analyzer_output.json
    - mis/tests/fixtures/llm_responses/dossier_generator_output.json
  modified: []

key-decisions:
  - "Env var ANTHROPIC_API_KEY injetada via monkeypatch nos testes — evita dependência de variável real nos testes"
  - "Fixture migrated_db cria cadeia platform→niche→product→dossier para satisfazer FK de llm_calls.dossier_id"
  - "dossier_generator recebe output do copy_analyzer como input (pipeline sequencial, não paralelo)"
  - "cost_usd calculado com preço claude-sonnet-4-6 (input: $0.000003/token, output: $0.000015/token)"

patterns-established:
  - "Pattern TDD: fixture JSON commitada em tests/fixtures/llm_responses/ — resposta LLM mockada realista"
  - "Pattern teste async: monkeypatch.setenv + patch('mis.intelligence.modulo.AsyncAnthropic') — sem chamar API real"
  - "Pattern prompt: instrução 'Responda APENAS com JSON válido, sem marcadores de código' — anti-prefill"

requirements-completed: [DOS-01, DOS-02, DOS-03, DOS-04]

# Metrics
duration: 10min
completed: 2026-03-15
---

# Phase 03 Plan 04: LLM Intelligence Pipeline Summary

**Pipeline LLM 2-etapas com copy_analyzer (framework PAS/AIDA/Story) e dossier_generator (dossiê pt-BR com opportunity_score, pains com fonte e modeling_template), tracking de custo por chamada em llm_calls**

## Performance

- **Duration:** 10 min
- **Started:** 2026-03-15T00:53:31Z
- **Completed:** 2026-03-15T01:03:26Z
- **Tasks:** 2
- **Files modified:** 9 (criados)

## Accomplishments

- `analyze_copy()` identifica framework de persuasão (PAS/AIDA/Story-based/Híbrido), gatilhos emocionais, estrutura narrativa e prova social a partir de SpyData — retorno JSON estruturado
- `generate_dossier()` gera dossiê completo em pt-BR com todos os campos obrigatórios: why_it_sells, pains_addressed (cada dor com fonte copy|review|ad), modeling_template, opportunity_score (0–100 + justificativa)
- Cada chamada LLM registrada em `llm_calls` com dossier_id, model, stage, input_tokens, output_tokens e cost_usd calculado
- Retry tenacity 3x com backoff exponencial para RateLimitError e APIConnectionError — mesmo padrão do BaseScraper
- 11/11 testes GREEN (5 copy_analyzer + 6 dossier_generator), 74/74 suíte completa sem regressões

## Task Commits

Cada task foi commitada atomicamente:

1. **Task 1: copy_analyzer (DOS-01)** - `49ea606` (feat)
2. **Task 2: dossier_generator (DOS-02/03/04)** - `b252470` (feat)

**Plan metadata:** [gerado a seguir] (docs: complete plan)

## Files Created/Modified

- `mis/intelligence/__init__.py` — Package com re-exports de analyze_copy, CopyAnalysisError, generate_dossier, DossierGenerationError
- `mis/intelligence/copy_analyzer.py` — Etapa 1: analyze_copy() com retry tenacity, CopyAnalysisError para falhas
- `mis/intelligence/dossier_generator.py` — Etapa 2: generate_dossier() com tracking llm_calls via sqlite-utils
- `mis/prompts/copy_analyzer.md` — System prompt para análise de copy, output JSON-only pt-BR
- `mis/prompts/dossier_generator.md` — System prompt para geração de dossiê completo, output JSON-only pt-BR
- `mis/tests/test_copy_analyzer.py` — 5 testes TDD: happy path, all keys, JSON error, retry, no copy
- `mis/tests/test_dossier_generator.py` — 6 testes TDD: pains, template, score, why_it_sells, llm_recorded, json_error
- `mis/tests/fixtures/llm_responses/copy_analyzer_output.json` — Fixture realista de resposta LLM da Etapa 1
- `mis/tests/fixtures/llm_responses/dossier_generator_output.json` — Fixture realista de resposta LLM da Etapa 2

## Decisions Made

- **Env var nos testes via monkeypatch:** `ANTHROPIC_API_KEY` injetada via `monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")` para evitar KeyError sem precisar de credenciais reais
- **FK chain no migrated_db fixture:** `llm_calls.dossier_id` tem FK para `dossiers.id`, que tem FK para `products.id` (que requer `platform_id` e `niche_id`) — fixture cria toda a cadeia de seed data
- **Pipeline sequencial não paralelo:** copy_analyzer roda primeiro, seu output é passado como input para dossier_generator — design deliberado para contexto LLM incremental
- **Custo calculado localmente:** `cost_usd = (input * 0.000003 + output * 0.000015)` seguindo preços claude-sonnet-4-6 no RESEARCH.md

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Env var ANTHROPIC_API_KEY ausente nos testes**
- **Found during:** Task 1 (copy_analyzer GREEN phase)
- **Issue:** Testes falhavam com `KeyError: 'ANTHROPIC_API_KEY'` pois o código lê `os.environ["ANTHROPIC_API_KEY"]` mas os testes não definiam a variável
- **Fix:** Adicionado `monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")` em todos os testes que chamam funções LLM
- **Files modified:** mis/tests/test_copy_analyzer.py, mis/tests/test_dossier_generator.py
- **Verification:** 5/5 e 6/6 testes GREEN após a correção
- **Committed in:** 49ea606 e b252470 (incluídos nos commits de task)

**2. [Rule 2 - Missing Critical] Fixture de DB sem seed para FK chain**
- **Found during:** Task 2 (dossier_generator GREEN phase)
- **Issue:** `sqlite3.IntegrityError: FOREIGN KEY constraint failed` ao inserir em `llm_calls` pois `dossier_id` referencia tabela `dossiers` que estava vazia
- **Fix:** Expandido fixture `migrated_db` para criar seed data completo: platform → niche → product → dossier (IDs 1 e 42 para cobrir ambos os testes)
- **Files modified:** mis/tests/test_dossier_generator.py
- **Verification:** 6/6 testes GREEN após a correção
- **Committed in:** b252470 (incluído no commit de task)

---

**Total deviations:** 2 auto-fixed (2x Rule 2 - missing critical test infrastructure)
**Impact on plan:** Ambas as correções eram necessárias para os testes funcionarem com o schema real do banco. Sem escopo extra.

## Issues Encountered

- `datetime.utcnow()` deprecated no Python 3.14 — warnings esperados (funcional, não bloqueante; migração para `datetime.now(UTC)` pode ser feita em refactor futuro)

## User Setup Required

Nenhuma configuração manual necessária para a suite de testes (testes usam mocks).
Para uso em produção, `ANTHROPIC_API_KEY` deve estar no `.env`.

## Next Phase Readiness

- Pipeline LLM completo e testado — pronto para ser orquestrado pela fase 04 (task orchestrator)
- `analyze_copy()` e `generate_dossier()` exportados via `mis.intelligence` — interface limpa para o orquestrador
- Tracking de custo LLM funcional — `llm_calls` populado automaticamente a cada dossiê gerado

---
*Phase: 03-product-espionage-dossiers*
*Completed: 2026-03-15*
