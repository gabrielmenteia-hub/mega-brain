---
phase: 6
slug: megabrain-integration
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-15
---

# Phase 6 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (pytest-asyncio) com asyncio_mode = auto |
| **Config file** | `mis/pytest.ini` — asyncio_mode = auto, testpaths = tests, timeout = 10 |
| **Quick run command** | `cd mis && python -m pytest tests/test_mis_agent.py -x` |
| **Full suite command** | `cd mis && python -m pytest tests/ -x` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd mis && python -m pytest tests/test_mis_agent.py -x`
- **After every plan wave:** Run `cd mis && python -m pytest tests/ -x`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 06-01-01 | 01 | 0 | INT-01 | unit | `cd mis && python -m pytest tests/test_mis_agent.py -x` | ❌ W0 | ⬜ pending |
| 06-01-02 | 01 | 1 | INT-01 | unit | `cd mis && python -m pytest tests/test_mis_agent.py::test_get_briefing_data_empty_db -x` | ❌ W0 | ⬜ pending |
| 06-01-03 | 01 | 1 | INT-01 | unit | `cd mis && python -m pytest tests/test_mis_agent.py::test_get_briefing_data_with_data -x` | ❌ W0 | ⬜ pending |
| 06-01-04 | 01 | 1 | INT-01 | unit | `cd mis && python -m pytest tests/test_mis_agent.py::test_export_incremental -x` | ❌ W0 | ⬜ pending |
| 06-02-01 | 02 | 1 | INT-02 | smoke | `python -c "from pathlib import Path; assert Path('.claude/skills/mis-briefing/SKILL.md').exists()"` | ❌ W0 | ⬜ pending |
| 06-02-02 | 02 | 1 | INT-02 | unit | `cd mis && python -m pytest tests/test_mis_agent.py -x` | ❌ W0 | ⬜ pending |
| 06-02-03 | 02 | 2 | INT-01 INT-02 | integration | `cd mis && python -m pytest tests/ -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `mis/tests/test_mis_agent.py` — stubs para INT-01 (3 cenários: DB vazio, DB com dados, export incremental) e INT-02 (importação via sys.path)
- [ ] Fixture de DB populado com produtos + dossiers + pain_reports + alertas para testes com dados

*Infraestrutura existente (pytest.ini, conftest.py, db_path fixture) já cobre o resto — sem novos arquivos de config necessários.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `/mis-briefing` renderiza visualmente correto no Claude Code | INT-02 | Output visual ASCII art não testável via assert | Invocar `/mis-briefing` no Claude Code com MIS configurado, verificar containers `╔═══╗`, Health Score, top-10 produtos, seção Pain Radar e rodapé |
| `python -m mis export` grava arquivos em `knowledge/mis/` | INT-01 | Requer MIS_PATH e MEGABRAIN_PATH reais no .env | Executar `python -m mis export`, verificar `knowledge/mis/` com dossiers e README.md |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** signed off 2026-03-16
