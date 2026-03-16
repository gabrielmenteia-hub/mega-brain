# Architecture Patterns: MIS v2.0 Platform Expansion

**Domain:** Multi-platform product intelligence — scanner integration + cross-platform ranking
**Researched:** 2026-03-16
**Based on:** Direct codebase analysis of v1.0 (89 files, 11.393 LOC)
**Overall confidence:** HIGH (codebase fully read, patterns derived from actual code, not assumptions)

---

## Executive Summary

The v1.0 architecture is well-designed for expansion. The `PlatformScanner` ABC and `SCANNER_MAP` pattern in `scanner.py` were built to accept new scanners without touching shared infrastructure. The primary integration points are: (1) add scanner file in `mis/scanners/`, (2) register in `SCANNER_MAP` in `scanner.py`, (3) add platform row to DB via migration, (4) expand `VALID_PLATFORMS` in `config.py`, and (5) register platform canary in `health_monitor.py`. Platform IDs must be migrated from magic constants to a DB-driven registry via seed migration. The cross-platform unified ranking requires one new SQL query and one new route — no schema changes needed.

---

## Existing Architecture: What v1.0 Actually Looks Like

### Scanner Integration Points (read from source)

```
mis/
├── scanner.py                  ← PlatformScanner ABC + Product dataclass + run_all_scanners()
│   SCANNER_MAP = {             ← THE registration point for all scanners
│       "kiwify": KiwifyScanner,
│       "hotmart": HotmartScanner,
│       "clickbank": ClickBankScanner,
│   }
├── scanners/
│   ├── hotmart.py              HOTMART_PLATFORM_ID = 1
│   ├── clickbank.py            CLICKBANK_PLATFORM_ID = 2
│   └── kiwify.py               KIWIFY_PLATFORM_ID = 3
├── config.py                   VALID_PLATFORMS = {"hotmart", "clickbank", "kiwify"}
├── health_monitor.py           platforms = [(1, "hotmart"), (2, "clickbank"), (3, "kiwify")]
├── scheduler.py                register_scan_and_spy_job() — no platform awareness needed
├── product_repository.py       upsert_product() — platform_id is a field, no platform logic
└── migrations/
    ├── _001_initial.py         platforms table: id, name, slug, base_url, created_at
    └── _005_alerts.py          ← current last migration
```

### How run_all_scanners() Dispatches

```python
# 1. SCANNER_MAP lookup by name string from config.yaml
scanner_cls = SCANNER_MAP.get(platform_name)
if scanner_cls is None:
    log.warning("scanner.platform.not_implemented", ...)
    continue  # graceful skip — does NOT crash

# 2. Platform ID is hardcoded IN the scanner file (e.g. HOTMART_PLATFORM_ID = 1)
#    The scanner passes it to every Product() it creates

# 3. Niche IDs are resolved from DB at runtime (already generic — no hardcoding)
```

The dispatch is already generic. A new platform is "implemented" the moment its key appears in `SCANNER_MAP` and its scanner class is importable.

### Platform ID Problem (v1.0 State)

Platform IDs are hardcoded as module-level constants in each scanner file:
- `hotmart.py`: `HOTMART_PLATFORM_ID = 1`
- `clickbank.py`: `CLICKBANK_PLATFORM_ID = 2`
- `kiwify.py`: `KIWIFY_PLATFORM_ID = 3`

The `platforms` table in SQLite holds the authoritative record, but the seeding of rows with specific IDs happens in test fixtures only (`INSERT OR IGNORE`). There is no production seed migration. This means:

1. The integers 1, 2, 3 are an implicit contract between scanner files and the DB.
2. Adding 13 new platforms extends this contract to IDs 4-16.
3. There is no single source of truth — it is split between scanner file constants and DB rows.
4. Without a seed migration, the FK constraint `products.platform_id -> platforms.id` will fail in production for every new scanner that tries to upsert a product.

---

## Component Boundaries

| Component | Responsibility | Change in v2.0 | Type |
|-----------|---------------|----------------|------|
| `mis/scanners/` | One file per platform, implement `PlatformScanner.scan_niche()` | 13 new files | NEW |
| `mis/scanner.py` | `SCANNER_MAP` registration, `run_all_scanners()` dispatch | 13 new entries | MODIFY |
| `mis/config.py` | `VALID_PLATFORMS` set validation | 13 new slugs | MODIFY |
| `mis/health_monitor.py` | `register_platform_canary_jobs()` platform list | 13 new tuples | MODIFY |
| `mis/migrations/_006_v2_platforms.py` | Seed all 16 platform rows with fixed IDs | New file | NEW |
| `mis/db.py` | Migration runner | 1-line addition | MODIFY |
| `mis/web/routes/ranking.py` | `/ranking/unified` cross-platform route | Append new route | MODIFY |
| `mis/dossier_repository.py` | `list_unified_ranking()` query | Append new function | MODIFY |
| `mis/web/templates/ranking_unified.html` | Cross-platform ranking view | New template | NEW |
| `mis/config.yaml` | User-configured platforms per niche | User-edited | MODIFY |

---

## Data Flow: How a New Scanner Integrates

```
config.yaml (niche to platform mapping)
         |
         v
run_all_scanners()
  -> niche_id_map resolved from DB (already generic, no changes needed)
  -> for each (niche, platform_name) in config:
      scanner_cls = SCANNER_MAP.get(platform_name)  <- ADD new entry here
      async with scanner_cls(...) as scanner:
          products = await scanner.scan_niche(niche_slug, platform_slug)
          # scanner creates Product(platform_id=NEW_ID, ...)
  -> save_batch_with_alerts(db, db_path, products)
      -> upsert_product() — platform_id FK must exist in platforms table
      -> alert if new top-20 entry
```

The FK constraint `platform_id -> platforms.id` means the `platforms` table row MUST exist before any products are saved. This is the only hard dependency for new scanners.

---

## Platform ID Management Strategy

### Recommended: DB-Authoritative IDs via Seed Migration

**Approach:** Create migration `_006_v2_platforms.py` that uses `INSERT OR IGNORE` to seed all 16 platform rows with fixed IDs. Scanner constants then reflect the seeded values.

```
Platform ID Assignment (v2.0 canonical):
  1  = Hotmart       (existing — seeded idempotently)
  2  = ClickBank     (existing)
  3  = Kiwify        (existing)
  4  = Eduzz
  5  = Monetizze
  6  = PerfectPay
  7  = Braip
  8  = JVZoo
  9  = Udemy
  10 = Teachable
  11 = Kajabi
  12 = Skool
  13 = Stan Store
  14 = Product Hunt
  15 = AppSumo
  16 = Gumroad
```

**Why fixed IDs work here:** `INSERT OR IGNORE INTO platforms (id, ...) VALUES (4, ...)` is deterministic and idempotent. Unlike auto-increment, explicit IDs survive DB recreations and can be committed to code as constants. This is the same pattern already used in test fixtures.

**Alternative rejected — DB lookup at runtime:** Scanner resolves platform_id via `SELECT id FROM platforms WHERE slug = ?` at init time. Rejected because: (1) adds a DB query per scanner instantiation, (2) creates hidden DB dependency at import time, (3) breaks tests that mock at HTTP level, (4) is inconsistent with the existing v1.0 pattern which all existing tests depend on.

### Migration _006 Data

```python
# mis/migrations/_006_v2_platforms.py
PLATFORMS_V2 = [
    (1,  "Hotmart",      "hotmart",      "https://hotmart.com"),
    (2,  "ClickBank",    "clickbank",    "https://clickbank.com"),
    (3,  "Kiwify",       "kiwify",       "https://kiwify.com.br"),
    (4,  "Eduzz",        "eduzz",        "https://eduzz.com"),
    (5,  "Monetizze",    "monetizze",    "https://monetizze.com.br"),
    (6,  "PerfectPay",   "perfectpay",   "https://perfectpay.com.br"),
    (7,  "Braip",        "braip",        "https://braip.com"),
    (8,  "JVZoo",        "jvzoo",        "https://jvzoo.com"),
    (9,  "Udemy",        "udemy",        "https://udemy.com"),
    (10, "Teachable",    "teachable",    "https://teachable.com"),
    (11, "Kajabi",       "kajabi",       "https://kajabi.com"),
    (12, "Skool",        "skool",        "https://skool.com"),
    (13, "Stan Store",   "stan-store",   "https://stan.store"),
    (14, "Product Hunt", "product-hunt", "https://producthunt.com"),
    (15, "AppSumo",      "appsumo",      "https://appsumo.com"),
    (16, "Gumroad",      "gumroad",      "https://gumroad.com"),
]
# INSERT OR IGNORE preserves existing rows (idempotent for IDs 1-3 on existing DBs)
```

---

## DB Schema Changes Required

### Assessment: No Schema Changes Needed

The existing schema already handles N platforms correctly:

- `platforms` table: generic `id, name, slug, base_url, created_at` — just needs new rows.
- `products` table: FK `platform_id -> platforms.id` — already works for any platform_id value.
- `dossiers`, `pains`, `alerts`: no platform-specific columns — unchanged.

The only change is **data** (new rows in `platforms`), not schema. This is handled entirely by `_006_v2_platforms.py`.

### Migration Chain Update

`mis/db.py` `run_migrations()` must be extended to call `_006`. This is a 2-line change:

```python
# mis/db.py — add import + call
from .migrations._006_v2_platforms import run_migration_006 as _run_006

def run_migrations(db_path: str) -> None:
    _run_001(db_path)
    _run_002(db_path)
    _run_003(db_path)
    _run_004(db_path)
    _run_005(db_path)
    _run_006(db_path)   # NEW
```

---

## New Scanner Implementation Pattern

Each new scanner follows the exact same structure as `hotmart.py` and `kiwify.py`:

```python
# mis/scanners/eduzz.py
EDUZZ_PLATFORM_ID = 4  # must match _006_v2_platforms.py seed

class EduzzScanner(PlatformScanner):
    async def scan_niche(
        self, niche_slug: str, platform_slug: str, niche_id: int = 0
    ) -> list[Product]:
        # fetch -> parse -> return list[Product(platform_id=EDUZZ_PLATFORM_ID, ...)]
        # return [] on any error (never raise)
        # log schema_drift alert when parsing fails
```

The scanner contract:
1. Define `{PLATFORM}_PLATFORM_ID = N` constant matching the migration seed.
2. Inherit from `PlatformScanner`.
3. Implement `scan_niche()` returning `list[Product]` or `[]` on failure.
4. Log `schema_drift` alert (structlog) when parsing fails.
5. Never raise exceptions from `scan_niche()`.

### Scanner Classification by Access Method

| Platform | Access Method | Complexity | Notes |
|----------|--------------|------------|-------|
| Eduzz | SSR HTML or unofficial API | MEDIUM | Similar to Hotmart; BR platform |
| Monetizze | SSR HTML | MEDIUM | BR platform, public marketplace |
| PerfectPay | SSR HTML | MEDIUM | BR platform |
| Braip | SSR HTML | MEDIUM | BR platform |
| JVZoo | Public marketplace listing (HTML) | MEDIUM | Gravity-like ranking metric |
| Udemy | Unofficial course search | MEDIUM-HIGH | Rate limiting enforced aggressively |
| Teachable | No public marketplace | HIGH | Must find alternative access approach |
| Kajabi | No public marketplace | HIGH | No browse page; alternative approach needed |
| Skool | Public community listings | MEDIUM | Newer platform, SSR likely |
| Stan Store | Public creator storefront | MEDIUM | Newer, structure not confirmed |
| Product Hunt | Official REST API (free) | LOW | `?category=` filter, rate-limited |
| AppSumo | Public browse page (SSR HTML) | LOW-MEDIUM | Stable structure |
| Gumroad | Discover page (SSR HTML) | LOW-MEDIUM | Public category browse |

**Confidence note on complexity:** MEDIUM confidence for Teachable, Kajabi, Skool, Stan Store — derived from general platform knowledge, not live HTML inspection. Each scanner must begin with a reconnaissance step to confirm current HTML structure before writing selectors.

---

## Cross-Platform Unified Ranking

### Design Decision

The cross-platform unified ranking must aggregate products across all platforms by niche and normalize scores. The key challenge: ClickBank uses gravity score (higher = better, range 0-600+), while Hotmart and Kiwify use positional rank (1 = best). These are incompatible raw values.

**Recommended normalization:** Convert all ranks to percentile within their platform-niche group using a SQLite window function. Lower percentile = better position.

```
normalized_rank = (rank - 1) / (max_rank_in_group - 1)
  -> 0.0 = top product in this platform-niche group
  -> 1.0 = bottom product in this platform-niche group
  -> Comparable across all platforms
```

For ClickBank, the existing `_gravity_to_rank()` function already converts gravity to positional rank (rank=1 means highest gravity). The normalization formula works consistently across all platforms without special-casing ClickBank.

### Implementation: New Route + New Query Function

Do not modify the existing `/ranking` route. The existing route handles per-platform filtering and is covered by existing tests. Add `/ranking/unified` as a new independent route.

**`mis/dossier_repository.py` — add `list_unified_ranking()`:**

```sql
SELECT
    p.id,
    p.title,
    p.url,
    pl.name  AS platform_name,
    pl.slug  AS platform_slug,
    n.name   AS niche_name,
    n.slug   AS niche_slug,
    p.rank   AS raw_rank,
    CAST(p.rank - 1 AS REAL) /
        NULLIF(MAX(p.rank) OVER (PARTITION BY p.platform_id, p.niche_id) - 1, 0)
        AS normalized_rank,
    d.opportunity_score,
    d.confidence_score,
    CASE WHEN d.id IS NOT NULL THEN 1 ELSE 0 END AS has_dossier
FROM products p
JOIN platforms pl ON pl.id = p.platform_id
JOIN niches    n  ON n.id  = p.niche_id
LEFT JOIN dossiers d ON d.product_id = p.id
WHERE (:niche IS NULL OR n.slug = :niche)
ORDER BY normalized_rank ASC
LIMIT :limit OFFSET :offset
```

SQLite window functions are available since version 3.25.0 (September 2018). Python 3.14 ships with SQLite >= 3.39. This query is safe with no additional dependencies.

### What to Add to ranking.py

```python
# mis/web/routes/ranking.py — append

@router.get("/ranking/unified")
async def unified_ranking(request: Request, niche: str | None = None, page: int = 1):
    db = get_db(request.app.state.db_path)
    products = list_unified_ranking(db, niche_slug=niche, per_page=50, page=page)
    return request.app.state.templates.TemplateResponse(
        "ranking_unified.html",
        {"request": request, "products": products, "niche": niche, "page": page},
    )
```

### Alternative Rejected: SQLite VIEW

A `CREATE VIEW unified_ranking AS ...` migration was considered. Rejected: views with window functions can produce suboptimal query plans in SQLite for paginated queries; the existing pattern uses Python-level query functions, not views; adding a view requires a migration when a query function is sufficient.

### Template Requirements

`mis/web/templates/ranking_unified.html` — new template:
- Table columns: niche name, platform badge (colored tag by slug), product title, normalized rank (0.0-1.0), opportunity score, dossier link.
- Platform badge distinguishes rows from different platforms visually.
- Reuse existing HTMX niche filter dropdown pattern from `ranking.html`.

---

## Registration Checklist Per New Scanner

For each of the 13 new scanners, these are the exact files to touch:

```
1. mis/scanners/{platform}.py              NEW  — implement PlatformScanner
2. mis/scanner.py SCANNER_MAP              MODIFY (1 line) — add "{slug}": {Class}
3. mis/config.py VALID_PLATFORMS           MODIFY (1 entry) — add "{slug}"
4. mis/health_monitor.py platform list     MODIFY (1 tuple) — add (ID, "{slug}")
5. mis/migrations/_006_v2_platforms.py     NEW once, covers all 13 platforms
6. mis/db.py run_migrations()              MODIFY 2 lines, once
7. mis/config.yaml                         User adds platform slug under each niche
8. mis/tests/test_{platform}_scanner.py   NEW  — unit + integration tests
```

Items 2, 3, 4 are single-line edits per scanner. Items 1, 8 are new files per scanner. Items 5, 6 are done once for all 13 platforms combined.

---

## Build Order

```
Step 1: Migration _006_v2_platforms.py  (blocker for all Steps 3-5)
  -> mis/migrations/_006_v2_platforms.py  (NEW)
  -> mis/db.py  (MODIFY: add _run_006 call)
  WHY FIRST: FK constraint means platforms rows must exist before any Product
  upsert. Without this, every new scanner crashes on first product save.

Step 2: Infrastructure updates  (depends on Step 1 constants, groups low-risk edits)
  -> mis/scanner.py SCANNER_MAP (add all 13 entries)
  -> mis/config.py VALID_PLATFORMS (add all 13 slugs)
  -> mis/health_monitor.py platforms list (add all 13 tuples)
  WHY GROUPED: Mechanical, low-risk edits. Doing together ensures consistency —
  no scanner is registered without its validation and health canary.

Step 3: BR platforms  (Eduzz, Monetizze, PerfectPay, Braip)
  -> 4 new scanner files + 4 test files
  WHY FIRST: Same SSR HTML pattern as Hotmart/Kiwify (well-understood). BR
  platforms are the primary target audience. Establishes implementation
  template for the remaining scanners.

Step 4: International high-confidence  (JVZoo, AppSumo, Gumroad, Product Hunt)
  -> 4 new scanner files + 4 test files
  WHY NEXT: Product Hunt has official API (lowest risk). AppSumo and Gumroad
  have public SSR pages. JVZoo has a public marketplace. Medium-low unknown surface.

Step 5: Course platforms  (Udemy, Teachable, Kajabi, Skool, Stan Store)
  -> 5 new scanner files + 5 test files
  WHY LAST: Highest implementation uncertainty. Teachable and Kajabi lack a
  marketplace browse page. Each requires a reconnaissance step before writing
  selectors. Do after the pattern is established in Steps 3-4.

Step 6: Cross-platform unified ranking  (depends on having multi-platform data)
  -> mis/dossier_repository.py (add list_unified_ranking)
  -> mis/web/routes/ranking.py (add /ranking/unified route)
  -> mis/web/templates/ranking_unified.html (new template)
  -> mis/tests/web/test_web_unified_ranking.py
  WHY LAST: Window function query can be unit-tested with fixture data, but
  end-to-end validation needs scanners from Steps 3-5 populating real data.
```

---

## Anti-Patterns to Avoid in v2.0

### Anti-Pattern 1: Skipping the Seed Migration

The current state: platform rows seeded in tests only, no production migration. For 13 new platforms this MUST be fixed first. Without `_006_v2_platforms.py`, the FK constraint on `products.platform_id` will raise `sqlite3.IntegrityError` in production for every new scanner's first product upsert.

**Fix:** `_006_v2_platforms.py` with `INSERT OR IGNORE INTO platforms (id, ...) VALUES ...` for all 16 platforms, including IDs 1-3 (idempotent on existing DBs).

### Anti-Pattern 2: Each Scanner Resolving Its Own Platform ID from DB

Tempting for "clean" design: `SELECT id FROM platforms WHERE slug = 'eduzz'` at scanner init time. Rejected: adds latency, creates hidden DB dependency at import time, breaks tests that mock at HTTP level, inconsistent with existing pattern all existing tests depend on.

**Fix:** Keep `EDUZZ_PLATFORM_ID = 4` constants in scanner files, matching the migration seed.

### Anti-Pattern 3: Materializing normalized_rank in the Products Table

Adding `normalized_rank FLOAT` to the products table is rejected: normalized rank depends on the max rank in the group, which changes every scan cycle. Storing it means either stale data or recomputing on every upsert. The SQL window function computes it correctly on read.

### Anti-Pattern 4: All 13 Scanners in One PR

Each scanner group (BR, international, course platforms) should be a separate PR. Every merged PR must have GREEN tests. A single 13-scanner PR is unreviable and a single broken scanner blocks all others.

### Anti-Pattern 5: Implementing Kajabi and Teachable Without Reconnaissance

Both platforms lack a standard marketplace browse page. Implementing with the SSR scraping pattern without live inspection will produce a scanner that returns `[]` immediately and logs `schema_drift`. These two scanners need a discovery step before implementation — they must be flagged as needing deeper research during phase planning.

---

## Scalability Assessment

v2.0 stays within the SQLite + APScheduler envelope. 16 platforms x 3-5 niches = 48-80 scan iterations per cycle. APScheduler handles this trivially in a single `AsyncIOScheduler`. No infrastructure changes are needed.

| Concern | At 16 platforms / daily | Notes |
|---------|------------------------|-------|
| Storage | SQLite fine | ~800 rows/cycle; trivial |
| Scheduler | APScheduler in-process fine | Same single scan_and_spy job, more iterations |
| Concurrency | `parallel_scanners: true` already handles this | Existing config key |
| Dashboard | Existing pagination handles more rows | No changes needed |

---

## Modified Files Summary

| File | Change Type | Risk |
|------|------------|------|
| `mis/migrations/_006_v2_platforms.py` | NEW | LOW |
| `mis/db.py` | MODIFY (2 lines) | LOW |
| `mis/scanner.py` | MODIFY (13 entries in SCANNER_MAP) | LOW |
| `mis/config.py` | MODIFY (13 entries in VALID_PLATFORMS) | LOW |
| `mis/health_monitor.py` | MODIFY (13 tuples in platform list) | LOW |
| `mis/scanners/eduzz.py` | NEW | MEDIUM |
| `mis/scanners/monetizze.py` | NEW | MEDIUM |
| `mis/scanners/perfectpay.py` | NEW | MEDIUM |
| `mis/scanners/braip.py` | NEW | MEDIUM |
| `mis/scanners/jvzoo.py` | NEW | MEDIUM |
| `mis/scanners/appsumo.py` | NEW | MEDIUM |
| `mis/scanners/gumroad.py` | NEW | MEDIUM |
| `mis/scanners/product_hunt.py` | NEW | LOW |
| `mis/scanners/udemy.py` | NEW | MEDIUM-HIGH |
| `mis/scanners/teachable.py` | NEW | HIGH |
| `mis/scanners/kajabi.py` | NEW | HIGH |
| `mis/scanners/skool.py` | NEW | MEDIUM |
| `mis/scanners/stan_store.py` | NEW | MEDIUM |
| `mis/dossier_repository.py` | MODIFY (add list_unified_ranking) | LOW |
| `mis/web/routes/ranking.py` | MODIFY (add /ranking/unified route) | LOW |
| `mis/web/templates/ranking_unified.html` | NEW | LOW |

---

## Confidence Assessment

| Area | Confidence | Basis |
|------|-----------|-------|
| Scanner integration points | HIGH | Directly read from scanner.py, config.py, health_monitor.py |
| Platform ID management strategy | HIGH | Pattern matches existing test fixtures; INSERT OR IGNORE is well-understood SQLite pattern |
| DB schema changes | HIGH | Schema is permissive; only new data rows needed, no ALTER TABLE |
| Cross-platform SQL query | HIGH | SQLite window function support confirmed (3.25+, 2018); syntax is standard |
| Scanner complexity per platform | MEDIUM | General knowledge of platform structures; live inspection required before implementation |
| Kajabi and Teachable feasibility | LOW | No public marketplace confirmed; access approach unclear without live reconnaissance |

---

## Sources

- All integration points derived from direct codebase reading: `mis/scanner.py`, `mis/scanners/hotmart.py`, `mis/scanners/clickbank.py`, `mis/config.py`, `mis/health_monitor.py`, `mis/migrations/_001_initial.py`, `mis/migrations/_002_product_enrichment.py`, `mis/product_repository.py`, `mis/scheduler.py`, `mis/web/app.py` (read 2026-03-16)
- SQLite window functions: https://www.sqlite.org/windowfunctions.html (available since SQLite 3.25.0, September 2018)
- Product Hunt API: https://api.producthunt.com/v2/docs (public REST API, free tier available)
- Scanner complexity estimates: MEDIUM confidence, general platform knowledge only
