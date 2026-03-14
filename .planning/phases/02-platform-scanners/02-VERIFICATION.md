---
phase: 02-platform-scanners
verified: 2026-03-14T22:32:49Z
status: passed
score: 12/12 must-haves verified
re_verification: false
---

# Phase 02: Platform Scanners Verification Report

**Phase Goal:** Implement platform scanners for Kiwify, ClickBank, and Hotmart with TDD, APScheduler jobs, and canary health monitoring.
**Verified:** 2026-03-14T22:32:49Z
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

All truths verified against the codebase and confirmed by the live test suite (34/34 GREEN).

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | KiwifyScanner.scan_niche() returns products with all mandatory fields | VERIFIED | `mis/scanners/kiwify.py` — full `_extract_products_from_primary()` implementation, 5 tests GREEN including `test_happy_path` (12 products) |
| 2 | price is float, rank is int, external_id is not None in any returned product | VERIFIED | `_parse_price()` returns float or None, rank assigned as `enumerate(..., start=1)`, external_id from URL slug or `data-product-id` |
| 3 | When all CSS selectors fail, returns [] and structlog emits alert='schema_drift' | VERIFIED | `kiwify.py:292 alert="schema_drift"`, confirmed by `test_drift_alert` GREEN |
| 4 | Upsert in real DB: two upserts with different rank result in 1 row with updated rank | VERIFIED | `product_repository.py` UPDATE-then-INSERT pattern; `test_upsert_no_duplicates` GREEN for Kiwify, ClickBank, and Hotmart |
| 5 | Config.yaml accepts platforms block per niche and new settings | VERIFIED | `mis/config.yaml` has `platforms:` block in all 3 niches; `max_products_per_niche`, `scan_schedule`, `parallel_scanners` present |
| 6 | ClickBankScanner returns products with gravity score as rank via GraphQL | VERIFIED | `mis/scanners/clickbank.py` — GraphQL POST to `accounts.clickbank.com/graphql`, `int(gravity)` as rank, 5 tests GREEN (20 products from live fixture) |
| 7 | ClickBankScanner uses httpx (no Playwright) | VERIFIED | `clickbank.py` uses `self._base._client.post()` directly — no `fetch_spa` or Playwright |
| 8 | HotmartScanner.scan_niche() returns at least 10 products via httpx SSR | VERIFIED | `mis/scanners/hotmart.py` — `self.fetch()` httpx, BeautifulSoup parsing `a.product-link`; fixture has 24 products; 5 tests GREEN |
| 9 | When all selectors fail, Hotmart returns [] and emits alert='schema_drift' | VERIFIED | `hotmart.py:182 alert="schema_drift"`, confirmed by `test_drift_alert` GREEN |
| 10 | register_scanner_jobs() registers 3 jobs with CronTrigger from scan_schedule | VERIFIED | `scheduler.py:63-97` — `CronTrigger.from_crontab(scan_schedule)`, jobs: `scanner_hotmart`, `scanner_clickbank`, `scanner_kiwify`; `test_jobs_registered` GREEN |
| 11 | Canary alerts when updated_at of most recent product is > 25 hours old | VERIFIED | `health_monitor.py:72-155` — `SELECT MAX(updated_at)`, 25h threshold, `alert='platform_data_stale'`; `test_platform_canary_stale` GREEN |
| 12 | run_all_scanners() partial failure: one platform failure does not cancel others | VERIFIED | `scanner.py:170 asyncio.gather(..., return_exceptions=True)`, exceptions caught per-key; `test_partial_failure` GREEN |

**Score:** 12/12 truths verified

---

### Required Artifacts

| Artifact | Status | Details |
|----------|--------|---------|
| `mis/scanner.py` | VERIFIED | `Product` dataclass (6 mandatory + 4 optional fields), `PlatformScanner` ABC, `run_all_scanners()` with `asyncio.gather(return_exceptions=True)`, SCANNER_MAP includes Hotmart + ClickBank + Kiwify |
| `mis/product_repository.py` | VERIFIED | `upsert_product()` UPDATE-then-INSERT pattern, `save_batch()` with empty-list guard |
| `mis/migrations/_002_product_enrichment.py` | VERIFIED | `run_migration_002()` idempotent — checks existing columns before `add_column()`; adds rank, commission_pct, rating, thumbnail_url, updated_at |
| `mis/scanners/__init__.py` | VERIFIED | Empty package init present |
| `mis/scanners/kiwify.py` | VERIFIED | `KiwifyScanner(PlatformScanner)`, `KIWIFY_PLATFORM_ID=3`, 3-selector fallback chain, `run_kiwify_scan()` |
| `mis/scanners/clickbank.py` | VERIFIED | `ClickBankScanner(PlatformScanner)`, `CLICKBANK_PLATFORM_ID=2`, GraphQL POST, gravity-to-rank, drift alert, `run_clickbank_scan()` |
| `mis/scanners/hotmart.py` | VERIFIED | `HotmartScanner(PlatformScanner)`, `HOTMART_PLATFORM_ID=1`, httpx SSR, 3-selector fallback, `run_hotmart_scan()` |
| `mis/scheduler.py` | VERIFIED | `register_scanner_jobs()` added; `CronTrigger.from_crontab()`, `replace_existing=True`, 3 jobs registered |
| `mis/health_monitor.py` | VERIFIED | `run_platform_canary()` added; `SELECT MAX(updated_at)`, 25h threshold, `alert='platform_data_stale'`, never raises |
| `mis/tests/test_kiwify_scanner.py` | VERIFIED | 5 tests — all GREEN (happy_path, field_types, fallback_selector, drift_alert, upsert_no_duplicates) |
| `mis/tests/test_clickbank_scanner.py` | VERIFIED | 5 tests — all GREEN (same pattern, uses respx.post for GraphQL) |
| `mis/tests/test_hotmart_scanner.py` | VERIFIED | 5 tests — all GREEN (uses respx.mock for SSR HTML) |
| `mis/tests/test_scanner_jobs.py` | VERIFIED | 4 tests — all GREEN (jobs_registered, cron_trigger, platform_canary_stale, partial_failure) |
| `mis/tests/fixtures/kiwify/catalog_saude.html` | VERIFIED | Exists, 7,268 bytes — synthetic but structurally valid HTML with `article.product-card` elements |
| `mis/tests/fixtures/kiwify/catalog_mkt.html` | VERIFIED | Exists, 7,314 bytes — synthetic HTML |
| `mis/tests/fixtures/hotmart/catalog_saude.html` | VERIFIED | Exists, 365,229 bytes — live HTML; contains 24 `product-link` matches |
| `mis/tests/fixtures/clickbank/marketplace_health.json` | VERIFIED | Exists, 19,333 bytes — live GraphQL JSON; 20 products with gravity scores (first: BRAINSONGX) |
| `mis/tests/fixtures/clickbank/marketplace_mktg.json` | VERIFIED | Exists, 19,099 bytes — live GraphQL JSON |
| `mis/tests/fixtures/clickbank/marketplace_health.html` | VERIFIED (placeholder) | Exists, 527 bytes — HTML placeholder; superseded by JSON fixture per architecture discovery |
| `mis/config.yaml` | VERIFIED | `platforms:` block in all 3 niches, `max_products_per_niche`, `scan_schedule: "0 3 * * *"`, `parallel_scanners: true` |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `mis/scanners/kiwify.py` | `mis/scanner.py` | `class KiwifyScanner(PlatformScanner)` | WIRED | Import at line 26; class declaration confirmed |
| `mis/scanners/clickbank.py` | `mis/scanner.py` | `class ClickBankScanner(PlatformScanner)` | WIRED | Import at line 28; class declaration confirmed |
| `mis/scanners/hotmart.py` | `mis/scanner.py` | `class HotmartScanner(PlatformScanner)` | WIRED | Import at line 32; class declaration confirmed |
| `mis/scanner.py` | `mis/scanners/*.py` | SCANNER_MAP in `run_all_scanners()` | WIRED | Lazy imports of Kiwify, Hotmart, ClickBank at lines 117-119; all three in SCANNER_MAP |
| `mis/scheduler.py` | `mis/scanners/hotmart.py,clickbank.py,kiwify.py` | `register_scanner_jobs()` imports `run_*_scan` | WIRED | Lines 76-78; `run_hotmart_scan`, `run_clickbank_scan`, `run_kiwify_scan` imported and registered |
| `mis/health_monitor.py` | `mis/db.py` (SQLite) | `SELECT MAX(updated_at)` via `sqlite3.connect()` | WIRED | `health_monitor.py:99-103`; `SELECT MAX(updated_at)` query confirmed |
| `mis/config.py` | `mis/config.yaml` | `load_config()` validates platforms block | WIRED | Config validation confirmed in SUMMARY (ValueError on typos, at least 1 platform per niche) |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| SCAN-01 | 02-03-PLAN.md | Sistema varre e rankeia produtos mais vendidos na Hotmart por nicho configurado | SATISFIED | `HotmartScanner.scan_niche()` fetches `hotmart.com/pt-br/marketplace/produtos?category={slug}`, returns ranked products; 5 tests GREEN |
| SCAN-02 | 02-01-PLAN.md | Sistema varre e rankeia produtos mais vendidos na Kiwify por nicho configurado | SATISFIED | `KiwifyScanner.scan_niche()` implemented with fallback selectors; 5 tests GREEN. Note: Kiwify marketplace has no public URL — fixtures are synthetic. Scanner architecture valid for when auth is available. |
| SCAN-03 | 02-02-PLAN.md | Sistema varre e rankeia produtos com maior gravity score no ClickBank por nicho | SATISFIED | `ClickBankScanner` uses GraphQL API (`accounts.clickbank.com/graphql`); gravity available without auth; `int(gravity)` as rank; 5 tests GREEN with live fixtures |
| SCAN-04 | 02-03-PLAN.md | Ranking é atualizado automaticamente em ciclo periódico (diário) | SATISFIED | `register_scanner_jobs()` registers 3 APScheduler CronTrigger jobs (default `"0 3 * * *"`); `test_jobs_registered` and `test_cron_trigger` GREEN |

All 4 requirements for Phase 2 are satisfied.

**Orphaned requirements check:** No requirements mapped to Phase 2 in REQUIREMENTS.md beyond SCAN-01 through SCAN-04. Coverage complete.

---

### Architecture Deviations (Non-blocking)

The following deviations from the original plan were resolved correctly during execution:

| Deviation | Impact | Resolution |
|-----------|--------|------------|
| Kiwify marketplace has no public URL (returns 404, API requires token) | Test fixtures are synthetic HTML instead of live-captured | Fixtures match realistic HTML structure; tests pass via `respx.mock`; architecture valid |
| ClickBank is GraphQL, not SSR HTML | `ClickBankScanner` is a GraphQL client instead of HTML scraper | Better outcome — structured data with official gravity scores; live JSON fixtures captured |
| Hotmart is SSR (not XHR/Playwright as originally assumed) | Plan 03 frontmatter truths still reference Playwright/XHR, but plan `<objective>` was updated before execution | Implementation correctly uses `self.fetch()` (httpx SSR); 24 live products confirmed |
| `sqlite-utils upsert()` incompatible with existing autoincrement PK | Cannot use library upsert with composite key on table that has separate PK | UPDATE-then-INSERT pattern implemented; all upsert tests GREEN |

**Note on Plan 03 frontmatter:** The `must_haves.truths` in `02-03-PLAN.md` still reference "XHR intercept do Playwright". The plan's own `<objective>` section explicitly supersedes this with the SSR discovery. The implementation is correct — `HotmartScanner` uses `self.fetch()` (httpx), not `fetch_spa()` (Playwright). This is a documentation artifact, not an implementation gap.

---

### Anti-Patterns Found

| File | Pattern | Severity | Assessment |
|------|---------|----------|------------|
| `mis/scanners/hotmart.py:160,188` | `return []` | Info | Intentional — error/drift cases, not stubs. Both are guarded by explicit conditions. |
| `mis/scanners/kiwify.py:271,298` | `return []` | Info | Intentional — same pattern as Hotmart. |
| `mis/scanners/clickbank.py:207,221,232` | `return []` | Info | Intentional — three specific error cases: fetch failure, parse error, empty hits. |
| `mis/tests/fixtures/clickbank/*.html` | HTML placeholder files | Info | Acknowledged in SUMMARY; superseded by JSON fixtures. ClickBank architecture is GraphQL. |

No blocker anti-patterns found.

---

### Human Verification Required

#### 1. Kiwify Live Scan

**Test:** Configure a valid Kiwify session/token and run `KiwifyScanner.scan_niche("emagrecimento", "saude")` against the live marketplace.
**Expected:** Returns real products (not synthetic fixtures). Marketplace URL `kiwify.com.br/marketplace?category=saude` returns accessible HTML.
**Why human:** Kiwify marketplace is not publicly accessible without authentication. Fixtures are synthetic. The scanner architecture is validated, but live integration cannot be confirmed programmatically without credentials.

#### 2. ClickBank GraphQL Availability

**Test:** Confirm `POST https://accounts.clickbank.com/graphql` still returns gravity data without authentication headers.
**Expected:** Response contains `data.marketplaceSearch.hits[]` with `marketplaceStats.gravity` values.
**Why human:** External API — availability may change without notice. Live fixtures were captured on 2026-03-14 and may become stale if ClickBank adds authentication gating.

#### 3. Hotmart Live Scan Against Actual Marketplace

**Test:** Run `HotmartScanner.scan_niche("saude", "saude-e-fitness")` against the live Hotmart URL with no mock.
**Expected:** Returns >= 10 products from `https://hotmart.com/pt-br/marketplace/produtos?category=saude-e-fitness`.
**Why human:** The fixture was captured live on 2026-03-14. Hotmart may add anti-bot protection or change the SSR structure. No programmatic verification against live URLs without running the scanner end-to-end.

---

## Test Suite Summary

```
34 passed in 74.58s
Phase 1 (foundation):    15 tests GREEN
KiwifyScanner:            5 tests GREEN
ClickBankScanner:         5 tests GREEN
HotmartScanner:           5 tests GREEN
Scanner jobs + canary:    4 tests GREEN
```

Commits verified:
- `2209ce1` — Wave 0 contracts, migration, Kiwify fixtures, RED tests
- `a64a91b` — KiwifyScanner GREEN
- `da1c9a2` — ClickBank RED
- `8bc2f85` — ClickBankScanner GREEN
- `18684ae` — Hotmart + jobs RED
- `ab18494` — HotmartScanner + register_scanner_jobs + run_platform_canary GREEN

---

_Verified: 2026-03-14T22:32:49Z_
_Verifier: Claude (gsd-verifier)_
