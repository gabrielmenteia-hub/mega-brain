---
phase: 16
slug: international-high-friction
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-17
---

# Phase 16 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + pytest-asyncio |
| **Config file** | `pytest.ini` (existente no projeto) |
| **Quick run command** | `pytest mis/tests/test_jvzoo_scanner.py mis/tests/test_gumroad_scanner.py mis/tests/test_appsumo_scanner.py -x` |
| **Full suite command** | `pytest mis/tests/ -x` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest mis/tests/test_jvzoo_scanner.py mis/tests/test_gumroad_scanner.py mis/tests/test_appsumo_scanner.py -x`
- **After every plan wave:** Run `pytest mis/tests/ -x`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 16-01-W0 | 01 | 0 | SCAN-INTL-03 | unit stub | `pytest mis/tests/test_jvzoo_scanner.py -x` | ❌ W0 | ⬜ pending |
| 16-01-01 | 01 | 1 | SCAN-INTL-03 | unit | `pytest mis/tests/test_jvzoo_scanner.py -x` | ✅ W0 | ⬜ pending |
| 16-01-02 | 01 | 1 | infra | unit | `pytest mis/tests/test_jvzoo_scanner.py::test_playwright_semaphore_exists -x` | ✅ W0 | ⬜ pending |
| 16-02-W0 | 02 | 0 | SCAN-INTL-04 + SCAN-INTL-05 | unit stub | `pytest mis/tests/test_gumroad_scanner.py mis/tests/test_appsumo_scanner.py -x` | ❌ W0 | ⬜ pending |
| 16-02-01 | 02 | 1 | SCAN-INTL-04 | unit | `pytest mis/tests/test_gumroad_scanner.py -x` | ✅ W0 | ⬜ pending |
| 16-02-02 | 02 | 1 | SCAN-INTL-05 | unit | `pytest mis/tests/test_appsumo_scanner.py -x` | ✅ W0 | ⬜ pending |
| 16-02-03 | 02 | 2 | wiring | integration | `pytest mis/tests/ -x` | ✅ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `mis/tests/test_jvzoo_scanner.py` — 6 testes SCAN-INTL-03 (stub RED) + `test_playwright_semaphore_exists`
- [ ] `mis/tests/test_gumroad_scanner.py` — 6 testes SCAN-INTL-04 (stub RED)
- [ ] `mis/tests/test_appsumo_scanner.py` — 6 testes SCAN-INTL-05 (stub RED)
- [ ] `mis/tests/fixtures/jvzoo/listings_category84.html` — fixture HTML JVZoo
- [ ] `mis/tests/fixtures/gumroad/discover_page.html` — fixture HTML Gumroad
- [ ] `mis/tests/fixtures/appsumo/browse_page.html` — fixture HTML AppSumo

> **Nota:** O teste do PLAYWRIGHT_SEMAPHORE está embutido em `test_jvzoo_scanner.py` como
> `test_playwright_semaphore_exists`. Não existe arquivo separado `test_base_scraper_semaphore.py`.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| JVZoo não bloqueia em produção real | SCAN-INTL-03 | Incapsula só ativa em requests reais | `python -m mis scan --platform jvzoo --niche marketing` |
| Gumroad scroll loop funciona em prod | SCAN-INTL-04 | SPA não renderiza em mocks | `python -m mis scan --platform gumroad --niche marketing` |
| 5 nichos simultâneos sem OOM | SCAN-INTL-05 | Requer RAM real | `python -m mis scan --platform appsumo` com 5 nichos em paralelo |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved
