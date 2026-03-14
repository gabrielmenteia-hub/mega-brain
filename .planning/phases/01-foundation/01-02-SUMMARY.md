---
phase: 01-foundation
plan: "02"
subsystem: mis-base-scraper
tags: [httpx, tenacity, playwright, stealth, rate-limiting, tdd, async]
dependency_graph:
  requires:
    - mis.exceptions.ScraperError (from plan 01-01)
  provides:
    - mis.base_scraper.BaseScraper
    - mis.base_scraper.DOMAIN_DELAYS
    - mis.base_scraper.DEFAULT_DELAY
  affects:
    - All platform scrapers in Phases 2-4 (subclass BaseScraper)
    - mis/tests/test_health_monitor.py (consumes BaseScraper in canary check)
tech_stack:
  added:
    - respx 0.22.0 (installed — httpx mock library for tests)
    - fake-useragent (installed — User-Agent rotation)
    - structlog (installed — JSON structured logging)
    - h2 (installed via httpx[http2] — HTTP/2 transport)
    - pytest-timeout (installed — timeout support in pytest)
  patterns:
    - TDD RED-GREEN: stubs replaced with real tests before implementation
    - Nested inner function with @retry decorator inside fetch() — avoids class-method decorator complications with tenacity
    - Lazy asyncio.Semaphore creation via _get_semaphore() — avoids module-level creation outside event loop
    - Long-lived httpx.AsyncClient via __aenter__/__aexit__ — one client per scraping job
key_files:
  created:
    - mis/base_scraper.py
  modified:
    - mis/tests/test_base_scraper.py (stubs replaced with 6 real tests)
decisions:
  - "Tenacity @retry as nested inner function inside fetch() — avoids issues with class-method retry decorators and allows ScraperError wrapping cleanly after reraise=True"
  - "h2 package installed (httpx[http2]) — was missing from environment; BaseScraper requires HTTP/2 per locked CONTEXT.md decision"
  - "DOMAIN_DELAYS module-level dict with DEFAULT_DELAY=2.0 fallback — allows per-domain tuning without code changes"
metrics:
  duration: "~10 minutes"
  completed_date: "2026-03-14T17:39:06Z"
  tasks_completed: 1
  files_created: 1
  files_modified: 1
  test_results: "6 passed"
---

# Phase 1 Plan 02: BaseScraper Implementation Summary

BaseScraper async HTTP scraper base class with httpx HTTP/2, tenacity retry (stop=3, exponential backoff), per-domain asyncio.Semaphore rate limiting, fake-useragent rotation, structlog JSON logging, ScraperError explicit failure, and Playwright+stealth fetch_spa() method.

## BaseScraper Public API

### Class: `BaseScraper(proxy_url: Optional[str] = None)`

| Method | Signature | Description |
|--------|-----------|-------------|
| `__aenter__` | `async def __aenter__(self) -> "BaseScraper"` | Opens httpx.AsyncClient (http2=True, follow_redirects=True, timeout=30s) |
| `__aexit__` | `async def __aexit__(self, *_) -> None` | Closes AsyncClient via `aclose()` |
| `fetch` | `async def fetch(self, url: str) -> str` | Fetch SSR/JSON via httpx; retries 3x; raises ScraperError on exhaustion |
| `fetch_spa` | `async def fetch_spa(self, url: str) -> str` | Fetch JS SPA via Playwright+stealth; raises ScraperError on failure |
| `_get_semaphore` | `def _get_semaphore(self, domain: str) -> asyncio.Semaphore` | Returns lazily-created per-domain Semaphore from module-level `_SEMAPHORE` dict |
| `_build_headers` | `def _build_headers(self) -> dict[str, str]` | Returns headers with `UserAgent().random` plus Accept, Accept-Language, DNT |

### Module-level exports

```python
from mis.base_scraper import BaseScraper, DOMAIN_DELAYS, DEFAULT_DELAY
```

| Export | Type | Value |
|--------|------|-------|
| `DOMAIN_DELAYS` | `dict[str, float]` | `{"hotmart.com": 2.0, "kiwify.com.br": 2.0, "clickbank.com": 2.0}` |
| `DEFAULT_DELAY` | `float` | `2.0` |
| `_SEMAPHORE` | `dict[str, asyncio.Semaphore]` | Module-level, populated lazily per domain |

## How ScraperError Is Raised (Tenacity Pattern)

`fetch()` uses a nested inner function `_do_fetch()` decorated with `@retry`:

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(
        (httpx.HTTPStatusError, httpx.HTTPError, httpx.TimeoutException)
    ),
    reraise=True,
)
async def _do_fetch() -> str:
    ...

try:
    return await _do_fetch()
except (httpx.HTTPStatusError, httpx.HTTPError, httpx.TimeoutException) as exc:
    raise ScraperError(url=url, attempts=3, cause=exc)
```

- `reraise=True` causes tenacity to re-raise the original exception after all attempts
- The outer `try/except` catches it and wraps in `ScraperError`
- `attempts` is set to `3` (the stop_after_attempt value) — satisfies `exc_info.value.attempts >= 1`
- ScraperError is NEVER returned as None — it always raises

## Pitfalls Avoided

1. **Duplicate `await self._client.get()`** — RESEARCH.md noted the reference pattern had an accidental duplicate call. Implemented with exactly ONE `await self._client.get()` per fetch() invocation.

2. **Semaphore created outside event loop** — `_SEMAPHORE` dict is module-level but empty; Semaphores are created lazily inside `_get_semaphore()` which is called from within async context. Avoids `RuntimeError: no running event loop` on Python 3.10+.

3. **stealth_async() before page.goto()** — `fetch_spa()` calls `await stealth_async(page)` strictly before `await page.goto()`. Calling it after would leave automation fingerprints visible.

4. **ResourceWarning from unclosed client** — `__aexit__` calls `await self._client.aclose()` unconditionally; test `test_client_closed_on_exit` verifies `s._client.is_closed` is True after context exit.

5. **h2 missing** — HTTP/2 requires the `h2` package. `pip install httpx[http2]` installed it as a Rule 3 auto-fix during execution.

## Test Status

| Test | Status | What it verifies |
|------|--------|-----------------|
| `test_fetch_success` | PASSED | 200 response text returned correctly |
| `test_fetch_retries_on_429` | PASSED | 429+429+200 sequence: returns text on 3rd attempt |
| `test_rate_limiting` | PASSED | `asyncio.sleep` called at least once per fetch |
| `test_headers_not_default` | PASSED | User-Agent is not "python-httpx" and non-empty |
| `test_scraper_error_raised` | PASSED | 500 response raises ScraperError with correct url and attempts>=1 |
| `test_client_closed_on_exit` | PASSED | `s._client.is_closed` is True after `async with` block |

**Result: 6/6 passed. No ResourceWarning.**

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] h2 package not installed for HTTP/2**
- **Found during:** Task 1 GREEN phase, first test run
- **Issue:** `ImportError: Using http2=True, but the 'h2' package is not installed` — httpx[http2] extra was not installed in the Python environment
- **Fix:** `pip install httpx[http2]` installed h2 package
- **Files modified:** none (runtime dependency install)
- **Commit:** d114a76

**2. [Rule 3 - Blocking] pytest-timeout not installed**
- **Found during:** Task 1 first verification run
- **Issue:** `error: unrecognized arguments: --timeout=30` — pytest-timeout was in requirements-dev.txt but not installed
- **Fix:** `pip install pytest-timeout`
- **Files modified:** none (runtime dependency install)
- **Commit:** d114a76

**3. [Rule 2 - Pattern] Tenacity as nested inner function instead of class decorator**
- **Found during:** Task 1 GREEN design
- **Issue:** Applying `@retry` directly to a class method creates complications when `reraise=True` + outer try/except for ScraperError wrapping
- **Fix:** Used nested `_do_fetch()` inner function with `@retry` inside `fetch()` — cleaner separation of retry logic from error wrapping
- **Impact:** No behavior change; improves maintainability

## Commits

| Hash | Message |
|------|---------|
| cc985b2 | test(01-02): replace stubs with real tests for BaseScraper (RED) |
| d114a76 | feat(01-02): implement BaseScraper with fetch(), fetch_spa(), and rate limiting (GREEN) |

## Self-Check: PASSED
