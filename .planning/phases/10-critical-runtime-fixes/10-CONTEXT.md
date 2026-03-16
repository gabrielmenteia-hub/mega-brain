# Phase 10: Critical Runtime Fixes - Context

**Gathered:** 2026-03-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Corrigir os 2 defects críticos identificados no audit v1.0:
1. **DEFECT-1**: `run_all_scanners()` salva todos os produtos com `niche_id=0` — `niche_id` nunca é resolvido via DB antes de salvar
2. **DEFECT-3**: Os 5 wrappers de radar jobs usam `asyncio.run()` dentro de um scheduler que já possui um event loop ativo (`AsyncIOScheduler`), causando `RuntimeError`

Fechar esses dois defects fecha também SCAN-01, SCAN-02, SCAN-03 e DASH-01 — os scanners já estão implementados e o dashboard já tem filtro por nicho; o problema é apenas que os produtos são salvos com `niche_id=0`, tornando o filtro inoperante.

Nenhum novo scanner, nenhuma UI adicional, nenhum backfill de dados existentes.

</domain>

<decisions>
## Implementation Decisions

### DEFECT-1 — niche_id resolution

- Resolução acontece **no início de `run_all_scanners()`**, antes de despachar qualquer coroutine
- Montar dict `slug → niche_id` via `SELECT id, slug FROM niches` para todos os nichos do config de uma vez
- Se um slug do config **não existir na tabela niches**: **skip + log warning estruturado** (não raise, não salvar com niche_id=0)
  - Padrão consistente com Phase 9 (soft-log, não hard-fail)
  - Scanner dos outros nichos continua normalmente
- `niche_id` injetado nos Products **após o scanner retornar**: `p.niche_id = niche_id_map[slug]` para cada produto retornado
  - Nenhuma mudança na assinatura de `scan_niche()` nem das 3 subclasses de scanner
- DB path via **`MIS_DB_PATH` env var** (padrão estabelecido) — sem mudança na assinatura de `run_all_scanners(config)`
- Nenhum script de backfill necessário — o próximo scan automático sobrescreverá os produtos existentes via upsert com o niche_id correto

### DEFECT-3 — async radar job wrappers

- Converter os 5 wrappers sync de `def _*_job(): asyncio.run(...)` para **`async def _*_job(): await ...`**
- APScheduler 3.11.2 `AsyncIOScheduler` usa `AsyncIOExecutor` por padrão e detecta `async def` automaticamente via `iscoroutinefunction_partial` — **zero configuração extra**
- `_cleanup_job` (único wrapper de função sync): usar **`asyncio.to_thread()`** para não bloquear o event loop:
  ```python
  async def _cleanup_job():
      await asyncio.to_thread(_run_cleanup, db_path)
  ```
- `register_radar_jobs()` permanece sync — apenas os wrappers internos mudam para `async def`

### Test strategy

- **DEFECT-1**: Teste RED → GREEN que:
  1. Insere niche no DB via fixture
  2. Chama `run_all_scanners()` com config contendo o slug
  3. Verifica que produtos salvos têm `niche_id` correto (não zero)
  4. Verifica que nicho com slug inexistente é skipped com warning (não raise)
- **DEFECT-3**: Unit tests com **`AsyncIOScheduler` real + coroutines mockadas**:
  1. Registrar os 5 jobs async
  2. Fazer `scheduler.start()`
  3. Verificar que jobs disparam sem `RuntimeError`
  4. Coroutines mockadas para não fazer I/O real
- Suite completa permanece green após ambos os fixes

### DASH-01 / SCAN-01 / SCAN-02 / SCAN-03

- Todos fechados pelo fix do niche_id — nenhum trabalho adicional
- Todos os 3 scanners já implementados (hotmart.py, kiwify.py, clickbank.py) e no `SCANNER_MAP`
- Dashboard já tem filtro por plataforma e nicho implementado desde Phase 5

### Claude's Discretion

- Estrutura exata dos test fixtures (conftest, helpers)
- Nomes dos jobs e chaves do log warning para nicho não encontrado
- Impl. interna do dict slug→id (sqlite3 direto vs sqlite-utils)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets

- `run_all_scanners(config)` (`mis/scanner.py:166`): ponto de entrada do fix DEFECT-1 — loop de nichos já existe (linha 213), adicionar resolução no topo
- `save_products()` (`mis/scanner.py:~120`): chamada após `asyncio.gather` — niche_id deve estar correto antes desta chamada
- `register_radar_jobs(config)` (`mis/radar/__init__.py:140`): contém os 5 wrappers sync a converter
- `_run_all_trends`, `_run_all_reddit_quora`, `_run_all_youtube`, `_run_all_synthesizers` (`mis/radar/__init__.py`): já são `async def` — wrappers apenas precisam `await` em vez de `asyncio.run()`
- `_run_cleanup(db_path)` (`mis/radar/__init__.py`): função sync — requer `asyncio.to_thread()`
- `_get_db_path()` (`mis/radar/__init__.py`): helper interno que lê `MIS_DB_PATH` — reutilizar no scanner

### Established Patterns

- `MIS_DB_PATH` env var como fonte do db_path (Phase 4+)
- `INSERT OR IGNORE` + UNIQUE index para idempotência em upserts (Phase 4)
- `replace_existing=True` em `scheduler.add_job()` (Phase 4)
- Soft-log via structlog `log.warning()` + continue (Phase 9)
- `asyncio.to_thread()` não usado ainda, mas `loop.run_in_executor()` já estabelecido em reddit_collector.py e youtube_collector.py como equivalente

### Integration Points

- **DEFECT-1**: `mis/scanner.py` função `run_all_scanners()` linhas 193-266 — adicionar lookup de niche_id antes do loop de coroutines
- **DEFECT-3**: `mis/radar/__init__.py` funções `_trends_job`, `_reddit_quora_job`, `_youtube_job`, `_synthesizer_job`, `_cleanup_job` (linhas 148-162)

</code_context>

<specifics>
## Specific Ideas

- Fix do niche_id é cirúrgico: ~10 linhas no topo de `run_all_scanners()` + loop de injeção após `asyncio.gather`
- Fix async é ainda mais cirúrgico: trocar `def` por `async def` e `asyncio.run(x)` por `await x` em 4 wrappers + `asyncio.to_thread()` em 1

</specifics>

<deferred>
## Deferred Ideas

None — discussão ficou dentro do escopo da fase.

</deferred>

---

*Phase: 10-critical-runtime-fixes*
*Context gathered: 2026-03-16*
