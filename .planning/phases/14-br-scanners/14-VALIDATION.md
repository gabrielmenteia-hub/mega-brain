---
phase: 14
slug: br-scanners
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-16
---

# Phase 14 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | mis/tests/conftest.py |
| **Quick run command** | `python -m pytest mis/tests/test_eduzz_scanner.py mis/tests/test_monetizze_scanner.py mis/tests/test_perfectpay_scanner.py mis/tests/test_braip_scanner.py mis/tests/test_migration_007.py -x -q` |
| **Full suite command** | `python -m pytest mis/tests/ -x -q` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run quick run command
- **After every plan wave:** Run full suite command
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 14-01-01 | 01 | 0 | SCAN-BR-01, SCAN-BR-02 | unit stubs | `python -m pytest mis/tests/test_eduzz_scanner.py mis/tests/test_monetizze_scanner.py -x -q` | ❌ W0 | ⬜ pending |
| 14-01-02 | 01 | 1 | SCAN-BR-01, SCAN-BR-02 | migration | `python -m pytest mis/tests/test_migration_007.py -x -q` | ❌ W0 | ⬜ pending |
| 14-01-03 | 01 | 1 | SCAN-BR-01 | unit | `python -m pytest mis/tests/test_eduzz_scanner.py -x -q` | ❌ W0 | ⬜ pending |
| 14-01-04 | 01 | 1 | SCAN-BR-02 | unit | `python -m pytest mis/tests/test_monetizze_scanner.py -x -q` | ❌ W0 | ⬜ pending |
| 14-02-01 | 02 | 0 | SCAN-BR-03, SCAN-BR-04 | unit stubs | `python -m pytest mis/tests/test_perfectpay_scanner.py mis/tests/test_braip_scanner.py -x -q` | ❌ W0 | ⬜ pending |
| 14-02-02 | 02 | 1 | SCAN-BR-04 | unit | `python -m pytest mis/tests/test_braip_scanner.py -x -q` | ❌ W0 | ⬜ pending |
| 14-02-03 | 02 | 1 | SCAN-BR-03 | unit | `python -m pytest mis/tests/test_perfectpay_scanner.py -x -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 — Note on TDD Inline Pattern

This project uses TDD inline: each task in the plans creates test stubs at the **start of the task** before writing production code (RED → GREEN → REFACTOR within the same task). There is no separate Wave 0 plan — the stub creation is the first step inside each `tdd="true"` task.

This satisfies the Nyquist Rule: every production code change is preceded by a failing test stub. The pattern is equivalent to Wave 0 in practice.

### Wave 0 Checklist (resolved inline)

- [x] `mis/tests/test_eduzz_scanner.py` — 6 test stubs created at start of Task 2 (14-01)
- [x] `mis/tests/test_monetizze_scanner.py` — 6 test stubs created at start of Task 2 (14-01)
- [x] `mis/tests/test_perfectpay_scanner.py` — 6 test stubs created at start of Task 1 (14-02)
- [x] `mis/tests/test_braip_scanner.py` — 6 test stubs created at start of Task 2 (14-02)
- [x] `mis/tests/test_migration_007.py` — 5 migration test stubs created at start of Task 1 (14-01)
- [x] `mis/tests/fixtures/eduzz/` — fixture directory (gitkeep, scanner is fallback-only)
- [x] `mis/tests/fixtures/monetizze/` — fixture directory (gitkeep, scanner is fallback-only)
- [x] `mis/tests/fixtures/perfectpay/` — fixture directory (gitkeep, scanner is fallback-only)
- [x] `mis/tests/fixtures/braip/` — fixture directory (HTML from marketplace.braip.com — captured live in Task 2)

*Existing infrastructure (conftest.py, respx, tmp_path DB) covers all shared fixture needs.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `python -m mis scan --platform eduzz` returns ranked products | SCAN-BR-01 | Live network + DB write | Run command, verify output shows products list |
| `python -m mis scan --platform monetizze` returns ranked products | SCAN-BR-02 | Live network + DB write | Run command, verify output shows products list |
| Dashboard `/ranking` shows BR platforms in filter | SCAN-BR-03, SCAN-BR-04 | Browser UI verification | Start dashboard, open /ranking, verify Eduzz/Monetizze/PerfectPay/Braip in platform filter |
| is_stale resets on successful scan after unavailability | SCAN-BR-01 to 04 | Requires real scheduler cycle | Set is_stale=True manually, run scan, verify is_stale=False in DB |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies (TDD inline — stubs created at task start)
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references (resolved inline per TDD pattern)
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved
