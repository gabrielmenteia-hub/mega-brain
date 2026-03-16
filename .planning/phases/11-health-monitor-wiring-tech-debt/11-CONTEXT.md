# Phase 11: Health Monitor Wiring & Tech Debt - Context

**Gathered:** 2026-03-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Fechar os gaps de observabilidade do audit v1.0: wire `run_schema_integrity_check()` e `run_platform_canary()` no caminho de execução de produção, corrigir 3 bugs latentes (`fetch_spa` proxy, `asyncio.run` em `_compute_health`, deprecated datetime), e remover código morto. Nada novo é construído — apenas código existente é conectado e corrigido.

Fora do escopo: novos módulos de health, alertas via UI, expansão do schema check para outras tabelas, corrigir datetime em core/intelligence/.

</domain>

<decisions>
## Implementation Decisions

### Schema integrity check (lifespan wiring)

- Rodar **uma vez no startup** (lifespan), não como job periódico do APScheduler
- Executar **depois de `run_migrations()`** e **antes do loop de job registrations**
- Rodar apenas para DBs reais — pular implicitamente quando `db_path == ':memory:'` (colocar a chamada no mesmo contexto que `run_migrations`)
- **Comportamento on failure:** log warning e continuar — servidor sobe mesmo com schema quebrado (consistente com filosofia soft-fail do lifespan)
- **Comportamento on success:** log info (já implementado em `run_schema_integrity_check()` — nenhum código extra)
- Verificar apenas as **5 tabelas core** da Phase 1: products, platforms, niches, pains, dossiers
- Implementar como **bloco try/except separado com await** (fora do for loop síncrono existente):
  ```python
  try:
      await run_schema_integrity_check(db_path)
  except Exception as exc:
      _log.warning("lifespan.schema_check_failed", error=str(exc))
  ```
- Resultado **não armazenado em `app.state`** — logging é suficiente para observabilidade
- Import em `app.py`: `from mis.health_monitor import register_canary_job, register_platform_canary_jobs, run_schema_integrity_check`

### Platform canary scheduling

- **3 jobs independentes**: `canary_hotmart`, `canary_clickbank`, `canary_kiwify` — cada plataforma verificada separadamente
- **Intervalo: 25h** para todas — alinhado com `threshold_hours=25` (verifica levemente mais frequente que a janela de staleness)
- **Nova função `register_platform_canary_jobs(db_path)`** em `health_monitor.py` — segue padrão de `register_canary_job()`
- `db_path` recebido como **parâmetro explícito** (não lido de env var internamente) — testável, sem dependências ocultas
- Chamado **dentro do for loop existente** no lifespan (zero código duplicado):
  ```python
  for name, fn, args in [
      ...,
      ("register_platform_canary_jobs", register_platform_canary_jobs, [db_path]),
  ]:
  ```
- `db_path` obtido do **closure de `create_app()`** — disponível antes de `app.state` ser setado
- `replace_existing=True` — seguro para restarts sem jobs duplicados
- **Sem guard `':memory:'`** — o job é registrado mas só usa `db_path` quando dispara; scheduler não inicia em testes
- **Não exportar em `mis/__init__.py`** — apenas visível via `mis.health_monitor` (consistente com `register_canary_job`)

### Dead code disposal

- **Remover completamente** (não documentar como deprecated):
  - `register_scanner_jobs()` em `mis/scheduler.py`
  - `run_hotmart_scan()` em `mis/scanners/hotmart.py`
  - `run_clickbank_scan()` em `mis/scanners/clickbank.py`
  - `run_kiwify_scan()` em `mis/scanners/kiwify.py`
- **Limpar todos os imports órfãos** em `scheduler.py` (linhas 158-160: imports de `run_hotmart_scan`, `run_clickbank_scan`, `run_kiwify_scan`)
- **Deletar `mis/tests/test_scanner_jobs.py`** — testa código que será removido
- **Atualizar docstring do módulo `scheduler.py`** (linha 4 menciona `register_scanner_jobs`) para refletir realidade atual
- **Verificar `scanner.fetch_spa()` wrapper** (linha 81) antes de decidir — se nenhum scanner o usa diretamente, remover também; se é usado, manter
- Import em `app.py` (`from mis.scheduler import get_scheduler, register_scan_and_spy_job`) já está correto — não tocar

### datetime.utcnow() → datetime.now(timezone.utc)

- **Escopo: todos os arquivos MIS** que usam `datetime.utcnow()` (7 arquivos identificados):
  - `mis/intelligence/dossier_generator.py`
  - `mis/radar/quora_collector.py`
  - `mis/radar/reddit_collector.py`
  - `mis/radar/synthesizer.py`
  - `mis/radar/trends_collector.py`
  - `mis/radar/youtube_collector.py`
  - `mis/radar/__init__.py`
- **Fora do escopo:** `core/intelligence/autonomous_processor.py` e `core/intelligence/task_orchestrator.py` — PR separada
- **Abordagem:** substituição pontual + adicionar `timezone` ao import existente onde faltar (`from datetime import datetime, timezone`)
- **Mudança de formato aceita:** timestamps passam de `'2026-03-16T12:00:00'` para `'2026-03-16T12:00:00+00:00'` — `fromisoformat()` aceita ambos, guard `tzinfo is None` já existe no código
- **Atualizar testes** que assertam strings de timestamp exatas para usar o novo formato com `+00:00`

### fetch_spa() proxy fix

- **Usar `_select_proxy()`** em vez de `self._proxy` para seleção de proxy no Playwright
- Proxy selecionado **uma vez no início de `fetch_spa()`** — mesmo proxy para toda a sessão Playwright daquela chamada
- Rotação implícita a cada chamada (browser é criado e fechado por chamada)
- Quando `_select_proxy()` retorna `None` (lista vazia): `proxy={"server": selected} if selected else None` — sem proxy (comportamento atual mantido)
- **Fix apenas em `BaseScraper.fetch_spa()`** — `scanner.fetch_spa()` é wrapper que delega, não precisa de mudança

### _compute_health() async fix

- **Tornar `_compute_health()` async**: `async def _compute_health(...)` com `scraper_ok = await run_canary_check()`
- **`get_briefing_data()` mantém sync**: usa `asyncio.run(_compute_health(...))` — um `asyncio.run()` em vez de dois (antes: `asyncio.run(run_canary_check())` dentro de `_compute_health` sync)
- Skill `/mis-briefing` consome `get_briefing_data()` em contexto sync (execution-script pattern) — sem quebra

### Claude's Discretion

- Implementação interna de `register_platform_canary_jobs()` — estrutura do loop e IDs dos jobs
- Estrutura exata do try/except do schema check no lifespan
- Ordem das plataformas no loop de canary jobs

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets

- `run_schema_integrity_check(db_path)` — já existe em `health_monitor.py`, já implementado com never-propagate e alert logging; apenas precisa ser chamado
- `run_platform_canary(db_path, platform_id, platform_name, threshold_hours=25)` — já existe em `health_monitor.py`, implementado e testado
- `register_canary_job()` — template a seguir para `register_platform_canary_jobs(db_path)`
- `_select_proxy()` — já existe em `base_scraper.py` (linha 84), usado em `fetch()` mas não em `fetch_spa()`
- For loop de job registrations em lifespan — pattern existente para adicionar novos jobs

### Established Patterns

- **Never-propagate-exceptions**: todos os canary/health checks retornam bool, nunca levantam exceções
- **`replace_existing=True`** em todos os APScheduler jobs (Phase 1 decision)
- **Lifespan soft-fail**: falhas em registros de jobs são logadas como warnings, não abortam startup
- **`run_canary_check` injetado como parâmetro em `_compute_health`** — padrão de injeção já existente, facilita mock

### Integration Points

- `mis/web/app.py` lifespan: onde schema check e platform canary jobs serão adicionados
- `mis/health_monitor.py`: onde `register_platform_canary_jobs(db_path)` será criada
- `mis/base_scraper.py` `fetch_spa()`: onde `self._proxy` → `_select_proxy()` será feito
- `mis/mis_agent.py` `_compute_health()`: onde `asyncio.run()` será substituído por `async/await`
- `mis/scheduler.py`: onde `register_scanner_jobs()` e imports órfãos serão removidos
- `mis/tests/test_lifespan.py`: adicionar patches para `run_schema_integrity_check` e `register_platform_canary_jobs`

</code_context>

<specifics>
## Specific Ideas

- `test_lifespan_registers_jobs_on_startup` deve ser atualizado (não novo teste criado) — adicionar patches e asserts para as duas novas funções
- Teste de `register_platform_canary_jobs`: usar scheduler fresh, chamar função, assert `len(scheduler.get_jobs()) == 3` com IDs `canary_hotmart`, `canary_clickbank`, `canary_kiwify`
- Teste de `fetch_spa` proxy: `patch('playwright.async_api.async_playwright')` como `AsyncMock` context manager, capturar `chromium.launch()` kwargs para verificar `proxy={'server': expected}`
- Testes de `_compute_health`: usar `AsyncMock` para `run_canary_check` (era `MagicMock` — precisa ser await-ável)

</specifics>

<deferred>
## Deferred Ideas

- Substituição de `datetime.utcnow()` em `core/intelligence/autonomous_processor.py` e `task_orchestrator.py` — PR separada, fora do escopo MIS
- Schema check periódico (APScheduler job a cada 12h) — apenas startup por enquanto
- Expor resultado do schema check na rota `/health` via `app.state.schema_ok` — desnecessário para v1

</deferred>

---

*Phase: 11-health-monitor-wiring-tech-debt*
*Context gathered: 2026-03-16*
