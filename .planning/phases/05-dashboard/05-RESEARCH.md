# Phase 5: Dashboard - Research

**Researched:** 2026-03-15
**Domain:** FastAPI + Jinja2 + HTMX server-side rendered web dashboard
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- FastAPI + Jinja2 + HTMX (fixado pelo roadmap — server-side rendering, sem React/Vue)
- Iniciado via `python -m mis dashboard --port 8000` (subcomando do __main__.py existente)
- Sem autenticacao — uso pessoal local (localhost)
- Sem endpoints JSON por agora — so HTML (API JSON e v2)
- Dark mode como padrao
- Estilo minimalista/funcional — foco em dados, sem design system customizado pesado
- Navbar com 3 itens: Ranking | Feed de Dores | Alertas
- Pagina inicial: Ranking de Produtos; Dossie e sub-pagina do Ranking (/dossier/{id})
- FastAPI acessa SQLite via repositorios existentes (product_repository.py) + novos repositorios para dossiers e pain_reports
- Nao acessa o DB diretamente nos route handlers
- Layout ranking: tabela com linhas (nao cards)
- Colunas ranking: posicao (#), nome, plataforma, nicho, score de oportunidade
- Filtros: dropdowns de Plataforma e Nicho no topo — HTMX recarrega a tabela sem reload
- Sem busca textual no ranking, sem sidebar de filtros
- Ordenacao: colunas clicaveis (posicao, score) para ordenar ASC/DESC
- Paginacao: configuravel (10/20/50 por pagina)
- Timestamp da ultima atualizacao visivel no topo da tabela
- Produtos sem dossie: badge "Pendente" — clique abre pagina com status
- Clique no produto navega para /dossier/{id}
- Dossie: header fixo com nome, plataforma, posicao, score, confidence score
- Dossie: tabs horizontais — Visao Geral | Copy | Anuncios | Reviews | Template
- Tab padrao: Visao Geral
- Tab Reviews: sintese IA + lista de reviews com rating
- Tab Anuncios: cards com copy, plataforma, data
- Tab Template: texto formatado + botao "Copiar para clipboard"
- Navegacao entre dossies: setas anterior/proximo
- Produtos com dossie pendente: dados disponiveis + status "Analise em andamento"
- Feed de Dores: abas por nicho, cada aba mostra o relatorio mais recente
- Cada relatorio: top 5 dores com titulo + descricao + nivel de interesse
- Timestamp: data/hora exatos + tempo relativo
- Contador de sinais visivel
- Links para fontes em cada dor
- Historico: selector de data/hora para ultimas 24-48h
- Busca textual nos relatorios historicos
- Filtro por nivel de interesse (checkboxes)
- Alertas: trigger quando produto entra no top 20 de qualquer plataforma pela primeira vez
- Pagina dedicada "Alertas" como terceiro item do navbar
- Badge de contador no navbar com polling
- Cada alerta: produto, nicho, posicao alcancada, data, link "Ver dossie"
- Alertas com status "Visto/Nao visto" (nao somem)
- Retencao: alertas expiram apos 7 dias automaticamente
- Pagina /health no rodape com status dos scrapers, ultima execucao, erros recentes

### Claude's Discretion
- Estrutura interna de arquivos em mis/web/ (routes, templates, static)
- CSS framework especifico (Tailwind vs Bootstrap) dentro do dark mode
- Implementacao do polling do badge de alertas (intervalo, endpoint)
- Design exato das paginas (spacing, cores dentro do dark mode)
- Paginacao: implementacao tecnica (HTMX ou server-side)
- Intervalo do selector de historico (ex: de hora em hora ou granularidade livre)

### Deferred Ideas (OUT OF SCOPE)
- Grafico de linha de evolucao do score de oportunidade por nicho ao longo do tempo
- Botao "Reanalisar" no dossie para re-disparar spy pipeline
- Notificacoes via WhatsApp/Telegram (v2 ADV-04)
- Export de dossie em PDF (v2 ADV-01)
- Comparacao lado a lado de 2+ produtos (v2 ADV-02)
- API JSON endpoints /api/products, /api/dossier/{id}
- Interface mobile nativa
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DASH-01 | Dashboard exibe ranking de produtos campeoes filtravel por plataforma e nicho | HTMX hx-get + hx-swap para filtros; FastAPI route /ranking; product_repository retorna produtos paginados com filtros |
| DASH-02 | Dashboard exibe pagina individual de dossie com todos os dados de espionagem e analise IA | FastAPI route /dossier/{id}; dossier_repository novo; tabs via HTMX hx-get por tab; JSON dossier_json parseado no template |
| DASH-03 | Dashboard exibe feed de dores do mercado com atualizacao horaria por nicho | FastAPI route /feed; pain_repository novo; abas por nicho via HTMX; relatorio mais recente de pain_reports |
| DASH-04 | Sistema envia alerta quando novo produto campiao entra no radar | Nova tabela alerts no DB; alert_repository novo; badge polling via HTMX every 30s; pagina /alerts com status visto/nao visto |
| SCAN-05 | Usuario pode filtrar ranking por plataforma e nicho no dashboard | Dropdowns de plataforma e nicho; HTMX recarrega tabela parcialmente sem full reload |
</phase_requirements>

---

## Summary

O Phase 5 implementa um dashboard web somente leitura usando FastAPI (ASGI server), Jinja2 (templates server-side), e HTMX (atualizacoes parciais sem JavaScript customizado). O stack esta fixado pelo roadmap e e o padrao correto para este caso: dados ja existem no SQLite, o usuario e unico e local, e renderizacao server-side elimina a necessidade de uma API JSON separada.

O principal desafio tecnico e a camada de dados: serao necessarios 3 novos repositorios (dossier_repository.py, pain_repository.py, alert_repository.py) seguindo o padrao estabelecido em product_repository.py, alem de uma nova migracao para a tabela de alertas. O subcomando `dashboard` e adicionado ao __main__.py existente chamando uvicorn.run() programaticamente.

A recomendacao de CSS e Tailwind CSS via CDN Play (sem build step), configurado com `darkMode: 'class'` e classe `dark` no `<html>`. Isso elimina qualquer toolchain de frontend e e compativel com o modelo de servidor puro Python.

**Primary recommendation:** Use FastAPI + Jinja2 + HTMX com Tailwind CDN. Crie mis/web/ com estrutura padronizada (app.py, routes/, templates/, static/). Implemente 3 novos repositorios seguindo o padrao de product_repository.py. Nova migracao _005 para tabela alerts.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| fastapi | >=0.115 | Web framework ASGI, rotas, TemplateResponse | Padrao Python async web, zero config |
| uvicorn | >=0.34 | ASGI server para rodar FastAPI | Servidor de referencia para FastAPI |
| jinja2 | >=3.1 | Template engine server-side (SSR) | Integrado nativamente ao FastAPI, suporte a heranca de templates |
| htmx | 2.0.8 (CDN) | Atualizacoes parciais HTML via atributos, polling, OOB swaps | Elimina necessidade de JavaScript customizado |
| aiofiles | >=24.1 | Servir arquivos estaticos com StaticFiles | Requerido pelo StaticFiles do Starlette/FastAPI |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| tailwindcss | Play CDN (sem versao fixa) | CSS utility-first com dark mode | Sem build step, ideal para projeto Python puro |
| python-multipart | >=0.0.12 | Suporte a form data no FastAPI | Necessario se usar form filters (GET params sao suficientes aqui) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Tailwind CDN | Bootstrap CDN | Bootstrap tem mais componentes prontos mas CDN e maior; Tailwind Play CDN e mais leve e flexivel para dark mode customizado |
| Tailwind CDN | CSS puro inline | Muito mais trabalho manual para dark mode consistente |
| HTMX via CDN | fasthx/fastapi-htmx | Libs adicionam decorators mas adiciona dependencia; HTMX puro via CDN e mais simples para este escopo |

**Installation:**
```bash
pip install "fastapi[standard]" uvicorn jinja2 aiofiles
# fastapi[standard] inclui uvicorn, mas instalar explicitamente e mais claro
```

Adicionar ao `mis/requirements.txt`:
```
fastapi>=0.115.0
uvicorn>=0.34.0
jinja2>=3.1.0
aiofiles>=24.1.0
```

**Nota:** `python-multipart` nao e necessario se os filtros forem via query params (GET /ranking?platform=hotmart&niche=emagrecimento), que e o padrao correto para filtros read-only.

---

## Architecture Patterns

### Recommended Project Structure
```
mis/
├── web/
│   ├── __init__.py          # exports create_app()
│   ├── app.py               # FastAPI app factory, monta rotas e static
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── ranking.py       # GET /ranking, GET /ranking/table (HTMX partial)
│   │   ├── dossier.py       # GET /dossier/{id}, GET /dossier/{id}/tab/{name}
│   │   ├── feed.py          # GET /feed, GET /feed/niche/{slug}
│   │   ├── alerts.py        # GET /alerts, POST /alerts/{id}/mark-seen, GET /alerts/badge
│   │   └── health.py        # GET /health
│   ├── templates/
│   │   ├── base.html        # Layout base com navbar, dark mode, HTMX CDN
│   │   ├── ranking.html     # Pagina de ranking (extends base.html)
│   │   ├── ranking_table.html  # Partial: so a tabela (para HTMX swap)
│   │   ├── dossier.html     # Pagina do dossie (extends base.html)
│   │   ├── dossier_tab.html # Partial: conteudo de uma tab do dossie
│   │   ├── feed.html        # Feed de dores (extends base.html)
│   │   ├── feed_report.html # Partial: relatorio de um nicho
│   │   ├── alerts.html      # Pagina de alertas (extends base.html)
│   │   ├── alerts_badge.html  # Partial: badge contador (para HTMX OOB poll)
│   │   └── health.html      # Status dos scrapers (extends base.html)
│   └── static/
│       └── app.js           # Minimo: clipboard copy handler, dark class init
├── dossier_repository.py    # NOVO: consultas a tabela dossiers + reviews + ads
├── pain_repository.py       # NOVO: consultas a tabela pain_reports + pain_signals
├── alert_repository.py      # NOVO: CRUD de alertas
└── migrations/
    └── _005_alerts.py       # NOVO: tabela alerts
```

### Pattern 1: FastAPI App Factory com APIRouter

**What:** App criada em funcao `create_app()` que aceita `db_path` como parametro, facilitando testes com banco temporario.

**When to use:** Sempre que o app precisa de configuracao injetada (db_path, config).

**Example:**
```python
# mis/web/app.py
# Source: https://fastapi.tiangolo.com/tutorial/bigger-applications/
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from .routes import ranking, dossier, feed, alerts, health

TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"

def create_app(db_path: str) -> FastAPI:
    app = FastAPI(title="MIS Dashboard")
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    # Injetar db_path nos routers via app.state
    app.state.db_path = db_path

    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
    app.state.templates = templates

    app.include_router(ranking.router)
    app.include_router(dossier.router)
    app.include_router(feed.router)
    app.include_router(alerts.router)
    app.include_router(health.router)

    return app
```

### Pattern 2: TemplateResponse com Request

**What:** Toda rota que retorna HTML usa `templates.TemplateResponse(request=request, name="...", context={...})`.

**When to use:** Toda rota HTML no dashboard.

**Example:**
```python
# mis/web/routes/ranking.py
# Source: https://fastapi.tiangolo.com/advanced/templates/
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/ranking", response_class=HTMLResponse)
async def ranking_page(
    request: Request,
    platform: str | None = None,
    niche: str | None = None,
    order_by: str = "rank",
    order_dir: str = "asc",
    per_page: int = 20,
    page: int = 1,
):
    db_path = request.app.state.db_path
    templates = request.app.state.templates
    # ... buscar dados via repositorio ...
    return templates.TemplateResponse(
        request=request,
        name="ranking.html",
        context={"products": products, "filters": {"platform": platform, "niche": niche}},
    )
```

### Pattern 3: HTMX Partial — Tabela sem Full Reload

**What:** Rota separada retorna apenas o fragmento HTML da tabela. O dropdown chama essa rota via `hx-get`.

**When to use:** Filtros de Plataforma/Nicho no ranking; ordenacao de colunas.

**Example:**
```html
<!-- templates/ranking.html -->
<!-- Source: https://htmx.org/docs/ -->
<select
  name="platform"
  hx-get="/ranking/table"
  hx-target="#ranking-table-wrapper"
  hx-swap="innerHTML"
  hx-include="[name='niche'],[name='per_page']"
>
  <option value="">Todas as plataformas</option>
  <option value="hotmart">Hotmart</option>
</select>

<div id="ranking-table-wrapper">
  {% include "ranking_table.html" %}
</div>
```

```python
# Rota separada para o partial
@router.get("/ranking/table", response_class=HTMLResponse)
async def ranking_table_partial(request: Request, platform: str | None = None, ...):
    # retorna so ranking_table.html sem extends base
    return templates.TemplateResponse(request=request, name="ranking_table.html", context={...})
```

### Pattern 4: HTMX Polling para Badge de Alertas

**What:** Um elemento no navbar faz polling a cada 30 segundos para atualizar o badge de alertas sem abrir a pagina.

**When to use:** Badge de alertas nao vistos no navbar.

**Example:**
```html
<!-- templates/base.html - dentro do navbar -->
<!-- Source: https://htmx.org/docs/#polling -->
<span
  id="alerts-badge"
  hx-get="/alerts/badge"
  hx-trigger="every 30s"
  hx-swap="outerHTML"
>
  {% if unseen_count > 0 %}
  <span class="bg-red-500 text-white text-xs rounded-full px-2">{{ unseen_count }}</span>
  {% endif %}
</span>
```

```python
# mis/web/routes/alerts.py
@router.get("/alerts/badge", response_class=HTMLResponse)
async def alerts_badge(request: Request):
    # retorna apenas o fragmento do badge
    unseen = alert_repository.count_unseen(db_path)
    return templates.TemplateResponse(
        request=request, name="alerts_badge.html", context={"unseen_count": unseen}
    )
```

### Pattern 5: HTMX Tabs no Dossie

**What:** Cada tab do dossie faz um `hx-get` para a rota de partial correspondente, sem recarregar a pagina.

**When to use:** Tabs Visao Geral / Copy / Anuncios / Reviews / Template no dossie.

**Example:**
```html
<!-- templates/dossier.html -->
<!-- Source: https://htmx.org/docs/ + https://testdriven.io/blog/fastapi-htmx/ -->
<nav class="flex border-b border-gray-700">
  {% for tab in ["visao-geral", "copy", "anuncios", "reviews", "template"] %}
  <button
    hx-get="/dossier/{{ product.id }}/tab/{{ tab }}"
    hx-target="#tab-content"
    hx-swap="innerHTML"
    class="px-4 py-2 {% if active_tab == tab %}border-b-2 border-blue-400{% endif %}"
  >{{ tab | title }}</button>
  {% endfor %}
</nav>
<div id="tab-content">
  {% include "dossier_tab_" + active_tab + ".html" %}
</div>
```

### Pattern 6: subcomando dashboard no __main__.py

**What:** Adicionar bloco `elif args.command == "dashboard"` no __main__.py existente, chamando `uvicorn.run()` programaticamente.

**When to use:** Ponto de entrada `python -m mis dashboard --port 8000`.

**Example:**
```python
# mis/__main__.py — adicionar parser e handler
# Source: https://fastapi.tiangolo.com/deployment/manually/
dashboard_parser = subparsers.add_parser("dashboard", help="Start the MIS web dashboard")
dashboard_parser.add_argument("--port", type=int, default=8000)
dashboard_parser.add_argument("--host", default="127.0.0.1")

# No dispatcher:
elif args.command == "dashboard":
    _handle_dashboard(args)

def _handle_dashboard(args) -> None:
    import uvicorn
    import os
    from mis.web.app import create_app

    db_path = os.environ.get("MIS_DB_PATH", "data/mis.db")
    app = create_app(db_path=db_path)
    uvicorn.run(app, host=args.host, port=args.port)
```

### Pattern 7: Repositorio para Web (padrao existente)

**What:** Novos repositorios web seguem exatamente o padrao de `product_repository.py`: funcoes puras que recebem `db_path: str`, criam o db internamente via `get_db()`, retornam tipos Python simples.

**When to use:** dossier_repository.py, pain_repository.py, alert_repository.py.

**Example:**
```python
# mis/dossier_repository.py — padrao a seguir
# Source: mis/product_repository.py (padrao estabelecido)
import sqlite_utils
from mis.db import get_db
import json

def get_dossier_by_product_id(db_path: str, product_id: int) -> dict | None:
    db = get_db(db_path)
    rows = list(db["dossiers"].rows_where("product_id = ?", [product_id]))
    if not rows:
        return None
    row = rows[0]
    if row.get("dossier_json"):
        row["dossier"] = json.loads(row["dossier_json"])
    return row
```

### Anti-Patterns to Avoid

- **Acessar DB direto no route handler:** Sempre usar repositorio. Mantem testabilidade e consistencia com o resto do projeto.
- **Usar `response_class=JSONResponse` para rotas de pagina:** So retornar HTML nas rotas do dashboard; endpoints JSON sao v2.
- **Passar `request` dentro do context dict do TemplateResponse:** Padrao antigo (pre-FastAPI 0.108). Usar `request=request` como argumento nomeado.
- **Template com logica de negocio pesada:** Templates so formatam dados. Toda query e transformacao no repositorio ou no route handler.
- **Polling muito frequente (< 10s) para badge:** 30 segundos e suficiente para uso local. Polling sub-10s cria ruido nos logs.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Template inheritance / layout base | Sistema de includes manual com strings Python | Jinja2 `{% extends %}` e `{% block %}` | Jinja2 resolve heranca, escaping, macros — mao de obra desnecessaria |
| Servir CSS/JS estatico | Rota Python que le arquivo e retorna bytes | `StaticFiles` do Starlette/FastAPI | Cache headers, streaming, directory scanning automaticos |
| Atualizacao parcial sem reload | fetch() + innerHTML manual no JavaScript | HTMX `hx-get` + `hx-swap` | Sem JavaScript customizado, funciona com HTML semantico |
| Polling do badge | setInterval + fetch em JavaScript | HTMX `hx-trigger="every 30s"` | Declarativo, sem state management, server cancela com HTTP 286 |
| Deteccao de request HTMX | Checar User-Agent no route | Header `HX-Request: true` via `request.headers.get("HX-Request")` | Standard HTMX, permite retornar partial ou full page conforme contexto |

**Key insight:** O valor de HTMX e eliminar JavaScript customizado para interacoes comuns (filtros, tabs, polling). Qualquer logica de interacao que possa ser expressa como "usuario clica, servidor responde com HTML" deve usar HTMX — nao construir fetch/XHR manualmente.

---

## Common Pitfalls

### Pitfall 1: TemplateResponse com API antiga (pre-0.108)
**What goes wrong:** `templates.TemplateResponse("item.html", {"request": request, "id": id})` funciona mas e padrao deprecado. Documentacao antiga usa essa forma.
**Why it happens:** FastAPI 0.108 mudou a assinatura — `request` agora e argumento nomeado direto, nao parte do context.
**How to avoid:** Sempre usar `templates.TemplateResponse(request=request, name="item.html", context={...})`
**Warning signs:** Warnings de deprecacao no console do uvicorn.

### Pitfall 2: SQLite concorrencia leitura/escrita durante dashboard
**What goes wrong:** APScheduler rodando jobs de escrita (scanner, radar) enquanto o dashboard le o mesmo arquivo SQLite pode causar `database is locked`.
**Why it happens:** SQLite WAL mode (ja configurado no projeto) permite multiplos leitores simultaneos com um escritor. O problema ocorre se o dashboard tentar escrever (ex: marcar alerta como visto) enquanto um job esta em commit longo.
**How to avoid:** Dashboard e majoritariamente read-only. Para a operacao de escrita (marcar alerta), usar `timeout=5` na conexao e tratar `OperationalError`. WAL mode ja esta ativo via `db.py`.
**Warning signs:** `sqlite3.OperationalError: database is locked` nos logs.

### Pitfall 3: HTMX partial retorna template com extends base
**What goes wrong:** Ao fazer swap de um partial (ex: tabela do ranking), o servidor retorna o HTML completo com navbar e rodape, quebrando o layout.
**Why it happens:** Rota de partial usa o mesmo template da pagina completa.
**How to avoid:** Templates partiais NUNCA usam `{% extends "base.html" %}`. Criar templates separados para cada fragmento (ex: `ranking_table.html` sem extends).
**Warning signs:** Navbar aparece duplicada na pagina apos filtro ser aplicado.

### Pitfall 4: `aiofiles` nao instalado para StaticFiles
**What goes wrong:** `RuntimeError: The aiofiles package is required to use StaticFiles` ao tentar servir arquivos estaticos.
**Why it happens:** `StaticFiles` do Starlette requer `aiofiles` para leitura assincrona de arquivos. Nao e instalado automaticamente com `fastapi`.
**How to avoid:** Adicionar `aiofiles` explicitamente ao `requirements.txt`.
**Warning signs:** Erro ao iniciar o servidor quando StaticFiles esta montado.

### Pitfall 5: Dossier JSON nao parseado no template
**What goes wrong:** Template exibe `{"analysis": "..."}` como string bruta em vez de campos individuais.
**Why it happens:** `dossier_json` esta armazenado como TEXT no SQLite. O repositorio precisa fazer `json.loads()` antes de passar ao template.
**How to avoid:** Repositorio sempre parseia campos JSON antes de retornar ao route handler. Nunca passar JSON string para o template.
**Warning signs:** Usuario ve JSON bruto na pagina de dossie.

### Pitfall 6: Alertas nao criados automaticamente (sem trigger)
**What goes wrong:** Pagina de alertas esta vazia mesmo com novos produtos no ranking.
**Why it happens:** A criacao de alertas precisa ser integrada ao ciclo de scanner existente — nao e auto-magica. O scanner precisa chamar `alert_repository.check_and_create_alert()` apos cada `save_batch()`.
**How to avoid:** Plano 05-04 deve incluir integracao do alert trigger no scanner job (register_scanner_jobs ou no proprio scanner). Verificar que o threshold top-20 esta sendo checado.
**Warning signs:** Tabela alerts vazia no banco mesmo apos ciclo de scanner.

---

## Code Examples

### Setup completo do FastAPI app com Jinja2 + StaticFiles
```python
# mis/web/app.py
# Source: https://fastapi.tiangolo.com/advanced/templates/
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"

def create_app(db_path: str) -> FastAPI:
    app = FastAPI(title="MIS Dashboard", docs_url=None, redoc_url=None)
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    app.state.db_path = db_path
    app.state.templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
    # include routers aqui
    return app
```

### Base template com dark mode e HTMX CDN
```html
<!-- mis/web/templates/base.html -->
<!-- Source: https://v3.tailwindcss.com/docs/installation/play-cdn + https://htmx.org/docs/ -->
<!DOCTYPE html>
<html lang="pt-BR" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}MIS Dashboard{% endblock %}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = { darkMode: 'class' }
  </script>
  <script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.8/dist/htmx.min.js"></script>
</head>
<body class="bg-gray-950 text-gray-100 min-h-screen">
  <nav class="border-b border-gray-800 px-6 py-3 flex items-center gap-6">
    <a href="/ranking" class="font-semibold hover:text-white">Ranking</a>
    <a href="/feed" class="hover:text-white">Feed de Dores</a>
    <a href="/alerts" class="hover:text-white flex items-center gap-1">
      Alertas
      <span id="alerts-badge"
            hx-get="/alerts/badge"
            hx-trigger="every 30s"
            hx-swap="outerHTML">
      </span>
    </a>
  </nav>
  <main class="px-6 py-6">
    {% block content %}{% endblock %}
  </main>
  <footer class="text-center py-4 text-gray-600 text-sm">
    <a href="/health" class="hover:text-gray-400">system health</a>
  </footer>
</body>
</html>
```

### Migracao _005 para tabela alerts
```python
# mis/migrations/_005_alerts.py
# Padrao: baseado em _004_pain_radar.py (padrao estabelecido no projeto)
def run_migration_005(db_path: str) -> None:
    db = sqlite_utils.Database(db_path)
    if "alerts" not in db.table_names():
        db["alerts"].create(
            {
                "id": int,
                "product_id": int,
                "platform_slug": str,
                "niche_slug": str,
                "position": int,
                "seen": int,        # BOOL como int (padrao SQLite do projeto)
                "created_at": str,  # ISO-8601
                "expires_at": str,  # ISO-8601 (+7 dias)
            },
            pk="id",
            not_null={"product_id", "platform_slug", "position", "created_at"},
        )
        db.execute(
            "CREATE INDEX IF NOT EXISTS idx_alerts_created "
            "ON alerts(created_at)"
        )
        db.execute(
            "CREATE INDEX IF NOT EXISTS idx_alerts_seen "
            "ON alerts(seen, expires_at)"
        )
```

### Teste de rota FastAPI com TestClient
```python
# mis/tests/test_web_ranking.py
# Source: https://fastapi.tiangolo.com/tutorial/testing/
from fastapi.testclient import TestClient
from mis.web.app import create_app

def test_ranking_page_returns_200(db_path):
    # db_path fixture ja disponivel no conftest.py do projeto
    from mis.db import run_migrations
    run_migrations(db_path)
    app = create_app(db_path=db_path)
    client = TestClient(app)
    response = client.get("/ranking")
    assert response.status_code == 200
    assert "Ranking" in response.text

def test_ranking_table_partial_htmx(db_path):
    from mis.db import run_migrations
    run_migrations(db_path)
    app = create_app(db_path=db_path)
    client = TestClient(app)
    # HTMX requests enviam header HX-Request: true
    response = client.get("/ranking/table", headers={"HX-Request": "true"})
    assert response.status_code == 200
    # Partial nao deve conter navbar
    assert "<nav" not in response.text
```

### Deteccao de request HTMX no route handler
```python
# mis/web/routes/ranking.py
# Source: https://htmx.org/reference/#request_headers
from fastapi import Request

def is_htmx(request: Request) -> bool:
    return request.headers.get("HX-Request") == "true"

@router.get("/ranking", response_class=HTMLResponse)
async def ranking_page(request: Request, platform: str | None = None, ...):
    template_name = "ranking_table.html" if is_htmx(request) else "ranking.html"
    return request.app.state.templates.TemplateResponse(
        request=request, name=template_name, context={...}
    )
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `TemplateResponse("name.html", {"request": req})` | `TemplateResponse(request=req, name="name.html", context={})` | FastAPI 0.108.0 | Assinatura mais clara; forma antiga ainda funciona mas gera deprecation warning |
| HTMX 1.x via CDN | HTMX 2.0.8 (fev/2025) | Jan 2025 | Melhorias em swap transitions, suporte a `hx-on:*` events; CDN path mudou para `htmx.org@2.0.8` |
| Tailwind v3 CDN | Tailwind v4 (CDN Play ainda disponivel) | Jan 2025 | v4 usa CSS variables nativas; CDN Play v3 ainda funciona e e mais simples para dark mode `class` strategy |

**Deprecated/outdated:**
- HTMX CDN path `unpkg.com/htmx.org@1.x`: Usar `cdn.jsdelivr.net/npm/htmx.org@2.0.8` (versao atual)
- `TemplateResponse` com `request` no context dict: Usar argumento nomeado `request=request`

---

## Open Questions

1. **Alert trigger — onde integrar no scanner?**
   - What we know: O scanner salva produtos via `save_batch()` em `product_repository.py`. A logica de "produto entrou no top 20 pela primeira vez" precisa comparar rank atual vs historico.
   - What's unclear: Se o schema atual armazena historico de rank suficiente para detectar "primeira vez no top 20". O campo `rank` em products e sobrescrito a cada ciclo (upsert).
   - Recommendation: Criar a deteccao no proprio scanner job: antes do upsert, checar se produto existia com rank > 20 e agora rank <= 20. Se sim, criar alerta. Isso requer leitura do rank anterior antes de sobrescrever.

2. **Pain report signal count — campo disponivel?**
   - What we know: pain_reports armazena `report_json` com as dores sintetizadas. O CONTEXT.md menciona "Baseado em 47 sinais coletados".
   - What's unclear: Se o `report_json` armazenado pelo synthesizer inclui contagem de sinais, ou se precisa ser calculado via query em pain_signals.
   - Recommendation: Verificar estrutura do report_json no synthesizer existente. Se nao incluir, pain_repository pode contar os sinais do ciclo via `SELECT COUNT(*) FROM pain_signals WHERE niche_slug = ? AND collected_at BETWEEN ...`.

3. **Migracao _005 e WAL — ordem de execucao segura?**
   - What we know: run_migrations() em db.py encadeia _001 ate _004. Sera necessario adicionar _005.
   - What's unclear: Nao ha incerteza real aqui — o padrao de adicao e idempotente.
   - Recommendation: Adicionar `_run_005(db_path)` ao chain em db.py seguindo o padrao estabelecido. Sem preocupacoes de concorrencia pois migracao so roda na inicializacao.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.4.2 + pytest-asyncio 0.24 |
| Config file | `mis/pytest.ini` (asyncio_mode = auto, testpaths = tests, timeout = 10) |
| Quick run command | `cd mis && python -m pytest tests/test_web_ranking.py tests/test_web_alerts.py -x` |
| Full suite command | `cd mis && python -m pytest tests/ -x` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DASH-01 | GET /ranking retorna 200 com tabela de produtos | unit | `pytest tests/test_web_ranking.py::test_ranking_page_returns_200 -x` | Wave 0 |
| DASH-01 | GET /ranking?platform=hotmart filtra corretamente | unit | `pytest tests/test_web_ranking.py::test_ranking_filter_by_platform -x` | Wave 0 |
| SCAN-05 | Filtro HTMX partial /ranking/table retorna so fragment sem navbar | unit | `pytest tests/test_web_ranking.py::test_ranking_table_partial_htmx -x` | Wave 0 |
| DASH-02 | GET /dossier/{id} retorna 200 com dados do dossie | unit | `pytest tests/test_web_dossier.py::test_dossier_page_returns_200 -x` | Wave 0 |
| DASH-02 | GET /dossier/{id}/tab/reviews retorna fragment correto | unit | `pytest tests/test_web_dossier.py::test_dossier_tab_reviews -x` | Wave 0 |
| DASH-03 | GET /feed retorna 200 com relatorio mais recente | unit | `pytest tests/test_web_feed.py::test_feed_page_returns_200 -x` | Wave 0 |
| DASH-04 | GET /alerts retorna lista com alertas | unit | `pytest tests/test_web_alerts.py::test_alerts_page -x` | Wave 0 |
| DASH-04 | GET /alerts/badge retorna contagem de nao vistos | unit | `pytest tests/test_web_alerts.py::test_alerts_badge_count -x` | Wave 0 |
| DASH-04 | Alert e criado quando produto entra no top 20 | unit | `pytest tests/test_alert_repository.py::test_alert_created_on_top20_entry -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `cd mis && python -m pytest tests/test_web_ranking.py tests/test_web_dossier.py tests/test_web_feed.py tests/test_web_alerts.py -x`
- **Per wave merge:** `cd mis && python -m pytest tests/ -x`
- **Phase gate:** Full suite green antes do `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `mis/tests/test_web_ranking.py` — cobre DASH-01, SCAN-05
- [ ] `mis/tests/test_web_dossier.py` — cobre DASH-02
- [ ] `mis/tests/test_web_feed.py` — cobre DASH-03
- [ ] `mis/tests/test_web_alerts.py` — cobre DASH-04 (badge + pagina)
- [ ] `mis/tests/test_alert_repository.py` — cobre logica de criacao de alertas
- [ ] `mis/tests/test_dossier_repository.py` — valida novos repositorios
- [ ] `mis/tests/test_pain_repository.py` — valida novos repositorios
- [ ] Framework install: `pip install "fastapi[standard]" uvicorn jinja2 aiofiles` — verificar se ja disponivel no env
- [ ] `httpx` para TestClient: ja incluso no `fastapi[standard]`; verificar se httpx esta no requirements-dev.txt (nao esta — adicionar)

---

## Sources

### Primary (HIGH confidence)
- https://fastapi.tiangolo.com/advanced/templates/ — Setup Jinja2, TemplateResponse, StaticFiles
- https://fastapi.tiangolo.com/tutorial/bigger-applications/ — APIRouter, include_router
- https://fastapi.tiangolo.com/deployment/manually/ — uvicorn.run() programatico
- https://fastapi.tiangolo.com/tutorial/testing/ — TestClient, pytest integration
- https://htmx.org/docs/ — hx-trigger polling, hx-swap-oob, atributos HTMX
- https://htmx.org/attributes/hx-trigger/ — Sintaxe de polling `every Xs`
- https://v3.tailwindcss.com/docs/installation/play-cdn — CDN sem build step
- https://tailwindcss.com/docs/dark-mode — Configuracao dark mode com `class` strategy
- Codigo existente: `mis/product_repository.py`, `mis/db.py`, `mis/__main__.py`, `mis/migrations/_004_pain_radar.py`

### Secondary (MEDIUM confidence)
- https://testdriven.io/blog/fastapi-htmx/ — Padroes HTMX + FastAPI verificados com exemplos
- https://www.johal.in/fastapi-templating-jinja2-server-rendered-ml-dashboards-with-htmx-2025/ — Dashboard ML com stack identico, 2025
- https://hamy.xyz/blog/2024-07_htmx-polling-example — Exemplo de polling HTMX

### Tertiary (LOW confidence)
- Nenhuma fonte apenas LOW confidence — todos os pontos criticos foram verificados com fontes primarias.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — FastAPI + Jinja2 + HTMX verificados via docs oficiais; versoes checadas
- Architecture: HIGH — Padrao product_repository.py e __main__.py existentes definem a estrutura; FastAPI APIRouter documentado
- Pitfalls: HIGH — Pitfalls 1, 3, 4 verificados com docs oficiais; pitfalls 2, 5, 6 derivados da analise do codigo existente do projeto

**Research date:** 2026-03-15
**Valid until:** 2026-04-15 (stack estavel; HTMX 2.x e FastAPI 0.11x estao maduros)
