---
phase: 8
slug: foundation-verification
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-15
---

# Phase 8 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + pytest-asyncio (asyncio_mode=auto) |
| **Config file** | `mis/pytest.ini` |
| **Quick run command** | `cd /c/Users/Gabriel/MEGABRAIN && python -m pytest mis/tests/test_base_scraper.py mis/tests/test_health_monitor.py -v --timeout=10` |
| **Full suite command** | `cd /c/Users/Gabriel/MEGABRAIN && python -m pytest mis/tests/ -v --timeout=30` |
| **Estimated runtime** | ~15 seconds (quick), ~45 seconds (full) |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest mis/tests/test_base_scraper.py mis/tests/test_health_monitor.py -v --timeout=10`
- **After every plan wave:** Run `python -m pytest mis/tests/ -v --timeout=30`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 8-01-01 | 01 | 0 | FOUND-02 | unit | `pytest mis/tests/test_base_scraper.py -v --timeout=10` | ❌ W0 | ⬜ pending |
| 8-01-02 | 01 | 0 | FOUND-04 | unit | `pytest mis/tests/test_health_monitor.py -v --timeout=10` | ❌ W0 | ⬜ pending |
| 8-01-03 | 01 | 1 | FOUND-02 | unit | `pytest mis/tests/test_base_scraper.py -v --timeout=10` | ✅ | ⬜ pending |
| 8-01-04 | 01 | 1 | FOUND-04 | unit | `pytest mis/tests/test_health_monitor.py -v --timeout=10` | ✅ | ⬜ pending |
| 8-01-05 | 01 | 2 | FOUND-01,FOUND-02,FOUND-03,FOUND-04 | manual | `pytest mis/tests/ -v --timeout=30` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `mis/tests/test_base_scraper.py` — add `test_proxy_rotation_selects_from_list` and `test_proxy_rotation_no_proxy_returns_none` (covers FOUND-02 proxy rotation)
- [ ] `mis/tests/test_health_monitor.py` — add `test_schema_integrity_check_ok` and `test_schema_integrity_check_missing_table` (covers FOUND-04 schema integrity canary)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| VERIFICATION.md for Phase 1 reflects real code state | FOUND-01–04 | Document correctness requires human judgment | Review `.planning/phases/01-foundation/VERIFICATION.md` — verify claims match actual code. All 4 requirements should be marked SATISFIED with specific evidence. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** signed off 2026-03-16
