# Phase 1: Foundation - Research

**Researched:** 2026-03-26
**Domain:** Typed data models (Pydantic v2), externalized configuration (pydantic-settings), review rubrics with few-shot calibration
**Confidence:** HIGH

## Summary

Phase 1 builds the data layer that every subsequent phase depends on: Pydantic models for review scores and creative bundles, a typed configuration object loaded from `.env`, and structured rubrics with few-shot examples that anchor LLM scoring consistency.

The stack is mature and well-documented. Pydantic v2 (current: 2.12.x) provides `BaseModel` with `Field` constraints for typed validation. `pydantic-settings` (current: 2.13.x) extends `BaseSettings` to load from `.env` with type coercion and prefix support. `instructor` (current: 1.14.x) now uses `from_provider("anthropic/model")` as the unified API (replacing the older `from_anthropic()`). Few-shot calibration is natively supported via `model_config = ConfigDict(json_schema_extra={"examples": [...]})` on Pydantic models.

The biggest risk in this phase is defining rubrics that are too vague to anchor LLM scoring. Each rubric dimension needs explicit criteria with numeric anchors ("8/10 means: clear hook in first 3 seconds, addresses specific pain point, includes CTA"). Without this, Phase 2 agents will produce inconsistent scores (Pitfall 1: LLM Scoring Drift).

**Primary recommendation:** Build models.py, config.py, and rubrics/ as three independent units, each fully testable without API calls.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| FND-01 | Modelos Pydantic tipados (ReviewScore, CreativeBundle, NexusConfig) como base de dados | Pydantic v2 BaseModel + Field with ge/le constraints, model_validator for cross-field rules. Fully unit-testable with pytest. |
| FND-02 | Toda configuracao carregada de .env sem hardcode | pydantic-settings BaseSettings with SettingsConfigDict(env_file=".env", env_prefix="NEXUS_"). Type coercion from env vars is automatic. |
| FND-03 | Rubricas com criterios objetivos e exemplos few-shot | Rubrics stored as Python dicts/dataclasses or YAML files. Few-shot examples embedded via ConfigDict(json_schema_extra={"examples": [...]}) for instructor integration. |
</phase_requirements>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pydantic | >=2.10.0 | Typed data models with validation | Industry standard for Python data validation. v2 is 5-17x faster than v1. Field constraints (ge, le, min_length) enforce data quality at creation time. |
| pydantic-settings | >=2.7.0 | Config from .env with type safety | Official Pydantic extension. Loads env vars with automatic type coercion, validates at startup, supports env_prefix for namespacing. |
| python-dotenv | >=1.0.0 | .env file loading | Already implied by pydantic-settings, but explicit for clarity. Mature, stable. |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| instructor | >=1.8.0 | Structured LLM output via Pydantic | Phase 2+ for review agents, but rubric examples in Phase 1 use the same Pydantic models instructor will consume. |
| PyYAML | >=6.0 | YAML rubric files (optional) | If rubrics are stored as .yaml rather than inline Python dicts. |

### Dev Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| pytest | >=8.0.0 | Test runner |
| pytest-asyncio | >=0.24.0 | Async test support (future phases) |
| ruff | >=0.8.0 | Linter + formatter |
| mypy | >=1.13.0 | Static type checking |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pydantic-settings | raw python-dotenv + manual parsing | Loses type coercion, no startup validation, more boilerplate |
| Pydantic BaseModel | dataclasses | Loses Field constraints (ge/le), validation errors, JSON schema generation (needed by instructor) |
| YAML rubrics | JSON rubrics | YAML is more readable for multi-line text (rubric descriptions). Either works. |

**Installation:**
```bash
pip install pydantic pydantic-settings python-dotenv
pip install pytest ruff mypy  # dev
```

## Architecture Patterns

### Recommended Project Structure

```
nexus/
  __init__.py
  models.py              # AgentScore, CreativeBundle, ReviewResult (Pydantic)
  config.py              # NexusConfig (BaseSettings from .env)
  rubrics/
    __init__.py
    copy_rubric.py        # COPY_RUBRIC dict + few-shot examples
    tech_rubric.py        # TECH_RUBRIC dict + few-shot examples
    compliance_rubric.py  # COMPLIANCE_RUBRIC dict + few-shot examples
    performance_rubric.py # PERFORMANCE_RUBRIC dict + few-shot examples
tests/
  __init__.py
  test_models.py          # Model validation (valid + invalid data)
  test_config.py          # Config loading from .env
  test_rubrics.py         # Rubric structure + few-shot completeness
.env.example              # Template with all NEXUS_ vars documented
```

### Pattern 1: Pydantic Models with Field Constraints

**What:** Define all data flowing through the pipeline as Pydantic models with explicit constraints.
**When to use:** Every data boundary (LLM output, config, inter-component).

```python
# Source: https://docs.pydantic.dev/latest/concepts/fields/
from pydantic import BaseModel, Field, model_validator

class AgentScore(BaseModel):
    """Structured output from a single review agent."""
    dimension: str = Field(description="Review dimension: copy|tech|compliance|performance")
    score: int = Field(ge=1, le=10, description="Quality score 1-10")
    approved: bool = Field(description="Meets minimum threshold for this dimension")
    feedback: str = Field(min_length=10, description="Specific actionable feedback")
    strengths: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "dimension": "copy",
                    "score": 8,
                    "approved": True,
                    "feedback": "Hook forte com urgencia temporal. CTA claro. Pode melhorar transicao do meio.",
                    "strengths": ["Hook com urgencia", "CTA direto"],
                    "issues": ["Transicao abrupta no segundo paragrafo"]
                },
                {
                    "dimension": "copy",
                    "score": 4,
                    "approved": False,
                    "feedback": "Hook generico sem diferenciacao. Sem CTA. Texto longo demais para formato video curto.",
                    "strengths": [],
                    "issues": ["Hook generico", "Sem CTA", "Texto excede 60 palavras"]
                }
            ]
        }
    )
```

### Pattern 2: BaseSettings with env_prefix

**What:** Single config object that loads all settings from `.env` with `NEXUS_` prefix.
**When to use:** Any configurable value (thresholds, model IDs, paths, retry limits).

```python
# Source: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
from pydantic_settings import BaseSettings, SettingsConfigDict

class NexusConfig(BaseSettings):
    """All NEXUS configuration. Loaded from .env with NEXUS_ prefix."""

    # API keys
    anthropic_api_key: str

    # Review thresholds (per dimension)
    min_copy_score: int = 7
    min_tech_score: int = 6
    min_compliance_score: int = 8
    min_performance_score: int = 6

    # Pipeline control
    max_review_attempts: int = 3
    review_model: str = "claude-sonnet-4-20250514"

    # Paths
    output_dir: str = "output"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="NEXUS_",
        env_file_encoding="utf-8",
    )
```

Corresponding `.env`:
```
NEXUS_ANTHROPIC_API_KEY=sk-ant-...
NEXUS_MIN_COPY_SCORE=7
NEXUS_MAX_REVIEW_ATTEMPTS=3
NEXUS_REVIEW_MODEL=claude-sonnet-4-20250514
NEXUS_OUTPUT_DIR=output
```

### Pattern 3: Rubric as Structured Data

**What:** Each review dimension has a rubric with numeric anchors and few-shot examples.
**When to use:** Every agent prompt in Phase 2 will reference these rubrics.

```python
# nexus/rubrics/copy_rubric.py

COPY_RUBRIC = {
    "dimension": "copy",
    "description": "Avalia qualidade do script para video publicitario curto",
    "criteria": [
        {
            "name": "hook",
            "weight": 0.3,
            "levels": {
                10: "Hook irresistivel - para o scroll, cria curiosidade imediata, urgencia temporal",
                8: "Hook forte - chama atencao, aborda dor especifica do nicho",
                6: "Hook adequado - funcional mas generico, sem diferenciacao",
                4: "Hook fraco - nao para o scroll, poderia ser de qualquer produto",
                2: "Sem hook - comeca com descricao do produto sem gatilho emocional",
            }
        },
        {
            "name": "cta",
            "weight": 0.2,
            "levels": {
                10: "CTA urgente e especifico - acao clara com motivo para agir AGORA",
                8: "CTA claro - acao definida, motivo presente",
                6: "CTA generico - 'compre agora' sem diferenciacao",
                4: "CTA vago - intencao presente mas acao indefinida",
                2: "Sem CTA",
            }
        },
        {
            "name": "length_fit",
            "weight": 0.2,
            "levels": {
                10: "Perfeito para formato - cada palavra necessaria, timing ideal",
                8: "Bom ajuste - leve excesso ou falta mas funcional",
                6: "Aceitavel - precisa de edicao para caber no formato",
                4: "Longo demais ou curto demais - requer reescrita significativa",
                2: "Completamente fora do formato",
            }
        },
        {
            "name": "persuasion",
            "weight": 0.3,
            "levels": {
                10: "Persuasao sofisticada - usa dor, prova social, escassez naturalmente",
                8: "Boa persuasao - tecnicas claras, execucao natural",
                6: "Persuasao basica - tenta convencer mas falta sofisticacao",
                4: "Fraca - lista features sem conectar a dores",
                2: "Anti-persuasivo - linguagem que afasta o publico",
            }
        }
    ],
    "few_shot_examples": [
        {
            "input": "Voce sabia que 73% dos brasileiros dormem mal? O SONO MAX resolve isso em 7 dias. Fale com sono ruim? Pare de sofrer. Use o cupom DORMIR30 e durma como nunca. Valido so hoje.",
            "expected_score": {
                "hook": 8,
                "cta": 9,
                "length_fit": 8,
                "persuasion": 7
            },
            "expected_total": 8,
            "expected_approved": True,
            "reasoning": "Hook com estatistica gera credibilidade. CTA urgente com cupom e prazo. Tamanho adequado. Persuasao boa mas poderia explorar mais a dor."
        },
        {
            "input": "Nosso produto e muito bom. Compre agora. Temos entrega rapida.",
            "expected_score": {
                "hook": 2,
                "cta": 4,
                "length_fit": 4,
                "persuasion": 2
            },
            "expected_total": 3,
            "expected_approved": False,
            "reasoning": "Sem hook, sem especificidade, sem urgencia. CTA generico. Curto demais sem conteudo. Zero persuasao."
        }
    ]
}
```

### Anti-Patterns to Avoid

- **Hardcoded thresholds in code:** Every numeric threshold must come from NexusConfig. Even "obvious" values like max score 10 should be in config for future flexibility.
- **Rubrics as inline strings:** Rubrics must be structured data (dicts or YAML), not f-string templates. Structured rubrics are testable, versionable, and parseable.
- **Monolithic models.py:** Keep models small and focused. AgentScore is for LLM output. CreativeBundle is for pipeline state. NexusConfig is for settings. Do not merge them.
- **Skipping .env.example:** Every NEXUS_ variable must be documented in .env.example with default values and descriptions. This is the user contract.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Env var loading + type coercion | Custom os.environ parser | pydantic-settings BaseSettings | Handles type coercion, defaults, validation errors, nested models. Edge cases: missing vars, wrong types, encoding. |
| Field validation (ge, le, min_length) | Custom if/raise blocks | Pydantic Field constraints | Declarative, generates JSON schema, consistent error messages. |
| JSON schema for LLM | Manual JSON schema dict | Pydantic model_json_schema() | Auto-generated from model, always in sync with code. |
| .env file parsing | Custom file reader | python-dotenv (via pydantic-settings) | Handles comments, quotes, multiline, encoding edge cases. |

**Key insight:** Phase 1 is 100% pure Python with zero API calls. Every model, config, and rubric is testable with standard pytest -- no mocking needed.

## Common Pitfalls

### Pitfall 1: Rubrics Too Vague for LLM Anchoring
**What goes wrong:** Rubric says "good copy quality" without numeric anchors. LLM scores inconsistently.
**Why it happens:** Natural language descriptions without examples leave interpretation to the model.
**How to avoid:** Every rubric level has a numeric score AND a concrete description. Include 2+ few-shot examples with expected scores and reasoning.
**Warning signs:** Same input gets different scores across test runs.

### Pitfall 2: Config Not Actually Loaded from .env
**What goes wrong:** Developer hardcodes defaults that shadow .env values. Changing .env has no effect.
**Why it happens:** Pydantic-settings defaults override missing env vars. If `min_copy_score: int = 7` and .env has no `NEXUS_MIN_COPY_SCORE`, the default wins -- this is correct. But if code uses `MIN_COPY_SCORE = 7` as a module-level constant instead of reading from config, .env is ignored.
**How to avoid:** Single source of truth: `config = NexusConfig()`. All code reads from `config.min_copy_score`, never from module constants.
**Warning signs:** Grep for hardcoded numbers (7, 6, 8, 3) outside of config.py default declarations.

### Pitfall 3: Missing Validation for Invalid Data
**What goes wrong:** Model accepts score=15 or feedback="" because constraints not defined.
**Why it happens:** Rushed model definition without Field constraints.
**How to avoid:** Every field has explicit constraints: `score: int = Field(ge=1, le=10)`, `feedback: str = Field(min_length=10)`. Test with invalid data to confirm rejection.
**Warning signs:** No tests for invalid input in test_models.py.

### Pitfall 4: Pydantic v1 Syntax in v2 Codebase
**What goes wrong:** Using `@validator` (v1) instead of `@field_validator` (v2). Using `class Config:` instead of `model_config = ConfigDict(...)`.
**Why it happens:** Training data and Stack Overflow answers still show v1 patterns.
**How to avoid:** Use v2 patterns exclusively: `@field_validator`, `@model_validator`, `model_config = ConfigDict(...)`, `model_json_schema()`.
**Warning signs:** DeprecationWarning from Pydantic at runtime.

## Code Examples

### Model Validation Test Pattern

```python
# tests/test_models.py
import pytest
from pydantic import ValidationError
from nexus.models import AgentScore

def test_valid_score():
    score = AgentScore(
        dimension="copy",
        score=8,
        approved=True,
        feedback="Hook forte com urgencia. CTA claro e direto.",
        strengths=["Hook urgente"],
        issues=[]
    )
    assert score.score == 8
    assert score.approved is True

def test_score_below_minimum():
    with pytest.raises(ValidationError) as exc_info:
        AgentScore(dimension="copy", score=0, approved=False, feedback="Too low score", strengths=[], issues=[])
    assert "greater than or equal to 1" in str(exc_info.value)

def test_score_above_maximum():
    with pytest.raises(ValidationError) as exc_info:
        AgentScore(dimension="copy", score=11, approved=True, feedback="Too high score value given", strengths=[], issues=[])
    assert "less than or equal to 10" in str(exc_info.value)

def test_feedback_too_short():
    with pytest.raises(ValidationError) as exc_info:
        AgentScore(dimension="copy", score=5, approved=False, feedback="short", strengths=[], issues=[])
    assert "min_length" in str(exc_info.value).lower() or "at least" in str(exc_info.value).lower()
```

### Config Loading Test Pattern

```python
# tests/test_config.py
import os
import pytest
from nexus.config import NexusConfig

def test_config_loads_from_env(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "NEXUS_ANTHROPIC_API_KEY=test-key-123\n"
        "NEXUS_MIN_COPY_SCORE=9\n"
        "NEXUS_MAX_REVIEW_ATTEMPTS=5\n"
    )
    monkeypatch.chdir(tmp_path)
    config = NexusConfig(_env_file=str(env_file))
    assert config.anthropic_api_key == "test-key-123"
    assert config.min_copy_score == 9
    assert config.max_review_attempts == 5

def test_config_uses_defaults_when_env_missing(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("NEXUS_ANTHROPIC_API_KEY=test-key\n")
    config = NexusConfig(_env_file=str(env_file))
    assert config.min_copy_score == 7  # default
    assert config.max_review_attempts == 3  # default

def test_config_rejects_missing_required_key(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("")  # No API key
    with pytest.raises(Exception):  # ValidationError
        NexusConfig(_env_file=str(env_file))

def test_config_env_override(monkeypatch, tmp_path):
    """Env var takes priority over .env file."""
    env_file = tmp_path / ".env"
    env_file.write_text("NEXUS_ANTHROPIC_API_KEY=from-file\nNEXUS_MIN_COPY_SCORE=5\n")
    monkeypatch.setenv("NEXUS_MIN_COPY_SCORE", "9")
    config = NexusConfig(_env_file=str(env_file))
    assert config.min_copy_score == 9  # env var wins
```

### Rubric Structure Test Pattern

```python
# tests/test_rubrics.py
from nexus.rubrics.copy_rubric import COPY_RUBRIC
from nexus.rubrics.tech_rubric import TECH_RUBRIC
from nexus.rubrics.compliance_rubric import COMPLIANCE_RUBRIC
from nexus.rubrics.performance_rubric import PERFORMANCE_RUBRIC

ALL_RUBRICS = [COPY_RUBRIC, TECH_RUBRIC, COMPLIANCE_RUBRIC, PERFORMANCE_RUBRIC]

def test_all_rubrics_have_required_fields():
    for rubric in ALL_RUBRICS:
        assert "dimension" in rubric, f"Missing dimension in {rubric.get('dimension', 'UNKNOWN')}"
        assert "criteria" in rubric
        assert "few_shot_examples" in rubric
        assert len(rubric["few_shot_examples"]) >= 2, \
            f"Rubric {rubric['dimension']} needs at least 2 few-shot examples"

def test_all_criteria_have_numeric_levels():
    for rubric in ALL_RUBRICS:
        for criterion in rubric["criteria"]:
            assert "name" in criterion
            assert "weight" in criterion
            assert "levels" in criterion
            levels = criterion["levels"]
            assert all(isinstance(k, int) for k in levels.keys()), \
                f"Levels must be numeric in {rubric['dimension']}.{criterion['name']}"
            assert 10 in levels and 2 in levels, \
                f"Must have levels 10 and 2 in {rubric['dimension']}.{criterion['name']}"

def test_criteria_weights_sum_to_one():
    for rubric in ALL_RUBRICS:
        total = sum(c["weight"] for c in rubric["criteria"])
        assert abs(total - 1.0) < 0.01, \
            f"Weights sum to {total} in {rubric['dimension']}, expected 1.0"

def test_few_shot_examples_have_expected_fields():
    for rubric in ALL_RUBRICS:
        for i, example in enumerate(rubric["few_shot_examples"]):
            assert "input" in example, f"Missing input in example {i} of {rubric['dimension']}"
            assert "expected_score" in example
            assert "expected_total" in example
            assert "expected_approved" in example
            assert "reasoning" in example
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `@validator` (Pydantic v1) | `@field_validator` (Pydantic v2) | Pydantic 2.0 (2023) | v1 syntax deprecated, will warn |
| `class Config:` inner class | `model_config = ConfigDict(...)` | Pydantic 2.0 (2023) | Must use ConfigDict for v2 features |
| `instructor.from_anthropic()` | `instructor.from_provider("anthropic/model")` | instructor ~1.8+ (2025) | Unified API, provider-specific methods may still work but from_provider is recommended |
| `schema_extra` in Config | `json_schema_extra` in ConfigDict | Pydantic 2.0 (2023) | Old key ignored silently |
| `pydantic.BaseSettings` | `pydantic_settings.BaseSettings` | Pydantic 2.0 (2023) | Settings moved to separate package |

**Deprecated/outdated:**
- `@validator`: Use `@field_validator` with `mode="before"` or `mode="after"`
- `schema()`: Use `model_json_schema()`
- `dict()`: Use `model_dump()`
- `json()`: Use `model_dump_json()`

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest >= 8.0 |
| Config file | None yet -- Wave 0 creates `pytest.ini` or `pyproject.toml [tool.pytest]` |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ -v --tb=short` |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FND-01 | AgentScore rejects score=0 and score=11 | unit | `pytest tests/test_models.py::test_score_below_minimum -x` | Wave 0 |
| FND-01 | AgentScore rejects empty feedback | unit | `pytest tests/test_models.py::test_feedback_too_short -x` | Wave 0 |
| FND-01 | CreativeBundle validates asset paths exist | unit | `pytest tests/test_models.py::test_creative_bundle_validates_paths -x` | Wave 0 |
| FND-01 | Valid data passes all models | unit | `pytest tests/test_models.py::test_valid_score -x` | Wave 0 |
| FND-02 | Config loads from .env with NEXUS_ prefix | unit | `pytest tests/test_config.py::test_config_loads_from_env -x` | Wave 0 |
| FND-02 | Config uses defaults for missing optional vars | unit | `pytest tests/test_config.py::test_config_uses_defaults_when_env_missing -x` | Wave 0 |
| FND-02 | Config fails on missing required key | unit | `pytest tests/test_config.py::test_config_rejects_missing_required_key -x` | Wave 0 |
| FND-02 | Env var overrides .env file value | unit | `pytest tests/test_config.py::test_config_env_override -x` | Wave 0 |
| FND-03 | All 4 rubrics have required structure | unit | `pytest tests/test_rubrics.py::test_all_rubrics_have_required_fields -x` | Wave 0 |
| FND-03 | All criteria have numeric levels with anchors | unit | `pytest tests/test_rubrics.py::test_all_criteria_have_numeric_levels -x` | Wave 0 |
| FND-03 | Criteria weights sum to 1.0 | unit | `pytest tests/test_rubrics.py::test_criteria_weights_sum_to_one -x` | Wave 0 |
| FND-03 | Each rubric has >= 2 few-shot examples with all fields | unit | `pytest tests/test_rubrics.py::test_few_shot_examples_have_expected_fields -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/ -x -q` (all Phase 1 tests, stop on first failure)
- **Per wave merge:** `pytest tests/ -v --tb=short` (full suite with verbose output)
- **Phase gate:** Full suite green before Phase 2 starts

### Wave 0 Gaps
- [ ] `tests/__init__.py` -- package marker
- [ ] `tests/test_models.py` -- covers FND-01
- [ ] `tests/test_config.py` -- covers FND-02
- [ ] `tests/test_rubrics.py` -- covers FND-03
- [ ] `pyproject.toml` with `[tool.pytest.ini_options]` -- test config
- [ ] `pip install pytest` -- if not already in environment

### Few-Shot Calibration Quality Verification

Few-shot quality cannot be fully automated but can be structurally validated:

1. **Structural tests (automated):** Each rubric has >= 2 examples, each example has all required fields, expected scores are within valid range.
2. **Consistency test (automated):** `expected_approved` aligns with `expected_total` vs config threshold (e.g., if threshold is 7, a score of 8 should be approved=True).
3. **Coverage test (automated):** At least one approved example AND one rejected example per rubric.
4. **Calibration test (manual, Phase 2):** Run examples through actual LLM with instructor and compare returned scores to expected scores. Drift > 1.5 points flags rubric issue.

## Open Questions

1. **CreativeBundle asset path validation**
   - What we know: CreativeBundle should reference script/audio/video paths
   - What's unclear: Should models validate file existence at creation time, or just store paths?
   - Recommendation: Store paths as `str` in Phase 1. Add `@model_validator` that checks file existence only when explicitly requested (via a flag or separate validation step). Phase 1 models should work without filesystem.

2. **Rubric storage format**
   - What we know: Rubrics need structured data with nested criteria and examples
   - What's unclear: Python dicts vs YAML files
   - Recommendation: Start with Python dicts (zero parsing dependency, type-checkable, IDE autocomplete). Migrate to YAML only if non-developers need to edit rubrics.

3. **instructor API stability**
   - What we know: `from_provider()` is the new unified API
   - What's unclear: Is `from_anthropic()` deprecated or just secondary?
   - Recommendation: Use `from_provider("anthropic/...")` in all new code. The models.py in Phase 1 does not call instructor directly, so this only matters in Phase 2.

## Sources

### Primary (HIGH confidence)
- [Pydantic v2 official docs](https://docs.pydantic.dev/latest/) - Models, Fields, validators, ConfigDict
- [pydantic-settings docs](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) - BaseSettings, env_prefix, env_file, SettingsConfigDict
- [instructor official docs](https://python.useinstructor.com/) - from_provider API, Anthropic integration, few-shot via json_schema_extra
- [instructor Anthropic tutorial](https://python.useinstructor.com/integrations/anthropic/) - Mode.TOOLS, async support, streaming caveats
- [instructor few-shot examples](https://python.useinstructor.com/examples/examples/) - ConfigDict json_schema_extra pattern

### Secondary (MEDIUM confidence)
- [PyPI pydantic-settings](https://pypi.org/project/pydantic-settings/) - Version 2.13.1 confirmed
- [PyPI instructor](https://pypi.org/project/instructor/) - Version 1.14.x confirmed
- [PyPI pydantic](https://pypi.org/project/pydantic/) - Version 2.12.5 confirmed

### Tertiary (LOW confidence)
- None. All findings verified with primary sources.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Pydantic v2, pydantic-settings, and instructor are all verified against official docs and PyPI
- Architecture: HIGH - Pure Python data models + config + structured dicts. No novel architecture.
- Pitfalls: HIGH - LLM scoring drift and config shadowing are well-documented patterns
- Few-shot calibration: MEDIUM - Structural validation is straightforward; quality calibration requires Phase 2 integration testing

**Research date:** 2026-03-26
**Valid until:** 2026-04-26 (stack is stable, 30-day window appropriate)
