---
phase: 18
slug: nyquist-signoff
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-17
---

# Phase 18 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | none — documentation-only phase |
| **Config file** | none |
| **Quick run command** | `grep -r "nyquist_compliant: false" .planning/phases/ --include="*.md"` |
| **Full suite command** | `grep -r "nyquist_compliant: false" .planning/phases/ --include="*.md"` |
| **Estimated runtime** | ~1 second |

---

## Sampling Rate

- **After every task commit:** Run `grep -r "nyquist_compliant: false" .planning/phases/ --include="*.md"`
- **After every plan wave:** Same grep — should return 0 results after task 3
- **Before `/gsd:verify-work`:** Full grep must return 0 results
- **Max feedback latency:** 1 second

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 18-01-01 | 01 | 1 | tech-debt-cleanup | manual-check | `grep "nyquist_compliant" .planning/phases/13-infrastructure-tech-debt/13-VALIDATION.md` | ✅ | ⬜ pending |
| 18-01-02 | 01 | 1 | tech-debt-cleanup | manual-check | `grep "nyquist_compliant" .planning/phases/15-international-api-based/15-VALIDATION.md` | ✅ | ⬜ pending |
| 18-01-03 | 01 | 1 | tech-debt-cleanup | manual-check | `grep -r "nyquist_compliant: false" .planning/phases/ --include="*.md"` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. No new test files needed — this phase only edits 3 VALIDATION.md files.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| VALIDATION.md signed off correctly | tech-debt-cleanup | File content inspection | Open each VALIDATION.md and verify frontmatter has `nyquist_compliant: true`, `wave_0_complete: true`, and `**Approval:** approved YYYY-MM-DD` |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (N/A — no new files)
- [x] No watch-mode flags
- [x] Feedback latency < 1s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
