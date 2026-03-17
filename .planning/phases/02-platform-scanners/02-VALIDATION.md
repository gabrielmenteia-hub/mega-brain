---
phase: 2
slug: platform-scanners
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-14
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x + pytest-asyncio 0.24.x |
| **Config file** | `mis/pytest.ini` (asyncio_mode = auto, testpaths = tests, timeout = 10) |
| **Quick run command** | `cd mis && python -m pytest tests/test_kiwify_scanner.py -x -q` |
| **Full suite command** | `cd mis && python -m pytest tests/ -q` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd mis && python -m pytest tests/test_{current_module}_scanner.py -x -q`
- **After every plan wave:** Run `cd mis && python -m pytest tests/ -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 0 | SCAN-02 | stub | `pytest tests/test_kiwify_scanner.py -x` | ❌ W0 | ⬜ pending |
| 02-01-02 | 01 | 0 | SCAN-01 | stub | `pytest tests/test_hotmart_scanner.py -x` | ❌ W0 | ⬜ pending |
| 02-01-03 | 01 | 1 | SCAN-02 | unit+fixture | `pytest tests/test_kiwify_scanner.py::test_happy_path -x` | ❌ W0 | ⬜ pending |
| 02-01-04 | 01 | 1 | SCAN-02 | unit+fixture | `pytest tests/test_kiwify_scanner.py::test_field_types -x` | ❌ W0 | ⬜ pending |
| 02-01-05 | 01 | 1 | SCAN-02 | unit+fixture | `pytest tests/test_kiwify_scanner.py::test_drift_alert -x` | ❌ W0 | ⬜ pending |
| 02-01-06 | 01 | 1 | SCAN-02 | integration | `pytest tests/test_kiwify_scanner.py::test_upsert -x` | ❌ W0 | ⬜ pending |
| 02-02-01 | 02 | 0 | SCAN-03 | stub | `pytest tests/test_clickbank_scanner.py -x` | ❌ W0 | ⬜ pending |
| 02-02-02 | 02 | 1 | SCAN-03 | unit+fixture | `pytest tests/test_clickbank_scanner.py::test_happy_path -x` | ❌ W0 | ⬜ pending |
| 02-02-03 | 02 | 1 | SCAN-03 | unit+fixture | `pytest tests/test_clickbank_scanner.py::test_field_types -x` | ❌ W0 | ⬜ pending |
| 02-02-04 | 02 | 1 | SCAN-03 | unit+fixture | `pytest tests/test_clickbank_scanner.py::test_drift_alert -x` | ❌ W0 | ⬜ pending |
| 02-02-05 | 02 | 1 | SCAN-03 | integration | `pytest tests/test_clickbank_scanner.py::test_upsert -x` | ❌ W0 | ⬜ pending |
| 02-03-01 | 03 | 0 | SCAN-01 | manual | Live DevTools inspection — no automated command | manual | ⬜ pending |
| 02-03-02 | 03 | 1 | SCAN-01 | unit+fixture | `pytest tests/test_hotmart_scanner.py::test_happy_path -x` | ❌ W0 | ⬜ pending |
| 02-03-03 | 03 | 1 | SCAN-01 | unit+fixture | `pytest tests/test_hotmart_scanner.py::test_fallback_selector -x` | ❌ W0 | ⬜ pending |
| 02-03-04 | 03 | 1 | SCAN-01 | unit+fixture | `pytest tests/test_hotmart_scanner.py::test_drift_alert -x` | ❌ W0 | ⬜ pending |
| 02-03-05 | 03 | 1 | SCAN-01 | integration | `pytest tests/test_hotmart_scanner.py::test_upsert_no_dup -x` | ❌ W0 | ⬜ pending |
| 02-03-06 | 03 | 2 | SCAN-04 | unit | `pytest tests/test_scanner_jobs.py::test_jobs_registered -x` | ❌ W0 | ⬜ pending |
| 02-03-07 | 03 | 2 | SCAN-04 | unit | `pytest tests/test_scanner_jobs.py::test_cron_trigger -x` | ❌ W0 | ⬜ pending |
| 02-03-08 | 03 | 2 | SCAN-04 | unit+DB | `pytest tests/test_scanner_jobs.py::test_platform_canary_stale -x` | ❌ W0 | ⬜ pending |
| 02-03-09 | 03 | 2 | SCAN-04 | unit | `pytest tests/test_scanner_jobs.py::test_partial_failure -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `mis/scanner.py` — Product dataclass + PlatformScanner abstract base + run_all_scanners()
- [ ] `mis/scanners/__init__.py` — subpackage init
- [ ] `mis/product_repository.py` — upsert_product() function
- [ ] `mis/migrations/_002_product_enrichment.py` — rank, commission_pct, rating, thumbnail_url, updated_at columns
- [ ] `mis/tests/fixtures/kiwify/catalog_saude.html` — gravar ao vivo (httpx SSR)
- [ ] `mis/tests/fixtures/kiwify/catalog_mkt.html` — gravar ao vivo
- [ ] `mis/tests/fixtures/clickbank/marketplace_health.html` — gravar ao vivo
- [ ] `mis/tests/fixtures/clickbank/marketplace_mktg.html` — gravar ao vivo
- [ ] `mis/tests/fixtures/hotmart/` — gravar JSON do XHR ao vivo (requer inspeção live DevTools primeiro)
- [ ] `mis/tests/test_kiwify_scanner.py` — 5 testes RED (happy path, field types, fallback, drift alert, upsert)
- [ ] `mis/tests/test_clickbank_scanner.py` — 5 testes RED (happy path, field types, fallback, drift alert, upsert)
- [ ] `mis/tests/test_hotmart_scanner.py` — 5 testes RED (happy path, fallback selector, drift alert, upsert, XHR intercept)
- [ ] `mis/tests/test_scanner_jobs.py` — 4 testes RED (jobs_registered, cron_trigger, canary_stale, partial_failure)
- [ ] `mis/requirements.txt` — adicionar beautifulsoup4 e lxml

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Hotmart XHR endpoint identificado | SCAN-01 | Endpoint não documentado; requer DevTools ao vivo | Abrir hotmart.com/pt-br/marketplace no browser, DevTools → Network → XHR/Fetch, navegar por categoria, identificar e gravar response JSON como fixture |
| ClickBank gravity score visível sem login | SCAN-03 | Verificar se dados aparecem no SSR HTML | httpx GET em `https://www.clickbank.com/view-marketplace/` e confirmar se gravity score está no HTML |
| Kiwify external_id campo estável | SCAN-02 | Estrutura HTML interna requer inspeção | Gravar fixture HTML ao vivo e confirmar qual atributo usar como external_id |
| Ranking diário executado sem intervenção | SCAN-04 | APScheduler CronTrigger não testável em tempo real | Verificar logs de APScheduler após período de 24h em staging |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** signed off 2026-03-16
