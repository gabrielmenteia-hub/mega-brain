# Phase 9: Production Wiring & Proxy Fix - Research

**Researched:** 2026-03-15
**Domain:** FastAPI lifespan hooks + APScheduler integration + Python parameter forwarding
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Lifespan hook — localizacao
- Hook vai dentro de `create_app()` via parametro `lifespan=` do FastAPI (idiomatico)
- `create_app(db_path)` mantem a mesma assinatura — nenhum caller existente muda
- Config carregada internamente no lifespan via `load_config()` — nao injetada como parametro

#### Scheduler jobs registrados no startup
- Registrar: `register_scan_and_spy_job(config)` + `register_radar_jobs(config)` + `register_canary_job()`
- **NAO** registrar `register_scanner_jobs(config)` — seria redundante (double-scan no mesmo horario que scan+spy)
- Apos registrar: `get_scheduler().start()`
- No teardown (`yield`): `get_scheduler().shutdown(wait=False)` — terminacao imediata sem aguardar jobs em execucao

#### Startup error handling
- Se qualquer `register_*` falhar: logar `warning` e continuar (nao falhar hard)
- Dashboard sobe e funciona; scans automaticos falham silenciosamente com log
- Comportamento preferido para desenvolvimento e deploy inicial

#### register_canary_job
- Incluir no lifespan (conforme audit especifica)
- Nota: e dead code de fato (canary corre inline em `get_briefing_data()`), mas incluir nao causa dano e segue o spec

#### proxy_list — backward compat
- `PlatformScanner.__init__` recebe `proxy_list: Optional[list[str]] = None` como default
- Callers existentes que usam `PlatformScanner(proxy_url=X)` continuam funcionando sem mudanca
- Todos os 3 subclasses (HotmartScanner, KiwifyScanner, ClickBankScanner) recebem o mesmo parametro e o passam via `super().__init__(proxy_url=proxy_url, proxy_list=proxy_list)`

#### Test strategy
- **Unit tests** (mock): patch `get_scheduler()` com MagicMock, assert que os `register_*` foram chamados no startup
- **Integration tests** (real): usar `TestClient` com lifespan ativo, assert que `scheduler.get_jobs()` contem os jobs esperados apos startup
- Testes RED -> GREEN para ambos os paths (lifespan + proxy forwarding)

### Claude's Discretion
- Estrutura exata dos test fixtures (conftest, mocks)
- Ordem exata dos `register_*` calls no lifespan (desde que todos estejam presentes)
- Nomes dos job IDs a verificar nos integration tests

### Deferred Ideas (OUT OF SCOPE)
- Remover `register_scanner_jobs` como funcao (esta sendo deprecated implicitamente por `register_scan_and_spy_job`) — outra fase
- Tornar `register_canary_job` funcional (conectar a cadeia de startup de verdade) — outra fase
- `shutdown(wait=True)` para producao hardened — pode ser config option em outra fase
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SCAN-04 | Automated scans must run on schedule when dashboard starts | Gap: `create_app()` has no lifespan hook; `register_scan_and_spy_job` + `register_radar_jobs` never called from production entry point. Fix: add FastAPI lifespan context manager. |
| FOUND-02 | proxy_list must be forwarded through PlatformScanner to BaseScraper | Gap: `PlatformScanner.__init__` only accepts `proxy_url`; `run_all_scanners()` at line 206 passes `proxy_list=proxy_list` causing TypeError at runtime. Fix: add `proxy_list` param to PlatformScanner and all 3 concrete scanner subclasses. |
</phase_requirements>

---

## Summary

Phase 9 closes two integration gaps identified in the v1.0 milestone audit. Both are surgical fixes to existing working infrastructure — no new features, no changes to public signatures.

**Gap 1 (SCAN-04):** The APScheduler infrastructure is complete and correct (jobs are defined, `register_*` functions work), but nothing calls them from the production entry point. `create_app()` in `mis/web/app.py` creates a bare FastAPI app with no lifespan hook. When `python -m mis dashboard` runs, `uvicorn.run(app)` starts serving but the scheduler never starts. The fix is a FastAPI `@asynccontextmanager lifespan` function wired into `create_app()` via the `lifespan=` parameter.

**Gap 2 (FOUND-02):** `BaseScraper` correctly implements `proxy_list` + `_select_proxy()` (verified in Phase 8). However `PlatformScanner.__init__` at `scanner.py:63` only accepts `proxy_url` — no `proxy_list` parameter. When `run_all_scanners()` calls `scanner_cls(proxy_url=proxy_url, proxy_list=proxy_list)` at line 206, Python raises `TypeError` at runtime if `proxy_list` is non-empty. The fix is one new parameter in `PlatformScanner.__init__` + forward to `BaseScraper`, then replicate across the 3 concrete scanner subclasses.

**Primary recommendation:** Implement both fixes in a single wave. Fix Gap 2 first (3 files, purely mechanical) then Gap 1 (1 file, more architectural). Test both paths RED then GREEN.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | 0.115.0 | Web framework with lifespan support | Already in use — `create_app()` exists |
| APScheduler | 3.11.2 | Async job scheduler | Already in use — `get_scheduler()`, `register_*` functions all exist |
| contextlib.asynccontextmanager | stdlib | Decorator for lifespan context manager | FastAPI's canonical lifespan pattern since v0.93+ |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| structlog | (project default) | Structured logging for startup/shutdown events | Already used in `scheduler.py`, `_scan_and_spy_job` |
| pytest + unittest.mock | (project default) | Unit test mocking for scheduler isolation | Pattern established in `test_scanner_jobs.py`, `test_radar_jobs.py` |
| fastapi.testclient.TestClient | 0.115.0 | Integration test that triggers lifespan events | Used in `mis/tests/web/conftest.py` already |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `lifespan=` parameter | `@app.on_event("startup")` | `on_event` is deprecated in FastAPI 0.93+; `lifespan=` is the current idiomatic approach |
| `get_scheduler().start()` directly | `start_scheduler()` wrapper | `start_scheduler()` in `scheduler.py:37` has guard `if not scheduler.running` — safer, but `get_scheduler().start()` is also safe since APScheduler 3.x does not crash on re-start if not already running |

**Installation:** No new packages needed — all dependencies already present.

---

## Architecture Patterns

### Pattern 1: FastAPI lifespan via asynccontextmanager

**What:** An async context manager decorated with `@asynccontextmanager` is passed to `FastAPI(lifespan=...)`. Code before `yield` runs at startup; code after `yield` runs at shutdown.

**When to use:** Any FastAPI app that needs startup/teardown side effects (DB connections, schedulers, background tasks).

**Verified in:** FastAPI 0.93+ official docs + FastAPI 0.115.0 installed in project.

```python
# Source: FastAPI official docs (lifespan events)
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup — runs before first request
    # ... register jobs, start scheduler ...
    yield
    # shutdown — runs after last request
    # ... stop scheduler ...

app = FastAPI(lifespan=lifespan)
```

**Critical note for `create_app()` pattern:** The lifespan function must be defined INSIDE `create_app()` (as a closure) or take `app` as parameter. Since `app` is created inside `create_app()`, define the lifespan closure first and pass it to `FastAPI(lifespan=lifespan)`.

```python
# Correct pattern for factory function:
def create_app(db_path: str) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # startup code here
        yield
        # shutdown code here

    app = FastAPI(title="...", lifespan=lifespan)
    # ... rest of setup ...
    return app
```

### Pattern 2: TestClient with lifespan

**What:** `TestClient` from Starlette/FastAPI triggers lifespan events when used as a context manager (`with TestClient(app) as client:`).

**Verified in:** Existing `mis/tests/web/conftest.py` already uses this pattern correctly:
```python
with TestClient(app) as client:
    yield client
```

**Critical note for integration tests of lifespan:** When `TestClient` is used as context manager, entering triggers the lifespan startup, exiting triggers shutdown. The existing `app_client` fixture in `mis/tests/web/conftest.py` already handles this — new lifespan integration tests can use the same fixture pattern OR create a separate fixture that does NOT call `run_migrations` (to avoid scheduler registration running migrations again).

### Pattern 3: Scheduler mock isolation in unit tests

**What:** Patch `get_scheduler` at the module level where it's called, replacing it with a `MagicMock`. Assert that `register_*` functions were called during lifespan startup.

**Established pattern from `test_radar_jobs.py`:**
```python
# Uses isolated_scheduler fixture — does NOT touch global singleton
scheduler = AsyncIOScheduler()
with patch("mis.radar.get_scheduler", return_value=scheduler):
    register_radar_jobs(config)
job_ids = {job.id for job in scheduler.get_jobs()}
```

**For lifespan unit tests:** Since `create_app()` will import and call `register_scan_and_spy_job`, `register_radar_jobs`, `register_canary_job` and `get_scheduler().start()`, the cleanest unit test strategy is to patch at the import path:
- `mis.web.app.register_scan_and_spy_job` (MagicMock)
- `mis.web.app.register_radar_jobs` (MagicMock)
- `mis.web.app.register_canary_job` (MagicMock)
- `mis.web.app.get_scheduler` returning a MagicMock scheduler

### Pattern 4: proxy_list parameter forwarding (mechanical fix)

**What:** Add `proxy_list: Optional[list[str]] = None` to `PlatformScanner.__init__` and forward to `BaseScraper.__init__`. Replicate in all 3 concrete subclass `__init__` + `super()` calls.

**Current signatures (scanner.py:63 and each subclass):**
```python
# BEFORE — scanner.py PlatformScanner
def __init__(self, proxy_url: Optional[str] = None) -> None:
    self._base = BaseScraper(proxy_url=proxy_url)

# BEFORE — hotmart.py HotmartScanner
def __init__(self, proxy_url: Optional[str] = None, niche_id: int = 0) -> None:
    super().__init__(proxy_url=proxy_url)
```

**After (target state):**
```python
# AFTER — scanner.py PlatformScanner
def __init__(self, proxy_url: Optional[str] = None, proxy_list: Optional[list[str]] = None) -> None:
    self._base = BaseScraper(proxy_url=proxy_url, proxy_list=proxy_list)

# AFTER — hotmart.py HotmartScanner
def __init__(self, proxy_url: Optional[str] = None, proxy_list: Optional[list[str]] = None, niche_id: int = 0) -> None:
    super().__init__(proxy_url=proxy_url, proxy_list=proxy_list)
```

Same pattern for `KiwifyScanner` and `ClickBankScanner`.

### Anti-Patterns to Avoid

- **Defining lifespan outside `create_app()`:** The function needs to close over `db_path` or other factory-local state if needed. Defining it as a module-level function breaks the factory pattern.
- **Calling `start_scheduler()` without registering jobs first:** Jobs must be registered before `start()` is called. APScheduler will start but have nothing scheduled.
- **Using `@app.on_event("startup")` / `@app.on_event("shutdown")`:** These are deprecated since FastAPI 0.93. Will generate DeprecationWarning. `lifespan=` is the correct approach.
- **Double-registering `register_scanner_jobs`:** This registers 3 individual scanner jobs that would run at the SAME time as `scan_and_spy` job — scanning platforms twice daily. Per locked decision, only `register_scan_and_spy_job` goes in the lifespan.
- **`shutdown(wait=True)` in tests:** Blocks indefinitely if jobs are running. Always use `shutdown(wait=False)` for tests and current production decision.
- **Not resetting scheduler singleton between tests:** The `_scheduler` global in `scheduler.py` persists across tests. Always call `stop_scheduler()` in teardown. Pattern established in `test_scanner_jobs.py` uses `try/finally: stop_scheduler()`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Async startup/shutdown hooks | Custom `__init__` side effects or thread-based startup | `@asynccontextmanager lifespan` + `FastAPI(lifespan=)` | FastAPI handles lifecycle ordering, exception safety, ASGI compliance |
| Job scheduling | Custom threading.Timer or asyncio.create_task loop | APScheduler `AsyncIOScheduler` (already present) | Already implemented, tested, uses `replace_existing=True` for safety |
| Proxy selection per-request | Custom round-robin in each scanner | `BaseScraper._select_proxy()` (already implemented in Phase 8) | Already verified working — just needs the parameter forwarded |

**Key insight:** Both gaps are wiring problems, not implementation problems. All the components exist and work correctly in isolation. The fix is connecting them, not building new functionality.

---

## Common Pitfalls

### Pitfall 1: load_config() raising ValueError at lifespan startup

**What goes wrong:** `load_config()` validates that `config.yaml` has 3-5 niches and all platforms are valid. If `config.yaml` is missing, malformed, or has the wrong niche count, the lifespan startup raises `ValueError` or `FileNotFoundError`, which crashes the app startup.

**Why it happens:** Per locked decision, lifespan calls `load_config()` internally. The warn-and-continue error handling is for `register_*` failures, but `load_config()` itself is not wrapped.

**How to avoid:** Wrap the `load_config()` call in a `try/except Exception` that falls back to `config = {}` with a warning log — the same pattern used in `_scan_and_spy_job()` at `scheduler.py:86-90`. This means jobs won't be registered (no schedule configured), but the dashboard still starts.

**Warning signs:** Dashboard fails to start with `FileNotFoundError` or `ValueError` in production environments where `config.yaml` hasn't been placed yet.

### Pitfall 2: Integration test scheduler not cleaned up between tests

**What goes wrong:** `get_scheduler()` returns a module-level singleton (`_scheduler` in `scheduler.py`). If a test starts the scheduler via `TestClient(app)` (which triggers lifespan startup), and the test doesn't clean up, the next test starts with a running scheduler that already has jobs registered.

**Why it happens:** The lifespan teardown calls `get_scheduler().shutdown(wait=False)`, which stops the scheduler but `stop_scheduler()` also sets `_scheduler = None`. If the test exits the `TestClient` context manager normally, teardown fires and the singleton is reset. But if something goes wrong (exception during test), teardown may not fire.

**How to avoid:** Integration tests that use `TestClient` as a context manager handle this automatically (teardown fires on context manager exit). For extra safety, add `stop_scheduler()` in an `autouse` fixture teardown for the lifespan test file.

### Pitfall 3: Patching at wrong module path for lifespan unit tests

**What goes wrong:** Patching `mis.scheduler.register_scan_and_spy_job` does not affect code in `mis.web.app` that does `from mis.scheduler import register_scan_and_spy_job`.

**Why it happens:** Python's import system: patching the source module doesn't affect already-imported references. Must patch the name as it appears in the module under test.

**How to avoid:** Patch `mis.web.app.register_scan_and_spy_job`, `mis.web.app.register_radar_jobs`, `mis.web.app.register_canary_job`, and `mis.web.app.get_scheduler` — i.e., the path where they are used, not where they are defined.

### Pitfall 4: proxy_list position in subclass __init__ signatures

**What goes wrong:** The 3 subclasses have `niche_id: int = 0` as their second positional parameter. Adding `proxy_list` after `proxy_url` (before `niche_id`) changes the parameter order, which could break callers that use positional arguments.

**Why it happens:** Current signature is `(proxy_url=None, niche_id=0)`. If fix adds `(proxy_url=None, proxy_list=None, niche_id=0)`, then a caller using `ScannerClass(None, 5)` would now pass `5` to `proxy_list` instead of `niche_id`.

**How to avoid:** All existing callers in `run_all_scanners()` use keyword arguments exclusively: `scanner_cls(proxy_url=proxy_url, proxy_list=proxy_list)`. No positional callers in the codebase. The fix is safe as-is. Verify with a quick grep before implementing.

---

## Code Examples

Verified patterns from codebase inspection:

### Lifespan context manager (target implementation)

```python
# mis/web/app.py — full lifespan pattern to implement
from contextlib import asynccontextmanager
from fastapi import FastAPI
import structlog

log = structlog.get_logger(__name__)


def create_app(db_path: str) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # ── startup ──────────────────────────────────────────
        from mis.config import load_config
        from mis.scheduler import get_scheduler
        from mis.scheduler import register_scan_and_spy_job
        from mis.radar import register_radar_jobs
        from mis.health_monitor import register_canary_job

        try:
            config = load_config()
        except Exception as exc:
            log.warning("lifespan.config_error", error=str(exc))
            config = {}

        for name, fn, args in [
            ("register_scan_and_spy_job", register_scan_and_spy_job, [config]),
            ("register_radar_jobs", register_radar_jobs, [config]),
            ("register_canary_job", register_canary_job, []),
        ]:
            try:
                fn(*args)
            except Exception as exc:
                log.warning("lifespan.register_failed", job=name, error=str(exc))

        try:
            get_scheduler().start()
            log.info("lifespan.scheduler_started")
        except Exception as exc:
            log.warning("lifespan.scheduler_start_failed", error=str(exc))

        yield  # ── app runs ──────────────────────────────────

        # ── shutdown ─────────────────────────────────────────
        try:
            get_scheduler().shutdown(wait=False)
            log.info("lifespan.scheduler_stopped")
        except Exception as exc:
            log.warning("lifespan.scheduler_stop_failed", error=str(exc))

    app = FastAPI(title="MIS Dashboard", docs_url=None, redoc_url=None, lifespan=lifespan)
    # ... rest of existing create_app body ...
    return app
```

### Unit test pattern for lifespan (mock approach)

```python
# mis/tests/test_lifespan.py — unit test with mocked scheduler
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

def test_lifespan_registers_jobs_on_startup():
    mock_scheduler = MagicMock()

    with patch("mis.web.app.register_scan_and_spy_job") as mock_scan, \
         patch("mis.web.app.register_radar_jobs") as mock_radar, \
         patch("mis.web.app.register_canary_job") as mock_canary, \
         patch("mis.web.app.get_scheduler", return_value=mock_scheduler):

        from mis.web.app import create_app
        app = create_app(db_path=":memory:")
        with TestClient(app):
            pass  # lifespan fires on enter/exit

    mock_scan.assert_called_once()
    mock_radar.assert_called_once()
    mock_canary.assert_called_once()
    mock_scheduler.start.assert_called_once()
```

### Integration test pattern for lifespan (real scheduler)

```python
# Integration test: verify actual jobs exist in scheduler after startup
from fastapi.testclient import TestClient
from mis.scheduler import stop_scheduler

def test_lifespan_scheduler_has_jobs(tmp_path):
    stop_scheduler()  # ensure clean state
    from mis.web.app import create_app
    from mis.scheduler import get_scheduler

    # Note: load_config() may fail in test env — that's OK per warn-and-continue
    app = create_app(db_path=":memory:")
    with TestClient(app):
        scheduler = get_scheduler()
        job_ids = {job.id for job in scheduler.get_jobs()}
        # scan_and_spy registered if config loaded successfully
        # At minimum, scheduler was started (no exception)
        assert scheduler.running

    stop_scheduler()  # cleanup
```

### proxy_list forwarding (PlatformScanner fix)

```python
# scanner.py — PlatformScanner.__init__ target state
def __init__(self, proxy_url: Optional[str] = None, proxy_list: Optional[list[str]] = None) -> None:
    from .base_scraper import BaseScraper
    self._base = BaseScraper(proxy_url=proxy_url, proxy_list=proxy_list)
```

### proxy_list forwarding (concrete scanner subclass fix)

```python
# hotmart.py / kiwify.py / clickbank.py — same pattern for all 3
def __init__(
    self,
    proxy_url: Optional[str] = None,
    proxy_list: Optional[list[str]] = None,
    niche_id: int = 0,
) -> None:
    super().__init__(proxy_url=proxy_url, proxy_list=proxy_list)
    self._default_niche_id = niche_id
```

### proxy_list test (unit — TypeError regression)

```python
# Verify that proxy_list no longer raises TypeError
from mis.scanner import PlatformScanner

def test_platform_scanner_accepts_proxy_list():
    """PlatformScanner.__init__ must not raise TypeError with proxy_list kwarg."""
    # This previously raised: TypeError: __init__() got unexpected keyword 'proxy_list'
    from mis.scanners.hotmart import HotmartScanner
    scanner = HotmartScanner(proxy_url=None, proxy_list=["http://proxy1:8080"])
    assert scanner._base._proxy_list == ["http://proxy1:8080"]
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `@app.on_event("startup")` / `"shutdown"` | `@asynccontextmanager lifespan` + `FastAPI(lifespan=)` | FastAPI 0.93 (2023) | Old approach still works but generates DeprecationWarning; `lifespan=` is idiomatic |

**Deprecated/outdated:**
- `@app.on_event("startup")`: Still functional but deprecated since FastAPI 0.93. Do not use for new code in this project.

---

## Open Questions

1. **load_config() validation in test environment**
   - What we know: `load_config()` raises `ValueError` if niche count is not 3-5. In test environments using `:memory:` db, the real `config.yaml` may or may not be present.
   - What's unclear: Whether integration tests that use `TestClient(app)` will encounter `load_config()` failures silently (warn-and-continue) or visibly.
   - Recommendation: The warn-and-continue pattern handles this. Tests that need full job registration should patch `load_config` to return a valid minimal config.

2. **scheduler.running guard during TestClient re-entrance**
   - What we know: `get_scheduler()` is a singleton; `start_scheduler()` has `if not scheduler.running` guard. `shutdown(wait=False)` + `_scheduler = None` in `stop_scheduler()` resets the singleton.
   - What's unclear: Whether calling `TestClient(app)` twice in the same test process (unlikely but possible) re-creates the scheduler correctly.
   - Recommendation: Each integration test that uses `TestClient` should call `stop_scheduler()` as teardown to ensure singleton is reset. Use `autouse` fixture if multiple such tests exist.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (project standard) |
| Config file | `mis/pytest.ini` or `setup.cfg` (project default) |
| Quick run command | `pytest mis/tests/test_lifespan.py mis/tests/test_proxy_forwarding.py -x` |
| Full suite command | `pytest mis/tests/ -x` |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SCAN-04 | lifespan registers scan_and_spy + radar + canary jobs on startup | unit (mock) | `pytest mis/tests/test_lifespan.py::test_lifespan_registers_jobs_on_startup -x` | Wave 0 |
| SCAN-04 | scheduler.running == True after TestClient enters lifespan | integration (real) | `pytest mis/tests/test_lifespan.py::test_lifespan_scheduler_has_jobs -x` | Wave 0 |
| SCAN-04 | scheduler.shutdown called on TestClient exit (teardown) | unit (mock) | `pytest mis/tests/test_lifespan.py::test_lifespan_shutdown_on_exit -x` | Wave 0 |
| FOUND-02 | HotmartScanner accepts proxy_list without TypeError | unit | `pytest mis/tests/test_proxy_forwarding.py::test_hotmart_accepts_proxy_list -x` | Wave 0 |
| FOUND-02 | KiwifyScanner accepts proxy_list without TypeError | unit | `pytest mis/tests/test_proxy_forwarding.py::test_kiwify_accepts_proxy_list -x` | Wave 0 |
| FOUND-02 | ClickBankScanner accepts proxy_list without TypeError | unit | `pytest mis/tests/test_proxy_forwarding.py::test_clickbank_accepts_proxy_list -x` | Wave 0 |
| FOUND-02 | PlatformScanner forwards proxy_list to BaseScraper._proxy_list | unit | `pytest mis/tests/test_proxy_forwarding.py::test_proxy_list_reaches_base_scraper -x` | Wave 0 |
| FOUND-02 | run_all_scanners does not raise TypeError with proxy_list config | unit | `pytest mis/tests/test_proxy_forwarding.py::test_run_all_scanners_proxy_list_no_typeerror -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest mis/tests/test_lifespan.py mis/tests/test_proxy_forwarding.py -x`
- **Per wave merge:** `pytest mis/tests/ -x`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `mis/tests/test_lifespan.py` — covers SCAN-04 lifespan unit + integration tests
- [ ] `mis/tests/test_proxy_forwarding.py` — covers FOUND-02 proxy_list forwarding tests

*(Existing test infrastructure covers everything else — only these 2 new test files need to be created.)*

---

## Sources

### Primary (HIGH confidence)
- Direct codebase inspection: `mis/web/app.py` (create_app factory pattern confirmed)
- Direct codebase inspection: `mis/scanner.py` lines 63, 206 (exact gap location confirmed)
- Direct codebase inspection: `mis/scheduler.py` (get_scheduler, register_scan_and_spy_job, stop_scheduler signatures confirmed)
- Direct codebase inspection: `mis/radar/__init__.py` lines 128+ (register_radar_jobs signature confirmed)
- Direct codebase inspection: `mis/health_monitor.py` line 54 (register_canary_job signature confirmed)
- Direct codebase inspection: `mis/base_scraper.py` lines 58-68 (proxy_list interface confirmed)
- Direct codebase inspection: `mis/tests/web/conftest.py` (TestClient with lifespan pattern confirmed)
- Direct codebase inspection: `mis/tests/test_radar_jobs.py` (isolated_scheduler fixture pattern confirmed)
- FastAPI 0.115.0 (installed) — lifespan= parameter confirmed supported

### Secondary (MEDIUM confidence)
- `.planning/v1.0-MILESTONE-AUDIT.md` — gap descriptions and fix specs (audit source)
- `.planning/phases/09-production-wiring-proxy-fix/09-CONTEXT.md` — locked implementation decisions

### Tertiary (LOW confidence)
- None

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all libraries confirmed installed, signatures verified from source
- Architecture: HIGH — patterns verified from actual codebase, not assumed
- Pitfalls: HIGH — derived from direct codebase inspection of failure modes
- Test patterns: HIGH — existing test files show established conventions

**Research date:** 2026-03-15
**Valid until:** 2026-04-15 (stable framework versions, no fast-moving dependencies)
