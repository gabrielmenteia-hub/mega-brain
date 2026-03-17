---
phase: 17
slug: unified-cross-platform-ranking
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-17
---

# Phase 17 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + pytest-asyncio (existente) |
| **Config file** | `mis/tests/conftest.py` — fixture `db_path(tmp_path)` |
| **Quick run command** | `pytest mis/tests/test_unified_ranking.py -x -q` |
| **Full suite command** | `pytest mis/tests/ -x -q` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest mis/tests/test_unified_ranking.py -x -q`
- **After every plan wave:** Run `pytest mis/tests/ -x -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 17-01-01 | 01 | 0 | DASH-V2-01 | unit | `pytest mis/tests/test_unified_ranking.py -x -q` | ❌ W0 | ⬜ pending |
| 17-01-02 | 01 | 1 | DASH-V2-01 | unit | `pytest mis/tests/test_unified_ranking.py::test_unified_score_order -x` | ❌ W0 | ⬜ pending |
| 17-01-03 | 01 | 1 | DASH-V2-01 | unit | `pytest mis/tests/test_unified_ranking.py::test_percentile_positional -x` | ❌ W0 | ⬜ pending |
| 17-01-04 | 01 | 1 | DASH-V2-01 | unit | `pytest mis/tests/test_unified_ranking.py::test_percentile_gravity -x` | ❌ W0 | ⬜ pending |
| 17-01-05 | 01 | 1 | DASH-V2-01 | unit | `pytest mis/tests/test_unified_ranking.py::test_null_rank_excluded -x` | ❌ W0 | ⬜ pending |
| 17-01-06 | 01 | 1 | DASH-V2-01 | unit | `pytest mis/tests/test_unified_ranking.py::test_min_products_threshold -x` | ❌ W0 | ⬜ pending |
| 17-01-07 | 01 | 1 | DASH-V2-01 | unit | `pytest mis/tests/test_unified_ranking.py::test_single_platform_warning -x` | ❌ W0 | ⬜ pending |
| 17-01-08 | 01 | 1 | DASH-V2-01 | unit | `pytest mis/tests/test_unified_ranking.py::test_pagination -x` | ❌ W0 | ⬜ pending |
| 17-01-09 | 01 | 1 | DASH-V2-02 | unit | `pytest mis/tests/test_unified_ranking.py::test_niche_filter -x` | ❌ W0 | ⬜ pending |
| 17-01-10 | 01 | 1 | DASH-V2-02 | unit | `pytest mis/tests/test_unified_ranking.py::test_multi_platform_filter -x` | ❌ W0 | ⬜ pending |
| 17-01-11 | 01 | 1 | DASH-V2-02 | unit | `pytest mis/tests/test_unified_ranking.py::test_title_normalization -x` | ❌ W0 | ⬜ pending |
| 17-01-12 | 01 | 1 | DASH-V2-03 | unit | `pytest mis/tests/test_unified_ranking.py::test_result_fields -x` | ❌ W0 | ⬜ pending |
| 17-01-13 | 01 | 1 | DASH-V2-03 | unit | `pytest mis/tests/test_unified_ranking.py::test_stale_included -x` | ❌ W0 | ⬜ pending |
| 17-01-14 | 01 | 2 | DASH-V2-01 | manual | `python -m mis dashboard` → acessa /ranking/unified | N/A | ⬜ pending |
| 17-01-15 | 01 | 2 | DASH-V2-03 | manual | Verificar tabs "Por Plataforma" | "Unificado" visíveis | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `mis/tests/test_unified_ranking.py` — 12 testes stub (RED) cobrindo todos os 3 requirements

*Nenhuma instalação de framework necessária — pytest + conftest.py já existem.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Tabs "Por Plataforma" e "Unificado" visíveis e clicáveis | DASH-V2-01 | Requer browser/render visual | `python -m mis dashboard` → navegar /ranking → verificar tabs |
| Badge ⚠️ aparece em produtos stale na unified view | DASH-V2-03 | Requer dados reais stale no DB | Marcar produto como stale via SQL, verificar visual no dashboard |
| Toggle multi-platform filtra corretamente na UI | DASH-V2-02 | Requer interação HTMX no browser | Ativar toggle → verificar que apenas produtos com título duplicado aparecem |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
