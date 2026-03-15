---
phase: 4
slug: pain-radar
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-15
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | `mis/pytest.ini` |
| **Quick run command** | `cd mis && python -m pytest tests/test_radar_*.py tests/test_migration_004.py tests/test_synthesizer.py -x -q` |
| **Full suite command** | `cd mis && python -m pytest tests/ -q` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd mis && python -m pytest tests/test_radar_*.py tests/test_migration_004.py tests/test_synthesizer.py -x -q`
- **After every plan wave:** Run `cd mis && python -m pytest tests/ -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 4-01-01 | 01 | 0 | RADAR-01 | unit | `pytest tests/test_trends_collector.py -x` | ❌ Wave 0 | ⬜ pending |
| 4-01-02 | 01 | 0 | RADAR-01 | unit | `pytest tests/test_trends_collector.py::test_ratelimited -x` | ❌ Wave 0 | ⬜ pending |
| 4-02-01 | 02 | 0 | RADAR-02 | unit | `pytest tests/test_reddit_collector.py -x` | ❌ Wave 0 | ⬜ pending |
| 4-02-02 | 02 | 0 | RADAR-02 | unit | `pytest tests/test_quora_collector.py -x` | ❌ Wave 0 | ⬜ pending |
| 4-03-01 | 03 | 0 | RADAR-03 | unit | `pytest tests/test_youtube_collector.py -x` | ❌ Wave 0 | ⬜ pending |
| 4-03-02 | 03 | 0 | RADAR-03 | unit | `pytest tests/test_youtube_collector.py::test_quota_guard -x` | ❌ Wave 0 | ⬜ pending |
| 4-04-01 | 04 | 0 | RADAR-05 | unit | `pytest tests/test_migration_004.py::test_upsert_idempotent -x` | ❌ Wave 0 | ⬜ pending |
| 4-04-02 | 04 | 0 | RADAR-05 | unit | `pytest tests/test_synthesizer.py::test_report_idempotent -x` | ❌ Wave 0 | ⬜ pending |
| 4-05-01 | 05 | 0 | RADAR-06 | unit | `pytest tests/test_synthesizer.py -x` | ❌ Wave 0 | ⬜ pending |
| 4-05-02 | 05 | 0 | RADAR-06 | unit | `pytest tests/test_synthesizer.py::test_no_signals_skip -x` | ❌ Wave 0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `mis/tests/test_trends_collector.py` — stubs para RADAR-01
- [ ] `mis/tests/test_reddit_collector.py` — stubs para RADAR-02 (Reddit)
- [ ] `mis/tests/test_quora_collector.py` — stubs para RADAR-02 (Quora)
- [ ] `mis/tests/test_youtube_collector.py` — stubs para RADAR-03 + quota guard
- [ ] `mis/tests/test_migration_004.py` — stubs para RADAR-05 (schema + upsert)
- [ ] `mis/tests/test_synthesizer.py` — stubs para RADAR-06
- [ ] `mis/tests/test_radar_jobs.py` — stubs para register_radar_jobs()
- [ ] `mis/tests/fixtures/reddit_response.json` — fixture PRAW mock
- [ ] `mis/tests/fixtures/youtube_search_response.json` — fixture YouTube API mock
- [ ] Framework install: `pip install pytrends-modern praw google-api-python-client` — se não instalado

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Quora retorna perguntas reais (não HTML vazio de SPA) | RADAR-02 | Playwright + anti-bot não reproduzível em CI unitário | Rodar `python -m mis radar --niche <slug>` e verificar `pain_signals` com `source='quora'` no banco |
| Scheduler registra 4 jobs ao iniciar | RADAR-01/02/03/06 | Requer processo APScheduler real rodando | Iniciar `python -m mis server` e verificar logs com `job_id in [radar_trends, radar_reddit_quora, radar_youtube, radar_synthesizer]` |
| YouTube quota guard reativa à meia-noite PT | RADAR-03 | Dependente de tempo real | Verificar `youtube_quota_log` está limpo após reset; job `radar_youtube` retorna a coletar |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
