---
phase: 15
slug: international-api-based
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-17
---

# Phase 15 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + pytest-asyncio |
| **Config file** | `mis/pytest.ini` (asyncio_mode = auto) |
| **Quick run command** | `cd mis && python -m pytest tests/test_product_hunt_scanner.py tests/test_udemy_scanner.py -x` |
| **Full suite command** | `cd mis && python -m pytest tests/ -x` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd mis && python -m pytest tests/test_product_hunt_scanner.py tests/test_udemy_scanner.py -x`
- **After every plan wave:** Run `cd mis && python -m pytest tests/ -x`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** ~10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 15-01-01 | 01 | 0 | SCAN-INTL-01 | unit (respx mock) | `pytest tests/test_product_hunt_scanner.py -x` | ❌ W0 | ⬜ pending |
| 15-01-02 | 01 | 0 | SCAN-INTL-02 | unit (respx mock) | `pytest tests/test_udemy_scanner.py -x` | ❌ W0 | ⬜ pending |
| 15-01-03 | 01 | 1 | SCAN-INTL-01 | unit | `pytest tests/test_product_hunt_scanner.py::test_happy_path -x` | ❌ W0 | ⬜ pending |
| 15-01-04 | 01 | 1 | SCAN-INTL-01 | unit | `pytest tests/test_product_hunt_scanner.py::test_missing_credentials -x` | ❌ W0 | ⬜ pending |
| 15-01-05 | 01 | 1 | SCAN-INTL-01 | unit | `pytest tests/test_product_hunt_scanner.py::test_empty_results -x` | ❌ W0 | ⬜ pending |
| 15-01-06 | 01 | 1 | SCAN-INTL-02 | unit | `pytest tests/test_udemy_scanner.py::test_happy_path -x` | ❌ W0 | ⬜ pending |
| 15-01-07 | 01 | 1 | SCAN-INTL-02 | unit | `pytest tests/test_udemy_scanner.py::test_missing_credentials -x` | ❌ W0 | ⬜ pending |
| 15-01-08 | 01 | 1 | SCAN-INTL-02 | unit | `pytest tests/test_udemy_scanner.py::test_empty_results -x` | ❌ W0 | ⬜ pending |
| 15-01-09 | 01 | 1 | SCAN-INTL-01+02 | unit (sqlite tmp) | `pytest tests/test_product_hunt_scanner.py::test_upsert_no_duplicates -x` | ❌ W0 | ⬜ pending |
| 15-01-10 | 01 | 1 | SCAN-INTL-01+02 | unit (sqlite tmp) | `pytest tests/test_product_hunt_scanner.py::test_is_stale -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `mis/tests/test_product_hunt_scanner.py` — stubs para SCAN-INTL-01 (happy_path, field_types, missing_credentials, empty_results, upsert_no_duplicates, is_stale)
- [ ] `mis/tests/test_udemy_scanner.py` — stubs para SCAN-INTL-02 (mesmo padrão)
- [ ] `mis/tests/fixtures/product_hunt/trending_today.json` — fixture JSON
- [ ] `mis/tests/fixtures/udemy/courses_marketing.json` — fixture JSON
- [ ] `mis/scanners/product_hunt.py` — stub da classe ProductHuntScanner
- [ ] `mis/scanners/udemy.py` — stub da classe UdemyScanner

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Udemy API status (descontinuada 01/01/2025) | SCAN-INTL-02 | Depende de credenciais reais e estado da API externa | Rodar `python -m mis scan --platform udemy --niche marketing-digital` com credenciais válidas; confirmar se retorna [] com alert=api_discontinued ou produtos reais |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
