---
phase: 5
slug: dashboard
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-15
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | pytest.ini (or pyproject.toml [tool.pytest.ini_options]) |
| **Quick run command** | `python -m pytest tests/web/ -x -q` |
| **Full suite command** | `python -m pytest tests/ -q` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/web/ -x -q`
- **After every plan wave:** Run `python -m pytest tests/ -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 01 | 1 | DASH-01 | integration | `python -m pytest tests/web/test_web_ranking.py -x -q` | ❌ W0 | ⬜ pending |
| 05-01-02 | 01 | 1 | DASH-01 | unit | `python -m pytest tests/web/test_web_ranking.py -x -q` | ❌ W0 | ⬜ pending |
| 05-01-03 | 01 | 1 | DASH-01 | integration | `python -m pytest tests/web/test_web_ranking.py -x -q` | ❌ W0 | ⬜ pending |
| 05-02-01 | 02 | 2 | DASH-01 | integration | `python -m pytest tests/web/test_web_ranking.py -x -q` | ❌ W0 | ⬜ pending |
| 05-02-02 | 02 | 2 | DASH-01 | integration | `python -m pytest tests/web/test_web_ranking.py -x -q` | ❌ W0 | ⬜ pending |
| 05-02-03 | 02 | 2 | DASH-01 | unit | `python -m pytest tests/web/test_web_ranking.py -x -q` | ❌ W0 | ⬜ pending |
| 05-03-01 | 03 | 2 | DASH-02 | integration | `python -m pytest tests/web/test_web_dossier.py -x -q` | ❌ W0 | ⬜ pending |
| 05-03-02 | 03 | 2 | DASH-02 | integration | `python -m pytest tests/web/test_web_dossier.py -x -q` | ❌ W0 | ⬜ pending |
| 05-03-03 | 03 | 2 | DASH-02 | unit | `python -m pytest tests/web/test_dossier_repository.py -x -q` | ❌ W0 | ⬜ pending |
| 05-04-01 | 04 | 3 | DASH-03 | integration | `python -m pytest tests/web/test_web_feed.py -x -q` | ❌ W0 | ⬜ pending |
| 05-04-02 | 04 | 3 | DASH-04 | integration | `python -m pytest tests/web/test_web_alerts.py -x -q` | ❌ W0 | ⬜ pending |
| 05-04-03 | 04 | 3 | DASH-04 | unit | `python -m pytest tests/web/test_alert_repository.py -x -q` | ❌ W0 | ⬜ pending |
| 05-04-04 | 04 | 3 | SCAN-05 | unit | `python -m pytest tests/web/test_alert_repository.py -x -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/web/__init__.py` — package marker
- [ ] `tests/web/conftest.py` — shared fixtures: TestClient, temp SQLite DB
- [ ] `tests/web/test_web_ranking.py` — stubs para DASH-01 (GET /, filtros, ordenação, paginação)
- [ ] `tests/web/test_web_dossier.py` — stubs para DASH-02 (GET /dossier/{id}, tabs, navegação)
- [ ] `tests/web/test_web_feed.py` — stubs para DASH-03 (GET /feed, abas por nicho, histórico)
- [ ] `tests/web/test_web_alerts.py` — stubs para DASH-04 (GET /alerts, badge polling, seen/unseen)
- [ ] `tests/web/test_alert_repository.py` — stubs para SCAN-05 (create_alert, get_unseen_count, mark_seen, expire)
- [ ] `tests/web/test_dossier_repository.py` — stubs para DASH-02 (get_dossier, list_by_rank)
- [ ] `tests/web/test_pain_repository.py` — stubs para DASH-03 (get_latest_report, get_historical)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Dark mode visual correto no browser | DASH-01..04 | Verificação visual de CSS/Tailwind no browser real | Abrir `http://localhost:8000` no browser, verificar tema escuro aplicado |
| Clipboard copy no Tab Template | DASH-02 | API `navigator.clipboard` requer browser real | Abrir /dossier/{id} → Tab Template → clicar "Copiar" → colar em editor |
| Polling badge de alertas no navbar | DASH-04 | Requer browser + servidor rodando + tempo real | Iniciar server, inserir alert direto no DB, aguardar 30s, verificar badge atualiza |
| Timestamp relativo ("há 2 horas") | DASH-03 | Verificação visual dependente de dados reais | Abrir /feed → verificar formato "DD/MM HH:MM — há N horas" |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
