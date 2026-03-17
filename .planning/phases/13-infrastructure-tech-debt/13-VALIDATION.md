---
phase: 13
slug: infrastructure-tech-debt
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-16
---

# Phase 13 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | pytest.ini or pyproject.toml (existing) |
| **Quick run command** | `python -m pytest mis/tests/ -x -q` |
| **Full suite command** | `python -m pytest mis/tests/ -v` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest mis/tests/ -x -q`
- **After every plan wave:** Run `python -m pytest mis/tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 13-01-01 | 01 | 1 | INFRA-01 | migration | `python -m pytest mis/tests/test_migrations.py -k migration_006 -v` | ❌ W0 | ✅ green |
| 13-01-02 | 01 | 1 | INFRA-02 | unit | `python -m pytest mis/tests/test_platform_ids.py -v` | ❌ W0 | ✅ green |
| 13-01-03 | 01 | 2 | INFRA-03 | schema | `python -m pytest mis/tests/test_rank_type.py -v` | ❌ W0 | ✅ green |
| 13-01-04 | 01 | 3 | DEBT-01 | lint/grep | `grep -r "nyquist_compliant: false" .planning/phases/` | manual | ✅ green |
| 13-01-05 | 01 | 3 | DEBT-02 | grep | `grep "6 jobs" mis/radar/__init__.py` | manual | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `mis/tests/test_migrations.py` — migration 006 applies cleanly, FK constraint not violated
- [x] `mis/tests/test_platform_ids.py` — platform_ids module exports all expected constants
- [x] `mis/tests/test_rank_type.py` — rank_type field exists in platforms table with valid enum values (criado como test_migration_006.py::test_rank_type_populated)

*Note: DEBT-01 and DEBT-02 use grep/manual verification — no new test files needed.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| nyquist_compliant: false → true in all VALIDATION.md | DEBT-01 | Requires human sign-off review of each file | `grep -r "nyquist_compliant: false" .planning/phases/` returns 0 results |
| Docstring reads "6 jobs" not "5 jobs" | DEBT-02 | Single-line text verification | `grep "6 jobs" mis/radar/__init__.py` at line ~141 |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 15s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** signed off 2026-03-17
