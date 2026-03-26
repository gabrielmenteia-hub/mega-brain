---
phase: 1
slug: foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-26
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest >= 8.0 |
| **Config file** | `pyproject.toml [tool.pytest.ini_options]` — Wave 0 creates |
| **Quick run command** | `pytest tests/ -x -q` |
| **Full suite command** | `pytest tests/ -v --tb=short` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -x -q`
- **After every plan wave:** Run `pytest tests/ -v --tb=short`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** ~5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| FND-01-a | 01-01 | 1 | FND-01 | unit | `pytest tests/test_models.py::test_score_below_minimum -x` | ❌ W0 | ⬜ pending |
| FND-01-b | 01-01 | 1 | FND-01 | unit | `pytest tests/test_models.py::test_feedback_too_short -x` | ❌ W0 | ⬜ pending |
| FND-01-c | 01-01 | 1 | FND-01 | unit | `pytest tests/test_models.py::test_creative_bundle_validates_paths -x` | ❌ W0 | ⬜ pending |
| FND-01-d | 01-01 | 1 | FND-01 | unit | `pytest tests/test_models.py::test_valid_score -x` | ❌ W0 | ⬜ pending |
| FND-02-a | 01-01 | 1 | FND-02 | unit | `pytest tests/test_config.py::test_config_loads_from_env -x` | ❌ W0 | ⬜ pending |
| FND-02-b | 01-01 | 1 | FND-02 | unit | `pytest tests/test_config.py::test_config_uses_defaults_when_env_missing -x` | ❌ W0 | ⬜ pending |
| FND-02-c | 01-01 | 1 | FND-02 | unit | `pytest tests/test_config.py::test_config_rejects_missing_required_key -x` | ❌ W0 | ⬜ pending |
| FND-02-d | 01-01 | 1 | FND-02 | unit | `pytest tests/test_config.py::test_config_env_override -x` | ❌ W0 | ⬜ pending |
| FND-03-a | 01-02 | 2 | FND-03 | unit | `pytest tests/test_rubrics.py::test_all_rubrics_have_required_fields -x` | ❌ W0 | ⬜ pending |
| FND-03-b | 01-02 | 2 | FND-03 | unit | `pytest tests/test_rubrics.py::test_all_criteria_have_numeric_levels -x` | ❌ W0 | ⬜ pending |
| FND-03-c | 01-02 | 2 | FND-03 | unit | `pytest tests/test_rubrics.py::test_criteria_weights_sum_to_one -x` | ❌ W0 | ⬜ pending |
| FND-03-d | 01-02 | 2 | FND-03 | unit | `pytest tests/test_rubrics.py::test_few_shot_examples_have_expected_fields -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/__init__.py` — package marker
- [ ] `tests/test_models.py` — stubs for FND-01
- [ ] `tests/test_config.py` — stubs for FND-02
- [ ] `tests/test_rubrics.py` — stubs for FND-03
- [ ] `pyproject.toml` with `[tool.pytest.ini_options]` — test config

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Few-shot examples calibrate LLM scoring correctly | FND-03 | Requires live LLM call to verify anchor quality | In Phase 2, submit known-good and known-bad scripts to review agents; verify scores match expected range |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
