# Phase 10: Critical Runtime Fixes - Research

**Researched:** 2026-03-16
**Domain:** Python asyncio + APScheduler 3.x + SQLite niche_id resolution
**Confidence:** HIGH

## Summary

This phase closes two surgical defects found in the v1.0 integration audit. Both fixes touch existing code at known exact line ranges; no new modules are required. The research confirms all decisions already captured in CONTEXT.md are technically sound and implementable in a single wave.

**DEFECT-1** (`niche_id=0`): `run_all_scanners()` in `mis/scanner.py` never queries the `niches` table before dispatching scanner coroutines. Products are created with `niche_id=0` (hardcoded default), making the dashboard niche filter inoperant. The fix is a bulk SELECT at the top of the function, building a `slug → id` dict, then injecting the correct `niche_id` onto each `Product` after `asyncio.gather` returns.

**DEFECT-3** (RuntimeError in APScheduler): The 5 job wrappers in `register_radar_jobs()` use `asyncio.run()`, which creates a new event loop — impossible when `AsyncIOScheduler` already owns one. `AsyncIOExecutor` (confirmed source, APScheduler 3.11.2) uses `iscoroutinefunction_partial(job.func)` to branch: `async def` functions are scheduled as `create_task()`, sync functions as `run_in_executor()`. Converting the 4 async wrappers to `async def + await` and the 1 sync wrapper to `async def + asyncio.to_thread()` eliminates the RuntimeError with zero scheduler configuration changes.

**Primary recommendation:** Fix DEFECT-1 in a single Task 1 (~12 lines in `scanner.py`), fix DEFECT-3 in a single Task 2 (~5 keyword changes in `radar/__init__.py`), write RED→GREEN tests for each in a Wave 0 + Task pair. Total code delta is under 30 lines.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**DEFECT-1 — niche_id resolution:**
- Resolução acontece no início de `run_all_scanners()`, antes de despachar qualquer coroutine
- Montar dict `slug → niche_id` via `SELECT id, slug FROM niches` para todos os nichos do config de uma vez
- Se um slug do config não existir na tabela niches: skip + log warning estruturado (não raise, não salvar com niche_id=0)
  - Padrão consistente com Phase 9 (soft-log, não hard-fail)
  - Scanner dos outros nichos continua normalmente
- `niche_id` injetado nos Products após o scanner retornar: `p.niche_id = niche_id_map[slug]` para cada produto retornado
  - Nenhuma mudança na assinatura de `scan_niche()` nem das 3 subclasses de scanner
- DB path via `MIS_DB_PATH` env var (padrão estabelecido) — sem mudança na assinatura de `run_all_scanners(config)`
- Nenhum script de backfill necessário — o próximo scan automático sobrescreverá os produtos existentes via upsert com o niche_id correto

**DEFECT-3 — async radar job wrappers:**
- Converter os 5 wrappers sync de `def _*_job(): asyncio.run(...)` para `async def _*_job(): await ...`
- APScheduler 3.11.2 `AsyncIOScheduler` usa `AsyncIOExecutor` por padrão e detecta `async def` automaticamente via `iscoroutinefunction_partial` — zero configuração extra
- `_cleanup_job` (único wrapper de função sync): usar `asyncio.to_thread()` para não bloquear o event loop:
  ```python
  async def _cleanup_job():
      await asyncio.to_thread(_run_cleanup, db_path)
  ```
- `register_radar_jobs()` permanece sync — apenas os wrappers internos mudam para `async def`

**Test strategy:**
- DEFECT-1: Teste RED → GREEN que insere niche no DB, chama `run_all_scanners()`, verifica niche_id correto, verifica skip+warning para slug inexistente
- DEFECT-3: Unit tests com `AsyncIOScheduler` real + coroutines mockadas, `scheduler.start()`, verificar jobs disparam sem RuntimeError
- Suite completa permanece green após ambos os fixes

**DASH-01 / SCAN-01 / SCAN-02 / SCAN-03:** Todos fechados pelo fix do niche_id — nenhum trabalho adicional.

### Claude's Discretion

- Estrutura exata dos test fixtures (conftest, helpers)
- Nomes dos jobs e chaves do log warning para nicho não encontrado
- Impl. interna do dict slug→id (sqlite3 direto vs sqlite-utils)

### Deferred Ideas (OUT OF SCOPE)

None — discussão ficou dentro do escopo da fase.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SCAN-01 | Sistema varre e rankeia produtos Hotmart por nicho configurado | Fechado pelo fix DEFECT-1: `niche_id` correto após lookup; HotmartScanner já implementado |
| SCAN-02 | Sistema varre e rankeia produtos Kiwify por nicho configurado | Fechado pelo fix DEFECT-1: `niche_id` correto após lookup; KiwifyScanner já implementado |
| SCAN-03 | Sistema varre produtos ClickBank por gravity score | Fechado pelo fix DEFECT-1: `niche_id` correto após lookup; ClickBankScanner já implementado |
| DASH-01 | Dashboard exibe ranking filtrável por plataforma e nicho | Fechado pelo fix DEFECT-1: dashboard já tem filtro por niche_id desde Phase 5; só falha porque niche_id=0 |
| RADAR-01 | Sistema monitora Google Trends por nicho a cada hora | Fechado pelo fix DEFECT-3: `_trends_job` → `async def`, `AsyncIOScheduler` dispara sem RuntimeError |
| RADAR-02 | Sistema coleta Reddit e Quora por nicho configurado | Fechado pelo fix DEFECT-3: `_reddit_quora_job` → `async def` |
| RADAR-03 | Sistema analisa YouTube por nicho com quota management | Fechado pelo fix DEFECT-3: `_youtube_job` → `async def` |
| RADAR-05 | Pipeline do radar é idempotente | Já implementado via INSERT OR IGNORE + UNIQUE index; não quebra com o fix |
| RADAR-06 | Relatório horário consolidado gerado com dores por nicho | Fechado pelo fix DEFECT-3: `_synthesizer_job` → `async def`; synthesizer já implementado |
</phase_requirements>

## Standard Stack

### Core (already installed — no new dependencies)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| apscheduler | 3.11.2 | Cron-based async job scheduling | Already the project scheduler; `AsyncIOExecutor` is the default executor for `AsyncIOScheduler` |
| asyncio | stdlib | Event loop, `to_thread()`, `gather()` | No install needed; `asyncio.to_thread()` available in Python 3.9+ |
| sqlite3 | stdlib | `SELECT id, slug FROM niches` for niche lookup | Already used throughout project; sqlite_utils also available as alternative |
| sqlite_utils | installed | ORM layer on top of sqlite3 | Already used in `_run_all_synthesizers` for niche lookup — identical pattern applies to scanner |
| structlog | installed | Structured warning logging | Already the project logging standard; `log.warning()` pattern established in Phase 9 |
| pytest-asyncio | installed | `@pytest.mark.asyncio` for async tests | Already used across the test suite |

**Installation:** No new packages required.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| sqlite_utils for niche lookup | sqlite3 direct | Both work; sqlite_utils is slightly cleaner but sqlite3 avoids any connection lifecycle concerns. Either is acceptable (Claude's Discretion). |
| `asyncio.to_thread()` | `loop.run_in_executor(None, ...)` | `asyncio.to_thread()` is the modern idiom (Python 3.9+); `run_in_executor` is established in reddit/youtube collectors. Both work — `to_thread()` is preferred per CONTEXT.md. |

## Architecture Patterns

### Recommended Project Structure

No new files or directories required. Changes are limited to:
```
mis/
├── scanner.py              # DEFECT-1 fix: ~12 lines at top of run_all_scanners()
└── radar/
    └── __init__.py         # DEFECT-3 fix: 5 wrapper keyword changes
mis/tests/
├── test_scanner_niche_id.py   # New: RED→GREEN tests for DEFECT-1
└── test_radar_async_jobs.py   # New: RED→GREEN tests for DEFECT-3
```

### Pattern 1: Bulk niche_id lookup before scatter-gather

**What:** Query all niche slugs from DB in one SELECT before dispatching async tasks. Build a dict. Skip slugs not found. Inject resolved IDs into returned products after gather.

**When to use:** Any time config-driven slugs need to be resolved to DB foreign keys before async fan-out.

**Example (sqlite_utils — existing pattern from `_run_all_synthesizers`):**
```python
# Source: mis/radar/__init__.py:93 — existing pattern
import sqlite_utils
db = sqlite_utils.Database(db_path)
row = next(db["niches"].rows_where("slug = ?", [niche_slug]), None)
niche_id = row["id"] if row else None
```

**Example (bulk variant for run_all_scanners):**
```python
import os, sqlite_utils
db_path = os.environ.get("MIS_DB_PATH", "data/mis.db")
db = sqlite_utils.Database(db_path)
niche_id_map = {
    row["slug"]: row["id"]
    for row in db["niches"].rows_where(
        "slug IN ({})".format(",".join("?" * len(slug_list))), slug_list
    )
}
```

**Simpler equivalent (sqlite3 direct — no dependency on sqlite_utils connection lifecycle):**
```python
import os, sqlite3
db_path = os.environ.get("MIS_DB_PATH", "data/mis.db")
conn = sqlite3.connect(db_path)
rows = conn.execute("SELECT id, slug FROM niches").fetchall()
niche_id_map = {slug: nid for nid, slug in rows}
conn.close()
```

### Pattern 2: Async job wrapper for AsyncIOScheduler

**What:** `AsyncIOExecutor` (APScheduler 3.11.2, confirmed from source) checks `iscoroutinefunction_partial(job.func)`. If `True`, it calls `loop.create_task(coroutine)` instead of `run_in_executor`. Converting `def` to `async def` is the only required change for coroutine-wrapping jobs.

**Source:** Confirmed from `AsyncIOExecutor._do_submit_job` source code inspection (APScheduler 3.11.2).

```python
# BEFORE (causes RuntimeError — asyncio.run() inside running loop)
def _trends_job():
    asyncio.run(_run_all_trends(config, db_path))

# AFTER (AsyncIOExecutor detects coroutine, schedules as create_task)
async def _trends_job():
    await _run_all_trends(config, db_path)
```

**For the sync `_cleanup_job` specifically:**
```python
# BEFORE (sync, no event loop issue but blocks the thread)
def _cleanup_job():
    _run_cleanup(db_path)

# AFTER (async wrapper, offloads blocking I/O to thread pool)
async def _cleanup_job():
    await asyncio.to_thread(_run_cleanup, db_path)
```

### Pattern 3: Product niche_id injection post-gather

**What:** After `asyncio.gather()` returns, loop over the products in each result batch and set `p.niche_id = resolved_id`. This avoids changing `scan_niche()` signatures on any of the 3 scanner subclasses.

```python
# After gather resolves:
for key, result in zip(keys, results_raw):
    if isinstance(result, Exception):
        ...
    else:
        _, products = result
        niche_slug = key.split(".")[0]
        niche_id = niche_id_map.get(niche_slug)
        if niche_id is not None:
            for p in products:
                p.niche_id = niche_id
        output[key] = products
```

### Anti-Patterns to Avoid

- **Skip-at-coroutine-registration time instead of post-gather:** Skipping a niche before dispatching its coroutines (when slug not in DB) is correct. Do NOT try to retroactively skip keys after gather when niche_id is missing — a product with niche_id=None would violate NOT NULL constraint.
- **Changing `scan_niche()` signatures:** CONTEXT.md explicitly locks this out. Inject niche_id post-gather only.
- **asyncio.run() inside AsyncIOScheduler jobs:** The exact bug being fixed. Never use `asyncio.run()` inside a function registered with `AsyncIOScheduler`.
- **Using `loop.run_in_executor` instead of `asyncio.to_thread`:** While functionally equivalent, the project decision is `asyncio.to_thread()` for `_cleanup_job`. Use it for consistency.
- **Backfilling existing niche_id=0 rows:** Explicitly out of scope. The next scan upsert will correct them.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Async-safe sync function offload | Custom thread pool wrapper | `asyncio.to_thread()` | Stdlib, clean, handles thread safety; already decided in CONTEXT.md |
| Niche slug→id resolution | In-memory config mapping | `SELECT id, slug FROM niches` (sqlite3 or sqlite_utils) | DB is the single source of truth; config could drift from DB |
| Async job detection in APScheduler | Custom executor subclass | Let APScheduler's `AsyncIOExecutor` handle it via `iscoroutinefunction_partial` | Already wired as default executor — zero config change needed |

**Key insight:** Both fixes are vocabulary-level changes (swap keywords, add a SELECT), not architecture changes. The infrastructure is already correct — only the usage pattern is wrong.

## Common Pitfalls

### Pitfall 1: niche_id lookup scope — fetching per-niche vs all niches at once

**What goes wrong:** Fetching niche_id inside the per-niche loop (one query per niche) instead of a single bulk query at the top of `run_all_scanners()`.
**Why it happens:** Natural coding pattern to resolve each slug as you encounter it.
**How to avoid:** Build the `slug → id` dict in one query before the loop. The CONTEXT.md decision specifies this explicitly.
**Warning signs:** Code that opens a DB connection inside the `for niche in niches:` loop.

### Pitfall 2: Closing the sqlite3/sqlite_utils connection before the coroutines complete

**What goes wrong:** Opening a connection for niche lookup then closing it — but the connection is still referenced in downstream code.
**Why it happens:** Over-careful resource management.
**How to avoid:** Open, fetch all rows into a plain dict, close — the dict is a value object independent of the connection. The connection is not needed after building `niche_id_map`.

### Pitfall 3: asyncio.run() in any APScheduler 3.x async context

**What goes wrong:** `RuntimeError: This event loop is already running` — `asyncio.run()` tries to create a new event loop in a thread that already has one.
**Why it happens:** Pattern works in a plain script context but fails when a scheduler owns the event loop.
**How to avoid:** Always `await` coroutines inside `async def` job wrappers when using `AsyncIOScheduler`. Never call `asyncio.run()` inside a job function.
**Warning signs:** `asyncio.run(some_coroutine())` inside any function registered with `add_job()`.

### Pitfall 4: Forgetting _cleanup_job is sync under the hood

**What goes wrong:** Converting `_cleanup_job` to `async def` without wrapping `_run_cleanup` in `asyncio.to_thread()` — this blocks the event loop during the SQL DELETE + commit.
**Why it happens:** The other 4 wrappers just `await` an already-async function; `_cleanup_job` wraps a sync function.
**How to avoid:** `await asyncio.to_thread(_run_cleanup, db_path)` — explicitly specified in CONTEXT.md.

### Pitfall 5: Test for DEFECT-3 not actually starting the scheduler

**What goes wrong:** Test registers jobs and inspects job objects (existing test pattern) but never calls `scheduler.start()` — the RuntimeError only manifests when the scheduler triggers a job.
**Why it happens:** Existing `test_radar_jobs.py` tests only verify job registration, not job execution.
**How to avoid:** New DEFECT-3 tests must call `scheduler.start()`, trigger a job manually (or advance time), and verify no RuntimeError is raised. Use `AsyncMock` to prevent actual I/O.
**Warning signs:** Test that only asserts `job_ids` membership without ever running the scheduler.

### Pitfall 6: Existing test_scanner_jobs.py uses niche_id=0 in fake_product

**What goes wrong:** After the DEFECT-1 fix, tests that construct `Product(niche_id=0, ...)` and pass them through `run_all_scanners` may fail if the fix raises or skips on unresolved niche_id.
**Why it happens:** `test_partial_failure` in `test_scanner_jobs.py` line 199 uses `niche_id=0` in a fake product. The fix injects niche_id post-gather, overwriting whatever the scanner set — so existing tests that mock scanners should still pass because the scanner mock returns products and the post-gather injection sets the correct id (from DB fixture). Just ensure the new tests seed the DB.
**How to avoid:** New niche_id tests should use `db_path` fixture with migrations run and a real niche row inserted.

## Code Examples

### Verified: AsyncIOExecutor async detection (APScheduler 3.11.2)

```python
# Source: APScheduler 3.11.2 AsyncIOExecutor._do_submit_job (confirmed via inspect)
if iscoroutinefunction_partial(job.func):
    coro = run_coroutine_job(job, job._jobstore_alias, run_times, self._logger.name)
    f = self._eventloop.create_task(coro)
else:
    f = self._eventloop.run_in_executor(
        None, run_job, job, job._jobstore_alias, run_times, self._logger.name
    )
```

Converting a wrapper to `async def` is sufficient — no `executor=` kwarg needed in `add_job()`.

### Verified: sqlite_utils niche lookup (existing pattern in codebase)

```python
# Source: mis/radar/__init__.py:93 — _run_all_synthesizers
db = sqlite_utils.Database(db_path)
row = next(db["niches"].rows_where("slug = ?", [niche_slug]), None)
niche_id = row["id"] if row else None
if not niche_id:
    log.warning("radar.synthesizer.niche_not_in_db", niche_slug=niche_slug)
    continue
```

The scanner fix replicates this pattern as a bulk pre-fetch.

### Verified: asyncio.to_thread() (Python stdlib, Python 3.9+)

```python
# Source: Python docs + runtime confirmation (Python version in use supports it)
import asyncio

async def _cleanup_job():
    await asyncio.to_thread(_run_cleanup, db_path)
```

`asyncio.to_thread()` confirmed available in the runtime (`python -c "import asyncio; print(asyncio.to_thread)"` → function object).

### Verified: structlog soft-log pattern (Phase 9 established)

```python
# Source: mis/radar/__init__.py existing pattern; Phase 9 decision
log.warning("scanner.niche.slug_not_in_db", niche_slug=niche_slug)
continue  # other niches proceed normally
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `asyncio.run()` in sync job wrappers | `async def` wrapper + `await` | Phase 10 (this phase) | Eliminates RuntimeError in AsyncIOScheduler context |
| `niche_id` hardcoded at Product construction time by scanner | `niche_id` resolved from DB + injected post-gather | Phase 10 (this phase) | Products saved with correct FK; dashboard filter becomes functional |

**Deprecated/outdated:**
- `asyncio.run()` inside `AsyncIOScheduler` jobs: replaced by `async def` pattern

## Open Questions

None. All technical decisions are locked in CONTEXT.md and verified via source code inspection.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest + pytest-asyncio (installed) |
| Config file | `mis/tests/conftest.py` (shared fixtures) |
| Quick run command | `python -m pytest mis/tests/test_scanner_niche_id.py mis/tests/test_radar_async_jobs.py -x -q` |
| Full suite command | `python -m pytest mis/tests/ -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SCAN-01 / SCAN-02 / SCAN-03 / DASH-01 | `run_all_scanners()` saves products with correct `niche_id` from DB | integration | `python -m pytest mis/tests/test_scanner_niche_id.py -x` | ❌ Wave 0 |
| SCAN-01 / DASH-01 | Nicho com slug inexistente é skipped com warning, não raise | unit | `python -m pytest mis/tests/test_scanner_niche_id.py::test_unknown_slug_skipped -x` | ❌ Wave 0 |
| RADAR-01 / RADAR-02 / RADAR-03 / RADAR-06 | Jobs async disparam sem RuntimeError em `AsyncIOScheduler` real | integration | `python -m pytest mis/tests/test_radar_async_jobs.py -x` | ❌ Wave 0 |
| RADAR-05 | Suite completa permanece green | regression | `python -m pytest mis/tests/ -q` | ✅ (existing suite) |

### Sampling Rate

- **Per task commit:** `python -m pytest mis/tests/test_scanner_niche_id.py mis/tests/test_radar_async_jobs.py -x -q`
- **Per wave merge:** `python -m pytest mis/tests/ -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `mis/tests/test_scanner_niche_id.py` — covers SCAN-01/02/03/DASH-01 (DEFECT-1 RED tests)
- [ ] `mis/tests/test_radar_async_jobs.py` — covers RADAR-01/02/03/06 (DEFECT-3 RED tests — scheduler.start() + mock coroutines)

*(Existing `mis/tests/conftest.py` already has `db_path` and `temp_config_yaml` fixtures — sufficient for both new test files)*

## Sources

### Primary (HIGH confidence)

- `mis/scanner.py` lines 166–252 — `run_all_scanners()` current implementation (read directly)
- `mis/radar/__init__.py` lines 128–182 — `register_radar_jobs()` with sync wrappers (read directly)
- APScheduler 3.11.2 `AsyncIOExecutor` source (inspected via `inspect.getsource`) — confirms `iscoroutinefunction_partial` branching
- Python stdlib `asyncio.to_thread` — confirmed present in runtime (`python -c "import asyncio; print(asyncio.to_thread)"`)
- `mis/radar/__init__.py` lines 82–105 — `_run_all_synthesizers` niche lookup pattern (existing sqlite_utils pattern to replicate)

### Secondary (MEDIUM confidence)

- APScheduler 3.x official docs — `AsyncIOScheduler` with `AsyncIOExecutor` as default executor; `async def` job support documented
- Python 3.9+ docs — `asyncio.to_thread()` for offloading sync callables to thread pool

### Tertiary (LOW confidence)

None — all claims are verified by direct source inspection.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all libraries already installed; versions confirmed in runtime
- Architecture: HIGH — exact line ranges read; patterns copied from existing working code in same codebase
- Pitfalls: HIGH — derived from direct code reading + APScheduler source inspection, not speculation
- Test strategy: HIGH — existing test patterns in `test_radar_jobs.py` provide direct template

**Research date:** 2026-03-16
**Valid until:** 2026-04-16 (APScheduler 3.x API stable; Python asyncio stdlib stable)
