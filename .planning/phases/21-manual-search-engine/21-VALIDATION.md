---
phase: 21
slug: manual-search-engine
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-18
---

# Phase 21 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (já instalado) |
| **Config file** | `mis/pytest.ini` |
| **Quick run command** | `python -m pytest mis/tests/test_search_repository.py -x -q` |
| **Full suite command** | `python -m pytest mis/tests/ -x -q` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest mis/tests/test_search_repository.py -x -q`
- **After every plan wave:** Run `python -m pytest mis/tests/ -x -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 21-01-01 | 01 | 1 | SEARCH-01 | unit | `python -m pytest mis/tests/test_search_repository.py::test_create_and_list_session -x` | ❌ W0 | ⬜ pending |
| 21-01-02 | 01 | 1 | SEARCH-03 | unit | `python -m pytest mis/tests/test_search_repository.py::test_startup_marks_running_as_timeout -x` | ❌ W0 | ⬜ pending |
| 21-02-01 | 02 | 2 | SEARCH-01 | unit | `python -m pytest mis/tests/test_search_orchestrator.py -x` | ❌ W0 | ⬜ pending |
| 21-02-02 | 02 | 2 | SEARCH-03 | unit | `python -m pytest mis/tests/web/test_web_search.py::test_no_scheduler_on_startup -x` | ❌ W0 | ⬜ pending |
| 21-03-01 | 03 | 3 | SEARCH-02 | unit | `python -m pytest mis/tests/test_search_repository.py::test_list_session_products -x` | ❌ W0 | ⬜ pending |
| 21-03-02 | 03 | 3 | SEARCH-01 | integration | `python -m pytest mis/tests/web/test_web_search.py::test_post_search_run_creates_session -x` | ❌ W0 | ⬜ pending |
| 21-03-03 | 03 | 3 | SEARCH-02 | integration | `python -m pytest mis/tests/web/test_web_search.py::test_results_page_200 -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `mis/tests/test_search_repository.py` — stubs para SEARCH-01, SEARCH-02, SEARCH-03 (camada repositório)
- [ ] `mis/tests/test_search_orchestrator.py` — stubs para run_manual_search: timeout, partial results, platform error isolation
- [ ] `mis/tests/web/test_web_search.py` — stubs para rotas FastAPI e integração HTMX

*Infraestrutura existente (conftest.py, app_client fixture) cobre todos os novos testes — nenhuma fixture nova obrigatória.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Polling HTMX a cada 2s atualiza lista de plataformas na página de status | SEARCH-01 | Comportamento de UI em tempo real | Iniciar scan, observar que a lista de plataformas atualiza a cada ~2s no browser |
| Auto-redirect 302 para /search/{id}/results ao concluir | SEARCH-01 | Redirect de browser em resposta HTMX | Iniciar scan, confirmar que browser navega para resultados automaticamente |
| Banner stale aparece após 7 dias | SEARCH-02 | Requer manipulação de data no banco | Inserir sessão com started_at = now() - 8 days, acessar /search/{id}/results |
| APScheduler não roda jobs automáticos | SEARCH-03 | Verificação de ausência de comportamento | Iniciar dashboard, observar que nenhum scan roda automaticamente por 5 minutos |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
