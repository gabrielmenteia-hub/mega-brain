# Phase 1: Foundation - Context

**Gathered:** 2026-03-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Infraestrutura base que torna possível coletar, armazenar e processar dados de mercado de forma confiável. Inclui: schema do banco de dados, BaseScraper (classe-base para todos os scrapers futuros), configuração de nichos e health monitor com canary checks. Nenhum scraper de plataforma real é implementado aqui — essa é a Fase 2.

</domain>

<decisions>
## Implementation Decisions

### Biblioteca HTTP
- **httpx async** como cliente HTTP principal (HTTP/2, async-first, connection pooling)
- Não usar requests (síncrono) nem Playwright como base universal (muito pesado)

### Interface Playwright no BaseScraper
- BaseScraper expõe dois métodos desde a Fase 1:
  - `fetch(url)` → httpx async (SSR, JSON endpoints)
  - `fetch_spa(url)` → Playwright (SPAs, JS-rendered content)
- Subclasses escolhem qual método usar — sem duplicação nas fases seguintes

### Stealth (anti-bot fingerprinting)
- `playwright-stealth` ativo no `fetch_spa()` desde a Fase 1
- Esconde `navigator.webdriver` e outros sinais de automation que Hotmart/Kiwify detectam
- Não adiar para Fase 2 — evita retrabalho

### Proxy e headers anti-bot
- Interface de proxy via `PROXY_URL` no `.env` (vazio na Fase 1, preenchido quando necessário)
- Rotação de User-Agent e headers HTTP realistas sempre ativos
- Proxy residencial pago é decisão de operação, não de código — BaseScraper apenas lê a variável

### Retry em falha
- **tenacity** com backoff exponencial: `stop_after_attempt(3)`, `wait_exponential(min=1, max=10)`
- Declarativo via decorator `@retry` nos métodos `fetch()` e `fetch_spa()`
- Retenta em: erros de rede, HTTP 429, HTTP 5xx

### Rate limiting
- `asyncio.Semaphore` para limitar concorrência + `asyncio.sleep()` entre requests
- Delay configurável por domínio: `DOMAIN_DELAYS = {'hotmart.com': 2.0, ...}` com fallback global de 2s
- Config permite override por domínio sem alterar o código base

### Ciclo de vida da instância
- **Long-lived**: uma instância por job de scraping, reutilizada entre todos os requests do job
- httpx `AsyncClient` fica aberto durante todo o job (connection pooling ativo)
- `__aenter__`/`__aexit__` implementados para fechamento correto ao final do job

### Error handling
- Falha após todas as tentativas de retry levanta `ScraperError(url, attempts, cause)`
- Exceção customizada — sem swallow silencioso, sem retorno de `None`
- O caller (health monitor ou job scheduler) decide o que fazer com a exceção

### Cookies e session
- httpx `AsyncClient` gerencia cookies automaticamente dentro da sessão
- Cookies persistem entre todos os requests da mesma instância (session-like)
- Necessário para plataformas com cookie de consent ou session token

### Logging interno
- **structlog** com output JSON
- Cada request loga: `url`, `status_code`, `duration_ms`, `attempt`, `domain`
- Erros logam também: `exception_type`, `last_error`
- Facilita parsing pelo health monitor e ferramentas externas

### Claude's Discretion
- Design exato do schema de banco de dados (nomes de colunas, tipos, índices)
- Estrutura de pastas interna do módulo `mis/`
- Formato do arquivo de configuração de nichos (YAML vs Python dataclass)
- Canal de alerta do health monitor (console/log é suficiente para Fase 1)
- APScheduler skeleton: nível de integração na Fase 1
- Ferramentas de migration (alembic, sqlite-utils, SQL puro)

</decisions>

<specifics>
## Specific Ideas

- BaseScraper deve ser a fundação sólida que nunca precisará ser reescrita — investir em fazer certo agora
- A interface `fetch()` / `fetch_spa()` permite que cada scraper de plataforma escolha o método sem saber dos detalhes de implementação
- `PROXY_URL` no `.env` como decisão de infra — o código não sabe se está usando proxy ou não, apenas passa para o cliente

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- MEGABRAIN já usa Python com `pathlib.Path` para paths cross-platform — seguir o mesmo padrão no MIS
- `.env` já existe e é o source of truth para credenciais — adicionar `PROXY_URL`, `MIS_NICHES` etc. no mesmo arquivo

### Established Patterns
- Snake_case para scripts Python (padrão MEGABRAIN)
- Módulos independentes dentro do repo (ex: `core/`, `agents/`) — `mis/` segue o mesmo padrão de isolamento

### Integration Points
- `mis/` como módulo independente dentro de `MEGABRAIN/`
- `mis_agent.py` será o único arquivo que cruza a fronteira MIS/MEGABRAIN (Fase 6)
- `mis.db` vive dentro de `mis/` ou em `.data/mis/` (gitignored, L3)

</code_context>

<deferred>
## Deferred Ideas

Nenhuma ideia fora do escopo surgiu durante a discussão.

</deferred>

---

*Phase: 01-foundation*
*Context gathered: 2026-03-14*
