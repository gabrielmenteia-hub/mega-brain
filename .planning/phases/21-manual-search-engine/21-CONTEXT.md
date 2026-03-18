# Phase 21: Manual Search Engine - Context

**Gathered:** 2026-03-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Usuário dispara pesquisa manual por subnicho e obtém produtos scaneados das plataformas, salvos no banco e consultáveis novamente sem re-scan. Zero automação de background — APScheduler não é iniciado. Espionagem automática dos resultados e favoritos pertencem a fases posteriores.

</domain>

<decisions>
## Implementation Decisions

### Scan Orchestrator
- Nova função `run_manual_search(subniche_id: int, db_path: str) -> search_id` — NÃO adapta `run_all_scanners()`
- Carrega slugs do banco via `get_platform_slug()` (niche_repository.py fase 20)
- Apenas plataformas com slug mapeado **E** que não são fallback-only (Eduzz/Monetizze/PerfectPay são excluídas automaticamente)
- Todas as plataformas elegíveis rodam em paralelo via `asyncio.gather` (mesmo padrão de `run_all_scanners`)
- PLAYWRIGHT_SEMAPHORE(3) já controla concorrência — não alterar
- Falha em uma plataforma não cancela as outras (resultado parcial + flag de erro por plataforma)
- Timeout global de **120s** por scan — ao expirar, cancela tasks pendentes e retorna o que foi coletado
- Produtos são persistidos via `product_repository.upsert_product()` — mesma tabela `products` do v2 (upsert por external_id+platform_id atualiza rank, preço, campos existentes)
- Endpoint: `POST /search/run` → retorna 202 com `search_id` imediatamente; scan roda como `asyncio.create_task()` no background
- Cancelamento disponível: `DELETE /search/{id}` — cancela asyncio.Task + marca sessão como `cancelled`
- Botão Pesquisar fica **desabilitado** se já há scan `running` para aquele subniche_id (previne duplos scans)
- Seleção obrigatória de **nicho → subnicho** (não é possível pesquisar pelo nicho inteiro)
- APScheduler **não é iniciado** quando o dashboard sobe — zero automação garantida por arquitetura (não apenas por disciplina de código)

### Persistência — Tabelas do Banco
- **Migration `_009_search_sessions.py`** (próxima na sequência após _008 de fase 20)
- Tabela `search_sessions`:
  ```
  id, subniche_id (FK → subniches), status (pending/running/done/timeout/cancelled),
  platform_statuses (JSON: {"hotmart": "done", "clickbank": "error"}),
  started_at, finished_at, product_count
  ```
- Tabela `search_session_products` (many-to-many):
  ```
  session_id (FK → search_sessions), product_id (FK → products),
  rank_at_scan (snapshot do rank no momento do scan), platform_slug
  ```
- Sessões com `status='running'` na startup do servidor são marcadas como `'timeout'` automaticamente (startup hook em `web/app.py` ou `__main__.py`)
- Sessões **não expiram** — ficam indefinidamente (cleanup em fase futura)
- Usuário **pode deletar** sessão: botão 'X' na lista de recentes → `DELETE /search/{id}` remove da `search_sessions` + `search_session_products` (mas não remove os `products` em si)
- Histórico: ambas as sessões ficam visíveis quando novo scan sobrescreve o mesmo subnicho (nova sessão é criada, antiga permanece)
- Sem coluna `notes` na tabela por agora

### Persistência — Acesso aos Dados
- Produtos do scan manual aparecem no `/ranking/unified` automaticamente (upsert na tabela `products` existente — sem coluna extra)
- `search_repository.py` — novo módulo com funções:
  - `list_recent_sessions(db_path, limit=10)` → 10 mais recentes, ordenadas por `started_at` DESC
  - `get_session(db_path, session_id)` → detalhes de uma sessão
  - `list_session_products(db_path, session_id, platform_filter, per_page, page)` → produtos com rank_at_scan + JOIN em products + platforms
  - `create_session(db_path, subniche_id)` → retorna search_id
  - `update_session_status(db_path, session_id, status, platform_statuses, product_count)`
  - `delete_session(db_path, session_id)`

### Rotas FastAPI
- **Módulo:** `mis/web/routes/search.py` (em inglês, como ranking.py/feed.py/alerts.py)
- **Rotas:**
  - `GET /pesquisar` — página principal de busca com formulário + lista de recentes
  - `GET /pesquisar/subniches` — partial HTMX: retorna `<option>` do select de subnicho dado `?niche_slug=`
  - `POST /search/run` — inicia scan, retorna 202 + redirect para `/search/{id}/status`
  - `GET /search/{id}/status` — página HTML completa de progresso (acessível direto pelo browser)
  - `GET /search/{id}/status/poll` — partial HTMX para polling (retorna JSON ou partial HTML)
  - `GET /search/{id}/results` — página de resultados da sessão
  - `GET /search/{id}/results/table` — partial HTMX para filtro de plataforma
  - `DELETE /search/{id}` — cancela ou deleta sessão; redireciona para `/pesquisar` com toast

### UI — Página de Busca (/pesquisar)
- **Navbar:** 4º item adicionado ao `base.html`: `Ranking | Feed de Dores | Alertas | **Buscar**`
- **Título:** "Pesquisar Produtos" (h1) + subtítulo "Selecione nicho e subnicho para buscar produtos nas plataformas"
- **Formulário:** `[Select Nicho] [Select Subnicho] [Pesquisar]` — mesma linha (barra de busca)
  - Primeiro nicho pré-selecionado por padrão
  - Select de Subnicho vazio/desabilitado até nicho ser escolhido — HTMX carrega via `GET /pesquisar/subniches?niche_slug=`
  - Botão Pesquisar desabilitado até subnicho ser selecionado
  - Aceita query params `?niche=saude&subniche=emagrecimento` para pré-popular selects (usado ao voltar de `/search/{id}/results`)
- **Lista de recentes:** abaixo do formulário, 10 mais recentes
  - Item: `Subnicho | N plataformas | N produtos | DD/MM HH:mm` + botão 'X' para deletar
  - Clicar no item navega para `/search/{id}/results`
- **Estado vazio:** "Nenhuma pesquisa realizada ainda. Selecione um subnicho e clique em Pesquisar."

### UI — Página de Progresso (/search/{id}/status)
- Acessível diretamente pelo browser (GET retorna página HTML completa — não apenas partial)
- Se scan já concluiu ao acessar: redirect 302 para `/search/{id}/results` (não entra no histórico do browser)
- **Header:** "Buscando: [Subnicho] ([Nicho])" com spinner
- **Progress bar:** "N de M plataformas concluídas" com barra visual
- **Timer:** "Tempo: 0:23 / 2:00" (elapsed / timeout de 120s)
- **Lista de plataformas:** status individual por plataforma:
  - `◆ scanning...` → em andamento
  - `✓ Hotmart — 12 produtos` → concluído
  - `✗ Kiwify — erro (0 produtos)` + badge/tooltip com mensagem do erro → falha
  - Plataformas fallback-only (Eduzz/Monetizze/PerfectPay) **ocultadas** da lista
- **Polling:** `hx-trigger="every 2s"` no partial — HTMX polling padrão
- **Botão Cancelar:** cancela imediatamente sem confirmação → redirect para `/pesquisar` com toast
- **Timeout:** ao expirar, banner "Timeout (120s). Exibindo resultados parciais." + redirect para `/search/{id}/results`

### UI — Página de Resultados (/search/{id}/results)
- **Breadcrumb/link:** "< Nova pesquisa" no topo → `/pesquisar?niche=...&subniche=...`
- **Botão "Atualizar":** `POST /search/run` com mesmo subniche_id → redireciona para nova `/search/{id}/status`
- **Timestamp:** "Resultados de DD/MM/YYYY HH:mm" no topo
- **Banner stale:** banner amarelo "Dados de DD/MM/YYYY — considere atualizar" se scan > 7 dias
- **Banner de cobertura:** "N de M plataformas retornaram produtos. X com erro." no topo dos resultados
- **Tabela de produtos:** mesmo padrão do `/ranking` — colunas: posição, produto (título + link dossier), plataforma (badge com flag de país), preço/comissão, badge 'Pendente' se sem dossier
  - País inferido da plataforma: badge `[H] Hotmart 🇧🇷` (BR), `[CB] ClickBank 🇺🇸` (US/Global) — sem coluna separada
  - Ordenação: `rank_at_scan ASC` dentro de cada grupo de plataforma (padrão)
- **Filtro:** dropdown de plataforma no topo — HTMX recarrega partial `/search/{id}/results/table`
- **Paginação:** 10/20/50 por página — mesmo padrão do `/ranking`
- **Link de dossier:** badge 'Pendente' (amarelo) para produtos sem dossier — mesmo padrão do `/ranking`

### Templates
- `pesquisar.html` — página de busca completa
- `pesquisar_recentes.html` — partial HTMX para lista de recentes (atualiza após scan concluir)
- `search_status.html` — página de progresso
- `search_status_poll.html` — partial HTMX para polling de status
- `search_results.html` — página de resultados
- `search_results_table.html` — partial HTMX para filtro de plataforma nos resultados

### Toasts
- Implementação: `HX-Trigger` header + `div#toast` em `base.html` com HTMX out-of-band swap (zero JavaScript manual)
- Mensagens: "Pesquisa removida", "Scan cancelado"

### Claude's Discretion
- Estrutura interna do asyncio.Task (como armazenar referência para cancelamento)
- Exata formatação dos badges de plataforma/país
- Espaçamento e tipografia das páginas
- Implementação do atributo `disabled` no botão Pesquisar (JavaScript inline vs hx-swap)
- Estrutura interna do módulo `search_repository.py`
- Timeout do asyncio por plataforma individual (vs timeout global)

</decisions>

<specifics>
## Specific Ideas

- Fluxo: `/pesquisar` → POST → redirect para `/search/{id}/status` (progresso) → auto-redirect 302 para `/search/{id}/results` ao concluir
- Timer na página de progresso mostra "Tempo: 0:23 / 2:00" — dá clareza sobre quando timeout ocorre
- "Buscando: Emagrecimento (Saúde)" como título da página de status — contexto imediato
- Lista de recentes: "Subnicho | 5 plataformas | 47 produtos | 17/03 22:00" — informativo e conciso
- Botão 'Atualizar' na página de resultados dispara novo scan sem ter que voltar ao formulário

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `mis/niche_repository.py` (fase 20): `list_niches()`, `list_subniches()`, `get_platform_slug()` — exatamente o que run_manual_search() e o formulário precisam
- `mis/product_repository.py`: `upsert_product()` — reaproveitado diretamente para persistir produtos do scan manual
- `mis/web/templates/base.html` — navbar a ser atualizado com 4º item "Buscar"
- `mis/web/templates/ranking.html` + `ranking_table.html` — padrão de tabela + partial HTMX a ser seguido
- `mis/web/templates/alerts_badge.html` — exemplo de polling HTMX no dashboard existente
- `mis/web/routes/ranking.py` — padrão `is_htmx()` + `_get_ranking_context()` + partial route a ser replicado em search.py
- `mis/scanner.py`: `PlatformScanner` ABC, `SCANNER_MAP` e `asyncio.gather` pattern — base para run_manual_search()
- `mis/db.py`: `get_db()`, `run_migrations()` — padrão de conexão SQLite

### Established Patterns
- HTMX: `hx-get`, `hx-target`, `hx-include`, `hx-trigger="every Ns"` para polling — já em uso
- Dark theme: `bg-gray-800`, `text-gray-200`, `border-gray-700`, `text-blue-400` para links
- Badge inline: `<span class="bg-yellow-600 text-xs px-1 rounded ml-1">Pendente</span>` — adaptar para status de plataforma
- Repositório pattern: módulo separado, funções puras com `db_path` como argumento — seguir em `search_repository.py`
- Migrations: `_00N_nome.py` com função `run_00N()` registrada em `db.py:run_migrations()`

### Integration Points
- `mis/web/app.py` (ou equivalente): registrar `router` de `search.py` + startup hook para marcar sessions 'running' como 'timeout'
- `mis/db.py:run_migrations()` — adicionar chamada para `_run_009` da nova migration
- `mis/web/templates/base.html` — adicionar link "Buscar" no navbar
- `mis/scheduler.py` — NÃO deve ser iniciado no startup do dashboard v3.0
- `mis/web/routes/ranking_tabs.html` (template de tabs existente) — pode ser referência para estrutura de página

</code_context>

<deferred>
## Deferred Ideas

- Espionagem automática dos produtos da pesquisa (top N por plataforma) — Phase 22
- Link para dossier completo na página de resultados — Phase 22 (quando spy-v3 estiver disponível)
- Notas/anotações por sessão de pesquisa — backlog v3.0
- Limpeza automática de sessões antigas — backlog v3.0
- Histórico de posição de produtos por sessão (gráfico de evolução) — Phase 24/backlog
- "Modo verboso" com logs do scan em tempo real na UI — backlog
- Estimativa de tempo restante baseada em histórico de scans — backlog
- Pesquisa por nicho inteiro (varrer todos os subnichos) — backlog v3.0
- Sessões compartilháveis por URL — backlog

</deferred>

---

*Phase: 21-manual-search-engine*
*Context gathered: 2026-03-18*
