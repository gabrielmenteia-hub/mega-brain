---
phase: 3
slug: product-espionage-dossiers
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-14
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.4.2 + pytest-asyncio 0.24 |
| **Config file** | `mis/pytest.ini` ou `pyproject.toml` |
| **Quick run command** | `pytest mis/tests/test_spy_*.py mis/tests/test_intelligence_*.py -x -q` |
| **Full suite command** | `pytest mis/tests/ -x -q` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest mis/tests/ -x -q --timeout=30`
- **After every plan wave:** Run `pytest mis/tests/ -x -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 3-01-01 | 01 | 0 | SPY-01 | unit | `pytest mis/tests/test_sales_page_spy.py -x` | ❌ W0 | ⬜ pending |
| 3-01-02 | 01 | 0 | SPY-03 | unit | `pytest mis/tests/test_sales_page_spy.py::test_offer_extraction -x` | ❌ W0 | ⬜ pending |
| 3-02-01 | 02 | 0 | SPY-02 | unit | `pytest mis/tests/test_meta_ads_spy.py -x` | ❌ W0 | ⬜ pending |
| 3-02-02 | 02 | 0 | SPY-02 | unit | `pytest mis/tests/test_meta_ads_spy.py::test_no_token -x` | ❌ W0 | ⬜ pending |
| 3-02-03 | 02 | 0 | SPY-04 | unit | `pytest mis/tests/test_reviews_spy.py -x` | ❌ W0 | ⬜ pending |
| 3-03-01 | 03 | 0 | SPY-05 | unit | `pytest mis/tests/test_completeness_gate.py::test_gate_passes -x` | ❌ W0 | ⬜ pending |
| 3-03-02 | 03 | 0 | SPY-05 | unit | `pytest mis/tests/test_completeness_gate.py::test_copy_missing -x` | ❌ W0 | ⬜ pending |
| 3-03-03 | 03 | 0 | SPY-05 | unit | `pytest mis/tests/test_completeness_gate.py::test_reviews_below_threshold -x` | ❌ W0 | ⬜ pending |
| 3-03-04 | 03 | 0 | DOS-05 | unit | `pytest mis/tests/test_completeness_gate.py::test_confidence_full -x` | ❌ W0 | ⬜ pending |
| 3-03-05 | 03 | 0 | DOS-05 | unit | `pytest mis/tests/test_completeness_gate.py::test_confidence_no_ads -x` | ❌ W0 | ⬜ pending |
| 3-04-01 | 04 | 0 | DOS-01 | unit | `pytest mis/tests/test_copy_analyzer.py::test_happy_path -x` | ❌ W0 | ⬜ pending |
| 3-04-02 | 04 | 0 | DOS-02 | unit | `pytest mis/tests/test_dossier_generator.py::test_pains_addressed -x` | ❌ W0 | ⬜ pending |
| 3-04-03 | 04 | 0 | DOS-03 | unit | `pytest mis/tests/test_dossier_generator.py::test_modeling_template -x` | ❌ W0 | ⬜ pending |
| 3-05-01 | 05 | 0 | DOS-04 | unit | `pytest mis/tests/test_dossier_generator.py::test_opportunity_score -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `mis/tests/test_sales_page_spy.py` — stubs para SPY-01, SPY-03
- [ ] `mis/tests/test_meta_ads_spy.py` — stubs para SPY-02
- [ ] `mis/tests/test_reviews_spy.py` — stubs para SPY-04
- [ ] `mis/tests/test_completeness_gate.py` — stubs para SPY-05, DOS-05
- [ ] `mis/tests/test_copy_analyzer.py` — stubs para DOS-01 (fixture JSON gravada ao vivo)
- [ ] `mis/tests/test_dossier_generator.py` — stubs para DOS-02, DOS-03, DOS-04
- [ ] `mis/tests/fixtures/sales_page/` — HTML fixtures de páginas de vendas reais
- [ ] `mis/tests/fixtures/meta_ads/` — JSON fixture da resposta da Meta API
- [ ] `mis/tests/fixtures/llm_responses/` — JSON fixtures das respostas do LLM
- [ ] `mis/migrations/_003_spy_dossiers.py` — migration additive (add_column, nunca DROP TABLE)
- [ ] `pip install anthropic markdownify` + adicionar ao `mis/requirements.txt`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Dossiê gerado com dados reais de produto Hotmart | DOS-01, DOS-02 | Requer acesso à API real + produto real | `python -m mis spy --url <URL>` e verificar output no terminal |
| Meta Ads retorna anúncios reais com token válido | SPY-02 | Requer META_ACCESS_TOKEN real | Configurar token e rodar scan com produto que tenha anúncios ativos |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** signed off 2026-03-16
