# Phase 9: Production Wiring & Proxy Fix - Context

**Gathered:** 2026-03-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Corrigir os 2 gaps de integração identificados no audit v1.0:
1. Scheduler nunca inicia quando `python -m mis dashboard` é executado — jobs de scan/spy/radar nunca disparam automaticamente
2. `proxy_list` não é propagado por `PlatformScanner` → `BaseScraper` — `TypeError` em runtime quando `proxy_list` é não-vazio em `config.yaml`

Não cria novas funcionalidades. Não altera o comportamento de CLI manual (spy, radar, export). Não altera a assinatura pública de `create_app()`.

</domain>

<decisions>
## Implementation Decisions

### Lifespan hook — localização
- Hook vai dentro de `create_app()` via parâmetro `lifespan=` do FastAPI (idiomático)
- `create_app(db_path)` mantém a mesma assinatura — nenhum caller existente muda
- Config carregada internamente no lifespan via `load_config()` — não injetada como parâmetro

### Scheduler jobs registrados no startup
- Registrar: `register_scan_and_spy_job(config)` + `register_radar_jobs(config)` + `register_canary_job()`
- **NÃO** registrar `register_scanner_jobs(config)` — seria redundante (double-scan no mesmo horário que scan+spy)
- Após registrar: `get_scheduler().start()`
- No teardown (`yield`): `get_scheduler().shutdown(wait=False)` — terminação imediata sem aguardar jobs em execução

### Startup error handling
- Se qualquer `register_*` falhar: logar `warning` e continuar (não falhar hard)
- Dashboard sobe e funciona; scans automáticos falham silenciosamente com log
- Comportamento preferido para desenvolvimento e deploy inicial

### register_canary_job
- Incluir no lifespan (conforme audit especifica)
- Nota: é dead code de fato (canary corre inline em `get_briefing_data()`), mas incluir não causa dano e segue o spec

### proxy_list — backward compat
- `PlatformScanner.__init__` recebe `proxy_list: Optional[list[str]] = None` como default
- Callers existentes que usam `PlatformScanner(proxy_url=X)` continuam funcionando sem mudança
- Todos os 3 subclasses (HotmartScanner, KiwifyScanner, ClickBankScanner) recebem o mesmo parâmetro e o passam via `super().__init__(proxy_url=proxy_url, proxy_list=proxy_list)`

### Test strategy
- **Unit tests** (mock): patch `get_scheduler()` com MagicMock, assert que os `register_*` foram chamados no startup
- **Integration tests** (real): usar `TestClient` com lifespan ativo, assert que `scheduler.get_jobs()` contém os jobs esperados após startup
- Testes RED → GREEN para ambos os paths (lifespan + proxy forwarding)

### Claude's Discretion
- Estrutura exata dos test fixtures (conftest, mocks)
- Ordem exata dos `register_*` calls no lifespan (desde que todos estejam presentes)
- Nomes dos job IDs a verificar nos integration tests

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `get_scheduler()` (scheduler.py:28): singleton APScheduler — usar diretamente no lifespan
- `start_scheduler()` / `stop_scheduler()` (scheduler.py:37/45): wrappers seguros para start/shutdown já existem
- `register_scan_and_spy_job(config)` (scheduler.py:126): registra job `scan_and_spy`
- `register_radar_jobs(config)` (radar/__init__.py): registra jobs de radar horário
- `register_canary_job()` (health_monitor.py): registra canary job
- `load_config()` (config.py): já usado em outros handlers do `__main__.py`

### Established Patterns
- `replace_existing=True` em todos os `scheduler.add_job()` calls — safe to call at startup
- `try/except` com structlog `log.error()` + continue — padrão estabelecido em `_scan_and_spy_job()`
- `proxy_url auto-wrapped` em list no BaseScraper — backward compat já resolvida na camada inferior

### Integration Points
- **Gap 1 — lifespan**: `mis/web/app.py` `create_app()` (linha 20) recebe `@asynccontextmanager lifespan`
- **Gap 2 — proxy**: `mis/scanner.py` `PlatformScanner.__init__` (linha 63) e os 3 subclasses:
  - `mis/scanners/hotmart.py` linha 116-121
  - `mis/scanners/kiwify.py` linha 227-232
  - `mis/scanners/clickbank.py` linha 146-151
- `run_all_scanners()` (scanner.py:206) já passa `proxy_list=proxy_list` — só falta `PlatformScanner` aceitar

</code_context>

<specifics>
## Specific Ideas

- O fix de proxy é cirúrgico: 1 linha na assinatura de `PlatformScanner.__init__`, 1 linha no `BaseScraper(...)` call, depois replicar nas 3 subclasses
- O audit especifica o lifespan exato — seguir fielmente como baseline, depois ajustar para omitir `register_scanner_jobs` (redundante)

</specifics>

<deferred>
## Deferred Ideas

- Remover `register_scanner_jobs` como função (está sendo deprecated implicitamente por `register_scan_and_spy_job`) — outra fase
- Tornar `register_canary_job` funcional (conectar à cadeia de startup de verdade) — outra fase
- `shutdown(wait=True)` para produção hardened — pode ser config option em outra fase

</deferred>

---

*Phase: 09-production-wiring-proxy-fix*
*Context gathered: 2026-03-15*
