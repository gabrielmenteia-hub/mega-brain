---
phase: 01-foundation
plan: 02
subsystem: testing
tags: [rubrics, few-shot, scoring, meta-ads, copy, compliance, performance, pydantic]

# Dependency graph
requires:
  - phase: 01-foundation-01
    provides: NexusConfig thresholds (min_copy_score=7, min_tech_score=6, min_compliance_score=8, min_performance_score=6)
provides:
  - COPY_RUBRIC: 4-criteria rubric (hook/cta/length_fit/persuasion) with numeric level anchors and few-shot examples
  - TECH_RUBRIC: 4-criteria rubric (visual_quality/audio_quality/sync/format_compliance)
  - COMPLIANCE_RUBRIC: 4-criteria rubric (prohibited_content/targeting_alignment/disclosure/community_standards)
  - PERFORMANCE_RUBRIC: 4-criteria rubric (scroll_stopping/engagement_potential/click_intent/audience_match)
  - ALL_RUBRICS: central export list for Phase 2 agent calibration
  - tests/test_rubrics.py: 6 structural tests ensuring rubric integrity
affects:
  - Phase 2 review agents (rubric calibration via few-shot examples)
  - instructor prompt engineering (criteria anchors and level descriptions)
  - scoring drift prevention (threshold-consistent expected_approved flags)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Rubric-as-dict: structured Python dicts with dimension/criteria/few_shot_examples keys"
    - "Numeric level anchors: int keys (10, 8, 6, 4, 2) with domain-specific descriptions"
    - "Few-shot TDD: test before implement, stubs cause RED, real data causes GREEN"
    - "Threshold consistency: expected_approved flags derived from NexusConfig defaults"

key-files:
  created:
    - nexus/rubrics/__init__.py
    - nexus/rubrics/copy_rubric.py
    - nexus/rubrics/tech_rubric.py
    - nexus/rubrics/compliance_rubric.py
    - nexus/rubrics/performance_rubric.py
    - tests/test_rubrics.py
  modified: []

key-decisions:
  - "Rubrics as plain Python dicts (not Pydantic models) — simpler to iterate on and embed directly in instructor prompts"
  - "Numeric level keys as int (10, 8, 6, 4, 2) not float for dict lookup clarity"
  - "compliance threshold=8 enforced strictly — highest threshold because account bans are irreversible"
  - "few-shot inputs in PT-BR matching target audience for max relevance during agent calibration"

patterns-established:
  - "Rubric pattern: {dimension, description, criteria: [{name, weight, description, levels: {int: str}}], few_shot_examples: [{input, expected_score, expected_total, expected_approved, reasoning}]}"
  - "Weight sum invariant: criteria weights must sum to 1.0 (tolerance 0.01) — tested structurally"
  - "Threshold alignment: expected_approved = (expected_total >= THRESHOLDS[dimension])"

requirements-completed: [FND-03]

# Metrics
duration: 4min
completed: 2026-03-26
---

# Phase 1 Plan 02: Review Rubrics Summary

**4 Meta Ads review rubrics com criterios objetivos, ancoras numericas e few-shot examples calibrados com thresholds do NexusConfig para prevencao de scoring drift nos agentes da Phase 2**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-26T23:24:28Z
- **Completed:** 2026-03-26T23:28:09Z
- **Tasks:** 2 (TDD: RED + GREEN)
- **Files modified:** 6 created

## Accomplishments

- 4 rubricas completas em nexus/rubrics/ com dimensao, criterios e few-shot examples
- Suite de 6 testes estruturais garantindo invariantes (weights=1.0, anchors 10+2, threshold consistency)
- TDD ciclo completo: stubs vazios causam RED, implementacao real causa GREEN
- 16/16 testes da suite completa passando em < 1 segundo (models + config + rubrics)
- expected_approved flags 100% consistentes com thresholds do NexusConfig (copy=7, tech=6, compliance=8, performance=6)

## Task Commits

Each task was committed atomically:

1. **Task 1: RED tests + stub files** - `868815a` (test)
2. **Task 2: GREEN — 4 rubrics implementadas** - `a0b14fb` (feat)

**Plan metadata:** (pendente — commit de docs a seguir)

_Note: TDD tasks — test commit precede feat commit_

## Files Created/Modified

- `nexus/rubrics/__init__.py` - Export central: COPY_RUBRIC, TECH_RUBRIC, COMPLIANCE_RUBRIC, PERFORMANCE_RUBRIC, ALL_RUBRICS
- `nexus/rubrics/copy_rubric.py` - Rubrica de copy com hook/cta/length_fit/persuasion (threshold=7)
- `nexus/rubrics/tech_rubric.py` - Rubrica tecnica com visual_quality/audio_quality/sync/format_compliance (threshold=6)
- `nexus/rubrics/compliance_rubric.py` - Rubrica Meta Ads compliance com 4 criterios (threshold=8, mais rigoroso)
- `nexus/rubrics/performance_rubric.py` - Rubrica de predicao de performance com scroll_stopping/engagement_potential/click_intent/audience_match (threshold=6)
- `tests/test_rubrics.py` - 6 testes estruturais para todas as rubricas

## Decisions Made

- **Rubrics como plain dicts** (nao Pydantic models): mais simples para iterar e embutir diretamente em prompts do instructor na Phase 2
- **Level keys como int** (10, 8, 6, 4, 2): clareza de lookup em comparacao com float ou string
- **compliance threshold=8 rigoroso**: bans de conta Meta sao irreversiveis — zero tolerancia a risco
- **Inputs few-shot em PT-BR**: alinhado com o publico-alvo real para maximizar relevancia durante calibracao dos agentes
- **2 examples por rubrica** (minimo exigido): 1 aprovado + 1 reprovado para cobrir ambos os lados da decisao binaria

## Deviations from Plan

None - plano executado exatamente como especificado.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Rubricas prontas para uso na Phase 2 pelos agentes revisores via `from nexus.rubrics import ALL_RUBRICS`
- Criterios e ancoras numericas prontos para embedding em system prompts do instructor
- Threshold consistency garante que agentes calibrados com few-shots vao aprovar/reprovar consistentemente
- Unica dependencia pendente: Phase 2 precisara de ANTHROPIC_API_KEY no .env (bloqueio ja documentado em STATE.md)

---
*Phase: 01-foundation*
*Completed: 2026-03-26*
