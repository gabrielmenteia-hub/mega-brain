---
phase: 9
slug: production-wiring-proxy-fix
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-15
---

# Phase 9 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (project standard) |
| **Config file** | `mis/pytest.ini` |
| **Quick run command** | `pytest mis/tests/test_lifespan.py mis/tests/test_proxy_forwarding.py -x` |
| **Full suite command** | `pytest mis/tests/ -x` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest mis/tests/test_lifespan.py mis/tests/test_proxy_forwarding.py -x`
- **After every plan wave:** Run `pytest mis/tests/ -x`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 9-01-01 | 01 | 0 | SCAN-04 + FOUND-02 | wave0-scaffold | `pytest mis/tests/test_lifespan.py mis/tests/test_proxy_forwarding.py -x` | ❌ W0 | ⬜ pending |
| 9-01-02 | 01 | 1 | FOUND-02 | unit | `pytest mis/tests/test_proxy_forwarding.py -x` | ❌ W0 | ⬜ pending |
| 9-01-03 | 01 | 1 | SCAN-04 | unit+integration | `pytest mis/tests/test_lifespan.py -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `mis/tests/test_proxy_forwarding.py` — stubs for FOUND-02 (TypeError regression + proxy forwarding)
- [ ] `mis/tests/test_lifespan.py` — stubs for SCAN-04 (unit mock + integration real scheduler)

*Existing infrastructure covers everything else — only 2 new test files needed.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `python -m mis dashboard` starts server AND scheduler fires at cron time | SCAN-04 | Requires waiting for cron schedule to trigger | Start server, check structlog output for `scheduler.job.executed` event |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** signed off 2026-03-16
