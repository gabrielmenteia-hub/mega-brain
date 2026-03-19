---
phase: 22
slug: spy-wiring
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-19
---

# Phase 22 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | `mis/tests/conftest.py` (existing) |
| **Quick run command** | `python -m pytest mis/tests/ -x -q --tb=short 2>&1 \| tail -20` |
| **Full suite command** | `python -m pytest mis/tests/ -q --tb=short 2>&1 \| tail -30` |
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
| 22-01-01 | 01 | 1 | SPY-V3-01 | unit | `python -m pytest mis/tests/test_spy_wiring.py::test_spy_v3_top_n -x -q` | ❌ W0 | ⬜ pending |
| 22-01-02 | 01 | 1 | SPY-V3-01 | unit | `python -m pytest mis/tests/test_spy_wiring.py::test_top5_per_platform_grouping -x -q` | ❌ W0 | ⬜ pending |
| 22-01-03 | 01 | 1 | SPY-V3-01 | unit | `python -m pytest mis/tests/test_spy_wiring.py::test_spy_triggers_after_scan -x -q` | ❌ W0 | ⬜ pending |
| 22-01-04 | 01 | 1 | SPY-V3-01 | unit | `python -m pytest mis/tests/test_spy_wiring.py::test_session_status_spying -x -q` | ❌ W0 | ⬜ pending |
| 22-01-05 | 01 | 1 | SPY-V3-01 | unit | `python -m pytest mis/tests/test_spy_wiring.py::test_respy_on_results_page -x -q` | ❌ W0 | ⬜ pending |
| 22-02-01 | 02 | 2 | SPY-V3-02 | unit | `python -m pytest mis/tests/test_spy_wiring.py::test_dossier_column_states -x -q` | ❌ W0 | ⬜ pending |
| 22-02-02 | 02 | 2 | SPY-V3-02 | unit | `python -m pytest mis/tests/web/test_web_spy_wiring.py::test_dossier_link_with_from_search -x -q` | ❌ W0 | ⬜ pending |
| 22-02-03 | 02 | 2 | SPY-V3-02 | unit | `python -m pytest mis/tests/web/test_web_spy_wiring.py::test_spy_banner_shown_when_spying -x -q` | ❌ W0 | ⬜ pending |
| 22-03-01 | 03 | 2 | SPY-V3-03 | unit | `python -m pytest mis/tests/web/test_web_dossier.py::test_dossier_oferta_tab -x -q` | ❌ W0 | ⬜ pending |
| 22-03-02 | 03 | 2 | SPY-V3-03 | unit | `python -m pytest mis/tests/web/test_web_dossier.py::test_dossier_copy_gatilhos -x -q` | ❌ W0 | ⬜ pending |
| 22-03-03 | 03 | 2 | SPY-V3-03 | unit | `python -m pytest mis/tests/web/test_web_dossier.py::test_from_search_back_link -x -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `mis/tests/test_spy_wiring.py` — stubs for SPY-V3-01 (spy trigger, top-5 grouping, status transitions)
- [ ] `mis/tests/web/test_web_spy_wiring.py` — stubs for SPY-V3-02 (UI column states, banner, from_search param)
- [ ] `mis/tests/web/test_web_dossier.py` — extend existing file with stubs for SPY-V3-03 (Oferta tab, Gatilhos, back-link)

*Existing infrastructure (conftest.py, app_client fixture, tmp_path DB) covers all phase requirements.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Bloco `<details>` expande e mostra texto completo da sales page | SPY-V3-03 | Browser DOM interaction | Abrir /dossier/{id} tab Oferta → clicar "Ver página de venda completa" → verificar texto visível |
| Banner "Espionando..." aparece e some ao recarregar após spy_done | SPY-V3-01 | Timing-dependent async state | POST /search/run → aguardar redirect → verificar banner na results page → aguardar spy_done → recarregar → verificar banner sumiu |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
