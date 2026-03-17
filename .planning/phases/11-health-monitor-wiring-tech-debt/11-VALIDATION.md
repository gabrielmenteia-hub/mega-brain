---
phase: 11
slug: health-monitor-wiring-tech-debt
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-16
---

# Phase 11 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + pytest-asyncio |
| **Config file** | pyproject.toml (root) |
| **Quick run command** | `pytest mis/tests/test_lifespan.py mis/tests/test_health_monitor.py mis/tests/test_mis_agent.py mis/tests/test_base_scraper.py -x -q` |
| **Full suite command** | `pytest mis/tests/ -q` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest mis/tests/test_lifespan.py mis/tests/test_health_monitor.py mis/tests/test_mis_agent.py mis/tests/test_base_scraper.py -x -q`
- **After every plan wave:** Run `pytest mis/tests/ -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** ~15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 11-01-01 | 01 | 1 | FOUND-04 | unit | `pytest mis/tests/test_lifespan.py -x -q` | ✅ update | ⬜ pending |
| 11-01-02 | 01 | 1 | FOUND-04 | unit | `pytest mis/tests/test_health_monitor.py -x -q` | ✅ update | ⬜ pending |
| 11-01-03 | 01 | 2 | FOUND-02 | unit | `pytest mis/tests/test_base_scraper.py -x -q` | ✅ update | ⬜ pending |
| 11-01-04 | 01 | 2 | FOUND-04 | unit | `pytest mis/tests/test_mis_agent.py -x -q` | ✅ update | ⬜ pending |
| 11-01-05 | 01 | 3 | — | unit | `pytest mis/tests/ -q` | ✅ delete | ⬜ pending |
| 11-01-06 | 01 | 3 | — | unit | `pytest mis/tests/ -q` | ✅ update × 7 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `mis/tests/test_health_monitor.py` — adicionar `test_register_platform_canary_jobs` (verifica 3 jobs com IDs corretos: canary_hotmart, canary_clickbank, canary_kiwify)
- [ ] `mis/tests/test_lifespan.py` — atualizar `test_lifespan_registers_jobs_on_startup` para incluir patches de `run_schema_integrity_check` (AsyncMock) e `register_platform_canary_jobs`
- [ ] `mis/tests/test_mis_agent.py` — atualizar mocks de `run_canary_check` de `MagicMock` para `AsyncMock` nos testes de `_compute_health`
- [ ] `mis/tests/test_base_scraper.py` — adicionar `test_fetch_spa_uses_select_proxy` para verificar que proxy_list é usado via `_select_proxy()`

*Arquivos de test existem — não precisam ser criados do zero, apenas atualizados/expandidos.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Schema warning visível nos logs no startup | FOUND-04 | Requer DB corrompido real | Renomear uma tabela temporariamente e iniciar servidor; verificar log `health.schema_integrity.failed` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** signed off 2026-03-16
