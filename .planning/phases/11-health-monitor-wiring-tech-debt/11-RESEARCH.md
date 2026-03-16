# Phase 11: Health Monitor Wiring & Tech Debt - Research

**Researched:** 2026-03-16
**Domain:** Python async patterns, APScheduler wiring, SQLite health monitoring, datetime timezone hygiene
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Schema integrity check (lifespan wiring):**
- Rodar uma vez no startup (lifespan), nao como job periódico do APScheduler
- Executar depois de `run_migrations()` e antes do loop de job registrations
- Rodar apenas para DBs reais — pular implicitamente quando `db_path == ':memory:'`
- Comportamento on failure: log warning e continuar — servidor sobe mesmo com schema quebrado
- Verificar apenas as 5 tabelas core da Phase 1: products, platforms, niches, pains, dossiers
- Implementar como bloco try/except separado com await (fora do for loop síncrono existente)
- Resultado nao armazenado em `app.state` — logging é suficiente
- Import em `app.py`: `from mis.health_monitor import register_canary_job, register_platform_canary_jobs, run_schema_integrity_check`

**Platform canary scheduling:**
- 3 jobs independentes: `canary_hotmart`, `canary_clickbank`, `canary_kiwify`
- Intervalo: 25h para todas
- Nova funcao `register_platform_canary_jobs(db_path)` em `health_monitor.py`
- `db_path` recebido como parâmetro explícito (nao lido de env var internamente)
- Chamado dentro do for loop existente no lifespan
- `db_path` obtido do closure de `create_app()`
- `replace_existing=True`
- Sem guard `':memory:'` — job é registrado mas scheduler nao inicia em testes
- Nao exportar em `mis/__init__.py`

**Dead code disposal:**
- Remover completamente (nao documentar como deprecated):
  - `register_scanner_jobs()` em `mis/scheduler.py`
  - `run_hotmart_scan()` em `mis/scanners/hotmart.py`
  - `run_clickbank_scan()` em `mis/scanners/clickbank.py`
  - `run_kiwify_scan()` em `mis/scanners/kiwify.py`
- Limpar todos os imports orfaos em `scheduler.py` (linhas 158-160)
- Deletar `mis/tests/test_scanner_jobs.py`
- Atualizar docstring do módulo `scheduler.py` (linha 4)
- Verificar `scanner.fetch_spa()` wrapper (linha 81) — se nao usado diretamente, remover também
- Import em `app.py` (`from mis.scheduler import get_scheduler, register_scan_and_spy_job`) — nao tocar

**datetime.utcnow() → datetime.now(timezone.utc):**
- Escopo: 7 arquivos MIS identificados:
  - `mis/intelligence/dossier_generator.py`
  - `mis/radar/quora_collector.py`
  - `mis/radar/reddit_collector.py`
  - `mis/radar/synthesizer.py`
  - `mis/radar/trends_collector.py`
  - `mis/radar/youtube_collector.py`
  - `mis/radar/__init__.py`
- Fora do escopo: `core/intelligence/autonomous_processor.py` e `core/intelligence/task_orchestrator.py`
- Abordagem: substituicao pontual + adicionar `timezone` ao import existente onde faltar
- Mudanca de formato aceita: timestamps com `+00:00` ao invés de sem timezone
- Atualizar testes que assertam strings de timestamp exatas

**fetch_spa() proxy fix:**
- Usar `_select_proxy()` em vez de `self._proxy` para selecao de proxy no Playwright
- Proxy selecionado uma vez no início de `fetch_spa()`
- Quando `_select_proxy()` retorna None: `proxy={"server": selected} if selected else None`
- Fix apenas em `BaseScraper.fetch_spa()` — `scanner.fetch_spa()` delega, sem mudanca

**_compute_health() async fix:**
- Tornar `_compute_health()` async: `async def _compute_health(...)`
- `get_briefing_data()` mantém sync: usa `asyncio.run(_compute_health(...))`
- Um `asyncio.run()` em vez de dois

### Claude's Discretion

- Implementacao interna de `register_platform_canary_jobs()` — estrutura do loop e IDs dos jobs
- Estrutura exata do try/except do schema check no lifespan
- Ordem das plataformas no loop de canary jobs

### Deferred Ideas (OUT OF SCOPE)

- Substituicao de `datetime.utcnow()` em `core/intelligence/autonomous_processor.py` e `task_orchestrator.py`
- Schema check periódico (APScheduler job a cada 12h)
- Expor resultado do schema check na rota `/health` via `app.state.schema_ok`
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| FOUND-02 | BaseScraper implementa rate limiting, retry automático, rotacao de proxies e headers anti-bot | `_select_proxy()` já existe e é usada em `fetch()` — basta estender para `fetch_spa()`. Confirms proxy rotation via `proxy_list`. |
| FOUND-04 | Health monitor detecta e alerta quando scrapers quebram silenciosamente (canary checks) | `run_schema_integrity_check()` e `run_platform_canary()` já implementados — apenas precisam ser conectados ao caminho de execucao de producao. |
</phase_requirements>

---

## Summary

Esta fase é exclusivamente de _wiring_ e _cleanup_: todo o código de monitoramento já foi implementado em fases anteriores (health_monitor.py foi construído na Phase 1 e Phase 8), mas nunca foi conectado ao caminho de execucao de producao. A tarefa é inserir 2 chamadas no lifespan, criar 1 funcao nova (`register_platform_canary_jobs`), corrigir 3 bugs latentes menores, e remover código morto.

O único código novo de substância é `register_platform_canary_jobs(db_path)` em `health_monitor.py` — uma funcao de ~10 linhas que segue o padrão exato de `register_canary_job()` já existente. Todo o restante é modificacoes cirúrgicas em arquivos existentes. Os testes de lifespan precisam de patches adicionais; os testes de `_compute_health` precisam trocar `MagicMock` por `AsyncMock`.

O escopo do datetime.utcnow() é maior do que parece (7 arquivos de producao + testes associados), mas cada substituicao é mecânica: trocar `.utcnow()` por `.now(timezone.utc)` e adicionar `timezone` ao import. A compatibilidade de `fromisoformat()` com ambos os formatos (com e sem `+00:00`) está confirmada no Python 3.7+ — e o código existente já tem guards `if lc_dt.tzinfo is None`.

**Primary recommendation:** Executar as 5 mudancas em ordem crescente de risco: (1) dead code removal, (2) fetch_spa proxy fix, (3) datetime fix nos 7 arquivos, (4) _compute_health async fix, (5) lifespan wiring. Verificar suite completa de 163 testes apos cada wave.

---

## Standard Stack

### Core (já instalado no projeto)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| APScheduler | 3.x | Job scheduling (AsyncIOScheduler) | Já em uso — `get_scheduler()` é singleton global |
| structlog | current | Structured logging com alert fields | Padrão do projeto — todos os health checks usam |
| pytest-asyncio | current | Testes de funcoes async | Já configurado — 163 testes existentes usam |
| unittest.mock | stdlib | `AsyncMock`, `patch`, `MagicMock` | Padrão dos testes existentes |

### Padroes de implementacao identificados no código

| Pattern | Onde Existe | Como Usar Nesta Fase |
|---------|-------------|----------------------|
| `replace_existing=True` em add_job | `register_canary_job()` | Usar em todos os 3 jobs de `register_platform_canary_jobs()` |
| Never-propagate-exceptions | `run_canary_check()`, `run_platform_canary()`, `run_schema_integrity_check()` | Todos retornam bool — manter contrato |
| Soft-fail no lifespan | For loop com try/except por job | Schema check fica em bloco try/except separado, fora do for loop |
| `db_path` como parâmetro explícito | `run_platform_canary(db_path, ...)` | `register_platform_canary_jobs(db_path)` recebe por parâmetro, nao por env var |
| `asyncio.run()` em contexto sync | `get_briefing_data()` chama `_compute_health()` | Manter um único `asyncio.run()` em `get_briefing_data()` |

---

## Architecture Patterns

### Estrutura atual do lifespan (app.py)

```
create_app(db_path):
    lifespan():
        [ANTES DO FOR LOOP] ← schema check vai aqui (try/except separado, await)
        for name, fn, args in [...job registrations...]:
            try: fn(*args)
            except: log warning
        [NO FOR LOOP] ← register_platform_canary_jobs entra na lista
        scheduler.start()
        yield
        scheduler.shutdown()

    if db_path != ':memory:':
        run_migrations(db_path)  ← schema check executa DEPOIS disto (no lifespan)
```

### Posicao exata do schema check no lifespan

O `run_migrations(db_path)` é chamado FORA do lifespan (na linha 84-85 de `app.py`), antes da definicao do lifespan. Portanto, quando o lifespan inicia, as migracoes já rodaram. O schema check deve ser o PRIMEIRO bloco dentro do lifespan `async with`, antes do for loop de jobs:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Schema check (primeiro, pós-migration)
    if db_path != ":memory:":
        try:
            await run_schema_integrity_check(db_path)
        except Exception as exc:
            _log.warning("lifespan.schema_check_failed", error=str(exc))

    # 2. Job registrations (for loop existente)
    for name, fn, args in [
        ("register_scan_and_spy_job", register_scan_and_spy_job, [config]),
        ("register_radar_jobs", register_radar_jobs, [config]),
        ("register_canary_job", register_canary_job, []),
        ("register_platform_canary_jobs", register_platform_canary_jobs, [db_path]),
    ]:
        try:
            fn(*args)
        except Exception as exc:
            _log.warning("lifespan.register_failed", job=name, error=str(exc))
    ...
```

**IMPORTANTE:** `run_schema_integrity_check()` já tem never-propagate internamente — o `except` externo no lifespan é uma camada de segurança adicional, consistente com o padrão do projeto.

### register_platform_canary_jobs — template de implementacao

Seguindo exatamente `register_canary_job()` como modelo:

```python
def register_platform_canary_jobs(db_path: str) -> None:
    """Register 3 platform data freshness canary jobs (Hotmart, ClickBank, Kiwify).

    Each job runs every 25h — slightly more frequent than the 25h staleness threshold.
    Safe to call multiple times (replace_existing=True).
    """
    from .scheduler import get_scheduler

    scheduler = get_scheduler()
    platforms = [
        (1, "hotmart", "canary_hotmart"),
        (2, "clickbank", "canary_clickbank"),
        (3, "kiwify", "canary_kiwify"),
    ]
    for platform_id, platform_name, job_id in platforms:
        scheduler.add_job(
            run_platform_canary,
            trigger="interval",
            hours=25,
            args=[db_path, platform_id, platform_name],
            id=job_id,
            replace_existing=True,
        )
    log.info("health.platform_canary.registered", count=len(platforms), interval_hours=25)
```

### _compute_health async fix

**Estado atual (mis_agent.py linhas 195-247):**
- `_compute_health()` é sync
- Internamente chama `asyncio.run(run_canary_check())` — linha 216
- `get_briefing_data()` chama `_compute_health()` diretamente (sync → sync)

**Estado pós-fix:**
- `_compute_health()` torna-se `async def`
- `scraper_ok = await run_canary_check()` — sem `asyncio.run()` aninhado
- `get_briefing_data()` chama `asyncio.run(_compute_health(...))` — um único `asyncio.run()` no nível correto

**Por que importa:** `asyncio.run()` dentro de `_compute_health()` falha quando há um event loop já rodando (contexto async). Tornar `_compute_health` async elimina o `asyncio.run()` interno, mantendo apenas o externo em `get_briefing_data()` (que roda em contexto sync).

### fetch_spa proxy fix

**Estado atual (base_scraper.py linha 193):**
```python
browser = await pw.chromium.launch(
    proxy={"server": self._proxy} if self._proxy else None
)
```

**Estado pós-fix:**
```python
selected = self._select_proxy()
browser = await pw.chromium.launch(
    proxy={"server": selected} if selected else None
)
```

`self._proxy` é `None` quando `proxy_list` é usado (linha 68 de base_scraper.py). `_select_proxy()` já existe na linha 84 e é usada corretamente em `fetch()`. A fix é 2 linhas.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Selecao de proxy para Playwright | Lógica própria de random.choice | `_select_proxy()` já implementado | Evita duplicacao — mesmo método usado em `fetch()` |
| Registro de jobs canary | Scheduler manual ou threading | `APScheduler add_job` com `interval` trigger | Padrão já estabelecido — `register_canary_job()` é o template |
| Never-propagate no lifespan | Múltiplos `try/except` distintos | Bloco try/except + log.warning (já é o padrão) | Consistência com todos os outros pontos de falha do lifespan |
| Async canary call em contexto sync | Novo event loop manual | `asyncio.run()` no nível de `get_briefing_data()` | Um único `asyncio.run()` por stack sync→async |

---

## Common Pitfalls

### Pitfall 1: asyncio.run() aninhado
**O que dá errado:** Chamar `asyncio.run()` dentro de uma funcao que já é chamada de um contexto async (ou de dentro de outro `asyncio.run()`) lança `RuntimeError: This event loop is already running`.
**Por que acontece:** O estado atual de `_compute_health()` tem `asyncio.run(run_canary_check())` dentro de si. Se `get_briefing_data()` for chamado de um contexto async no futuro, tudo quebra.
**Como evitar:** Tornar `_compute_health` async e usar `await` diretamente. Manter único `asyncio.run()` em `get_briefing_data()`.
**Sinais de alerta:** `RuntimeError: This event loop is already running` nos logs.

### Pitfall 2: Schema check antes das migracoes
**O que dá errado:** Se `run_schema_integrity_check()` for chamado antes de `run_migrations()`, reportará tabelas faltando mesmo em instâncias saudáveis.
**Por que acontece:** `run_migrations()` é chamado na linha 84-85 de `app.py` SINCRONO (fora do lifespan). O lifespan async é executado depois. Portanto, a ordem está correta: o schema check no lifespan sempre rodará pós-migration.
**Como evitar:** Manter o schema check dentro do lifespan (não mover para `create_app()` sync).
**Sinais de alerta:** `health.schema_integrity.failed` com `missing_tables` contendo todas as 5 tabelas em ambiente saudável.

### Pitfall 3: Guard ':memory:' inconsistente
**O que dá errado:** `register_platform_canary_jobs()` sem guard `:memory:` registra jobs, mas o scheduler não inicia em testes. Isso está correto. Porém, o schema check SEM guard em contexto `:memory:` tentaria abrir `:memory:` via `sqlite3.connect(':memory:')` — que cria um novo banco vazio, reportando tabelas faltando.
**Como evitar:** O schema check DEVE ter o guard `if db_path != ':memory:'` (conforme decisao do usuário — "mesmo contexto que `run_migrations`").
**Sinais de alerta:** Falso positivo `SCHEMA_INTEGRITY_FAILED` em testes usando `':memory:'`.

### Pitfall 4: MagicMock vs AsyncMock em testes de _compute_health
**O que dá errado:** Após tornar `_compute_health` async, testes que usam `MagicMock` para `run_canary_check` falharão porque `await MagicMock()()` não é awaitable.
**Por que acontece:** `MagicMock` não implementa `__await__`. `AsyncMock` sim.
**Como evitar:** Substituir `MagicMock` por `AsyncMock` em todos os testes que mocam `run_canary_check` passado para `_compute_health`.
**Sinais de alerta:** `TypeError: object MagicMock can't be used in 'await' expression`.

### Pitfall 5: Imports órfaos em scheduler.py após remoção de dead code
**O que dá errado:** Remover `register_scanner_jobs()` mas deixar as linhas 158-160 de import (`from mis.scanners.hotmart import run_hotmart_scan`, etc.) causa `ImportError` se os módulos forem também alterados, ou cria imports desnecessários que confundem linters.
**Como evitar:** Remover os imports junto com a funcao. Verificar com `python -c "import mis.scheduler"` que nao há `ImportError`.

### Pitfall 6: Formato de timestamp nos testes após datetime fix
**O que dá errado:** Testes que assertam strings de timestamp exatas (ex: `assert ts == "2026-03-16T12:00:00"`) quebrarão porque `datetime.now(timezone.utc).isoformat()` produz `"2026-03-16T12:00:00+00:00"`.
**Como evitar:** Atualizar os asserts para aceitar o novo formato, ou usar `datetime.fromisoformat(ts)` para comparar sem depender do formato de string.
**Arquivos afetados:** `test_youtube_collector.py` (linhas 124, 192), `test_synthesizer.py` (múltiplas), `test_dossier_generator.py` (linha 72).

---

## Code Examples

### Patch correto para test_lifespan_registers_jobs_on_startup

O teste existente (test_lifespan.py linha 15) precisará de 2 patches adicionais:

```python
def test_lifespan_registers_jobs_on_startup(tmp_path):
    db_path = str(tmp_path / "mis.db")
    mock_scheduler = MagicMock()
    mock_scheduler.running = False

    with patch("mis.web.app.register_scan_and_spy_job") as mock_scan, \
         patch("mis.web.app.register_radar_jobs") as mock_radar, \
         patch("mis.web.app.register_canary_job") as mock_canary, \
         patch("mis.web.app.register_platform_canary_jobs") as mock_platform_canary, \
         patch("mis.web.app.run_schema_integrity_check") as mock_schema, \
         patch("mis.web.app.get_scheduler", return_value=mock_scheduler), \
         patch("mis.web.app.load_config", return_value={}):

        from mis.web.app import create_app
        app = create_app(db_path)

        with TestClient(app):
            mock_scan.assert_called_once()
            mock_radar.assert_called_once()
            mock_canary.assert_called_once()
            mock_platform_canary.assert_called_once_with(db_path)
            mock_schema.assert_called_once_with(db_path)
```

**NOTA:** `run_schema_integrity_check` é `async` — `patch` retorna um `MagicMock`. O lifespan faz `await run_schema_integrity_check(db_path)`. Para o `TestClient` funcionar, o patch precisa retornar um awaitable. Use `AsyncMock` no lugar:

```python
from unittest.mock import AsyncMock
patch("mis.web.app.run_schema_integrity_check", new_callable=AsyncMock) as mock_schema
```

### Teste de register_platform_canary_jobs

```python
def test_register_platform_canary_jobs():
    from mis.scheduler import stop_scheduler
    from mis.health_monitor import register_platform_canary_jobs

    stop_scheduler()
    try:
        register_platform_canary_jobs("/tmp/test.db")
        from mis.scheduler import get_scheduler
        scheduler = get_scheduler()
        job_ids = {job.id for job in scheduler.get_jobs()}
        assert "canary_hotmart" in job_ids
        assert "canary_clickbank" in job_ids
        assert "canary_kiwify" in job_ids
        assert len(scheduler.get_jobs()) == 3
    finally:
        stop_scheduler()
```

### Teste de fetch_spa proxy via AsyncMock

```python
@pytest.mark.asyncio
async def test_fetch_spa_uses_select_proxy():
    from unittest.mock import AsyncMock, MagicMock, patch
    from mis.base_scraper import BaseScraper

    proxy_list = ["http://proxy1:8080", "http://proxy2:8080"]
    scraper = BaseScraper(proxy_list=proxy_list)

    mock_page = AsyncMock()
    mock_page.content = AsyncMock(return_value="<html>ok</html>")
    mock_browser = AsyncMock()
    mock_browser.new_page = AsyncMock(return_value=mock_page)
    mock_pw = AsyncMock()
    mock_pw.chromium.launch = AsyncMock(return_value=mock_browser)

    with patch("playwright.async_api.async_playwright") as mock_ap:
        mock_ap.return_value.__aenter__ = AsyncMock(return_value=mock_pw)
        mock_ap.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await scraper.fetch_spa("https://example.com")

    launch_kwargs = mock_pw.chromium.launch.call_args
    proxy_arg = launch_kwargs[1].get("proxy") or launch_kwargs[0][0] if launch_kwargs[0] else None
    # Proxy deve ser um dos da lista, nao None
    assert proxy_arg is not None
    assert proxy_arg["server"] in proxy_list
```

### Teste de _compute_health com AsyncMock

```python
@pytest.mark.asyncio
async def test_compute_health_uses_await():
    import mis.mis_agent as agent_mod
    from unittest.mock import AsyncMock

    mock_canary = AsyncMock(return_value=True)
    health = await agent_mod._compute_health(
        db_path=":memory:",
        last_cycle=None,
        data_stale=True,
        unseen_alerts=0,
        run_canary_check=mock_canary,
    )
    mock_canary.assert_awaited_once()
    assert health["scraper_ok"] is True
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `datetime.utcnow()` | `datetime.now(timezone.utc)` | Python 3.12 (deprecated) | Formato ISO inclui `+00:00`; `fromisoformat()` aceita ambos |
| `asyncio.run()` aninhado | `async def` + `await` | Python 3.7+ | Evita RuntimeError em contextos async |
| `self._proxy` diretamente no Playwright | `_select_proxy()` | Phase 8 (fix incompleto) | Habilita rotacao real de proxy list em fetch_spa |

**Deprecated/outdated:**
- `datetime.utcnow()`: deprecated no Python 3.12, removido no 3.14. Todos os 7 arquivos MIS afetados ainda usam a forma antiga.
- `register_scanner_jobs()`: substituído por `register_scan_and_spy_job()` na Phase 3. Continua no código mas nunca é chamado em producao (Phase 9 confirmou que é dead code).

---

## Open Questions

1. **`scanner.fetch_spa()` wrapper (scanner.py linha 81)**
   - O que sabemos: É um wrapper que delega para `self._base.fetch_spa(url)`. Nenhum scanner de producao atual (Hotmart=SSR, ClickBank=GraphQL, Kiwify=API) usa Playwright.
   - O que está unclear: Se algum futuro scanner precisa dele.
   - Recomendacao: Verificar se `fetch_spa` é chamado em algum scanner antes de remover. Se nao há callers além do wrapper, o wrapper pode ser removido junto com `run_*_scan`. Se houver callers potenciais, manter.

2. **Testes de datetime em test_spy_orchestrator.py**
   - O que sabemos: `spy_orchestrator.py` também usa `datetime.utcnow()` (linhas 115, 255, 274), mas o CONTEXT.md nao o lista explicitamente nos 7 arquivos de escopo.
   - O que está unclear: Se `spy_orchestrator.py` está dentro ou fora do escopo desta fase.
   - Recomendacao: O CONTEXT.md lista explicitamente apenas os 7 arquivos. `spy_orchestrator.py` nao está listado — tratar como fora do escopo desta fase para manter o foco.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest + pytest-asyncio |
| Config file | nenhum detectado — pyproject.toml ou setup.cfg a verificar |
| Quick run command | `pytest mis/tests/test_lifespan.py mis/tests/test_health_monitor.py -x -q` |
| Full suite command | `pytest mis/tests/ -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FOUND-02 | `fetch_spa()` usa `_select_proxy()` para proxy_list | unit | `pytest mis/tests/test_base_scraper.py -x -q` | Existe — adicionar teste |
| FOUND-04 | `run_schema_integrity_check()` chamado no startup | unit | `pytest mis/tests/test_lifespan.py -x -q` | Existe — atualizar teste |
| FOUND-04 | `register_platform_canary_jobs()` registra 3 jobs | unit | `pytest mis/tests/test_health_monitor.py -x -q` | Existe — adicionar teste |
| FOUND-04 | `_compute_health()` é awaitable (async def) | unit | `pytest mis/tests/test_mis_agent.py -x -q` | Existe — atualizar mocks |

### Sampling Rate

- **Per task commit:** `pytest mis/tests/test_lifespan.py mis/tests/test_health_monitor.py mis/tests/test_mis_agent.py mis/tests/test_base_scraper.py -x -q`
- **Per wave merge:** `pytest mis/tests/ -q`
- **Phase gate:** Full suite green (163 testes atuais + novos) antes de `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `mis/tests/test_health_monitor.py` — adicionar `test_register_platform_canary_jobs` (3 jobs, IDs corretos)
- [ ] `mis/tests/test_lifespan.py` — atualizar `test_lifespan_registers_jobs_on_startup` para incluir patches de `run_schema_integrity_check` (AsyncMock) e `register_platform_canary_jobs`
- [ ] `mis/tests/test_mis_agent.py` — atualizar mocks de `run_canary_check` de `MagicMock` para `AsyncMock` nos testes de `_compute_health`
- [ ] `mis/tests/test_base_scraper.py` — adicionar `test_fetch_spa_uses_select_proxy` para proxy_list

*(Arquivos de test existem — nao precisam ser criados do zero, apenas atualizados/expandidos)*

---

## Sources

### Primary (HIGH confidence)

- Inspecao direta de `mis/web/app.py` — lifespan atual, for loop de jobs, posicao de `run_migrations()`
- Inspecao direta de `mis/health_monitor.py` — `run_schema_integrity_check()`, `run_platform_canary()`, `register_canary_job()` como template
- Inspecao direta de `mis/mis_agent.py` — `_compute_health()` sync com `asyncio.run()` aninhado
- Inspecao direta de `mis/base_scraper.py` — `_select_proxy()` linha 84, `fetch_spa()` linha 176-203, `self._proxy` linha 193
- Inspecao direta de `mis/scheduler.py` — `register_scanner_jobs()` dead code, imports orfaos linhas 158-160
- Inspecao direta de `mis/tests/test_lifespan.py` — testes existentes, patches atuais
- Inspecao direta de `mis/tests/test_health_monitor.py` — cobertura existente
- Grep de `datetime.utcnow()` — 7 arquivos de producao confirmados

### Secondary (MEDIUM confidence)

- Python docs (knowledge cutoff Aug 2025): `datetime.utcnow()` deprecated no 3.12; `datetime.now(timezone.utc)` é o substituto canônico
- Python docs: `asyncio.run()` nao pode ser chamado quando um event loop já está rodando — confirma o bug latente em `_compute_health`
- APScheduler 3.x docs: `add_job` com `trigger="interval"` e `hours=25` — padrão confirmado por `register_canary_job()` existente usando `minutes=15`

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — todo o código é lido diretamente da base existente, sem dependência externa
- Architecture: HIGH — patterns todos verificados no código real; nenhuma suposicao necessária
- Pitfalls: HIGH — identificados por leitura direta do código (ex: `asyncio.run()` em linha 216 de mis_agent.py)

**Research date:** 2026-03-16
**Valid until:** 2026-04-16 (base estável — nenhuma dependência externa em evolucao ativa)
