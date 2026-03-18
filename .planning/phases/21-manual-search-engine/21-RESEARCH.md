# Phase 21: Manual Search Engine - Research

**Researched:** 2026-03-18
**Domain:** FastAPI background tasks, HTMX polling, SQLite migrations, asyncio scan orchestration
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Scan Orchestrator**
- Nova função `run_manual_search(subniche_id: int, db_path: str) -> search_id` — NÃO adapta `run_all_scanners()`
- Carrega slugs do banco via `get_platform_slug()` (niche_repository.py fase 20)
- Apenas plataformas com slug mapeado **E** que não são fallback-only (Eduzz/Monetizze/PerfectPay excluídas automaticamente — `get_platform_slug()` retorna `None` para elas)
- Todas as plataformas elegíveis rodam em paralelo via `asyncio.gather` (mesmo padrão de `run_all_scanners`)
- `PLAYWRIGHT_SEMAPHORE(3)` já controla concorrência — não alterar
- Falha em uma plataforma não cancela as outras (resultado parcial + flag de erro por plataforma)
- Timeout global de **120s** por scan — ao expirar, cancela tasks pendentes e retorna o que foi coletado
- Produtos persistidos via `product_repository.upsert_product()` — mesma tabela `products` do v2
- Endpoint: `POST /search/run` → retorna 202 com `search_id` imediatamente; scan roda como `asyncio.create_task()` no background
- Cancelamento: `DELETE /search/{id}` — cancela `asyncio.Task` + marca sessão como `cancelled`
- Botão Pesquisar **desabilitado** se já há scan `running` para aquele `subniche_id`
- Seleção obrigatória de **nicho → subnicho** (não é possível pesquisar pelo nicho inteiro)
- APScheduler **não é iniciado** quando o dashboard v3.0 sobe — zero automação

**Persistência — Tabelas do Banco**
- Migration `_009_search_sessions.py` (próxima na sequência após _008)
- Tabela `search_sessions`: `id, subniche_id (FK → subniches), status (pending/running/done/timeout/cancelled), platform_statuses (JSON), started_at, finished_at, product_count`
- Tabela `search_session_products` (many-to-many): `session_id (FK → search_sessions), product_id (FK → products), rank_at_scan, platform_slug`
- Sessões com `status='running'` na startup são marcadas como `'timeout'` automaticamente
- Sessões não expiram — ficam indefinidamente
- `DELETE /search/{id}` remove `search_sessions` + `search_session_products` (não remove `products`)

**Persistência — Acesso aos Dados**
- `search_repository.py` — novo módulo com: `list_recent_sessions`, `get_session`, `list_session_products`, `create_session`, `update_session_status`, `delete_session`

**Rotas FastAPI**
- Módulo: `mis/web/routes/search.py`
- `GET /pesquisar` — página principal
- `GET /pesquisar/subniches` — partial HTMX: `<option>` dado `?niche_slug=`
- `POST /search/run` → 202 + redirect para `/search/{id}/status`
- `GET /search/{id}/status` — página HTML completa de progresso
- `GET /search/{id}/status/poll` — partial HTMX polling
- `GET /search/{id}/results` — página de resultados
- `GET /search/{id}/results/table` — partial HTMX para filtro
- `DELETE /search/{id}` — cancela ou deleta; redireciona para `/pesquisar` com toast

**UI**
- Navbar: 4º item adicionado ao `base.html`: "Buscar"
- Templates: `pesquisar.html`, `pesquisar_recentes.html`, `search_status.html`, `search_status_poll.html`, `search_results.html`, `search_results_table.html`
- Toasts: `HX-Trigger` header + `div#toast` em `base.html` com HTMX out-of-band swap
- HTMX polling: `hx-trigger="every 2s"` no partial de status

### Claude's Discretion
- Estrutura interna do `asyncio.Task` (como armazenar referência para cancelamento)
- Exata formatação dos badges de plataforma/país
- Espaçamento e tipografia das páginas
- Implementação do atributo `disabled` no botão Pesquisar (JavaScript inline vs hx-swap)
- Estrutura interna do módulo `search_repository.py`
- Timeout do asyncio por plataforma individual (vs timeout global)

### Deferred Ideas (OUT OF SCOPE)
- Espionagem automática dos produtos da pesquisa — Phase 22
- Link para dossier completo — Phase 22
- Notas/anotações por sessão — backlog v3.0
- Limpeza automática de sessões antigas — backlog v3.0
- Histórico de posição de produtos por sessão (gráfico) — Phase 24/backlog
- "Modo verboso" com logs em tempo real na UI — backlog
- Estimativa de tempo restante baseada em histórico — backlog
- Pesquisa por nicho inteiro — backlog v3.0
- Sessões compartilháveis por URL — backlog
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SEARCH-01 | Usuário seleciona nicho → subnicho → clica "Pesquisar" para iniciar scan sob demanda | Formulário hierárquico HTMX, POST /search/run → asyncio.create_task, search_repository.create_session |
| SEARCH-02 | Resultado exibe produtos agrupados por plataforma e país de origem (BR / US / Global) | search_results.html com agrupamento, badge plataforma+bandeira, list_session_products com platform_slug |
| SEARCH-03 | Zero automação — nenhum scan roda sem ação explícita do usuário | APScheduler não é iniciado no lifespan v3.0; run_manual_search() só chamada via POST /search/run |
</phase_requirements>

---

## Summary

Esta fase implementa o núcleo do v3.0: um motor de pesquisa manual onde o usuário dispara scans por subnicho via formulário web e obtém resultados persistidos no banco. A arquitetura tem três camadas: (1) orquestrador assíncrono `run_manual_search()` que usa o padrão existente `asyncio.gather + SCANNER_MAP` mas lê slugs do banco v3 em vez de `config.yaml`; (2) repositório `search_repository.py` para gerenciar sessões e produtos linkados; (3) interface HTMX com polling a cada 2s para progresso e páginas de resultado reutilizando os padrões de `ranking.py`.

O ponto crítico de arquitetura é a supressão do APScheduler: o lifespan atual em `web/app.py` inicia o scheduler incondicionalmente. A versão v3.0 precisa de uma variante de `create_app()` que não registre nem inicie o scheduler — garantindo SEARCH-03 por arquitetura, não por disciplina.

O segundo ponto crítico é o gerenciamento da referência `asyncio.Task` para cancelamento. `asyncio.create_task()` retorna um objeto Task que precisa ser armazenado em algum estado global (dict em memória) para que `DELETE /search/{id}` possa chamá-lo. Esse dicionário vive apenas em memória — um restart do servidor perde tasks rodando, o que é tratado pelo startup hook que marca sessões `running` como `timeout`.

**Primary recommendation:** Implementar em TDD RED/GREEN. Plan 21-01 escreve testes RED para migration _009, search_repository e run_manual_search. Plan 21-02 implementa. Plan 21-03 implementa rotas + templates.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | já instalado | APIRouter, Request, Response, BackgroundTasks | Framework web do projeto |
| sqlite-utils | já instalado | DDL idempotente, queries, insert/upsert | Padrão de todas as migrations |
| HTMX | 2.0.8 (CDN no base.html) | Polling, swaps parciais, out-of-band | Já em uso em alerts, ranking |
| asyncio | stdlib Python | gather, create_task, wait_for, CancelledError | Padrão do scanner existente |
| structlog | já instalado | Logging estruturado | Padrão do projeto |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| fastapi.testclient | já instalado | TestClient síncrono para rotas | Todos os testes de rota web |
| pytest + tmp_path | já instalado | Fixtures de DB efêmero | Padrão de todos os testes |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| asyncio.create_task | FastAPI BackgroundTasks | BackgroundTasks não retorna referência para cancelamento — não serve |
| Dict em memória para tasks | Redis/estado persistido | Overkill — restart marca como timeout via startup hook |
| HTMX polling | WebSockets | Polling a 2s é mais simples; sem dependência de WS; padrão já em uso |

**Installation:** Nenhum pacote novo necessário — tudo já instalado.

---

## Architecture Patterns

### Recommended Project Structure

```
mis/
├── migrations/
│   └── _009_search_sessions.py    # nova migration
├── search_repository.py           # novo módulo (padrão niche_repository.py)
├── search_orchestrator.py         # run_manual_search() + _TASK_REGISTRY
├── web/
│   ├── routes/
│   │   └── search.py              # novo router (padrão ranking.py)
│   └── templates/
│       ├── pesquisar.html
│       ├── pesquisar_recentes.html
│       ├── search_status.html
│       ├── search_status_poll.html
│       ├── search_results.html
│       └── search_results_table.html
└── tests/
    ├── test_search_repository.py  # testes RED plan 21-01
    ├── test_search_orchestrator.py
    └── web/
        └── test_web_search.py     # testes de rota
```

### Pattern 1: asyncio.create_task com registry para cancelamento

**What:** `POST /search/run` cria uma sessão no banco, lança `asyncio.create_task(run_manual_search(...))` e armazena a referência em `_TASK_REGISTRY: dict[int, asyncio.Task]`. `DELETE /search/{id}` chama `task.cancel()` e marca sessão como `cancelled`.

**When to use:** Sempre que a rota precisa retornar 202 imediatamente enquanto o scan roda em background e o cancelamento precisa ser possível.

**Example:**
```python
# mis/search_orchestrator.py
import asyncio
from typing import Optional

_TASK_REGISTRY: dict[int, asyncio.Task] = {}

def register_task(session_id: int, task: asyncio.Task) -> None:
    _TASK_REGISTRY[session_id] = task

def cancel_task(session_id: int) -> bool:
    task = _TASK_REGISTRY.pop(session_id, None)
    if task and not task.done():
        task.cancel()
        return True
    return False
```

```python
# mis/web/routes/search.py — POST /search/run
@router.post("/search/run")
async def run_search(request: Request, subniche_id: int = Form(...)):
    db_path = request.app.state.db_path
    session_id = search_repository.create_session(db_path, subniche_id)
    task = asyncio.create_task(
        run_manual_search(session_id, subniche_id, db_path)
    )
    register_task(session_id, task)
    return RedirectResponse(url=f"/search/{session_id}/status", status_code=302)
```

### Pattern 2: HTMX Polling com redirect automático ao concluir

**What:** `search_status_poll.html` é retornado por `GET /search/{id}/status/poll` com `hx-trigger="every 2s"`. Quando o scan conclui, o partial retorna `HX-Redirect` header → HTMX redireciona a página inteira para `/search/{id}/results`.

**When to use:** Quando o usuário precisa aguardar uma operação assíncrona com feedback visual de progresso.

**Example:**
```python
# mis/web/routes/search.py — GET /search/{id}/status/poll
@router.get("/search/{session_id}/status/poll")
async def search_status_poll(request: Request, session_id: int):
    db_path = request.app.state.db_path
    session = search_repository.get_session(db_path, session_id)
    if session["status"] in ("done", "timeout"):
        # Redirecionar via HX-Redirect header
        from fastapi.responses import HTMLResponse
        resp = request.app.state.templates.TemplateResponse(
            request=request,
            name="search_status_poll.html",
            context={"session": session},
        )
        resp.headers["HX-Redirect"] = f"/search/{session_id}/results"
        return resp
    return request.app.state.templates.TemplateResponse(
        request=request,
        name="search_status_poll.html",
        context={"session": session},
    )
```

### Pattern 3: Migration _009 seguindo padrão _008

**What:** Arquivo `_009_search_sessions.py` com função `run_migration_009(db_path)`, idempotente via `IF NOT EXISTS` e COUNT check. Registrado em `db.py:run_migrations()`.

**Example:**
```python
# mis/migrations/_009_search_sessions.py
import sqlite_utils

def run_migration_009(db_path: str) -> None:
    db = sqlite_utils.Database(db_path)
    db.execute("PRAGMA foreign_keys=ON")
    table_names = db.table_names()

    if "search_sessions" not in table_names:
        db.execute("""
            CREATE TABLE search_sessions (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                subniche_id      INTEGER NOT NULL REFERENCES subniches(id),
                status           TEXT    NOT NULL DEFAULT 'pending',
                platform_statuses TEXT,
                started_at       TEXT,
                finished_at      TEXT,
                product_count    INTEGER DEFAULT 0
            )
        """)

    if "search_session_products" not in table_names:
        db.execute("""
            CREATE TABLE search_session_products (
                session_id   INTEGER NOT NULL REFERENCES search_sessions(id) ON DELETE CASCADE,
                product_id   INTEGER NOT NULL REFERENCES products(id),
                rank_at_scan INTEGER,
                platform_slug TEXT,
                PRIMARY KEY (session_id, product_id)
            )
        """)

    db.conn.commit()
```

### Pattern 4: APScheduler suprimido no lifespan v3.0

**What:** O lifespan atual em `web/app.py` sempre inicia o scheduler. Para v3.0, o lifespan precisa ser alterado para NÃO registrar nem iniciar `register_scan_and_spy_job`. As opções são: (a) adicionar parâmetro `start_scheduler: bool = True` a `create_app()`; ou (b) criar lifespan condicional via variável de ambiente `MIS_NO_SCHEDULER=1`. A opção (a) é mais limpa e testável.

**Example:**
```python
# mis/web/app.py — create_app com parâmetro opcional
def create_app(db_path: str, start_scheduler: bool = True) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if start_scheduler:
            # ... registro de jobs e start_scheduler()
            pass
        # startup hook v3.0: marcar sessions running como timeout
        _mark_stale_sessions(db_path)
        yield
        if start_scheduler:
            get_scheduler().shutdown(wait=False)
    ...
```

### Pattern 5: run_manual_search — diferenças em relação a run_all_scanners

**What:** `run_all_scanners()` lê slugs do `config.yaml` e itera por nicho+plataforma. `run_manual_search()` consulta `get_platform_slug()` para cada plataforma do `SCANNER_MAP` dado um `subniche_id`, filtrando `None` automaticamente (exclui Eduzz/Monetizze/PerfectPay). Timeout 120s via `asyncio.wait_for()`.

**Example:**
```python
# mis/search_orchestrator.py
FALLBACK_PLATFORM_IDS = {4, 5, 6}  # Eduzz, Monetizze, PerfectPay

async def run_manual_search(session_id: int, subniche_id: int, db_path: str) -> None:
    from mis.niche_repository import get_platform_slug
    from mis.db import get_db
    import json

    db = get_db(db_path)
    search_repository.update_session_status(db_path, session_id, "running", {}, 0)

    platform_tasks = {}
    for platform_slug, scanner_cls in SCANNER_MAP.items():
        slug = get_platform_slug(db_path, subniche_id, platform_slug)
        if slug is None:
            continue  # fallback-only ou sem mapeamento — skip automático
        platform_tasks[platform_slug] = (scanner_cls, slug)

    async def _scan_one(platform_slug, scanner_cls, search_slug):
        async with scanner_cls() as scanner:
            return await scanner.scan_niche(search_slug, search_slug)

    # asyncio.gather com timeout global
    try:
        results = await asyncio.wait_for(
            asyncio.gather(
                *[_scan_one(ps, sc, sl) for ps, (sc, sl) in platform_tasks.items()],
                return_exceptions=True,
            ),
            timeout=120.0,
        )
    except asyncio.TimeoutError:
        # Marcar como timeout — salvar o que foi coletado
        search_repository.update_session_status(db_path, session_id, "timeout", ...)
        return

    # Persistir produtos e preencher search_session_products
    ...
    search_repository.update_session_status(db_path, session_id, "done", ...)
```

### Anti-Patterns to Avoid

- **Usar BackgroundTasks do FastAPI:** Não retorna referência para cancelamento. `asyncio.create_task()` é obrigatório.
- **Persistir referência asyncio.Task em banco:** Tasks são objetos Python em memória — não serializáveis. Usar registry em memória.
- **Chamar `asyncio.wait_for()` com tasks individuais antes do gather:** O timeout precisa envolver o `gather` inteiro para garantir que seja um timeout global de 120s, não por plataforma.
- **Iniciar APScheduler no lifespan v3.0:** Viola SEARCH-03. Verificar `start_scheduler` parameter ou equivalente.
- **Usar `asyncio.gather(*coroutines)` sem `return_exceptions=True`:** Uma plataforma com erro cancelaria todas as outras.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| HTMX polling de status | JavaScript fetch loop customizado | `hx-trigger="every 2s"` no partial | Já em uso em `alerts_badge.html` — testado, zero JS manual |
| Redirect ao concluir scan | JavaScript `window.location` | `HX-Redirect` header no response | HTMX suporta nativamente, sem JS |
| Upsert de produto | INSERT ON CONFLICT custom | `product_repository.upsert_product(db, product)` | Já implementado, handles UPDATE-then-INSERT |
| Slugs por plataforma | Dicionário hardcoded no orchestrator | `niche_repository.get_platform_slug(db_path, subniche_id, platform_slug)` | Fonte de verdade já no banco (migration _008) |
| Exclusão de fallback platforms | Verificação manual de IDs 4,5,6 | `get_platform_slug()` retorna `None` para Eduzz/Monetizze/PerfectPay | Já modelado na migration _008 — não adiciona mapeamento para essas plataformas |
| Toast notifications | JavaScript alert/snackbar manual | `HX-Trigger` header + `div#toast` em `base.html` com `hx-swap-oob` | Zero JS manual — HTMX out-of-band swap |

**Key insight:** O scanner existente (`run_all_scanners`) já resolve os problemas de concorrência, rate limiting e tratamento de erros por plataforma. `run_manual_search` é uma adaptação do mesmo padrão com fonte de dados diferente (banco v3 em vez de `config.yaml`).

---

## Common Pitfalls

### Pitfall 1: asyncio.Task perdida após restart — startup hook obrigatório
**What goes wrong:** Server reinicia enquanto scan está `running`. O Task registry é perdido. A sessão fica eternamente em status `running`.
**Why it happens:** Tasks asyncio vivem apenas em memória; banco persiste o status `running` mas não há Task para executar.
**How to avoid:** Startup hook no lifespan que executa `UPDATE search_sessions SET status='timeout' WHERE status='running'` antes de `yield`. Deve rodar mesmo quando `start_scheduler=False`.
**Warning signs:** GET /search/{id}/status mostra `running` mas nenhuma task existe para o scan.

### Pitfall 2: asyncio.wait_for cancela tasks filhas mas gather não propaga CancelledError corretamente
**What goes wrong:** `asyncio.wait_for(asyncio.gather(...))` ao atingir timeout lança `asyncio.TimeoutError` no chamador, mas as coroutines internas continuam executando até o próximo ponto de await.
**Why it happens:** `asyncio.gather` com `return_exceptions=True` captura `CancelledError` internamente — o cancel precisa ser explícito.
**How to avoid:** Usar `asyncio.wait_for` sem `return_exceptions=True` no gather quando timeout é crítico, OU criar tasks explícitas e cancelá-las via `task.cancel()` no bloco `except asyncio.TimeoutError`.
**Warning signs:** Scan marcado como `timeout` mas scanners Playwright continuam abrindo browsers por até 30s depois.

### Pitfall 3: POST /search/run cria sessão duplicada se clicado rapidamente
**What goes wrong:** Usuário clica "Pesquisar" duas vezes antes do redirect. Dois scans do mesmo subnicho rodam simultaneamente.
**Why it happens:** POST endpoint não verifica se já há scan `running` para o subnicho.
**How to avoid:** No endpoint `POST /search/run`, verificar `list_recent_sessions` ou `get_session` por `subniche_id` com `status='running'`. Se existir, redirecionar para a sessão existente. Botão desabilitado no front não é suficiente (requisição direta burla o frontend).
**Warning signs:** Duas sessões na lista de recentes com mesmo subnicho em status `running` ao mesmo tempo.

### Pitfall 4: `platform_statuses` JSON — serialização manual necessária
**What goes wrong:** `platform_statuses` é armazenado como TEXT (JSON) no SQLite via sqlite-utils. Ao ler, retorna string — não dict. Template recebe string em vez de dict e quebra.
**Why it happens:** SQLite não tem tipo JSON nativo. sqlite-utils armazena TEXT.
**How to avoid:** `search_repository.get_session()` deve fazer `import json; row['platform_statuses'] = json.loads(row['platform_statuses'] or '{}')` antes de retornar.
**Warning signs:** `{{ session.platform_statuses.hotmart }}` no template retorna AttributeError ou string bruta.

### Pitfall 5: ON DELETE CASCADE em search_session_products não está ativo por padrão
**What goes wrong:** `DELETE /search/{id}` remove `search_sessions` mas `search_session_products` fica órfão.
**Why it happens:** SQLite tem foreign key enforcement OFF por padrão. `ON DELETE CASCADE` só funciona se `PRAGMA foreign_keys=ON` foi executado na conexão atual.
**How to avoid:** `get_db()` já executa `PRAGMA foreign_keys=ON` — usar sempre `get_db()` para operações de delete. `delete_session()` em `search_repository` deve usar `get_db()`, não `sqlite_utils.Database()` diretamente (que não executa os PRAGMAs).
**Warning signs:** Registros órfãos em `search_session_products` após delete de sessão.

### Pitfall 6: niche_id na tabela products — scan manual usa niches_v3 mas products usa niches legada
**What goes wrong:** `upsert_product()` recebe um `Product` dataclass com `niche_id`. Os scanners existentes esperam um `niche_id` da tabela `niches` (legada). A fase 20 criou `niches_v3` separada. Se `run_manual_search` passa `niche_id` de `subniches.niche_id` (FK para `niches_v3`), mas os produtos existentes usam FK para `niches` (legada), há incompatibilidade.
**Why it happens:** Duas tabelas de nichos coexistem: `niches` (legada, v1/v2) e `niches_v3` (v3). `products.niche_id` é FK para `niches`.
**How to avoid:** Ao construir o `Product` dataclass em `run_manual_search`, resolver o `niche_id` correto da tabela `niches` legada. A migration _008 não toca a tabela `niches` — verificar que existe um niche correspondente em `niches` para cada niche em `niches_v3`. Alternativa: usar `niche_id=1` (primeiro nicho disponível) como fallback se mapeamento não existir — com log de aviso.
**Warning signs:** IntegrityError FK ao fazer `upsert_product()` com `niche_id` de `niches_v3`.

---

## Code Examples

Verified patterns from codebase:

### SCANNER_MAP com fallback automático via get_platform_slug
```python
# Baseado em scanner.py SCANNER_MAP — adaptar em search_orchestrator.py
SCANNER_MAP = {
    "kiwify":        KiwifyScanner,
    "hotmart":       HotmartScanner,
    "clickbank":     ClickBankScanner,
    "braip":         BraipScanner,
    "product_hunt":  ProductHuntScanner,
    "udemy":         UdemyScanner,
    "jvzoo":         JVZooScanner,
    "gumroad":       GumroadScanner,
    "appsumo":       AppSumoScanner,
    # Eduzz (4), Monetizze (5), PerfectPay (6) EXCLUÍDOS:
    # get_platform_slug() retorna None para eles (sem mapeamento em _008)
}
```

### Polling HTMX — padrão idêntico ao alerts_badge.html
```html
<!-- search_status_poll.html — PARTIAL sem extends base.html -->
<div id="search-status-poll"
     hx-get="/search/{{ session.id }}/status/poll"
     hx-trigger="every 2s"
     hx-swap="outerHTML">
  <!-- conteúdo de progresso aqui -->
</div>
```

### Registro de router no create_app
```python
# mis/web/app.py — adicionar após imports existentes
from mis.web.routes.search import router as search_router
# ...
app.include_router(search_router)
```

### Migration _009 registrada em db.py
```python
# mis/db.py — adicionar import e chamada
from .migrations._009_search_sessions import run_migration_009 as _run_009

def run_migrations(db_path: str) -> None:
    _run_001(db_path)
    # ... _002 a _008 ...
    _run_009(db_path)
```

### Teste de rota — padrão app_client fixture existente
```python
# mis/tests/web/test_web_search.py
def test_pesquisar_page_returns_200(app_client):
    response = app_client.get("/pesquisar")
    assert response.status_code == 200
    assert "Pesquisar" in response.text

def test_post_search_run_returns_302(app_client, db_path):
    from mis.db import run_migrations
    from mis.niche_repository import list_subniches
    run_migrations(db_path)
    subniches = list_subniches(db_path, "saude")
    subniche_id = subniches[0]["id"]
    response = app_client.post("/search/run", data={"subniche_id": subniche_id},
                               follow_redirects=False)
    assert response.status_code in (302, 303)
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| APScheduler lança scans automáticos | Scans apenas por ação explícita do usuário | v3.0 (esta fase) | `register_scan_and_spy_job` não deve ser registrado no lifespan v3.0 |
| Slugs de nicho em `config.yaml` | Slugs em banco via `niches_v3 + subniche_platform_slugs` (migration _008) | Phase 20 | `run_manual_search` lê banco via `get_platform_slug()`, não config.yaml |
| `run_all_scanners(config)` para scans | `run_manual_search(session_id, subniche_id, db_path)` | Esta fase | Função dedicada, não adaptação |

---

## Open Questions

1. **niche_id legado vs niches_v3 em products.niche_id**
   - What we know: `products.niche_id` é FK para tabela `niches` (legada, v1/v2). `niches_v3` é separada.
   - What's unclear: Existe mapeamento entre `niches_v3.id` e `niches.id`? (Ambas têm IDs 1-4 para os mesmos nichos? Provavelmente sim por coincidência.)
   - Recommendation: Verificar durante implementação. Se IDs coincidem (niches_v3.id=1 == niches.id=1), usar diretamente. Se não, criar função helper para mapear. Documentar no código.

2. **Comportamento do timeout quando PLAYWRIGHT_SEMAPHORE está saturado**
   - What we know: `PLAYWRIGHT_SEMAPHORE(3)` é global e pode estar retendo outros scans. `asyncio.wait_for(120s)` inclui o tempo de espera pelo semáforo.
   - What's unclear: Se 3 scans manuais paralelos (impossível pela UI mas possível via API) disputam o semáforo, o timeout pode ocorrer antes de qualquer scan completar.
   - Recommendation: Documentar no código que o timeout de 120s inclui espera por semáforo. Não alterar o semáforo.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (já instalado) |
| Config file | `mis/pytest.ini` ou `pyproject.toml` — verificar localização |
| Quick run command | `cd C:/Users/Gabriel/MEGABRAIN && python -m pytest mis/tests/test_search_repository.py -x -q` |
| Full suite command | `cd C:/Users/Gabriel/MEGABRAIN && python -m pytest mis/tests/ -x -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SEARCH-01 | Formulário nicho→subnicho dispara POST /search/run que cria sessão e inicia scan | integration | `pytest mis/tests/web/test_web_search.py::test_post_search_run_creates_session -x` | ❌ Wave 0 |
| SEARCH-01 | list_recent_sessions retorna sessão criada | unit | `pytest mis/tests/test_search_repository.py::test_create_and_list_session -x` | ❌ Wave 0 |
| SEARCH-02 | list_session_products retorna produtos com platform_slug e rank_at_scan | unit | `pytest mis/tests/test_search_repository.py::test_list_session_products -x` | ❌ Wave 0 |
| SEARCH-02 | GET /search/{id}/results retorna 200 com produtos agrupados | integration | `pytest mis/tests/web/test_web_search.py::test_results_page_200 -x` | ❌ Wave 0 |
| SEARCH-03 | create_app não inicia APScheduler quando start_scheduler=False | unit | `pytest mis/tests/web/test_web_search.py::test_no_scheduler_on_startup -x` | ❌ Wave 0 |
| SEARCH-03 | Sessões running na startup são marcadas como timeout | unit | `pytest mis/tests/test_search_repository.py::test_startup_marks_running_as_timeout -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest mis/tests/test_search_repository.py -x -q`
- **Per wave merge:** `python -m pytest mis/tests/ -x -q`
- **Phase gate:** Full suite green antes de `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `mis/tests/test_search_repository.py` — covers SEARCH-01, SEARCH-02, SEARCH-03 (repository layer)
- [ ] `mis/tests/test_search_orchestrator.py` — covers run_manual_search timeout, partial results, platform error isolation
- [ ] `mis/tests/web/test_web_search.py` — covers rotas FastAPI e integração HTMX
- [ ] `mis/migrations/_009_search_sessions.py` — migration nova
- [ ] `mis/search_repository.py` — repositório novo
- [ ] `mis/search_orchestrator.py` — orquestrador novo

*(Infraestrutura de testes existente (conftest.py, app_client fixture) cobre todos os novos testes — nenhuma fixture nova obrigatória)*

---

## Sources

### Primary (HIGH confidence)
- Codebase direto — `mis/scanner.py` (SCANNER_MAP, run_all_scanners, asyncio.gather pattern)
- Codebase direto — `mis/web/app.py` (lifespan, scheduler registration, create_app)
- Codebase direto — `mis/web/routes/ranking.py` (is_htmx, _get_ranking_context, partial route pattern)
- Codebase direto — `mis/web/templates/alerts_badge.html` (hx-trigger="every Ns" polling pattern)
- Codebase direto — `mis/web/templates/base.html` (dark theme classes, navbar structure)
- Codebase direto — `mis/migrations/_008_niche_v3.py` (migration pattern, idempotência, seed data)
- Codebase direto — `mis/migrations/_007_is_stale.py` (migration simples pattern)
- Codebase direto — `mis/db.py` (get_db PRAGMAs, run_migrations chain)
- Codebase direto — `mis/product_repository.py` (upsert_product signature)
- Codebase direto — `mis/niche_repository.py` (get_platform_slug, list_niches, list_subniches)
- Codebase direto — `mis/base_scraper.py` (PLAYWRIGHT_SEMAPHORE, async context manager pattern)
- Codebase direto — `mis/tests/web/conftest.py` (app_client fixture, TestClient pattern)

### Secondary (MEDIUM confidence)
- HTMX 2.0.8 docs (CDN em base.html) — `hx-trigger`, `hx-swap="outerHTML"`, `HX-Redirect` header behavior — padrão bem estabelecido

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — tudo já instalado e em uso no projeto
- Architecture: HIGH — padrões copiados diretamente do código existente
- Pitfalls: HIGH — identificados via leitura direta do código e análise de edge cases arquiteturais
- niche_id legacy mapping: MEDIUM — requer verificação durante implementação

**Research date:** 2026-03-18
**Valid until:** 2026-04-17 (30 dias — stack estável)
