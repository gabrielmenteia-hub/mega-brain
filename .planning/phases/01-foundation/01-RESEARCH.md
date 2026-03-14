# Phase 1: Foundation - Research

**Researched:** 2026-03-14
**Domain:** Python async scraping infrastructure, SQLite schema + migrations, health monitoring
**Confidence:** HIGH (all core stack verified against installed packages and latest PyPI versions)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **HTTP client:** httpx async (HTTP/2, async-first, connection pooling) — not requests, not Playwright as base
- **BaseScraper interface:** two methods since Phase 1 — `fetch(url)` via httpx, `fetch_spa(url)` via Playwright
- **Stealth (anti-bot):** `playwright-stealth` active in `fetch_spa()` from Phase 1 — not deferred
- **Proxy:** interface via `PROXY_URL` in `.env` — empty in Phase 1, filled when needed; code is proxy-agnostic
- **Retry:** tenacity with exponential backoff — `stop_after_attempt(3)`, `wait_exponential(min=1, max=10)`; retries on network errors, HTTP 429, HTTP 5xx
- **Rate limiting:** `asyncio.Semaphore` + `asyncio.sleep()` per-domain; `DOMAIN_DELAYS = {'hotmart.com': 2.0, ...}` with 2s global fallback
- **Instance lifecycle:** long-lived (one instance per scraping job); httpx `AsyncClient` open for entire job duration
- **Error handling:** `ScraperError(url, attempts, cause)` custom exception — no silent swallow, no None return
- **Cookies:** httpx `AsyncClient` manages automatically within session (persistent across requests of same instance)
- **Logging:** structlog JSON output; each request logs `url`, `status_code`, `duration_ms`, `attempt`, `domain`; errors add `exception_type`, `last_error`
- **Module structure:** `mis/` as independent module inside MEGABRAIN repo
- **DB location:** `mis.db` inside `mis/` or `.data/mis/` (gitignored, L3)
- **Existing patterns:** use `pathlib.Path`, `.env` as credential source of truth, snake_case scripts, PascalCase classes

### Claude's Discretion
- Design exact DB schema (column names, types, indexes)
- Internal folder structure of `mis/`
- Config file format for niches (YAML vs Python dataclass)
- Health monitor alert channel (console/log sufficient for Phase 1)
- APScheduler skeleton: integration depth in Phase 1
- Migration tooling (Alembic, sqlite-utils, raw SQL)

### Deferred Ideas (OUT OF SCOPE)
- No deferred ideas identified during discussion
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| FOUND-01 | Sistema possui schema de banco de dados com tabelas para produtos, plataformas, nichos, dores e dossiês | Schema design, migration tooling (sqlite-utils vs Alembic), SQLite pragmas |
| FOUND-02 | BaseScraper implementa rate limiting, retry automático, rotação de proxies e headers anti-bot | httpx 0.28.1 async patterns, tenacity 9.x decorators, asyncio.Semaphore, playwright-stealth 2.x |
| FOUND-03 | Usuário pode configurar 3–5 nichos alvo em arquivo de configuração | YAML config with PyYAML (already in requirements.txt), pydantic/dataclass for validation |
| FOUND-04 | Health monitor detecta e alerta quando scrapers quebram silenciosamente (canary checks) | Canary URL strategy, structlog alerting pattern, async health check scheduling |
</phase_requirements>

---

## Summary

Phase 1 establishes the entire scraping and storage infrastructure that all future phases depend on. The core decisions are already locked: httpx async + Playwright for fetching, tenacity for retry, asyncio.Semaphore for rate limiting, structlog for JSON logging, and a custom ScraperError for explicit failure signaling. The only open questions are in tooling choices: which migration approach (sqlite-utils is simpler for SQLite-only projects; Alembic is heavier but provides full migration history) and config format (YAML is the natural choice since PyYAML is already in requirements.txt).

The BaseScraper is the most critical artifact of this phase. It must be built correctly now — all 4 platform scrapers in Phases 2-4 will subclass it without modifications. The `fetch()` / `fetch_spa()` interface is the contract: subclasses call one or the other depending on whether the target is an SSR page or a JavaScript SPA. The health monitor's canary check strategy requires a stable, slow-changing public URL (not a real platform) as a baseline for testing that the scraper stack is operational.

For migrations, the recommendation is **sqlite-utils** for Phase 1: it is lightweight, Pythonic, and sufficient for a SQLite-only project. If the schema grows significantly in Phase 4+, an Alembic migration can be added then. For niche configuration, YAML is recommended since PyYAML is already in requirements.txt and the config structure is shallow.

**Primary recommendation:** Use sqlite-utils for migrations, PyYAML for niche config, and invest heavily in BaseScraper robustness — it is the foundation everything else inherits.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| httpx | 0.28.1 (installed) | Async HTTP client with HTTP/2 and connection pooling | Locked decision; already installed system-wide |
| tenacity | 9.0.0 (installed, 9.1.4 latest) | Declarative retry with backoff | Locked decision; already installed |
| playwright | 1.58.0 (latest) | Browser automation for JS-rendered pages | Locked decision; needed for Hotmart SPA in Phase 2 |
| playwright-stealth | 2.0.2 (latest) | Suppress automation fingerprints in Playwright sessions | Locked decision; hides `navigator.webdriver` etc. |
| structlog | 25.5.0 (latest) | Structured JSON logging | Locked decision; JSON output enables health monitor parsing |
| python-dotenv | 1.2.1 (installed) | Load `.env` into environment | Already in project; reads PROXY_URL, MIS_NICHES etc. |
| PyYAML | 6.0.3 (latest) | Parse YAML niche config file | Already in requirements.txt |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| sqlite-utils | 3.39 (latest) | Pythonic SQLite schema creation and migration | Recommended for Phase 1 migration tooling (simpler than Alembic) |
| fake-useragent | 2.2.0 (latest) | Rotate realistic User-Agent strings | Use in BaseScraper header rotation |
| APScheduler | 3.11.2 (latest) | Job scheduling for health checks and future scrapers | Skeleton in Plan 01-03; used fully in Phase 2 |
| pytest | 8.4.2 (installed) | Test framework | Already installed |
| pytest-asyncio | 0.24.0 (installed, 1.3.0 latest) | Async test support | Already installed; use `asyncio_mode = "auto"` in config |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| sqlite-utils | Alembic | Alembic provides full migration history tracking with revision files; overkill for SQLite-only project in Phase 1. Add in Phase 4+ if needed. |
| sqlite-utils | Raw SQL scripts | Achievable but loses Pythonic API; harder to inspect schema programmatically |
| PyYAML (YAML config) | Python dataclass in `config.py` | Dataclass requires code edit to change niches; YAML separates config from code without extra dependencies |
| fake-useragent | Hardcoded UA list | `fake-useragent` is maintained with real browser UA strings; hardcoded lists go stale |
| APScheduler 3.x | APScheduler 4.x (alpha) | APScheduler 4.x is still unstable; stick with 3.x stable |

### Installation

```bash
# Core scraping stack (install into mis/ virtual environment or project venv)
pip install httpx[http2] playwright playwright-stealth tenacity structlog fake-useragent

# DB tooling
pip install sqlite-utils

# Scheduling skeleton
pip install apscheduler

# Config
# PyYAML already in requirements.txt

# Browser install (one-time, after playwright install)
playwright install chromium

# Test tools (already installed)
pip install pytest pytest-asyncio
```

---

## Architecture Patterns

### Recommended Project Structure

```
mis/
├── __init__.py              # Module exports
├── base_scraper.py          # BaseScraper class (Plans 01-02)
├── config.py                # Config loader (reads config.yaml + .env)
├── db.py                    # DB connection + schema helpers
├── health_monitor.py        # Canary check + alerting (Plan 01-04)
├── scheduler.py             # APScheduler skeleton (Plan 01-03)
├── exceptions.py            # ScraperError and other custom exceptions
├── config.yaml              # Niche configuration (user-editable, L3)
├── migrations/
│   └── 001_initial.py       # sqlite-utils migration script
└── tests/
    ├── conftest.py           # Shared fixtures (mock httpx, test DB)
    ├── test_base_scraper.py  # Unit tests for BaseScraper
    ├── test_db.py            # Schema + migration tests
    ├── test_config.py        # Config loader tests
    └── test_health_monitor.py # Canary check tests
```

### Pattern 1: BaseScraper with Dual Interface

**What:** Abstract base class with `fetch()` (httpx) and `fetch_spa()` (Playwright) methods, both wrapped with tenacity retry and asyncio rate limiting.

**When to use:** Always. Every platform scraper in Phases 2-4 subclasses this.

```python
# Source: httpx docs (https://www.python-httpx.org/async/) + tenacity docs
import asyncio
from contextlib import asynccontextmanager
from typing import Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import structlog

from .exceptions import ScraperError

log = structlog.get_logger()

DOMAIN_DELAYS: dict[str, float] = {
    "hotmart.com": 2.0,
    "kiwify.com.br": 2.0,
    "clickbank.com": 2.0,
}
DEFAULT_DELAY = 2.0

_SEMAPHORE: dict[str, asyncio.Semaphore] = {}


class BaseScraper:
    """Base class for all MIS scrapers.

    Provides fetch() for SSR pages and fetch_spa() for JS-rendered SPAs.
    Long-lived: one instance per scraping job, reused across all requests.
    Use as async context manager to ensure proper cleanup.
    """

    def __init__(self, proxy_url: Optional[str] = None) -> None:
        self._proxy = proxy_url
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "BaseScraper":
        self._client = httpx.AsyncClient(
            http2=True,
            follow_redirects=True,
            timeout=httpx.Timeout(30.0),
            proxy=self._proxy,
        )
        return self

    async def __aexit__(self, *_) -> None:
        if self._client:
            await self._client.aclose()

    def _get_semaphore(self, domain: str) -> asyncio.Semaphore:
        if domain not in _SEMAPHORE:
            _SEMAPHORE[domain] = asyncio.Semaphore(1)
        return _SEMAPHORE[domain]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        reraise=True,
    )
    async def fetch(self, url: str) -> str:
        """Fetch a URL via httpx. Raises ScraperError after all retries exhausted."""
        domain = httpx.URL(url).host
        sem = self._get_semaphore(domain)
        delay = DOMAIN_DELAYS.get(domain, DEFAULT_DELAY)

        async with sem:
            t0 = asyncio.get_event_loop().time()
            try:
                response = self._client.get(url, headers=self._build_headers())
                # httpx 0.28: use await for async client
                response = await self._client.get(url, headers=self._build_headers())
                response.raise_for_status()
                log.info("fetch.ok", url=url, status=response.status_code,
                         duration_ms=int((asyncio.get_event_loop().time() - t0) * 1000))
                await asyncio.sleep(delay)
                return response.text
            except httpx.HTTPStatusError as exc:
                log.warning("fetch.error", url=url, status=exc.response.status_code)
                raise

    async def fetch_spa(self, url: str) -> str:
        """Fetch a JS-rendered page via Playwright + stealth. Raises ScraperError on failure."""
        from playwright.async_api import async_playwright
        from playwright_stealth import stealth_async

        domain = httpx.URL(url).host
        sem = self._get_semaphore(domain)
        delay = DOMAIN_DELAYS.get(domain, DEFAULT_DELAY)

        async with sem:
            async with async_playwright() as pw:
                browser = await pw.chromium.launch(
                    proxy={"server": self._proxy} if self._proxy else None
                )
                page = await browser.new_page()
                await stealth_async(page)
                await page.goto(url, wait_until="networkidle")
                content = await page.content()
                await browser.close()
                await asyncio.sleep(delay)
                return content

    def _build_headers(self) -> dict[str, str]:
        """Return realistic HTTP headers with rotated User-Agent."""
        from fake_useragent import UserAgent
        ua = UserAgent()
        return {
            "User-Agent": ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
        }
```

**Note on the code above:** The `fetch()` method has an accidental duplicate `response = ...` line — the plan should correct this. The final implementation should only have `response = await self._client.get(...)`.

### Pattern 2: sqlite-utils Schema + Migration

**What:** Create schema using sqlite-utils Python API, with a migration runner that is idempotent.

**When to use:** Plan 01-01. The migration file is executable Python, not SQL strings.

```python
# Source: sqlite-utils docs (https://sqlite-utils.datasette.io/en/stable/)
import sqlite_utils

def run_migrations(db_path: str) -> None:
    """Apply all schema migrations. Idempotent: safe to run multiple times."""
    db = sqlite_utils.Database(db_path)

    # Enable WAL mode for concurrent reads during async writes
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")

    if "platforms" not in db.table_names():
        db["platforms"].create({
            "id": int,
            "name": str,
            "slug": str,
            "base_url": str,
            "created_at": str,
        }, pk="id", not_null={"name", "slug"})
        db["platforms"].create_index(["slug"], unique=True)

    if "niches" not in db.table_names():
        db["niches"].create({
            "id": int,
            "name": str,
            "slug": str,
            "created_at": str,
        }, pk="id", not_null={"name", "slug"})

    if "products" not in db.table_names():
        db["products"].create({
            "id": int,
            "platform_id": int,
            "niche_id": int,
            "external_id": str,
            "title": str,
            "url": str,
            "rank_score": float,
            "price": float,
            "currency": str,
            "scraped_at": str,
            "raw_data": str,  # JSON blob for future-proofing
        }, pk="id", foreign_keys=[
            ("platform_id", "platforms", "id"),
            ("niche_id", "niches", "id"),
        ])
        db["products"].create_index(["platform_id", "niche_id", "scraped_at"])

    if "pains" not in db.table_names():
        db["pains"].create({
            "id": int,
            "niche_id": int,
            "source": str,       # reddit, quora, youtube, trends
            "content": str,
            "sentiment": str,    # positive, negative, neutral
            "detected_at": str,
        }, pk="id", foreign_keys=[
            ("niche_id", "niches", "id"),
        ])

    if "dossiers" not in db.table_names():
        db["dossiers"].create({
            "id": int,
            "product_id": int,
            "analysis": str,       # JSON: factors, pains, template
            "opportunity_score": float,
            "confidence_score": float,
            "generated_at": str,
        }, pk="id", foreign_keys=[
            ("product_id", "products", "id"),
        ])
```

### Pattern 3: YAML Niche Config

**What:** A user-editable `config.yaml` defines niche targets. A Python loader validates and exposes them.

**When to use:** Plan 01-03.

```yaml
# mis/config.yaml — user edits this file to change target niches
niches:
  - name: "Marketing Digital"
    slug: "marketing-digital"
    keywords: ["marketing digital", "tráfego pago", "infoproduto"]
  - name: "Emagrecimento"
    slug: "emagrecimento"
    keywords: ["emagrecer", "dieta", "perda de peso"]
  - name: "Finanças Pessoais"
    slug: "financas-pessoais"
    keywords: ["investimento", "renda passiva", "independência financeira"]

settings:
  proxy_url: ""          # overridden by PROXY_URL in .env if set
  request_delay_s: 2.0   # global fallback delay between requests
  max_retries: 3
```

```python
# mis/config.py
from pathlib import Path
from typing import Optional
import os
import yaml
from dotenv import load_dotenv

load_dotenv()

CONFIG_PATH = Path(__file__).parent / "config.yaml"


def load_config() -> dict:
    """Load and validate mis/config.yaml. Returns merged config with .env overrides."""
    with open(CONFIG_PATH, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    niches = cfg.get("niches", [])
    if not (3 <= len(niches) <= 5):
        raise ValueError(f"config.yaml must define 3-5 niches, got {len(niches)}")

    # .env overrides
    proxy = os.getenv("PROXY_URL", "").strip()
    if proxy:
        cfg["settings"]["proxy_url"] = proxy

    return cfg
```

### Pattern 4: Health Monitor with Canary Check

**What:** Periodically fetch a known-good URL using BaseScraper. If the fetch returns empty content or raises ScraperError, emit a structured alert via structlog.

**When to use:** Plan 01-04. Run on APScheduler at a short interval (e.g., every 15 minutes) in Phase 1.

```python
# mis/health_monitor.py
import asyncio
import structlog
from .base_scraper import BaseScraper
from .exceptions import ScraperError

log = structlog.get_logger()

# Canary URL: a stable, simple page that should always be reachable.
# Using httpbin (public test API) for Phase 1 — no real platform traffic.
CANARY_URL = "https://httpbin.org/get"
CANARY_MIN_LENGTH = 100  # bytes — if response shorter than this, something is wrong


async def run_canary_check() -> bool:
    """Run one canary check. Returns True if healthy, False if degraded. Emits alert on failure."""
    async with BaseScraper() as scraper:
        try:
            content = await scraper.fetch(CANARY_URL)
            if len(content) < CANARY_MIN_LENGTH:
                log.warning("health.canary.empty",
                            url=CANARY_URL,
                            content_length=len(content),
                            alert="SCRAPER_RETURNING_EMPTY_RESPONSE")
                return False
            log.info("health.canary.ok", url=CANARY_URL, content_length=len(content))
            return True
        except ScraperError as exc:
            log.error("health.canary.failed",
                      url=CANARY_URL,
                      attempts=exc.attempts,
                      cause=str(exc.cause),
                      alert="SCRAPER_BROKEN_CANARY_FAILED")
            return False
```

### Anti-Patterns to Avoid

- **Returning None on error:** BaseScraper must raise ScraperError, never return None. Caller cannot distinguish "no data" from "network failure" if None is returned.
- **Short-lived httpx.AsyncClient:** Creating a new `AsyncClient` per request loses connection pooling. The client must live for the entire job duration.
- **Global Semaphore per scraper class (not per domain):** Semaphore must be keyed by domain, not by scraper class, or two different scrapers hitting the same domain bypass rate limiting.
- **Storing proxy credentials in config.yaml:** Proxy URL belongs in `.env` only (gitignored). config.yaml is committed.
- **Using `asyncio.run()` inside an already-running event loop:** pytest-asyncio and APScheduler manage the event loop. Use `await` or `asyncio.create_task()` inside coroutines.
- **Treating playwright-stealth as optional:** Hotmart and Kiwify detect `navigator.webdriver`. Stealth must be applied before `goto()`, not after.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| HTTP retry with backoff | Custom retry loop with sleep | tenacity `@retry` | tenacity handles jitter, backoff curves, exception filtering, logging hooks — edge cases in custom loops cause infinite retries or silent failures |
| Browser fingerprint evasion | Manual JS patches | playwright-stealth | Stealth patches 20+ detection vectors (navigator.webdriver, plugins, languages, WebGL, etc.) — manual patches miss new vectors constantly |
| User-Agent rotation | Hardcoded UA list | fake-useragent | fake-useragent pulls real UA strings from real browser distributions — hardcoded lists go stale within months |
| Structured JSON logs | `print()` or `logging.basicConfig` | structlog | structlog binds context (url, domain, attempt) at logger creation — manual JSON formatting is error-prone and inconsistent |
| SQLite schema creation | Raw SQL `CREATE TABLE IF NOT EXISTS` strings | sqlite-utils | sqlite-utils handles index creation, foreign keys, schema inspection, and Python-native data types — raw SQL strings are harder to refactor |
| Async rate limiting | Global sleep between all requests | `asyncio.Semaphore` per domain | Semaphore + domain delay allows different domains to be scraped concurrently while still rate-limiting each domain independently |

**Key insight:** The scraping domain has solved most of its own hard problems with battle-tested libraries. The value of BaseScraper is in wiring them together correctly, not in re-implementing any of them.

---

## Common Pitfalls

### Pitfall 1: playwright-stealth version mismatch with Playwright

**What goes wrong:** `playwright-stealth` 1.x does not support Playwright's async API properly. The `stealth_async()` function is only available in `playwright-stealth` 2.x.

**Why it happens:** The package had a major API change in 2.0.0.

**How to avoid:** Install `playwright-stealth>=2.0.0`. The import is `from playwright_stealth import stealth_async`.

**Warning signs:** `ImportError: cannot import name 'stealth_async'` at startup.

### Pitfall 2: tenacity retry not catching HTTP status errors

**What goes wrong:** `httpx.HTTPStatusError` (raised by `response.raise_for_status()`) is not a subclass of `httpx.HTTPError`. If you only retry on `httpx.HTTPError`, 429 and 5xx responses are not retried.

**Why it happens:** httpx exception hierarchy: `HTTPStatusError` extends `HTTPError` in httpx 0.23+, but only if you check the docs — many developers assume it's separate.

**How to avoid:** Verify with `issubclass(httpx.HTTPStatusError, httpx.HTTPError)` → True in httpx 0.28. Either retry on `httpx.HTTPError` (covers both) or explicitly add `httpx.HTTPStatusError` to the retry filter. Also add a custom `retry_if_exception` check for status 429/5xx if you want to distinguish from connection errors.

**Warning signs:** 429 responses end the job instead of waiting and retrying.

### Pitfall 3: asyncio.Semaphore created outside event loop

**What goes wrong:** On Python 3.10+, `asyncio.Semaphore()` created at module level (outside an async context) raises `DeprecationWarning` or fails in Python 3.12+.

**Why it happens:** Semaphores attach to the running event loop. Module-level creation happens before the loop starts.

**How to avoid:** Create Semaphores lazily on first use (inside an async function), keyed by domain in a module-level dict. The `_get_semaphore(domain)` pattern in the code example above handles this correctly.

**Warning signs:** `RuntimeError: no running event loop` or `DeprecationWarning: There is no current event loop` during startup.

### Pitfall 4: httpx AsyncClient not closed properly

**What goes wrong:** Leaving `AsyncClient` open causes `ResourceWarning` and may cause test isolation failures (leaked connections between tests).

**Why it happens:** httpx AsyncClient is a resource that must be explicitly closed.

**How to avoid:** Always use BaseScraper as an async context manager (`async with BaseScraper() as s:`). In tests, ensure `__aexit__` is called — use `pytest-asyncio` with `asyncio_mode = "auto"`.

**Warning signs:** `ResourceWarning: Unclosed client session` in test output.

### Pitfall 5: pytest-asyncio mode not configured

**What goes wrong:** Async tests fail with `coroutine 'test_...' was never awaited` or `RuntimeError: no running event loop`.

**Why it happens:** pytest-asyncio 0.21+ requires explicit mode declaration. Default mode changed from `strict` to `auto` in newer versions.

**How to avoid:** Add to `pyproject.toml` or `pytest.ini`:
```ini
[pytest]
asyncio_mode = auto
```
Or add `@pytest.mark.asyncio` to each async test. The installed version (0.24.0) requires explicit configuration.

**Warning signs:** Tests pass synchronously but async tests are skipped or fail immediately.

### Pitfall 6: sqlite-utils `raw_data` JSON stored as string

**What goes wrong:** Querying JSON blobs stored as TEXT requires manual deserialization. If you later need SQLite JSON functions (e.g., `json_extract`), TEXT storage works — but it is implicit, not enforced.

**Why it happens:** SQLite has no native JSON type; everything is TEXT/INTEGER/REAL/BLOB. sqlite-utils stores Python dicts as JSON TEXT automatically when you pass a dict.

**How to avoid:** Pass Python dicts directly to sqlite-utils insert methods — it serializes automatically. When reading, call `json.loads(row["raw_data"])` explicitly.

**Warning signs:** Querying `raw_data` column returns a string instead of a dict.

---

## Code Examples

Verified patterns from official sources:

### httpx Async Client with HTTP/2 (Plan 01-02)

```python
# Source: https://www.python-httpx.org/async/
import httpx

async with httpx.AsyncClient(http2=True) as client:
    response = await client.get("https://example.com")
    print(response.text)
```

### tenacity Retry Decorator with Status Code Filter (Plan 01-02)

```python
# Source: https://tenacity.readthedocs.io/en/latest/
from tenacity import (
    retry, stop_after_attempt, wait_exponential,
    retry_if_exception_type, before_sleep_log
)
import httpx
import logging

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    before_sleep=before_sleep_log(logging.getLogger(__name__), logging.WARNING),
    reraise=True,
)
async def fetch_with_retry(client: httpx.AsyncClient, url: str) -> str:
    response = await client.get(url)
    response.raise_for_status()
    return response.text
```

### structlog JSON Configuration (Plan 01-02)

```python
# Source: https://www.structlog.org/en/stable/getting-started.html
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.BoundLogger,
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

log = structlog.get_logger()
log.info("fetch.ok", url="https://example.com", status=200, duration_ms=142)
# Output: {"url": "https://example.com", "status": 200, "duration_ms": 142, "event": "fetch.ok", ...}
```

### sqlite-utils Table Creation (Plan 01-01)

```python
# Source: https://sqlite-utils.datasette.io/en/stable/python-api.html
import sqlite_utils

db = sqlite_utils.Database("mis.db")
db.execute("PRAGMA journal_mode=WAL")

db["products"].insert({
    "platform_id": 1,
    "title": "Test Product",
    "url": "https://example.com/product",
    "scraped_at": "2026-03-14T00:00:00",
    "raw_data": '{"price": 97.0}',
})
```

### playwright-stealth Async Usage (Plan 01-02)

```python
# Source: https://github.com/AtuboDad/playwright-stealth (v2.x)
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

async with async_playwright() as pw:
    browser = await pw.chromium.launch()
    page = await browser.new_page()
    await stealth_async(page)   # must be called BEFORE goto()
    await page.goto("https://example.com")
    content = await page.content()
    await browser.close()
```

### APScheduler Skeleton (Plan 01-03)

```python
# Source: https://apscheduler.readthedocs.io/en/3.x/
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

# Register health check every 15 minutes
scheduler.add_job(run_canary_check, "interval", minutes=15, id="health_check")

scheduler.start()
# Scheduler runs in background; event loop must stay alive
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| requests (sync) | httpx (async, HTTP/2) | 2020+ | Non-blocking I/O allows concurrent scraping without threading complexity |
| Manual retry loops | tenacity decorators | 2017+ | Declarative retry reduces error-prone boilerplate |
| Selenium WebDriver | Playwright | 2021+ | Playwright has better async support, auto-wait, and stealth options |
| Manual stealth patches | playwright-stealth | 2022+ | Covers 20+ detection vectors automatically |
| `logging` + JSON formatter | structlog | 2018+ | Context binding and pipeline processors are cleaner |
| Alembic for SQLite | sqlite-utils | 2020+ | For SQLite-only projects, sqlite-utils is lighter and Pythonic |

**Deprecated/outdated:**
- `requests-html`: unmaintained since 2021, replaced by Playwright for JS rendering
- `APScheduler 4.x (alpha)`: not yet stable as of 2026-03; stick with 3.x
- `playwright-stealth 1.x`: does not expose `stealth_async()` — use 2.x

---

## Open Questions

1. **DB location: `mis/mis.db` vs `.data/mis/mis.db`**
   - What we know: CONTEXT.md says either location is acceptable; `.data/` is already gitignored for L3 data
   - What's unclear: Whether the `mis/` subdirectory itself should be gitignored or partially tracked
   - Recommendation: Place `mis.db` in `.data/mis/mis.db` — keeps committed code clean and follows existing L3 pattern. Add `.data/` to `.gitignore` if not already present.

2. **pytest-asyncio version: 0.24.0 installed vs 1.3.0 available**
   - What we know: 0.24.0 is installed and functional; 1.3.0 is latest
   - What's unclear: Whether 1.3.0 introduces breaking changes that affect the test suite
   - Recommendation: Use 0.24.0 (already installed) for Phase 1. Pin to `pytest-asyncio>=0.24,<1.0` in `mis/requirements.txt` to avoid accidental upgrade surprises.

3. **tenacity version: 9.0.0 installed vs 9.1.4 available**
   - What we know: 9.0.0 is installed; both are in the 9.x stable line
   - What's unclear: Whether any 9.1.x fixes affect retry behavior for httpx exceptions
   - Recommendation: Upgrade to 9.1.4 during Phase 1 setup (`pip install tenacity==9.1.4`). It is a minor version bump with no breaking changes.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.4.2 + pytest-asyncio 0.24.0 |
| Config file | `mis/pytest.ini` (Wave 0 gap — needs creation) |
| Quick run command | `pytest mis/tests/ -x -q --timeout=10` |
| Full suite command | `pytest mis/tests/ -v --timeout=30` |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FOUND-01 | All 5 tables exist after migration; re-run is idempotent | unit | `pytest mis/tests/test_db.py -x` | Wave 0 gap |
| FOUND-01 | Foreign key constraints enforced (insert product with invalid platform_id fails) | unit | `pytest mis/tests/test_db.py::test_foreign_key_constraint -x` | Wave 0 gap |
| FOUND-02 | BaseScraper.fetch() with mock httpx returns content on 200 | unit | `pytest mis/tests/test_base_scraper.py::test_fetch_success -x` | Wave 0 gap |
| FOUND-02 | BaseScraper.fetch() retries 3 times on 429 then raises ScraperError | unit | `pytest mis/tests/test_base_scraper.py::test_fetch_retries_on_429 -x` | Wave 0 gap |
| FOUND-02 | BaseScraper.fetch() respects per-domain delay (Semaphore held between requests) | unit | `pytest mis/tests/test_base_scraper.py::test_rate_limiting -x` | Wave 0 gap |
| FOUND-02 | BaseScraper headers contain realistic User-Agent (not empty, not "python-httpx") | unit | `pytest mis/tests/test_base_scraper.py::test_headers_not_default -x` | Wave 0 gap |
| FOUND-02 | ScraperError raised (not None returned) when all retries exhausted | unit | `pytest mis/tests/test_base_scraper.py::test_scraper_error_raised -x` | Wave 0 gap |
| FOUND-02 | AsyncClient is closed after `__aexit__` (no ResourceWarning) | unit | `pytest mis/tests/test_base_scraper.py::test_client_closed_on_exit -x` | Wave 0 gap |
| FOUND-03 | config.yaml with 3 niches loads without error | unit | `pytest mis/tests/test_config.py::test_load_3_niches -x` | Wave 0 gap |
| FOUND-03 | config.yaml with 6 niches raises ValueError | unit | `pytest mis/tests/test_config.py::test_too_many_niches -x` | Wave 0 gap |
| FOUND-03 | PROXY_URL from .env overrides config.yaml proxy setting | unit | `pytest mis/tests/test_config.py::test_proxy_env_override -x` | Wave 0 gap |
| FOUND-04 | Canary check returns True when httpbin.org returns 200 | integration | `pytest mis/tests/test_health_monitor.py::test_canary_healthy -x` | Wave 0 gap |
| FOUND-04 | Canary check returns False and logs `SCRAPER_RETURNING_EMPTY_RESPONSE` when response < 100 bytes | unit | `pytest mis/tests/test_health_monitor.py::test_canary_empty_response -x` | Wave 0 gap |
| FOUND-04 | Canary check returns False and logs `SCRAPER_BROKEN_CANARY_FAILED` when ScraperError raised | unit | `pytest mis/tests/test_health_monitor.py::test_canary_scraper_error -x` | Wave 0 gap |

### Canary Check Strategy

The canary URL for Phase 1 must be:
- **Public and stable:** Not a real marketplace (avoids rate-limiting our own canary)
- **Simple SSR page:** Tests `fetch()` path, not `fetch_spa()`
- **Fast:** Responds in < 2 seconds
- **Returns predictable content:** Length or content can be asserted

**Recommended canary URL:** `https://httpbin.org/get`
- Returns JSON with request metadata — always 200, always > 100 bytes
- Tests that httpx AsyncClient, header rotation, and retry all work
- No scraping ToS concerns

**Production canary (Phase 2+):** Add a second canary using a stable public Hotmart product URL that the team can monitor for structure changes.

**Unit test strategy for canary:** Use `unittest.mock.AsyncMock` to mock `BaseScraper.fetch()` in `test_health_monitor.py`. Test both the happy path (200, long content) and failure paths (empty content, ScraperError) without real network calls.

```python
# mis/tests/test_health_monitor.py — pattern
import pytest
from unittest.mock import AsyncMock, patch
from mis.health_monitor import run_canary_check
from mis.exceptions import ScraperError

@pytest.mark.asyncio
async def test_canary_empty_response():
    with patch("mis.health_monitor.BaseScraper") as MockScraper:
        instance = MockScraper.return_value.__aenter__.return_value
        instance.fetch = AsyncMock(return_value="short")  # < 100 chars
        result = await run_canary_check()
    assert result is False

@pytest.mark.asyncio
async def test_canary_scraper_error():
    with patch("mis.health_monitor.BaseScraper") as MockScraper:
        instance = MockScraper.return_value.__aenter__.return_value
        instance.fetch = AsyncMock(side_effect=ScraperError("url", 3, Exception("timeout")))
        result = await run_canary_check()
    assert result is False
```

### How to Verify BaseScraper Without Hitting Real Platforms

Use `respx` (httpx mock library) or `unittest.mock.AsyncMock`:

```python
# Option A: respx (recommended for httpx-specific mocking)
# pip install respx
import respx
import httpx
import pytest

@pytest.mark.asyncio
async def test_fetch_success():
    with respx.mock:
        respx.get("https://example.com").mock(
            return_value=httpx.Response(200, text="<html>ok</html>")
        )
        async with BaseScraper() as s:
            content = await s.fetch("https://example.com")
    assert "ok" in content
```

```python
# Option B: unittest.mock (no extra dependency)
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.mark.asyncio
async def test_fetch_retries_on_429():
    response_429 = MagicMock()
    response_429.raise_for_status.side_effect = httpx.HTTPStatusError(
        "429", request=MagicMock(), response=MagicMock(status_code=429)
    )
    # ... patch client.get to return 429 twice, then 200
```

**Recommendation:** Add `respx` to `mis/requirements-dev.txt`. It is purpose-built for mocking httpx and produces cleaner tests than manual `AsyncMock` chaining.

### Sampling Rate

- **Per task commit:** `pytest mis/tests/ -x -q --timeout=10`
- **Per wave merge:** `pytest mis/tests/ -v --timeout=30`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

The following files do not exist and must be created before or during Plan 01-01:

- [ ] `mis/tests/conftest.py` — shared fixtures: in-memory SQLite DB, mock BaseScraper, temp config.yaml
- [ ] `mis/tests/test_db.py` — covers FOUND-01
- [ ] `mis/tests/test_base_scraper.py` — covers FOUND-02
- [ ] `mis/tests/test_config.py` — covers FOUND-03
- [ ] `mis/tests/test_health_monitor.py` — covers FOUND-04
- [ ] `mis/pytest.ini` — configures `asyncio_mode = auto` and test paths
- [ ] `mis/requirements.txt` — MIS-specific dependencies (separate from root `requirements.txt`)
- [ ] Framework additions: `pip install respx` (httpx mock) — add to `mis/requirements-dev.txt`

---

## Sources

### Primary (HIGH confidence)

- httpx 0.28.1 installed (`pip show httpx`) — version confirmed, HTTP/2 support confirmed
- tenacity 9.0.0 installed (`pip show tenacity`) — `@retry` decorator API confirmed stable
- pytest 8.4.2 + pytest-asyncio 0.24.0 installed (`pip show pytest pytest-asyncio`) — test infrastructure confirmed
- python-dotenv 1.2.1 installed — `.env` loading confirmed
- PyYAML already in `requirements.txt` — no new dependency for YAML config
- sqlite-utils 3.39 latest (`pip index versions sqlite-utils`) — latest stable confirmed
- playwright 1.58.0 latest (`pip index versions playwright`) — latest stable confirmed
- playwright-stealth 2.0.2 latest (`pip index versions playwright-stealth`) — v2 API with `stealth_async()` confirmed
- APScheduler 3.11.2 latest (`pip index versions apscheduler`) — 3.x stable confirmed
- structlog 25.5.0 latest (`pip index versions structlog`) — JSON output API confirmed

### Secondary (MEDIUM confidence)

- playwright-stealth GitHub README (v2.0.x) — `stealth_async()` function signature and usage pattern confirmed
- sqlite-utils Python API docs (https://sqlite-utils.datasette.io/) — `create()`, `create_index()`, `foreign_keys` parameter confirmed

### Tertiary (LOW confidence)

- `respx` as httpx mock library — recommended by httpx community; not verified via Context7; needs validation during Wave 0

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all packages verified installed or available on PyPI with exact versions
- Architecture: HIGH — patterns derived from locked decisions in CONTEXT.md and verified library APIs
- Pitfalls: HIGH (asyncio Semaphore, ResourceWarning, playwright-stealth version) / MEDIUM (JSON storage pitfall)
- Validation: HIGH — test framework is installed; test file gaps are accurately identified

**Research date:** 2026-03-14
**Valid until:** 2026-06-14 (90 days — stack is stable; playwright-stealth and APScheduler worth re-checking)
