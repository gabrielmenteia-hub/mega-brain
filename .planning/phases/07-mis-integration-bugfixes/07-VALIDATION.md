---
phase: 7
slug: mis-integration-bugfixes
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-15
---

# Phase 7 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | mis/pytest.ini or pyproject.toml |
| **Quick run command** | `cd mis && python -m pytest tests/test_mis_agent.py tests/test_scan_and_spy_job.py -v` |
| **Full suite command** | `cd mis && python -m pytest tests/ -v` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd mis && python -m pytest tests/test_mis_agent.py tests/test_scan_and_spy_job.py -v`
- **After every plan wave:** Run `cd mis && python -m pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 20 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 07-01-01 | 01 | 0 | INT-01, INT-02 | unit | `pytest tests/test_mis_agent.py tests/test_scan_and_spy_job.py -v` | ❌ W0 | ⬜ pending |
| 07-01-02 | 01 | 1 | INT-01 | unit | `pytest tests/test_mis_agent.py::test_incremental_export -v` | ✅ | ⬜ pending |
| 07-01-03 | 01 | 1 | INT-01, INT-02 | unit | `pytest tests/test_mis_agent.py::test_with_data -v` | ✅ | ⬜ pending |
| 07-01-04 | 01 | 1 | INT-01, INT-02 | unit | `pytest tests/test_scan_and_spy_job.py -v` | ❌ W0 | ⬜ pending |
| 07-01-05 | 01 | 1 | INT-01, INT-02 | integration | `pytest tests/ -v` (full suite green) | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `mis/tests/test_scan_and_spy_job.py` — RED stubs for BUG-03: `test_scan_and_spy_saves_products`, `test_scan_and_spy_triggers_spy_pipeline`
- [ ] Update `mis/tests/test_mis_agent.py` seed to use `status='done'` and `generated_at` column

*Existing `test_mis_agent.py` infrastructure covers BUG-01 and BUG-02 after seed correction.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `python -m mis export` exports real dossiers to knowledge/mis/ | INT-02 | Requires live DB with spy pipeline having run | Run scanner + spy manually, then `python -m mis export`, verify files in knowledge/mis/ |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 20s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
