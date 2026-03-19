# Phase 22: Spy Wiring - Research

**Researched:** 2026-03-19
**Domain:** asyncio task chaining, FastAPI background tasks, SQLite status transitions, Jinja2 template extension
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- SPY_V3_TOP_N = 5 por plataforma — constante separada de SPY_TOP_N = 10 (legado)
- Top 5 por plataforma, prioridade rank_at_scan ASC
- Nunca re-espionar produtos com dossier status='done' — usa run_spy(force=False)
- Plataformas fallback-only (PerfectPay, Eduzz, Monetizze) NAO disparam spy
- Sem timeout global — cada run_spy() tem retries internos
- Dossiers em 'running' ao reiniciar ficam assim indefinidamente (sem startup cleanup)
- Concorrencia: 5 paralelos (SPY_V3_TOP_N workers)
- Spy dispara ao final de run_manual_search(), no mesmo asyncio.Task — sem nova infraestrutura
- run_spy_batch() chamado apos gather de scanners + persistencia de produtos
- search_session.status ganha 'spying' e 'spy_done'
- Status page redireciona para results assim que scan='done' — spy e transparente
- Re-spy ao reabrir resultados antigos: asyncio.create_task() em GET /search/{id}/results
- Cancelar sessao (DELETE /search/{id}) cancela spy batch via mesmo _TASK_REGISTRY
- Nova coluna 'Dossie' na search_results_table.html
- Estados: done=link azul, pending/running=badge amarelo, failed=badge vermelho, fora top5=sem badge
- Banner discreto no topo enquanto session.status == 'spying'
- Usuario NAO ve atualizacao automatica — precisa recarregar
- Nova tab 'Oferta' (6a tab) com preco/bonus/garantia/upsells/downsells + bloco colapsavel sales page
- Tab Copy ganha secao 'Gatilhos' com gatilhos emocionais
- Link de retorno dinamico: ?from_search={session_id} -> "← Voltar aos resultados"
- Tabs existentes permanecem sem mudanca estrutural

### Claude's Discretion

- Implementacao interna do bloco `<details>` colapsavel da sales page
- Estilos exatos da nova coluna e badges na tabela
- Ordem exata dos campos na tab Oferta
- Como run_manual_search() chama run_spy_batch() internamente (await vs create_task interno)
- Exata mensagem de tooltip no badge "Falhou"

### Deferred Ideas (OUT OF SCOPE)

- Polling ao vivo dos badges de dossier na tabela de resultados
- Contagem de progresso no banner "Espionando X de Y prontos"
- Re-spy forcado (force=True) a partir da UI
- Timeout global do spy batch por sessao
- Startup hook para marcar dossiers 'running' como 'failed' na reinicializacao
- Exportacao PDF do dossie — Phase 26
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SPY-V3-01 | Ao pesquisar, espionagem automatica roda nos top produtos de cada plataforma do resultado | run_spy_batch() ja existe com API publica pronta; wiring em run_manual_search() e re-spy em GET /results |
| SPY-V3-02 | Usuario pode clicar em qualquer produto para abrir dossie completo | dossier.py ja serve /dossier/{id}; precisa aceitar ?from_search e expor product_id em search_results_table |
| SPY-V3-03 | Dossie inclui anuncios Meta Ads, pagina de venda completa, upsell/downsell, copy e gatilhos, estrutura de oferta | dossier_json ja contem offer_data; nova tab Oferta + secao Gatilhos na tab Copy |
</phase_requirements>

## Summary

A Phase 22 e predominantemente uma fase de **wiring** — conectar infraestrutura existente em novos pontos de disparo — com uma camada de UI moderada para expor o estado de espionagem na tabela de resultados e enriquecer o dossie com conteudo ja produzido pelo pipeline.

O spy_orchestrator.py ja tem `run_spy()` e `run_spy_batch()` com API publica estavel. O search_orchestrator.py ja tem `_TASK_REGISTRY` e o padrao `asyncio.create_task() + register_task()`. O dossier_repository.py ja retorna `offer_data` via `dossier_json`. O que falta e: (1) chamar `run_spy_batch()` ao final de `run_manual_search()`, (2) transicionar `search_session.status` para `'spying'`/`'spy_done'`, (3) expor badges de estado do dossie na tabela, (4) adicionar re-spy no GET /results, e (5) enriquecer o template do dossie com a tab Oferta e secao Gatilhos.

**Recomendacao primaria:** Nao inventar infraestrutura nova. Toda a complexidade de concorrencia, semaforo, e persistencia ja esta testada. O risco principal esta na query SQL para identificar top-5-por-plataforma e no join com dossiers para os badges — essas queries precisam ser eficientes e corretas.

## Standard Stack

### Core (ja em uso — sem instalacao nova)

| Biblioteca | Versao | Proposito | Por que Padrao |
|------------|--------|-----------|----------------|
| asyncio (stdlib) | 3.11+ | Task registry, semaforo, create_task | Ja usada em todo o projeto |
| FastAPI | 0.115+ | Rotas HTTP, query params | Ja usada |
| Jinja2 | 3.1+ | Templates HTML + tab rendering | Ja usada |
| sqlite-utils | 3.x | Queries SQLite, upserts | Ja usada em toda camada de repo |
| structlog | 23+ | Logging estruturado | Ja usada |

### Sem dependencias novas

Esta fase NAO requer instalacao de nenhum pacote. Todo o stack necessario ja esta presente.

## Architecture Patterns

### Padrao estabelecido: asyncio.create_task + register_task

O projeto ja usa este padrao em `search.py:search_run()`:

```python
# Fonte: mis/web/routes/search.py (linha 113-114)
task = asyncio.create_task(run_manual_search(session_id, subniche_id, db_path))
register_task(session_id, task)
```

O spy batch deve seguir o mesmo padrao — registrar no mesmo `_TASK_REGISTRY` com a mesma `session_id` para que `DELETE /search/{id}` cancele ambos.

### Padrao de status transitions

O `update_session_status()` existente aceita qualquer string de status. Os novos estados `'spying'` e `'spy_done'` sao additive — nao quebram o schema. A coluna `finished_at` so e preenchida para terminal_statuses (done, timeout, cancelled). `spy_done` deve ser adicionado a essa lista ou tratado como estado nao-terminal dependendo da decisao de design (ver Open Questions).

### Padrao de badge inline (ja estabelecido)

```html
<!-- Fonte: mis/web/templates/ — padrao usado em search_status -->
<span class="bg-yellow-600 text-xs px-1 rounded">Em processamento</span>
<span class="bg-red-700 text-xs px-1 rounded">Falhou</span>
<a href="/dossier/{{ product.product_id }}?from_search={{ session.id }}"
   class="text-blue-400 hover:text-blue-300 text-xs">Ver Dossie</a>
```

### Estrutura de arquivos modificados nesta fase

```
mis/
├── spy_orchestrator.py              # + constante SPY_V3_TOP_N = 5
├── search_orchestrator.py           # + chamada run_spy_batch() ao final + status 'spying'/'spy_done'
├── search_repository.py             # + spy_done em terminal_statuses (ou nao — ver Open Questions)
├── web/
│   ├── routes/
│   │   ├── search.py                # + re-spy trigger em GET /search/{id}/results
│   │   └── dossier.py               # + ?from_search param + tab 'oferta' no contexto
│   └── templates/
│       ├── search_results_table.html  # + coluna Dossie + badges
│       ├── search_results.html        # + banner "Espionando em background..."
│       ├── dossier.html               # + tab Oferta + link dinamico
│       ├── dossier_tab_copy.html      # + secao Gatilhos
│       └── dossier_tab_oferta.html    # NOVO arquivo
```

### Anti-patterns a evitar

- **Nao criar nova infraestrutura de task registry:** Usar o `_TASK_REGISTRY` existente com mesma chave `session_id`.
- **Nao fazer polling de badges:** A decisao e badges estaticos que atualizam no reload.
- **Nao usar SPY_TOP_N = 10:** Usar SPY_V3_TOP_N = 5 para o fluxo novo. O SPY_TOP_N = 10 continua no scheduler legado.
- **Nao re-espionar produtos com dossier 'done':** run_spy(force=False) ja cuida disso — nao adicionar logica duplicada.

## Don't Hand-Roll

| Problema | Nao Construir | Usar em vez disso | Por que |
|----------|---------------|-------------------|---------|
| Concorrencia limitada | Semaforo manual com contador | run_spy_batch(max_concurrent=5) existente | Ja testado com semaphore test |
| Skip de produto ja espionado | Logica de check de dossier | run_spy(force=False) existente | Ja testado em test_manual_forces_respy |
| Persistencia de dossier | Upsert manual | _upsert_dossier_status() existente | Ja usado em producao |
| Status de sessao | SQL direto | update_session_status() existente | Testado + documentado |
| Identificar top-5 por plataforma | Loop em Python | Query SQL com ROW_NUMBER ou LIMIT + platform_slug grouping | SQL e mais eficiente e testavel |

**Insight chave:** O risco real desta fase nao e concorrencia (ja resolvida) mas a **query SQL para top-5-por-plataforma**. Ver secao de pitfalls.

## Common Pitfalls

### Pitfall 1: Query top-5-por-plataforma incorreta

**O que falha:** Buscar top-5 globais em vez de top-5 por plataforma. Com 5 plataformas produtoras, o certo e ate 25 spies (5 x 5). Se pegar top-5 global, plataformas menores nunca sao espionadas.

**Por que acontece:** SQL simples `ORDER BY rank_at_scan ASC LIMIT 5` pega top-5 global.

**Como evitar:** Agrupar por `platform_slug`, pegar top-N por grupo. Em SQLite sem window functions simples, usar subquery:

```sql
-- Fonte: padrao derivado do schema de search_session_products
SELECT ssp.product_id, ssp.platform_slug, ssp.rank_at_scan
FROM search_session_products ssp
WHERE ssp.session_id = ?
  AND ssp.rank_at_scan <= ?        -- SPY_V3_TOP_N = 5
  AND NOT EXISTS (
      SELECT 1 FROM search_session_products ssp2
      WHERE ssp2.session_id = ssp.session_id
        AND ssp2.platform_slug = ssp.platform_slug
        AND ssp2.rank_at_scan < ssp.rank_at_scan
        AND ssp2.rank_at_scan <= 5
      HAVING COUNT(*) >= 5
  )
ORDER BY ssp.platform_slug, ssp.rank_at_scan ASC
```

**Alternativa mais simples (recomendada):** Python puro sobre resultado da query completa:

```python
# Fonte: padrao derivado da arquitetura existente
from collections import defaultdict

rows = db.execute(
    "SELECT product_id, platform_slug, rank_at_scan "
    "FROM search_session_products "
    "WHERE session_id = ? ORDER BY platform_slug, rank_at_scan ASC",
    [session_id]
).fetchall()

top_per_platform = defaultdict(list)
for product_id, platform_slug, rank in rows:
    if len(top_per_platform[platform_slug]) < SPY_V3_TOP_N:
        top_per_platform[platform_slug].append({"id": product_id, "rank": rank})

products_to_spy = [p for ps in top_per_platform.values() for p in ps]
```

**Sinal de alerta:** Teste que conta spies disparados com 3 plataformas x 10 produtos cada deve resultar em 15 spies (3 x 5), nao 5.

### Pitfall 2: Race condition entre scan completion e spy trigger

**O que falha:** run_spy_batch() e chamado antes de todos os produtos serem persistidos no banco. Como os produtos sao inseridos em loop dentro de run_manual_search(), chamar run_spy_batch() antes do loop terminar significa espionar produtos que ainda nao existem no banco.

**Por que acontece:** Se run_spy_batch() for chamado com asyncio.create_task() dentro do loop de persistencia.

**Como evitar:** Chamar run_spy_batch() APOS o loop de persistencia completar, ainda dentro do mesmo `run_manual_search()`, mas depois da chamada `update_session_status(..., 'done', ...)`.

Sequencia correta:
1. `update_session_status(... 'done' ...)` — marca scan como done
2. `update_session_status(... 'spying' ...)` — transiciona para spying
3. Calcula top-5 por plataforma
4. `await run_spy_batch(products, max_concurrent=5)` — ou `asyncio.create_task()` se quiser retornar antes
5. `update_session_status(... 'spy_done' ...)`

### Pitfall 3: search_status_poll redireciona para /results antes do spy terminar

**O que falha:** O poll endpoint ja tem `if session["status"] in ("done", "timeout", "cancelled")` — se os novos status 'spying' e 'spy_done' nao forem incluidos, o poll continua em loop mesmo depois do scan terminar.

**Como evitar:** O CONTEXT.md ja define que o redirect acontece quando scan='done' (antes do spy). A decisao e: o status page NAO espera o spy terminar. Ao mudar status para 'spying', o poll endpoint deve também incluir 'spying' e 'spy_done' como terminais para redirect:

```python
# Fonte: padrao de search.py — precisa atualizar
if session["status"] in ("done", "timeout", "cancelled", "spying", "spy_done"):
    response.headers["HX-Redirect"] = f"/search/{session_id}/results"
```

### Pitfall 4: Banner de espionagem persiste apos spy_done

**O que falha:** O banner "Espionando em background..." aparece no template verificando `session.status == 'spying'`. Se o usuario recarregar e o status ainda for 'spy_done', o banner nao aparece (correto). Mas se o servidor reiniciar e o session ficar preso em 'spying', o banner aparece para sempre.

**Como evitar:** O CONTEXT.md aceita este comportamento (dossiers em 'running' ficam assim ao reiniciar). Para o banner, o mesmo se aplica — sem startup cleanup nesta fase (deferred).

### Pitfall 5: ?from_search ignorado quando tab e trocada via HTMX

**O que falha:** O link de retorno dinamico e construido no header do `dossier.html`. Quando o usuario troca de tab via HTMX, o tab fragment nao inclui o header. Porem, se o header precisar do from_search para construir o link de retorno, e necessario que o contexto da rota `/dossier/{id}` passe `from_search` para o template completo.

**Como evitar:** Passar `from_search` como variavel de contexto em `dossier_detail()` e usar no template base. NAO tentar passar pelo tab fragment (HTMX swap de #tab-content nao inclui o header).

```python
# Fonte: dossier.py — padrao a adicionar
from_search = request.query_params.get("from_search")
context["from_search"] = from_search
context["back_url"] = f"/search/{from_search}/results" if from_search else "/ranking"
context["back_label"] = "← Voltar aos resultados" if from_search else "← Voltar ao Ranking"
```

### Pitfall 6: list_session_products nao retorna product_id

**O que falha:** A funcao `list_session_products()` em search_repository.py retorna dicts com `rank_at_scan, platform_slug, title, url, price, commission_pct, thumbnail_url, platform_name` — mas NAO retorna `product_id`. Para gerar o link `/dossier/{product_id}?from_search={session_id}`, o template precisa do `product_id`.

**Como evitar:** Adicionar `ssp.product_id` ao SELECT e ao dict de retorno em `list_session_products()`. Esta e uma mudanca aditiva que nao quebra nada.

### Pitfall 7: dossier_json.offer_data pode estar ausente ou com estrutura diferente

**O que falha:** O template da tab Oferta acessa `dossier.dossier.offer_data` (dossier parsed do JSON). Dependendo de quando o produto foi espionado (v1, v2 ou v3), o campo pode estar ausente ou com chaves diferentes.

**Como evitar:** Sempre usar o filtro `| default({})` do Jinja2 para campos opcionais, e testar com `{% if dossier.dossier and dossier.dossier.offer_data %}`.

O pipeline atual em `_execute_spy_pipeline()` ja popula `offer_data`:
```python
# Fonte: spy_orchestrator.py linha 224-231
spy_data = SpyData(
    ...
    offer_data={
        k: extracted[k]
        for k in ("price", "bonuses", "guarantees", "upsells", "downsells")
        if k in extracted
    },
    ...
)
```

## Code Examples

### Chamada de run_spy_batch ao final de run_manual_search

```python
# Fonte: padrao derivado de search_orchestrator.py + spy_orchestrator.py
# Adicionar ao final de run_manual_search(), depois do update_session_status 'done'

from .spy_orchestrator import run_spy_batch

SPY_V3_TOP_N = 5

# Transiciona para 'spying'
update_session_status(db_path, session_id, "spying", platform_statuses, total_products)

# Calcula top-5 por plataforma
rows = get_db(db_path).execute(
    "SELECT product_id, platform_slug, rank_at_scan "
    "FROM search_session_products WHERE session_id = ? "
    "ORDER BY platform_slug, rank_at_scan ASC",
    [session_id],
).fetchall()

from collections import defaultdict
top_per_platform = defaultdict(list)
for product_id, platform_slug, rank_at_scan in rows:
    if len(top_per_platform[platform_slug]) < SPY_V3_TOP_N:
        top_per_platform[platform_slug].append({"id": product_id, "rank": rank_at_scan or 999})

products_to_spy = [p for ps in top_per_platform.values() for p in ps]

if products_to_spy:
    await run_spy_batch(products_to_spy, max_concurrent=SPY_V3_TOP_N)

update_session_status(db_path, session_id, "spy_done", platform_statuses, total_products)
```

### Re-spy no GET /search/{id}/results

```python
# Fonte: padrao derivado de search.py:search_results()
# Adicionar em search_results() antes do return

# Re-spy top-5 por plataforma sem dossier (para resultados antigos)
if session["status"] in ("done", "spy_done"):
    db = get_db(db_path)
    rows = db.execute(
        """
        SELECT ssp.product_id, ssp.platform_slug, ssp.rank_at_scan
        FROM search_session_products ssp
        LEFT JOIN dossiers d ON d.product_id = ssp.product_id
        WHERE ssp.session_id = ?
          AND (d.id IS NULL OR d.status != 'done')
        ORDER BY ssp.platform_slug, ssp.rank_at_scan ASC
        """,
        [session_id],
    ).fetchall()

    from collections import defaultdict
    top_per_platform = defaultdict(list)
    for product_id, platform_slug, rank_at_scan in rows:
        if len(top_per_platform[platform_slug]) < SPY_V3_TOP_N:
            top_per_platform[platform_slug].append({"id": product_id, "rank": rank_at_scan or 999})

    products_to_spy = [p for ps in top_per_platform.values() for p in ps]
    if products_to_spy:
        task = asyncio.create_task(
            run_spy_batch(products_to_spy, max_concurrent=SPY_V3_TOP_N)
        )
        register_task(session_id, task)
        update_session_status(db_path, session_id, "spying", {}, session.get("product_count", 0))
```

### Nova coluna Dossie em search_results_table.html

```html
<!-- Fonte: padrao de badge inline dos templates existentes -->
<!-- Adicionar ao thead -->
<th class="pb-2 font-medium text-right">Dossie</th>

<!-- Adicionar ao tbody, ultimo td de cada produto -->
<td class="py-3 text-right">
  {% if product.dossier_status == 'done' %}
    <a href="/dossier/{{ product.product_id }}?from_search={{ session.id }}"
       class="text-blue-400 hover:text-blue-300 text-xs">Ver Dossie</a>
  {% elif product.dossier_status in ('pending', 'running') %}
    <span class="bg-yellow-600 text-xs px-1 rounded" title="Espionagem em andamento">Em processamento</span>
  {% elif product.dossier_status == 'failed' %}
    <span class="bg-red-700 text-xs px-1 rounded" title="Falha na espionagem">Falhou</span>
  {% endif %}
  {# Produtos fora do top-5 nao exibem nada #}
</td>
```

### Nova tab Oferta com bloco colapsavel

```html
<!-- Fonte: padrao HTML5 nativo <details>/<summary> -->
{% if dossier and dossier.dossier %}
{% set offer = dossier.dossier.get('offer_data', {}) %}
<div class="space-y-6">

  <!-- Preco -->
  {% if offer.price %}
  <section>
    <h2 class="text-lg font-semibold text-white mb-2">Preco Principal</h2>
    <span class="text-2xl font-bold text-green-400">R$ {{ "%.2f"|format(offer.price) }}</span>
  </section>
  {% endif %}

  <!-- Bonus -->
  {% if offer.bonuses %}
  <section>
    <h2 class="text-lg font-semibold text-white mb-3">Bonus</h2>
    <ul class="space-y-1">
      {% for bonus in offer.bonuses %}
        <li class="text-gray-300 flex items-start gap-2"><span class="text-yellow-400">+</span>{{ bonus }}</li>
      {% endfor %}
    </ul>
  </section>
  {% endif %}

  <!-- Upsells / Downsells -->
  {% if offer.upsells or offer.downsells %}
  <section>
    <h2 class="text-lg font-semibold text-white mb-3">Funil de Oferta</h2>
    {% for upsell in offer.upsells | default([]) %}
      <p class="text-gray-300 text-sm">↑ Upsell: {{ upsell }}</p>
    {% endfor %}
    {% for downsell in offer.downsells | default([]) %}
      <p class="text-gray-400 text-sm">↓ Downsell: {{ downsell }}</p>
    {% endfor %}
  </section>
  {% endif %}

  <!-- Pagina de venda colapsavel -->
  {% set sales_text = dossier.dossier.get('sales_page_text') or dossier.dossier.get('full_copy') %}
  {% if sales_text %}
  <details class="bg-gray-800 rounded-lg p-4">
    <summary class="cursor-pointer text-gray-300 text-sm font-medium select-none">
      Ver pagina de venda completa
    </summary>
    <div class="mt-3 text-gray-400 text-sm leading-relaxed whitespace-pre-wrap">{{ sales_text }}</div>
  </details>
  {% endif %}

</div>
{% else %}
<div class="text-center py-16 text-gray-500">
  <p>Dados de oferta nao disponiveis.</p>
</div>
{% endif %}
```

### Secao Gatilhos na tab Copy

```html
<!-- Fonte: padrao de copy_analysis existente em dossier_tab_copy.html -->
{% if dossier and dossier.dossier and dossier.dossier.get('copy_analysis') %}
{% set ca = dossier.dossier.copy_analysis %}
{% if ca.get('emotional_triggers') %}
<section>
  <h2 class="text-lg font-semibold text-white mb-3">Gatilhos Emocionais</h2>
  <div class="flex flex-wrap gap-2">
    {% for trigger in ca.emotional_triggers %}
      <span class="bg-purple-900/40 border border-purple-700/40 text-purple-300 text-xs px-3 py-1 rounded-full">
        {{ trigger }}
      </span>
    {% endfor %}
  </div>
</section>
{% endif %}
{% endif %}
```

## State of the Art

| Abordagem Antiga | Abordagem Atual | Quando Mudou | Impacto |
|-----------------|-----------------|--------------|---------|
| Spy disparado pelo APScheduler (v1/v2) | Spy disparado ao final de run_manual_search() (v3) | Phase 22 | Sem automacao de background — so roda apos pesquisa manual |
| SPY_TOP_N = 10 por nicho/plataforma | SPY_V3_TOP_N = 5 por plataforma por sessao | Phase 22 | Custo LLM controlado, mais focado |
| max_concurrent_spy = 3 (config v1) | 5 paralelos hardcoded para v3 | Phase 22 | Mais rapido, constante separada |
| Dossie via /ranking → produto | Dossie via /search/{id}/results → produto com ?from_search | Phase 22 | Back-link contextual |

## Open Questions

1. **spy_done como terminal status ou nao**
   - O que sabemos: `update_session_status()` define `terminal_statuses = {"done", "timeout", "cancelled"}` e seta `finished_at` para eles. 'spy_done' nao esta na lista.
   - O que esta incerto: Deve 'spy_done' ter `finished_at` setado? Se sim, adiciona-lo a `terminal_statuses`. Se nao, o session nunca tera `finished_at` real.
   - Recomendacao: Adicionar 'spy_done' como terminal (ele e o estado final real da sessao v3). Adicionar `'spy_done'` ao set `terminal_statuses` em `update_session_status()`.

2. **Estrutura de offer_data em dossier_json — garantia de campos**
   - O que sabemos: `_execute_spy_pipeline()` cria `offer_data` com keys `price, bonuses, guarantees, upsells, downsells` se presentes em `extracted`. O campo pode ser vazio `{}`.
   - O que esta incerto: Se o dossier foi criado por versao mais antiga do pipeline, `offer_data` pode ter estrutura diferente ou estar ausente.
   - Recomendacao: Template sempre usa `.get()` e `| default`. Sem assumir presenca de nenhum campo.

3. **Como list_session_products expoe dossier_status**
   - O que sabemos: A funcao atual nao faz JOIN com dossiers. Para exibir os badges, o template precisa de `dossier_status` e `product_id` por produto.
   - O que esta incerto: Fazer o JOIN em list_session_products() (mudanca de API existente) ou criar nova funcao `list_session_products_with_dossier()`.
   - Recomendacao: Estender a funcao existente adicionando LEFT JOIN com dossiers e retornando `product_id, dossier_id, dossier_status`. E mudanca aditiva, nao quebra nada.

## Validation Architecture

### Test Framework

| Propriedade | Valor |
|-------------|-------|
| Framework | pytest + pytest-asyncio |
| Config file | mis/pytest.ini ou conftest.py |
| Comando rapido | `pytest mis/tests/test_spy_wiring.py -x` |
| Suite completa | `pytest mis/tests/ -x` |

### Phase Requirements -> Test Map

| Req ID | Comportamento | Tipo | Comando Automatizado | Arquivo Existe? |
|--------|---------------|------|---------------------|-----------------|
| SPY-V3-01 | run_manual_search() chama run_spy_batch() apos scan com top-5 por plataforma | unit | `pytest mis/tests/test_spy_wiring.py::test_spy_triggered_after_scan -x` | Nao — Wave 0 |
| SPY-V3-01 | session.status transiciona para 'spying' e depois 'spy_done' | unit | `pytest mis/tests/test_spy_wiring.py::test_session_status_transitions -x` | Nao — Wave 0 |
| SPY-V3-01 | Re-spy disparado ao carregar /search/{id}/results com produtos sem dossier | unit | `pytest mis/tests/test_spy_wiring.py::test_results_page_triggers_respy -x` | Nao — Wave 0 |
| SPY-V3-01 | Plataformas fallback-only (eduzz, monetizze, perfectpay) nao disparam spy | unit | `pytest mis/tests/test_spy_wiring.py::test_fallback_platforms_excluded -x` | Nao — Wave 0 |
| SPY-V3-01 | Cancelar sessao tambem cancela spy batch em andamento | unit | `pytest mis/tests/test_spy_wiring.py::test_cancel_session_cancels_spy -x` | Nao — Wave 0 |
| SPY-V3-02 | list_session_products retorna product_id e dossier_status | unit | `pytest mis/tests/test_search_repository.py::test_list_session_products_with_dossier -x` | Nao — Wave 0 |
| SPY-V3-03 | dossier.py aceita ?from_search e passa back_url para contexto | unit | `pytest mis/tests/test_dossier_routes.py::test_from_search_param -x` | Nao — Wave 0 |
| SPY-V3-03 | Tab Oferta renderiza com offer_data presente | smoke | `pytest mis/tests/test_spy_wiring.py::test_oferta_tab_renders -x` | Nao — Wave 0 |

### Sampling Rate

- **Por task commit:** `pytest mis/tests/test_spy_wiring.py -x`
- **Por wave merge:** `pytest mis/tests/ -x`
- **Phase gate:** Suite completa verde antes de `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `mis/tests/test_spy_wiring.py` — cobre SPY-V3-01, SPY-V3-02, SPY-V3-03 (tests de wiring + UI)
- [ ] Estender `mis/tests/test_search_repository.py` com `test_list_session_products_with_dossier`
- [ ] Criar ou estender `mis/tests/test_dossier_routes.py` com `test_from_search_param`

*Infraestrutura de pytest ja existe — sem instalacao nova necessaria.*

## Sources

### Primary (HIGH confidence)

- Leitura direta de `mis/spy_orchestrator.py` — API run_spy, run_spy_batch, SPY_TOP_N
- Leitura direta de `mis/search_orchestrator.py` — _TASK_REGISTRY, register_task, run_manual_search
- Leitura direta de `mis/search_repository.py` — update_session_status, list_session_products, terminal_statuses
- Leitura direta de `mis/web/routes/search.py` — padrao asyncio.create_task + register_task
- Leitura direta de `mis/web/routes/dossier.py` — _VALID_TABS, query params, contexto de template
- Leitura direta de `mis/web/templates/dossier.html` — estrutura de tabs, back link existente
- Leitura direta de `mis/web/templates/dossier_tab_copy.html` — estrutura de secoes existentes
- Leitura direta de `mis/web/templates/search_results_table.html` — estrutura de colunas existentes
- Leitura direta de `mis/web/templates/search_results.html` — estrutura de banners
- Leitura direta de `mis/migrations/_009_search_sessions.py` — schema de search_session_products
- Leitura direta de `mis/migrations/_003_spy_dossiers.py` — schema de dossiers
- Leitura direta de `mis/dossier_repository.py` — get_dossier_by_product_id, offer_data
- Leitura direta de `mis/tests/test_spy_orchestrator.py` — padroes de teste estabelecidos
- Leitura direta de `.planning/phases/22-spy-wiring/22-CONTEXT.md` — decisoes do discuss-phase

### Secondary (MEDIUM confidence)

- `mis/tests/test_search_orchestrator.py` — confirma padrao de testes para orchestrator

## Metadata

**Confidence breakdown:**
- Standard Stack: HIGH — todo o stack e existente e ja em producao
- Architecture: HIGH — padroes derivados do codigo real lido diretamente
- Pitfalls: HIGH — identificados via analise do codigo existente + decisoes do CONTEXT.md
- SQL queries: MEDIUM — derivadas do schema real, mas nao testadas em execucao

**Research date:** 2026-03-19
**Valid until:** 2026-04-19 (stack estavel, prazo de 30 dias)
