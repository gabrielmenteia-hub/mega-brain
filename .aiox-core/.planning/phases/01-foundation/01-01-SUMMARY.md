---
phase: 01-foundation
plan: 01
subsystem: data-models-and-config
tags: [pydantic-v2, pydantic-settings, models, config, tdd]
dependency_graph:
  requires: []
  provides: [nexus.models.AgentScore, nexus.models.CreativeBundle, nexus.config.NexusConfig]
  affects: [Phase 2 agents (import AgentScore for instructor), Phase 3 pipeline (import CreativeBundle), all phases (import NexusConfig)]
tech_stack:
  added: [pydantic>=2.10.0, pydantic-settings>=2.7.0, python-dotenv>=1.0.0, pytest>=8.0.0]
  patterns: [Pydantic v2 BaseModel with Field constraints (ge/le/min_length), BaseSettings with SettingsConfigDict and env_prefix, TDD RED-GREEN cycle]
key_files:
  created:
    - nexus/models.py
    - nexus/config.py
    - nexus/__init__.py
    - tests/test_models.py
    - tests/test_config.py
    - tests/__init__.py
    - pyproject.toml
    - .env.example
  modified: []
decisions:
  - "Pydantic v2 exclusively — ConfigDict, SettingsConfigDict (zero v1 syntax)"
  - "AgentScore carries json_schema_extra with 2 few-shot examples for Phase 2 instructor calibration"
  - "CreativeBundle stores asset paths as str|None without filesystem validation (deferred to Phase 2)"
  - "NexusConfig requires NEXUS_ANTHROPIC_API_KEY at startup — fail-fast over silent default"
metrics:
  duration_minutes: 2
  completed_date: "2026-03-26"
  tasks_completed: 2
  files_created: 8
  tests_added: 10
  tests_passing: 10
requirements_covered: [FND-01, FND-02]
---

# Phase 1 Plan 01: Typed Models and Externalized Config Summary

**One-liner:** Pydantic v2 AgentScore + CreativeBundle models with Field constraints and NexusConfig BaseSettings loading from .env with NEXUS_ prefix — 10 tests, all passing in under 1 second.

## What Was Built

### nexus/models.py

Two Pydantic v2 models forming the data layer for the entire pipeline:

**AgentScore** — structured LLM output boundary:
- `dimension: str` — review dimension (copy|tech|compliance|performance)
- `score: int = Field(ge=1, le=10)` — quality score with hard bounds
- `approved: bool` — meets minimum threshold
- `feedback: str = Field(min_length=10)` — actionable feedback
- `strengths/issues: list[str]` — with `default_factory=list`
- `json_schema_extra` with 2 calibrated few-shot examples (score 8 approved, score 4 rejected) for Phase 2 instructor integration

**CreativeBundle** — pipeline state tracker:
- `id: str` — UUID4 auto-generated
- `niche: str` — required, min_length=1
- `script_text: str` — required, min_length=1
- `audio_path/video_path/image_path: str | None` — optional asset paths
- `status: str` — pipeline status (pending|reviewing|approved|rejected|quarantined)
- `attempt: int = Field(default=1, ge=1)` — regeneration counter
- `reviews: list[AgentScore]` — agent review history

### nexus/config.py

**NexusConfig** (BaseSettings) with `env_prefix="NEXUS_"`:
- `anthropic_api_key: str` — required, no default (fail-fast)
- Threshold defaults: min_copy_score=7, min_tech_score=6, min_compliance_score=8, min_performance_score=6
- Pipeline defaults: max_review_attempts=3, review_model="claude-sonnet-4-20250514"
- Path default: output_dir="output"
- Precedence: system env > .env file > default

### Test Suite

10 tests, all passing in 0.71s:

| Test | File | Validates |
|------|------|-----------|
| test_valid_score | test_models.py | AgentScore accepts valid data |
| test_score_below_minimum | test_models.py | score=0 raises ValidationError with "greater than or equal to 1" |
| test_score_above_maximum | test_models.py | score=11 raises ValidationError with "less than or equal to 10" |
| test_feedback_too_short | test_models.py | feedback="short" raises ValidationError (min_length) |
| test_valid_creative_bundle | test_models.py | CreativeBundle with niche+script creates valid instance |
| test_creative_bundle_missing_required | test_models.py | Missing niche raises ValidationError |
| test_config_loads_from_env | test_config.py | .env values loaded with NEXUS_ prefix |
| test_config_uses_defaults_when_env_missing | test_config.py | Optional vars fall back to defaults |
| test_config_rejects_missing_required_key | test_config.py | Missing API key raises on startup |
| test_config_env_override | test_config.py | System env var overrides .env value |

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| Task 1 — RED | 1f71993 | test(01-01): add failing RED tests for AgentScore, CreativeBundle, and NexusConfig |
| Task 2 — GREEN | cee05de | feat(01-01): implement AgentScore, CreativeBundle (models.py) and NexusConfig (config.py) |

## Decisions Made

1. **Pydantic v2 syntax exclusively:** ConfigDict, SettingsConfigDict, Field with named args — zero v1 patterns to avoid deprecation warnings.
2. **Few-shot examples in AgentScore model_config:** `json_schema_extra={"examples": [...]}` with calibrated approved/rejected examples, ready for Phase 2 instructor integration without modification.
3. **CreativeBundle paths stored as str|None:** No filesystem validation at creation time — models work without filesystem access, keeping Phase 1 pure Python with zero API calls.
4. **NexusConfig fail-fast on missing API key:** `anthropic_api_key: str` with no default forces explicit configuration before the pipeline can start.

## Deviations from Plan

None — plan executed exactly as written.

## Success Criteria Check

- [x] AgentScore rejects score=0, score=11 with ValidationError
- [x] AgentScore rejects feedback shorter than 10 chars with ValidationError
- [x] CreativeBundle accepts valid data (niche + script_text)
- [x] CreativeBundle rejects missing required field (niche)
- [x] NexusConfig loads from .env with NEXUS_ prefix
- [x] NexusConfig uses defaults for optional missing vars
- [x] NexusConfig fails with clear error when API key absent
- [x] System env var overrides .env value
- [x] All 10 tests pass in under 5 seconds (0.71s actual)
- [x] .env.example documents all 8 NEXUS_ variables with comments

## Self-Check: PASSED
