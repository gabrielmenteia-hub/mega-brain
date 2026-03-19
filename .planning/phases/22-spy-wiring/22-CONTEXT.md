# Phase 22: Spy Wiring - Context

**Gathered:** 2026-03-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Após uma pesquisa manual concluir (search_session status='done'), os top 5 produtos por plataforma são espionados automaticamente via spy_orchestrator. O usuário pode clicar em qualquer produto da tabela de resultados para abrir o dossiê completo. O dossiê exibe: anúncios Meta Ads, página de venda (estrutura + texto completo colapsável), upsell/downsell, copy e gatilhos, estrutura de oferta (preço, bônus, garantia). Produtos sem dossiê pronto exibem estado visual claro ("Em processamento" ou "Falhou").

Favoritos, alertas e exportação PDF pertencem a fases posteriores.

</domain>

<decisions>
## Implementation Decisions

### Limite de espionagem por plataforma

- **SPY_V3_TOP_N = 5** — constante em `spy_orchestrator.py` (separada de SPY_TOP_N = 10 do fluxo antigo)
- Top 5 **por plataforma** (não global) — até 25 spies por pesquisa em 5 plataformas
- Prioridade: rank_at_scan ASC (posição 1 primeiro)
- **Nunca re-espionar** produtos com dossier `status='done'` — reutiliza `run_spy(force=False)` existente
- Plataformas fallback-only (PerfectPay, Eduzz, Monetizze) não geram spy — sem produtos reais
- Plataformas com erro/0 produtos no scan não disparam spy
- **Sem timeout global** no spy batch — cada `run_spy()` tem seus retries internos
- Dossiers em status `'running'` quando o servidor reinicia ficam assim indefinidamente (sem startup cleanup)
- Concorrência: **5 paralelos** (novo valor — diferente do max_concurrent_spy=3 do config v1)

### Trigger e timing do spy

- Spy dispara **ao final de `run_manual_search()`**, no mesmo `asyncio.Task` — sem nova infraestrutura
- `run_spy_batch()` é chamado após o gather de scanners concluir e persistir produtos
- `search_session.status` ganha dois novos estados: `'spying'` (scan done, spy rodando) e `'spy_done'` (tudo concluído)
- Status page (`/search/{id}/status`) redireciona para `/search/{id}/results` assim que scan='done' — spy é transparente na results page
- **Re-spy ao reabrir resultados antigos**: ao acessar `/search/{id}/results`, produtos top 5 por plataforma sem dossier são re-espionados automaticamente via `asyncio.create_task()`
  - Usa `rank_at_scan` de `search_session_products` para identificar quais são top 5
  - Apenas produtos sem dossier `done` — respeita `force=False`
- Cancelar sessão (`DELETE /search/{id}`) cancela também o spy batch via **mesmo `_TASK_REGISTRY`** com chave `session_id`
- Status 'spying' é interno — poll da status page não é usado durante spy; results page usa badges individuais

### Estado visual na tabela de resultados

- **Nova coluna 'Dossiê'** no lado direito da `search_results_table.html`
- Estados por produto:
  - Dossier `done`: link **"Ver Dossiê"** azul → `/dossier/{product_id}?from_search={session_id}`
  - Dossier `pending/running`: badge **"Em processamento"** amarelo — link desabilitado
  - Dossier `failed`: badge **"Falhou"** vermelho
  - Sem dossier (produto fora do top 5): sem badge — sem link
- **Banner discreto** no topo da results page enquanto `session.status == 'spying'`:
  `"Espionando produtos em background..."` — texto fixo, sem contagem ao vivo
  - Some ao recarregar quando status não é mais 'spying'
- Usu rio **não** vê atualização automática — precisa recarregar para ver badges mudarem

### Conteúdo do dossiê (SPY-V3-03)

- **Nova tab 'Oferta'** (6ª tab, após Template):
  - Preço principal, lista de bônus, garantia, upsells, downsells — dados de `offer_data` do `dossier_json`
  - Bloco colapsável `<details>` **"Ver página de venda completa"** abaixo dos elementos estruturados
- **Tab Copy** ganha seção extra **"Gatilhos"** com os gatilhos emocionais identificados pelo `copy_analyzer` (medo, urgência, prova social, escassez, etc.)
- **Link de retorno dinâmico**: `dossier.py` aceita `?from_search={session_id}` — exibe "← Voltar aos resultados" em vez de "← Voltar ao Ranking" quando parâmetro presente
- Tabs existentes (Visão Geral, Copy, Anúncios, Reviews, Template) permanecem sem mudança estrutural

### Claude's Discretion

- Implementação interna do bloco `<details>` colapsável da sales page
- Estilos exatos da nova coluna e badges na tabela
- Ordem exata dos campos na tab Oferta
- Como `run_manual_search()` chama `run_spy_batch()` internamente (await vs create_task interno)
- Exata mensagem de tooltip no badge "Falhou"

</decisions>

<specifics>
## Specific Ideas

- SPY_V3_TOP_N = 5 é constante separada de SPY_TOP_N = 10 — não quebra o fluxo antigo
- Re-spy ao reabrir resultados usa `rank_at_scan` de `search_session_products` para saber quais são top 5 — dado já existe
- `?from_search={session_id}` no link do dossiê é adicionado pelo template `search_results_table.html`
- Status 'spying' na search_session permite que a results page mostre/esconda o banner sem poll extra
- Tab Oferta: elementos estruturados primeiro (escaneáveis), texto full colapsável abaixo (para quem quer ver tudo)

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets

- `mis/spy_orchestrator.py`: `run_spy(product_id, force=False)`, `run_spy_batch(products, max_concurrent)` — API pública já pronta, sem alteração de interface
- `mis/search_orchestrator.py`: `run_manual_search()` como asyncio.Task, `_TASK_REGISTRY` para cancelamento, `register_task()` — spy batch registra-se no mesmo registry
- `mis/search_repository.py`: `update_session_status()` — reutilizado para transições 'done'→'spying'→'spy_done'
- `mis/web/routes/search.py`: padrão de rotas já estabelecido (asyncio.create_task, redirect, HTMX partials)
- `mis/web/templates/search_results_table.html`: tabela a ser modificada com nova coluna Dossiê
- `mis/web/templates/dossier.html`: header + tabs a ser atualizado com tab Oferta e link dinâmico
- `mis/web/templates/dossier_tab_copy.html`: template a ser atualizado com seção Gatilhos
- `mis/web/routes/dossier.py`: route `/dossier/{product_id}` a aceitar `?from_search` query param
- `mis/dossier_repository.py`: `get_dossier_by_product_id()` — já retorna `offer_data` via dossier_json

### Established Patterns

- Badge inline: `<span class="bg-yellow-600 text-xs px-1 rounded">` — replicar para "Em processamento"
- Badge vermelho: usar `bg-red-700` (mesmo padrão de erros em search_status)
- HTMX: sem polling extra na results page — badges são estáticos (atualizam em refresh)
- `asyncio.create_task()` + `register_task(session_id, task)` — padrão de background tasks
- Repositório com `db_path` como argumento — manter em qualquer nova função

### Integration Points

- `mis/search_orchestrator.py:run_manual_search()` → adicionar chamada a `run_spy_batch()` ao final
- `mis/search_repository.py` → novos status 'spying' e 'spy_done' na migration ou validação
- `mis/web/routes/search.py:GET /search/{id}/results` → trigger de re-spy para top 5 sem dossier
- `mis/web/templates/search_results_table.html` → nova coluna Dossiê com query param `?from_search=`
- `mis/web/routes/dossier.py` → aceitar `?from_search` e construir link de retorno
- `mis/web/templates/dossier.html` → nova tab Oferta + link dinâmico no header

</code_context>

<deferred>
## Deferred Ideas

- Polling ao vivo dos badges de dossier na tabela de resultados — backlog v3.0
- Contagem de progresso no banner "Espionando X de Y prontos" — backlog
- Re-spy forçado (force=True) a partir da UI — backlog
- Timeout global do spy batch por sessão — backlog
- Startup hook para marcar dossiers 'running' como 'failed' na reinicialização — backlog v3.1
- Exportação PDF do dossiê — Phase 26

</deferred>

---

*Phase: 22-spy-wiring*
*Context gathered: 2026-03-19*
