# Phase 7: MIS Integration Bug Fixes - Research

**Researched:** 2026-03-15
**Domain:** Python SQLite column name fixes, scheduler pipeline wiring, test refactoring
**Confidence:** HIGH — all findings are from direct code inspection of the actual source files

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| INT-01 | MIS integrado ao MEGABRAIN como módulo independente (`mis/`) com único ponto de integração (`mis_agent.py`) | BUG-01 e BUG-02 quebram get_briefing_data() e export_to_megabrain() — a interface existe mas está defeituosa |
| INT-02 | Usuário pode invocar análise do MIS via agente/comando dentro do MEGABRAIN | BUG-02 degrada o health score silenciosamente; BUG-01 impede export de dossiês reais |
</phase_requirements>

---

## Summary

Esta fase consiste em corrigir 3 bugs cirúrgicos e bem-documentados no codebase MIS. Nenhum novo design é necessário — os bugs foram identificados com precisão pelo audit v1.0 e confirmados por leitura direta dos arquivos-fonte. As correções são minimais (alterações de string literal ou adição de uma chamada de função), mas os testes precisam ser atualizados para refletir o comportamento correto.

**BUG-01** (`mis_agent.py:308`): A query SQL usa `WHERE d.status = 'complete'` mas `spy_orchestrator.py` escreve `status = 'done'`. Correção: substituir a string `'complete'` por `'done'` na query SQL.

**BUG-02** (`mis_agent.py:149, 229`): Duas queries SQL usam `created_at` mas a coluna na tabela `dossiers` (conforme `_001_initial.py`) se chama `generated_at`. A coluna `created_at` foi adicionada retroativamente pela migration `_005_alerts.py`, mas ela não é populada pelos escritores do dossier (`spy_orchestrator.py` usa `generated_at`). Correção: usar `generated_at` nas queries de `get_briefing_data()`.

**BUG-03** (`mis/scheduler.py:89-110`): `_scan_and_spy_job()` chama `run_all_scanners()` que retorna objetos `Product` em memória (sem IDs de DB). A função então tenta usar `product.id` que não existe. Correção: chamar `save_batch_with_alerts()` após o scan e antes do spy para persistir os produtos e obter IDs reais.

**Primary recommendation:** Aplicar as 3 correções cirúrgicas nos arquivos identificados e atualizar/adicionar testes que validem o comportamento correto — especialmente que `export_to_megabrain()` retorna `exported > 0` quando dossiês com `status='done'` existem.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| sqlite3 | stdlib | Queries SQL diretas em `mis_agent.py` | Já em uso no arquivo |
| sqlite_utils | instalado | ORM leve para upserts e migrações | Padrão do projeto MIS desde Phase 1 |
| pytest | instalado | Framework de testes | Padrão do projeto |
| pytest-asyncio | instalado | Testes de funções async | Necessário para `_scan_and_spy_job` (async) |

### Sem novas dependências

Esta fase não requer instalação de nenhum pacote novo. Todas as dependências necessárias já estão instaladas no ambiente.

---

## Architecture Patterns

### Padrão Existente de Status no Dossier

O schema dos dossiês (`_003_spy_dossiers.py`) define os seguintes valores válidos para `status`:
```
'pending' | 'running' | 'done' | 'failed'
```

`spy_orchestrator.py` escreve `status = 'done'` na linha 250 (update final) e na linha 81 (verificação de skip: `existing[0]["status"] == "done"`). O valor `'complete'` **nunca** é escrito por nenhum módulo do sistema.

### Padrão Existente de Coluna Temporal em Dossiers

A tabela `dossiers` foi criada em `_001_initial.py` com a coluna `generated_at` (linha 101). A migration `_003` adicionou `status`, `dossier_json`, `ads_json`, `incomplete`, `updated_at` — mas **não** `created_at`. A migration `_005_alerts.py` retroativamente adicionou `created_at` à tabela `dossiers` (linha 67), mas essa coluna é NULL para todos os registros existentes porque nenhum escritor a popula.

O `spy_orchestrator.py` popula `generated_at` ao criar novos registros (linha 293: `"generated_at": now`). Portanto, a coluna correta a usar em queries temporais de dossiês é `generated_at`.

### Padrão Existente de save_batch_with_alerts

`save_batch_with_alerts(db, db_path, products)` em `mis/scanner.py` (linhas 100-163):
- Recebe uma instância aberta de `sqlite_utils.Database` (`db`) e o `db_path` (string)
- Captura ranks existentes, chama `save_batch()` para upsert, cria alertas para novos entrants no top-20
- Retorna os produtos persistidos com IDs reais no banco

Os scanners individuais (`register_scanner_jobs`) já chamam `save_batch_with_alerts()` corretamente. O `_scan_and_spy_job()` precisa replicar esse padrão antes de tentar espionar.

### Padrão de Resolução de DB ID pós-save

Após `save_batch_with_alerts()`, o DB ID real de cada produto pode ser obtido via:
```python
rows = list(db.execute(
    "SELECT id FROM products WHERE platform_id=? AND external_id=?",
    [p.platform_id, p.external_id],
))
db_id = rows[0][0] if rows else None
```

Esse é exatamente o padrão já usado internamente em `save_batch_with_alerts()` (linhas 143-149 de `scanner.py`).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Obter DB ID após upsert | Lógica customizada de resolução | `save_batch_with_alerts()` já faz upsert + retorna dados | Já testado, inclui lógica de alertas |
| Iterar produtos pós-scan com IDs | Loop manual sobre objetos Product sem ID | Query `SELECT id FROM products WHERE platform_id=? AND external_id=?` após save | Padrão já usado em `scanner.py:143` |

---

## Common Pitfalls

### Pitfall 1: Coluna created_at existe mas está vazia
**What goes wrong:** A coluna `created_at` existe na tabela `dossiers` (adicionada por `_005`), então a query não dá erro de "column not found" em databases migradas até _005. Mas o valor é sempre `NULL` porque `spy_orchestrator.py` popula `generated_at`, não `created_at`.
**Why it happens:** O `_005` backfill adicionou a coluna mas não retroativamente preencheu os dados. Nenhum writer foi atualizado.
**How to avoid:** Usar sempre `generated_at` para queries temporais em dossiês. Se quiser unificar no futuro, atualizar `spy_orchestrator.py` para escrever `created_at` também.
**Warning signs:** `last_cycle` retorna `None` mesmo com dossiês no banco; `dossiers_today` sempre `False`.

### Pitfall 2: Teste existente usa status='complete' propositalmente
**What goes wrong:** O `_seed_db()` em `test_mis_agent.py` insere dossiês com `status='complete'` (linha 55). Após corrigir BUG-01 para filtrar `status='done'`, o teste `test_incremental_export` continuará exportando 0 dossiês — não porque o bug foi corrigido, mas porque o seed ainda usa `'complete'`.
**Why it happens:** O teste foi escrito com o bug presente — ele valida `result1["exported"] >= 0` (aceita 0), mascarando o bug.
**How to avoid:** Atualizar `_seed_db()` para usar `status='done'` e ajustar a assertion para `result1["exported"] > 0`.
**Warning signs:** `test_incremental_export` passa mas `exported == 0`.

### Pitfall 3: _scan_and_spy_job precisa de sqlite_utils.Database aberta
**What goes wrong:** `save_batch_with_alerts()` recebe `db` (instância de `sqlite_utils.Database`) e `db_path` (string). Se tentar passar apenas `db_path`, a função vai falhar.
**Why it happens:** A assinatura de `save_batch_with_alerts(db, db_path, products)` requer a instância aberta.
**How to avoid:** Em `_scan_and_spy_job()`, abrir o DB via `get_db(db_path)` antes de chamar `save_batch_with_alerts()`. Importar `get_db` de `mis.db` (já importado em `spy_orchestrator.py`; `scheduler.py` pode importar diretamente também).

### Pitfall 4: run_all_scanners retorna dict de listas, não lista flat
**What goes wrong:** `run_all_scanners(config)` retorna `dict[str, list[Product]]` — chaves são `"niche_slug.platform_name"`. O loop em `_scan_and_spy_job()` já itera `results.items()` corretamente. O fix deve preservar essa estrutura e apenas inserir o `save_batch_with_alerts()` dentro do loop existente por plataforma.
**Why it happens:** Scanner retorna agrupado por `(niche, platform)` — cada grupo precisa de seu próprio upsert.
**How to avoid:** Chamar `save_batch_with_alerts(db, db_path, platform_products)` por grupo no loop, depois coletar IDs reais dos produtos persistidos.

---

## Code Examples

Verified patterns from direct source code inspection:

### BUG-01: Localização exata e fix

```python
# mis/mis_agent.py:308 — BUGGY
WHERE d.status = 'complete'

# FIXED
WHERE d.status = 'done'
```

### BUG-02: Localização exata e fix (duas ocorrências)

```python
# mis/mis_agent.py:149 — BUGGY
row = conn.execute(
    "SELECT MAX(created_at) FROM dossiers"
).fetchone()

# FIXED
row = conn.execute(
    "SELECT MAX(generated_at) FROM dossiers"
).fetchone()

# mis/mis_agent.py:229 — BUGGY
row = conn.execute(
    "SELECT COUNT(*) FROM dossiers WHERE created_at >= ?",
    [today_str],
).fetchone()

# FIXED
row = conn.execute(
    "SELECT COUNT(*) FROM dossiers WHERE generated_at >= ?",
    [today_str],
).fetchone()
```

### BUG-03: Padrão de fix para _scan_and_spy_job

```python
# Após run_all_scanners, antes do loop de spy:
# 1. Abrir o DB
from mis.db import get_db
db_path = os.environ.get("MIS_DB_PATH", "data/mis.db")
db = get_db(db_path)

# 2. Por grupo de plataforma, salvar e coletar IDs
products_to_spy: list[dict] = []
for platform_key, platform_products in results.items():
    if not platform_products:
        continue
    # Save to DB e cria alertas de top-20
    save_batch_with_alerts(db, db_path, platform_products)
    # Agora coletar IDs reais do DB
    top_products = platform_products[:SPY_TOP_N]
    for p in top_products:
        rows = list(db.execute(
            "SELECT id FROM products WHERE platform_id=? AND external_id=?",
            [p.platform_id, p.external_id],
        ))
        if not rows:
            log.warning("scan_and_spy_job.product_no_db_id", ...)
            continue
        db_id = rows[0][0]
        products_to_spy.append({"id": db_id, "rank": p.rank})
```

### Atualização necessária em test_mis_agent.py — _seed_db

```python
# BUGGY (linha 54-55) — usa 'complete', não reflete o sistema real
"(product_id, status, opportunity_score, confidence_score, dossier_json, created_at) "
"VALUES (?, 'complete', ?, 0.9, ?, ?)",

# FIXED — usa 'done' e generated_at
"(product_id, status, opportunity_score, confidence_score, dossier_json, generated_at) "
"VALUES (?, 'done', ?, 0.9, ?, ?)",
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Teste aceita `exported >= 0` | Teste deve assertar `exported > 0` com seed de dossiês válidos | Phase 7 | Garante que o fix do BUG-01 é realmente testado |
| `_scan_and_spy_job` retorna antes de salvar | Salvar no DB antes de resolver IDs | Phase 7 | Habilita pipeline automático scan→spy→dossier |

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (com pytest-asyncio para testes async) |
| Config file | `mis/pytest.ini` ou `pyproject.toml` (verificar) |
| Quick run command | `pytest mis/tests/test_mis_agent.py -x` |
| Full suite command | `pytest mis/tests/ -x` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INT-01 | `export_to_megabrain()` exporta dossiês com `status='done'` e retorna `exported > 0` | unit | `pytest mis/tests/test_mis_agent.py::test_incremental_export -x` | ✅ (requer update) |
| INT-01 | `get_briefing_data()` retorna `last_cycle` não-nulo quando dossiês existem | unit | `pytest mis/tests/test_mis_agent.py::test_with_data -x` | ✅ (requer update do seed) |
| INT-02 | `get_briefing_data()` health score inclui `dossiers_today=True` quando há dossiê de hoje | unit | `pytest mis/tests/test_mis_agent.py::test_health_with_dossier_today -x` | ❌ Wave 0 |
| INT-01, INT-02 | `_scan_and_spy_job()` salva produtos no DB antes de tentar spy | unit/integration | `pytest mis/tests/test_scan_and_spy_job.py -x` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest mis/tests/test_mis_agent.py -x`
- **Per wave merge:** `pytest mis/tests/ -x`
- **Phase gate:** Full suite green antes de `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `mis/tests/test_mis_agent.py` — atualizar `_seed_db()` para usar `status='done'` e `generated_at`; fortalecer assertion em `test_incremental_export` para `exported > 0`; adicionar `test_health_with_dossier_today` cobrindo o fix do BUG-02
- [ ] `mis/tests/test_scan_and_spy_job.py` — novo arquivo cobrindo BUG-03: mock de `run_all_scanners`, verificar que `save_batch_with_alerts` é chamado, verificar que produtos com IDs reais chegam ao `run_spy_batch`

---

## Open Questions

1. **A coluna `created_at` em dossiers deve continuar existindo?**
   - What we know: `_005_alerts.py` a adicionou mas nenhum writer a popula. `_render_dossier_markdown` em `mis_agent.py` usa `row.get("created_at")` para o frontmatter do Markdown exportado.
   - What's unclear: Se devemos manter `created_at` no frontmatter do Markdown (usando o valor de `generated_at` como fallback) ou simplesmente mudar o campo do frontmatter para `generated_at`.
   - Recommendation: No fix do BUG-02, mudar as queries para `generated_at`. Em `_render_dossier_markdown`, usar `row.get("generated_at") or row.get("created_at")` como fallback seguro — sem quebrar exports existentes.

2. **O `_scan_and_spy_job` deve importar `get_db` de `mis.db`?**
   - What we know: `spy_orchestrator.py` já importa e usa `get_db` e `run_migrations`. `scheduler.py` não importa nenhum deles atualmente.
   - What's unclear: Se há alguma razão para `scheduler.py` não abrir o DB diretamente.
   - Recommendation: Adicionar as importações necessárias em `_scan_and_spy_job()` como imports locais (padrão existente no arquivo — `load_config` já é importado localmente na linha 80).

---

## Sources

### Primary (HIGH confidence)

- `mis/mis_agent.py` — inspecionado diretamente; BUGs 01 e 02 confirmados nas linhas exatas indicadas pelo audit
- `mis/scheduler.py` — inspecionado diretamente; BUG-03 confirmado: nenhuma chamada a `save_batch_with_alerts()` em `_scan_and_spy_job()`
- `mis/scanner.py` — inspecionado diretamente; `save_batch_with_alerts(db, db_path, products)` signature e comportamento confirmados
- `mis/spy_orchestrator.py` — inspecionado diretamente; `status='done'` confirmado nas linhas 81 e 250; `generated_at` confirmado na linha 293
- `mis/migrations/_001_initial.py` — inspecionado diretamente; `generated_at` é o nome da coluna original
- `mis/migrations/_003_spy_dossiers.py` — inspecionado diretamente; `created_at` NÃO adicionado nesta migration
- `mis/migrations/_005_alerts.py` — inspecionado diretamente; `created_at` adicionado à tabela `dossiers` mas sem dados
- `mis/tests/test_mis_agent.py` — inspecionado diretamente; seed usa `status='complete'` e `created_at` — ambos precisam de correção
- `.planning/v1.0-MILESTONE-AUDIT.md` — audit com evidências e linhas exatas dos 3 bugs

### Secondary (MEDIUM confidence)

- N/A — toda evidência é diretamente verificável no código-fonte

---

## Metadata

**Confidence breakdown:**
- Localização dos bugs: HIGH — confirmada por leitura direta dos arquivos, consistente com o audit
- Correções necessárias: HIGH — cada correção é uma mudança mínima e cirúrgica verificável
- Impacto nos testes: HIGH — `_seed_db()` usa `'complete'` e `created_at`, confirmado nas linhas 54-55 de `test_mis_agent.py`
- Assinatura de `save_batch_with_alerts`: HIGH — lida diretamente em `scanner.py:100-104`

**Research date:** 2026-03-15
**Valid until:** Sem prazo de expiração — baseado em código estático, não em APIs externas
