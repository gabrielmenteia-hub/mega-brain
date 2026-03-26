---
phase: 19
slug: code-quality-cleanup
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-17
---

# Phase 19 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (existing) |
| **Config file** | mis/pytest.ini or pyproject.toml |
| **Quick run command** | `cd mis && python -m pytest tests/web/test_web_ranking.py tests/test_unified_ranking.py -x -q` |
| **Full suite command** | `cd mis && python -m pytest -x -q` |
| **Estimated runtime** | ~5 seconds (quick), ~260 seconds (full) |

---

## Sampling Rate

- **After every task commit:** Run quick command
- **After every plan wave:** Run full suite
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds (quick)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 19-01-01 | 01 | 1 | tech-debt-null-guard | grep | `grep -n "if platform_slug is None" mis/scanner.py` | ✅ | ⬜ pending |
| 19-01-02 | 01 | 1 | tech-debt-badges | grep | `grep -n "badge" mis/web/templates/unified_table.html` | ✅ | ⬜ pending |
| 19-01-03 | 01 | 1 | tech-debt-requirements | grep | `grep "tabela platforms" .planning/REQUIREMENTS.md` | ✅ | ⬜ pending |
| 19-01-04 | 01 | 1 | tech-debt-fallback-docs | grep | `grep -n "fallback" mis/scanner.py \| head -5` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. No new test files needed — all changes are in existing production files.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Platform badge visual appearance | tech-debt-badges | Browser rendering | Load /ranking/unified in browser, verify platform badges have background color and rounded style |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (N/A)
- [x] No watch-mode flags
- [x] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
