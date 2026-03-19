---
phase: 21-manual-search-engine
plan: 03
subsystem: search-frontend
tags: [htmx, fastapi, jinja2, polling, templates, dark-theme]

requires:
  - phase: 21-manual-search-engine
    plan: 02
    provides: search_repository, search_orchestrator, app.py start_scheduler param

provides:
  - mis/web/routes/search.py with 8 routes for manual search UI
  - 6 Jinja2 templates (pesquisar, status, results + partials)
  - base.html updated with 4th navbar item Buscar + toast handler
  - app.py lifespan teardown cancels pending search tasks

affects: []

tech-stack:
  added: []
  patterns:
    - "HTMX polling: hx-trigger='every 2s' in search_status_poll.html partial"
    - "HX-Redirect header in status/poll route triggers browser redirect on scan completion"
    - "HX-Trigger showToast header in DELETE route triggers JS toast via custom event"
    - "asyncio.create_task() for non-blocking scan launch; lifespan teardown cancels tasks"
    - "Platform country badge via Jinja2 dict lookup (PLATFORM_FLAGS in results_table)"

key-files:
  created:
    - mis/web/routes/search.py
    - mis/web/templates/pesquisar.html
    - mis/web/templates/pesquisar_recentes.html
    - mis/web/templates/search_status.html
    - mis/web/templates/search_status_poll.html
    - mis/web/templates/search_results.html
    - mis/web/templates/search_results_table.html
  modified:
    - mis/web/app.py
    - mis/web/templates/base.html

key-decisions:
  - "Template pesquisar.html created in Task 1 (alongside routes) because test_pesquisar_page_returns_200 requires it to pass — plan ordered routes before templates but tests needed template to exist"
  - "Lifespan teardown cancels _TASK_REGISTRY tasks — prevents TestClient timeout when test triggers POST /search/run which creates a real asyncio scan task"
  - "search_status_poll.html uses Jinja2 namespace(n=0) for counter inside loop — Jinja2 scoping requires namespace object for mutation inside for loops"

requirements-completed: [SEARCH-02]

duration: 18min
completed: 2026-03-19
---

# Phase 21 Plan 03: Manual Search Engine - Web Routes + Templates Summary

**FastAPI APIRouter with 8 search routes + 6 Jinja2 templates + navbar Buscar + toast — interface de pesquisa manual completa pronta para verificacao humana**

## Performance

- **Duration:** 18 min
- **Started:** 2026-03-18T23:50:24Z
- **Completed:** 2026-03-19T00:08:21Z
- **Tasks:** 2 (+ 1 checkpoint awaiting human verify)
- **Files modified:** 9

## Accomplishments

- `mis/web/routes/search.py`: APIRouter com 8 rotas seguindo padrao de ranking.py — GET /pesquisar (main page), GET /pesquisar/subniches (HTMX options partial), POST /search/run (cria sessao + asyncio.create_task), GET /search/{id}/status (redirect se done), GET /search/{id}/status/poll (HX-Redirect header ao concluir), GET /search/{id}/results (tabela + filtro plataforma), GET /search/{id}/results/table (partial sempre), DELETE /search/{id} (cancel + delete + HX-Trigger showToast)
- `mis/web/templates/pesquisar.html`: formulario com select Nicho (HTMX hx-get subniches) + select Subnicho (HTMX target) + botao Pesquisar (habilitado via JS no change do subnicho) + lista de recentes
- `mis/web/templates/pesquisar_recentes.html`: partial da lista de recentes com status badges + botao X (hx-delete)
- `mis/web/templates/search_status.html`: pagina de progresso com spinner animate-spin, timer JS setInterval, e include do partial de polling
- `mis/web/templates/search_status_poll.html`: partial com hx-trigger="every 2s" — lista plataformas com icones ✓/✗/◆ + progress bar
- `mis/web/templates/search_results.html`: pagina de resultados com breadcrumb, timestamp, cobertura, filtro dropdown HTMX, div#results-table incluindo partial
- `mis/web/templates/search_results_table.html`: tabela com colunas Pos/Produto/Plataforma/Preco+Comissao; badges de bandeira via dict PLATFORM_FLAGS; thumbnail opcional; estado vazio
- `mis/web/templates/base.html`: 4o item Buscar no navbar + div#toast com JS handler showToast (setTimeout 3s)
- `mis/web/app.py`: lifespan teardown cancela tasks do _TASK_REGISTRY antes de fechar

## Task Commits

1. **Task 1: Módulo de rotas search.py + wiring em app.py** - `e2733e7` (feat)
2. **Task 2: Templates HTMX + navbar + toast** - `3acbf59` (feat)

## Files Created/Modified

- `mis/web/routes/search.py` — APIRouter com 8 rotas (CRIADO)
- `mis/web/templates/pesquisar.html` — pagina principal de busca (CRIADO)
- `mis/web/templates/pesquisar_recentes.html` — partial de recentes (CRIADO)
- `mis/web/templates/search_status.html` — pagina de progresso (CRIADO)
- `mis/web/templates/search_status_poll.html` — partial de polling HTMX (CRIADO)
- `mis/web/templates/search_results.html` — pagina de resultados (CRIADO)
- `mis/web/templates/search_results_table.html` — partial de tabela de produtos (CRIADO)
- `mis/web/app.py` — include search_router + teardown cancel tasks (MODIFICADO)
- `mis/web/templates/base.html` — navbar Buscar + toast (MODIFICADO)

## Decisions Made

- Template pesquisar.html criado junto com as rotas (Task 1) porque o teste test_pesquisar_page_returns_200 requer o template para passar, mesmo que o plano separasse rotas e templates em tasks distintas.
- Lifespan teardown cancelamento de tasks: o TestClient aguarda o event loop limpar antes de fechar. Sem cancelamento, o POST /search/run cria uma task real de scan que fica presa na rede, causando timeout de 10s nos testes. Adicionar _TASK_REGISTRY cleanup no teardown resolve.
- Jinja2 namespace object para contador no loop de plataformas: Jinja2 nao permite mutacao de variaveis simples dentro de loops (scoping Python nao se aplica). namespace(n=0) e o padrao correto.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Template pesquisar.html criado em Task 1 em vez de Task 2**
- **Found during:** Task 1 — primeiro pytest run
- **Issue:** test_pesquisar_page_returns_200 requer template para retornar 200. O plano separava rotas (Task 1) e templates (Task 2), mas os testes de verificacao da Task 1 dependem do template.
- **Fix:** Criado pesquisar.html em Task 1 juntamente com as rotas. Task 2 criou os demais templates e atualizou pesquisar.html se necessario.
- **Files modified:** mis/web/templates/pesquisar.html
- **Commit:** e2733e7

**2. [Rule 2 - Missing critical functionality] Teardown de tasks asyncio no lifespan**
- **Found during:** Task 1 — timeout no TestClient ao rodar test_post_search_run_creates_session
- **Issue:** asyncio.create_task() dentro do route handler cria uma task real de scan. O TestClient tenta aguardar o event loop limpar no shutdown, causando timeout de 10s porque o scanner fica preso em conexoes de rede.
- **Fix:** Adicionado bloco de cancelamento de _TASK_REGISTRY no teardown do lifespan em app.py.
- **Files modified:** mis/web/app.py
- **Commit:** e2733e7

## Issues Encountered

Nenhum alem dos auto-fixados acima.

## User Setup Required

Checkpoint de verificacao visual — ver instrucoes abaixo.

## Checkpoint: Verificacao Visual Pendente

Para verificar a interface completa:

1. `cd C:/Users/Gabriel/MEGABRAIN && python -m mis.web`
2. Acessar http://localhost:8000/pesquisar
3. Selecionar nicho "Saude" — subnicho deve carregar via HTMX sem reload
4. Selecionar subnicho — botao Pesquisar deve ser habilitado
5. Clicar Pesquisar — redirect para /search/1/status com lista de plataformas e timer
6. Aguardar 2s — lista de plataformas deve atualizar (polling HTMX)
7. Aguardar conclusao — redirect automatico para /search/1/results
8. Confirmar produtos com badges de plataforma e bandeira de pais
9. Clicar "< Nova pesquisa" — retorno com nicho/subniche pre-populados
10. Clicar X em recente — toast "Pesquisa removida" deve aparecer
11. APScheduler NAO deve ter rodado scans automaticos

## Next Phase Readiness

- Todos os 26 testes web GREEN (incluindo 5 novos de test_web_search.py)
- Interface completa implementada e testada automaticamente
- Apos aprovacao do checkpoint, Phase 21 esta concluida

## Self-Check: PASSED

- FOUND: mis/web/routes/search.py
- FOUND: mis/web/templates/pesquisar.html
- FOUND: mis/web/templates/search_status.html
- FOUND: mis/web/templates/search_results.html
- FOUND commit: e2733e7 (Task 1)
- FOUND commit: 3acbf59 (Task 2)

---
*Phase: 21-manual-search-engine*
*Completed: 2026-03-19*
