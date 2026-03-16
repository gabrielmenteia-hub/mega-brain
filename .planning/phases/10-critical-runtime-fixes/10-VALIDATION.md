---
phase: 10
slug: critical-runtime-fixes
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-16
---

# Phase 10 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | `mis/tests/` (existing) |
| **Quick run command** | `python -m pytest mis/tests/test_scanner.py mis/tests/test_radar_jobs.py -x -q` |
| **Full suite command** | `python -m pytest mis/tests/ -x -q` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest mis/tests/test_scanner.py mis/tests/test_radar_jobs.py -x -q`
- **After every plan wave:** Run `python -m pytest mis/tests/ -x -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 10-01-W0 | 01 | 0 | SCAN-01,02,03 DASH-01 | unit stub | `python -m pytest mis/tests/test_scanner.py -x -q -k niche_id` | ❌ W0 | ⬜ pending |
| 10-01-01 | 01 | 1 | SCAN-01, SCAN-02, SCAN-03, DASH-01 | unit | `python -m pytest mis/tests/test_scanner.py -x -q -k niche_id` | ✅ after W0 | ⬜ pending |
| 10-01-W0b | 01 | 0 | RADAR-01,02,03,05,06 | unit stub | `python -m pytest mis/tests/test_radar_jobs.py -x -q -k async_job` | ❌ W0 | ⬜ pending |
| 10-01-02 | 01 | 1 | RADAR-01, RADAR-02, RADAR-03, RADAR-05, RADAR-06 | unit | `python -m pytest mis/tests/test_radar_jobs.py -x -q -k async_job` | ✅ after W0 | ⬜ pending |
| 10-01-03 | 01 | 1 | All | integration | `python -m pytest mis/tests/ -x -q` | ✅ existing | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `mis/tests/test_scanner.py` — add `test_niche_id_resolved_correctly` and `test_missing_niche_slug_skipped` stubs (RED)
- [ ] `mis/tests/test_radar_jobs.py` — add `test_async_radar_jobs_no_runtime_error` stub (RED)

*Existing `mis/tests/` infrastructure covers all fixtures and conftest. No new framework installs needed.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Dashboard ranking shows products grouped by niche after scan | DASH-01 | Requires live scan cycle + browser | Run `python -m mis scan`, open dashboard, verify niche filter returns results |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
