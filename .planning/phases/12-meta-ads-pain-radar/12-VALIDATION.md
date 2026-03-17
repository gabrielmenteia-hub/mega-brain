---
phase: 12
slug: meta-ads-pain-radar
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-16
---

# Phase 12 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | mis/pytest.ini |
| **Quick run command** | `cd mis && python -m pytest tests/test_meta_ads_radar.py -x -q` |
| **Full suite command** | `cd mis && python -m pytest -x -q` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd mis && python -m pytest tests/test_meta_ads_radar.py -x -q`
- **After every plan wave:** Run `cd mis && python -m pytest -x -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 12-01-01 | 01 | 1 | RADAR-04 | unit | `cd mis && python -m pytest tests/test_meta_ads_radar.py -x -q` | ❌ W0 | ⬜ pending |
| 12-01-02 | 01 | 1 | RADAR-04 | unit | `cd mis && python -m pytest tests/test_meta_ads_radar.py tests/test_lifespan.py -x -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `mis/tests/test_meta_ads_radar.py` — RED stubs for RADAR-04 (happy path, no token, idempotência, no creative body)
- [ ] `mis/tests/fixtures/meta_ads/ads_archive_radar_response.json` — fixture de resposta da API Meta por keyword

*Existing infrastructure covers conftest.py, pytest.ini, and respx — no new installs needed.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Sinais Meta Ads aparecem no pain_reports após ciclo de síntese | RADAR-04 | Requer token real + ciclo APScheduler completo | Configurar META_ACCESS_TOKEN real, executar `python -m mis radar --niche emagrecimento`, verificar pain_reports mais recente |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** signed off 2026-03-16
