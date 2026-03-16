# Domain Pitfalls — MIS v2.0 Platform Expansion (13 New Scanners)

**Domain:** Adding new platform scanners to an existing multi-platform scraping system
**Researched:** 2026-03-16
**Confidence:** MEDIUM (training data cutoff August 2025; web search unavailable; findings grounded in v1.0 codebase direct read + known platform behaviors)

---

## Context: What Already Exists

v1.0 shipped with:
- `BaseScraper` with rate limiting, retry, proxy rotation, anti-bot headers
- `PlatformScanner` ABC with `scan_niche()` contract
- `SCANNER_MAP` dict in `run_all_scanners()` — new scanners register here
- `Product` dataclass with `rank` (int), `price` (float|None), `commission_pct` (float|None), `rating` (float|None)
- Known lessons: Kiwify has no public marketplace (synthetic fixtures), ClickBank is React SPA with GraphQL, Playwright stealth needed for some platforms, APScheduler `replace_existing` bug on stopped scheduler

The 13 new platforms fall into 4 categories by integration difficulty:

- **Category A (Easy — SSR HTML):** Hotmart-like pattern. Eduzz, Monetizze, PerfectPay, Braip.
- **Category B (Medium — JS SPA or API):** JVZoo (HTML but bot-hostile), Gumroad (JS discover page), Product Hunt (GraphQL API), AppSumo (SSR but aggressive rate limiting).
- **Category C (Hard — Cloudflare + JS):** Udemy (Cloudflare Enterprise + React SPA).
- **Category D (No Public Marketplace — synthetic fixtures or defer):** Kajabi, Teachable, Skool, Stan Store.

---

## Critical Pitfalls

Mistakes that cause data corruption, silent failures, or integration breaks.

---

### Pitfall 1: Mapping "Rank" to Incompatible Metrics Across Platforms

**What goes wrong:** The existing `Product.rank` field (int) works cleanly for positional rank (Hotmart) and gravity score (ClickBank, gravity stored as int). But the 13 new platforms use completely different ranking signals:
- Udemy: enrollment count (volume) — a 6-figure number stored as rank
- Product Hunt: upvote count (resets every 24 hours) — not a stable ranking
- AppSumo: positional from search results, weighted by "staff pick" (editorial)
- Gumroad: no explicit ranking — discover page sorted by pageviews (volume)
- JVZoo: EPC (earnings per click) — a float metric, not a position
- Kajabi / Teachable / Skool: no marketplace ranking at all

Storing all of these into `rank: int` produces a cross-platform products table where rank=150 means "ClickBank gravity 150" and rank=2 means "position 2 in Udemy enrollment-sorted search" — completely different semantics. The DASH-V2 unified cross-platform ranking view will silently produce wrong comparisons.

**Why it happens:** The v1.0 `Product` dataclass was designed for positional or score-based ranking. The new platforms force a mapping decision that has not been made yet.

**Consequences:** DASH-V2 "unified ranking" becomes meaningless. Sorting products by `rank` DESC mixes JVZoo EPC scores against ClickBank gravity against Udemy enrollment counts — apples vs. oranges. The user will see incoherent rankings and lose trust in the intelligence product.

**Prevention:**
- Before writing any of the 13 scanners, add `rank_type` metadata to the `platforms` table: valid values are `positional`, `score`, `volume`, `editorial`. Or add a `rank_raw_metric` varchar column to `products` documenting what the stored int represents.
- For the unified cross-platform view, normalize all ranks to a 0–100 percentile scale per platform, stored separately from raw rank. Do not use raw `rank` int for cross-platform sorting.
- Document the mapping explicitly in a companion `PLATFORM_RANK_SEMANTICS` dict in `mis/platform_ids.py`: `{"udemy": "volume_enrollment", "jvzoo": "epc_floor_int", "product_hunt": "daily_upvotes_resets", ...}`.
- Phase the work: Phase 1 of v2.0 stores raw rank correctly per platform; the normalization layer is built before DASH-V2 is implemented.

**Warning signs:**
- Dashboard shows a $9 Gumroad ebook ranked above a $1,997 course because both used raw positional rank from different result sets
- Any cross-platform query sorted by `rank` that does not first filter by `platform_id`
- A single product appearing with rank values oscillating between 1 and 500,000 across two platforms

**Phase:** Resolve BEFORE writing any scanner for the 13 new platforms. This is a schema and contract decision.

---

### Pitfall 2: Kajabi, Teachable, Skool, Stan Store — No Public Marketplace (Same Category as Kiwify)

**What goes wrong:** These four platforms are hosted content management systems — they sell tools to course creators, not products in a public browseable marketplace. There is no `platform.com/marketplace` URL to scrape. Attempting to build scanners for them as if they had a marketplace will result in immediate 404s or login walls, and the scanners will silently return `[]` forever.

v1.0 already resolved this with Kiwify (confirmed: no public marketplace; used synthetic HTML fixtures for tests). The v2.0 requirement `SCAN-V2` lists all 13 platforms without distinguishing open marketplaces from closed platforms.

**Why it happens:** The project requirement was written based on platform names from market research, not based on verifying whether each platform exposes a public ranking page.

**Consequences:** 4 of 13 scanner slots will be permanently empty if built as standard marketplace scanners. If synthetic data is used in production, the health monitor will think the scanners are working when they are returning fabricated data. If the team realizes this mid-sprint, significant rework is required.

**Prevention:**
- Before writing any scanner code, manually verify each platform: does a public marketplace URL exist? Can you browse top-selling products without a login? Document the result in the scanner module docstring.
- For confirmed closed platforms: either (a) design an alternative discovery strategy (Google SERP `site:kajabi.com` + public preview pages for member count), or (b) defer to v3.0 as `SCAN-V2-DEFERRED`.
- Do not build scanners that return synthetic data in production — the health monitor will never fire alerts, hiding the permanent data gap.
- Better to ship 9 working scanners than 13 where 4 always return empty.

**Warning signs:**
- Scanner always returns exactly 0 products even with confirmed working network
- Canary check passes (HTTP 200 on homepage) but 0 products in DB for that platform_id
- The platform's public-facing homepage markets itself as "build your own course" with no "browse courses" navigation

**Phase:** Pre-build classification. Resolve before writing any scanner code for these 4 platforms.

---

### Pitfall 3: SCANNER_MAP Registration — Silent Miss When New Scanner Is Not Registered

**What goes wrong:** `run_all_scanners()` in `scanner.py` has a hardcoded dict:

```python
SCANNER_MAP = {
    "kiwify": KiwifyScanner,
    "hotmart": HotmartScanner,
    "clickbank": ClickBankScanner,
}
```

When a new scanner is built (e.g., `EduzzScanner`), it must be manually added to this dict AND imported inside the function. If either step is missed:
- The scanner class exists and passes all unit tests
- Config entries for `eduzz:` in `config.yaml` are silently skipped with a `scanner.platform.not_implemented` warning log
- The dashboard shows 0 products for Eduzz indefinitely
- Developers do not notice because their unit tests test the scanner class directly, not via `run_all_scanners()`

This is the integration failure mode for every one of the 13 new platforms.

**Why it happens:** The `SCANNER_MAP` is an explicit registry, not auto-discovery. It requires a manual two-step process per scanner. v1.0 had 3 scanners and this was manageable. At 16 scanners, the probability of missing one step is high.

**Consequences:** Scanner built and tested in isolation but never runs in production. User reports 0 products for a platform. Debugging is non-obvious because unit tests are all green.

**Prevention:**
- Create an integration test `test_scanner_map_complete.py` that asserts `set(SCANNER_MAP.keys()) == set(EXPECTED_PLATFORM_SLUGS)` where `EXPECTED_PLATFORM_SLUGS` is a frozenset maintained in `mis/platform_ids.py`.
- Better: refactor `SCANNER_MAP` to be auto-populated from scanner modules that expose a `SCANNER_SLUG: str` constant — import all scanner modules at startup, collect those that define the constant. This eliminates the manual registration step entirely.
- At minimum: add a comment block in `scanner.py` next to `SCANNER_MAP` listing all expected entries, making missing entries obvious during code review.

**Warning signs:**
- `scanner.platform.not_implemented` log entries for a platform that has a scanner file in `mis/scanners/`
- `config.yaml` has a platform entry but `products` table shows 0 rows for that `platform_id`
- New scanner file exists in `mis/scanners/` but no corresponding import in `scanner.py`

**Phase:** Phase 1 of v2.0 implementation. Fix registration mechanism before adding any of the 13 scanners.

---

### Pitfall 4: Udemy — Cloudflare Enterprise + React SPA (Two Problems Together)

**What goes wrong:** Udemy runs Cloudflare Enterprise and renders course listings as a React SPA. `BaseScraper.fetch()` (httpx-based) will reliably return a 403 or a Cloudflare challenge page. `fetch_spa()` (Playwright) renders the JS, but Cloudflare's browser fingerprinting detects Playwright even with stealth plugins when requests originate from datacenter IPs.

However, Udemy has an undocumented JSON API (`https://www.udemy.com/api-2.0/courses/?page_size=50&ordering=enrollment&category_id=<id>`) that returns structured course data without authentication and bypasses Cloudflare entirely. This is the correct path for a Udemy scanner.

**Why it happens:** The obvious approach (scrape the marketplace HTML like Hotmart) fails hard on Cloudflare Enterprise. The API path requires knowing the undocumented endpoint format.

**Consequences:** If built as an HTML scraper, Udemy scanner returns empty results on every run, silently. Health monitor fires `schema_drift` when the real problem is bot blocking. The team may spend days trying to tune Playwright stealth settings for a problem that has a simpler solution.

**Prevention:**
- Use the undocumented Udemy API instead of HTML scraping. Verify the endpoint before building: `GET https://www.udemy.com/api-2.0/courses/?page_size=50&ordering=enrollment&category_id=268` (268 = Business, example). Confirm JSON response structure before writing the parser.
- Rate limit to 1 request per 10 seconds with random jitter. Udemy has been known to IP-ban scrapers hitting this endpoint at high frequency.
- Rank signal: use the `enrollment` field (enrollment count) as the rank proxy — store as `rank` int and document `rank_type: "volume_enrollment"` in the platform metadata.
- Add a Udemy-specific canary that distinguishes "Cloudflare block" (403 + `cf-ray` header) from "schema drift" (200 + empty `results` list) — the current generic `schema_drift` alert conflates both.
- Confidence: MEDIUM — API endpoint format based on training data (August 2025); verify current path before implementation.

**Warning signs:**
- HTTP 403 with `cf-ray` header in the response
- Response time < 80ms (Cloudflare edge block before reaching origin)
- `{"detail": "Authentication credentials were not provided."}` — hit an authenticated API path
- Response is HTML (not JSON) when hitting the API endpoint — Cloudflare challenge page returned

**Phase:** Phase 1 investigation. Test API endpoint manually before writing any scraper code.

---

### Pitfall 5: JVZoo — Incapsula Bot Detection (Different From Cloudflare)

**What goes wrong:** JVZoo's marketplace (`jvzoo.com/marketplace`) uses Incapsula/Imperva bot detection, not Cloudflare. Incapsula uses different fingerprinting techniques: it tracks cookie injection patterns, checks for canvas/WebGL fingerprints in browser contexts, and rotates its challenge cookies more aggressively. `playwright-stealth` was developed primarily to bypass Cloudflare; it may be insufficient for Incapsula.

Additionally, JVZoo uses EPC (earnings per click) as its ranking signal — displayed in the HTML as a float. Its format has changed multiple times.

**Why it happens:** Developers familiar with Cloudflare assume all modern bot protection uses the same techniques. Incapsula requires distinct fingerprint evasion approaches.

**Consequences:** JVZoo scanner gets blocked silently — the response is valid HTML containing an Incapsula challenge page. BeautifulSoup finds 0 product cards and returns `[]` with `schema_drift` alert. This is the same symptom as a legitimate HTML structure change, making diagnosis non-obvious.

**Prevention:**
- Before writing the full scanner, make a manual httpx GET to `jvzoo.com/marketplace` and inspect the response. If it contains `_Incapsula_resource` or `visid_incap_` cookie strings, Incapsula is confirmed active.
- If Incapsula is confirmed: use a residential proxy (Incapsula is significantly less aggressive on residential IPs than on datacenter IPs). If residential proxy still fails, Playwright with additional fingerprint patches beyond `playwright-stealth` is required.
- Add a JVZoo-specific bot detection check in the response parser: if HTML contains `_Incapsula_resource`, emit `alert="bot_detected"` instead of `alert="schema_drift"` — these require different mitigations.
- EPC rank: JVZoo shows EPC as a float (e.g., `$2.47`). Store as `int(epc * 100)` (cents) in the `rank` field and document `rank_type: "epc_cents"`.

**Warning signs:**
- Response HTML contains `_Incapsula_resource`, `visid_incap_`, or `incap_ses_` string patterns
- HTTP 200 response with a ~15KB HTML body that has no product elements but contains a hidden challenge form
- Response varies on consecutive identical requests (Incapsula rotates challenges)

**Phase:** Phase 1 investigation for JVZoo. Confirm bot protection type before writing parser.

---

### Pitfall 6: Product Hunt — Daily Rank Reset Breaks Rank Continuity

**What goes wrong:** Product Hunt's rankings reset every 24 hours. A product with 500 upvotes ranked #1 today will disappear from the daily ranking tomorrow, replaced by a completely different product. The `INSERT OR IGNORE` + `url_hash` idempotency pattern from v1.0 correctly prevents duplicates within the same day, but it means yesterday's #1 is a completely different DB row from today's #1 — cross-day rank comparison is meaningless.

Furthermore, Product Hunt has an official GraphQL API (`api.producthunt.com/v2/api/graphql`) that requires OAuth. Scraping the HTML without the API misses important signals (topic categories, upvote velocity, maker comments).

**Why it happens:** Product Hunt's ranking model is fundamentally different from affiliate marketplace rankings. It is a discovery voting mechanism, not a stable bestseller list. The `rank` field abstraction breaks here.

**Consequences:** After 30 days of scanning, the Product Hunt products table has 30 rows all with `rank` between 1 and 50, each for a different day, with no continuity. The "top products over time" chart is empty because no product appears more than 1–2 days. The unified ranking view cannot meaningfully include Product Hunt without a different schema treatment.

**Prevention:**
- Use the Product Hunt GraphQL API instead of HTML scraping. OAuth token required — document this as `product_hunt_api_key: <optional>` in `config.yaml`. Scanner degrades gracefully if token is absent.
- Add a `rank_date` column to the `products` table (or a separate `product_hunt_daily_ranks` table) to represent that Product Hunt rank is date-scoped, not absolute.
- For the unified ranking view, use "peak rank ever" or "number of days in top 10" as the Product Hunt signal, not the most recent raw rank.
- Classify Product Hunt as requiring OAuth setup in pre-build platform classification.

**Warning signs:**
- Product Hunt products table has 100+ rows all with `rank` 1–50 after weeks of scanning, with 0 repeated `external_id` values
- The "trending products" dashboard section changes 100% every day for Product Hunt (expected behavior, but indicates the schema is not capturing continuity)

**Phase:** Phase 1 classification. Product Hunt requires different DB schema treatment before any scanner code is written.

---

### Pitfall 7: AppSumo — Aggressive Per-Endpoint Rate Limiting Breaks Parallel Scans

**What goes wrong:** AppSumo (`appsumo.com`) has a public deal marketplace with SSR product listings that appears straightforward to scrape. However, AppSumo uses aggressive IP-based rate limiting per endpoint path (not just per-domain). Hitting the same category URL more than 4–5 times per minute triggers a soft ban: HTTP 429 or silent HTTP 200 with an empty product list. The soft ban lasts 15–30 minutes.

The `run_all_scanners()` coroutine runs all platform scans in parallel via `asyncio.gather()`. If AppSumo is scanned across 5 niches simultaneously, 5 concurrent requests hit the same IP on the same endpoint path, triggering the rate limit immediately.

**Why it happens:** The parallel scan architecture was designed for platforms that tolerate reasonable concurrency. AppSumo's rate limiting is niche-scoped (per endpoint path), not just per-domain. The v1.0 `BaseScraper` rate limiter operates per-domain but does not enforce cross-niche serialization.

**Consequences:** AppSumo scanner succeeds for the first niche and silently fails for all subsequent niches in every parallel scan cycle. Data appears "partially working" because one niche returns products. The root cause is disguised as `schema_drift` on the failing niches.

**Prevention:**
- `run_all_scanners()` needs per-platform concurrency controls before AppSumo is added. Add a `max_concurrent_per_platform: int` config option. AppSumo should be `max_concurrent: 1`.
- Add minimum 6-second delay between consecutive AppSumo requests regardless of which niche they belong to (cross-niche serialization, not just per-niche rate limiting).
- This is an infrastructure change to `run_all_scanners()` — the current flat `asyncio.gather()` cannot enforce per-platform sequencing. A per-platform semaphore is required.
- Alternative (simpler): run AppSumo in a separate scheduled job with a dedicated serialized coroutine, outside the main parallel scan.

**Warning signs:**
- First niche for AppSumo returns 20+ products; all subsequent niches return 0
- HTTP 429 appearing in logs immediately after the first AppSumo request in each scan cycle
- AppSumo result count varies depending on which niche was processed first in that run

**Phase:** Phase 1 infrastructure — add per-platform concurrency controls before registering AppSumo in `SCANNER_MAP`.

---

### Pitfall 8: Gumroad — Discover Page Is React Infinite Scroll, Not SSR

**What goes wrong:** Gumroad has a public discover page (`gumroad.com/discover`) for browsing products. The page appears to return HTML content but product listings are loaded dynamically via React infinite scroll — the initial HTML contains only a skeleton. `BaseScraper.fetch()` will return the page shell with no product cards. `fetch_spa()` with Playwright will render the first batch of products but miss all subsequent batches loaded on scroll.

Gumroad also has a public API (`api.gumroad.com/v2/`) but this API is scoped to a seller's own products (requires OAuth). It cannot be used for marketplace discovery.

**Why it happens:** Gumroad's discover page was built as a React SPA with lazy loading — standard modern web architecture. The API was designed for seller automation, not competitive intelligence.

**Consequences:** Scanner built with httpx returns 0 products. Scanner built with basic Playwright returns only the first ~12 products (initial render batch), missing the rest. The limitation is silent — scanner reports success with partial data.

**Prevention:**
- Build the Gumroad scanner with Playwright and add a scroll-and-wait loop: scroll to bottom, wait for new products to load, repeat until no new products appear (or a max count is reached).
- Rank signal: the discover page does not expose an explicit rank number. Use the card's position in the loaded sequence as positional rank (`rank_type: "positional_from_discover"`), or use the visible "wishlist count" or "sales count" if displayed on cards.
- Rate limit Playwright scrolling — each scroll triggers a new API call from the browser. Add 2-second waits between scrolls.
- Confirm the API scope before implementation: attempt a GET to `api.gumroad.com/v2/products` without a token and verify the 401 response to confirm it requires authentication.

**Warning signs:**
- `fetch()` returns HTML with `<div id="discover-app">` containing no nested product elements (CSR confirmed)
- Playwright scan returns exactly 12 products every time (initial render batch — scroll not implemented)
- API endpoint returns `{"success": false, "message": "..."}` without OAuth token

**Phase:** Phase 1 investigation. Classify as Playwright-required. Build scroll loop before integration testing.

---

## Moderate Pitfalls

---

### Pitfall 9: Brazilian Platforms May Have Changed Architecture Post-2023

**What goes wrong:** Eduzz, Monetizze, PerfectPay, and Braip are Brazilian infoproduct platforms similar to Hotmart. However, several underwent major rebranding and platform migrations between 2023 and 2025:
- Eduzz rebranded (possibly migrated domain/marketplace URL structure)
- Monetizze had significant platform changes post-2023
- PerfectPay and Braip are smaller platforms where marketplace discoverability is less certain

The training data (August 2025) reflects these platforms' state at that time. Their current marketplace URLs, HTML structure, and public accessibility in March 2026 are unverified.

**Why it happens:** Brazilian digital marketing platforms are in a consolidation phase. Rebrands that include domain changes make all prior URL knowledge stale.

**Consequences:** Scanner built against old URL structure gets HTTP 301 redirects or 404s. HTML parser fails because redesigned pages use different class names. All 4 scanners fail to return data silently.

**Prevention:**
- Manual verification of each platform before writing any parser: navigate to the expected marketplace URL and confirm it exists, is public (no login required), and is SSR (View Page Source shows product data).
- Document findings in the scanner module docstring: `# Verified: {date} — Marketplace at {URL} — SSR — Selectors: {primary}`.
- Build these 4 scanners in the same SSR/BeautifulSoup pattern as Hotmart but do not assume identical URL structure or selector names.
- Check Brazilian digital marketing community resources for recent platform migration reports before implementation.

**Warning signs:**
- HTTP 301 redirect on the expected marketplace URL (domain migration)
- Login page returned on what should be a public marketplace URL
- BeautifulSoup returns HTML but with zero product cards (possible CSR migration)

**Phase:** Phase 1 investigation for each. Low implementation risk once URL confirmed; high investigation risk if marketplace has moved.

---

### Pitfall 10: Platform ID Collision — No Central Registry for IDs 4–16

**What goes wrong:** v1.0 assigned platform IDs as hardcoded constants in each scanner file: `HOTMART_PLATFORM_ID = 1`, `CLICKBANK_PLATFORM_ID = 2`, `KIWIFY_PLATFORM_ID = 3`. These must match the `platforms` table rows seeded at DB initialization.

Adding 13 new platforms requires IDs 4–16. If IDs are not consistently assigned across (1) each scanner's constant, (2) the DB seed / migration SQL, and (3) any config references, products get stored with wrong `platform_id`, corrupting all cross-platform queries silently. SQLite does not enforce FK by default unless `PRAGMA foreign_keys = ON` — orphaned platform IDs write without error.

**Why it happens:** The v1.0 pattern works at 3 platforms. At 16, it requires 16 source locations to agree on the same integers.

**Consequences:** Eduzz products stored with `platform_id=4` but DB `platforms` table only has rows up to 3 (migration not run). Products are written with orphaned platform IDs. Dashboard shows 0 products for the new platform. Root cause is non-obvious because the scanner itself runs successfully.

**Prevention:**
- Create `mis/platform_ids.py` as a single source of truth: `PLATFORM_IDS: dict[str, int] = {"hotmart": 1, "clickbank": 2, "kiwify": 3, "appsumo": 4, "braip": 5, "eduzz": 6, "gumroad": 7, "jvzoo": 8, "kajabi": 9, "monetizze": 10, "perfectpay": 11, "product_hunt": 12, "skool": 13, "stan_store": 14, "teachable": 15, "udemy": 16}`.
- All scanner files import their platform ID from `platform_ids.py` — no hardcoded integers in scanner files.
- DB seed SQL and migration files use values from this dict (or load it via a Python migration script).
- Add a startup assertion in `mis/__init__.py` that compares `PLATFORM_IDS` against `SELECT id, slug FROM platforms` — raises `RuntimeError` if they diverge.

**Warning signs:**
- `products` table rows with `platform_id` values not present in the `platforms` table
- Scanner returns products successfully but they do not appear in the dashboard (wrong platform_id stored)
- Two scanner files both declare `PLATFORM_ID = 4`

**Phase:** Phase 1. Must be resolved before the first new scanner is registered.

---

### Pitfall 11: Price Normalization Complexity With Global Platforms

**What goes wrong:** v1.0 handles BRL (`R$ 197,00`) and USD (`$97.00`). The 13 new platforms introduce new complications:
- Udemy: USD with 90–99% permanent sale prices (a $199 course selling for $13.99 indefinitely). The scraped price is the sale price, not the real market value.
- Gumroad: creator-set currency — EUR, GBP, BRL, or USD all possible within the same category page.
- AppSumo: "lifetime deal" pricing (one-time payment, not subscription) — structurally incompatible with comparing against subscription-model platforms.
- Free/freemium products: Product Hunt and AppSumo list many $0 products. Storing `price=0.0` without a flag makes these look like broken price extractions rather than intentional free products.

**Why it happens:** The `Product.price: Optional[float]` field assumes a single meaningful price value per product. Global platforms with permanent sale pricing and multi-currency content break this assumption.

**Consequences:** Udemy products all show $13.99 price in the dashboard — the intelligence value of knowing "this course market trades at $197" is lost. Multi-currency comparisons produce nonsensical price rankings.

**Prevention:**
- For Udemy: capture both displayed price and original (strikethrough) price when both are visible. Use the original price as `price` for market intelligence purposes.
- Always store `currency_code` alongside `price` — do not assume USD for non-BR platforms.
- Flag $0 products explicitly: use `price=None` for unknown and `price=0.0` only for confirmed free products, with a convention documented in the schema.
- Document in the scanner that AppSumo "lifetime" prices are one-time and not comparable to subscription pricing.

**Phase:** Phase 1 (Product dataclass extension decision). Resolve before building any global platform scanner.

---

### Pitfall 12: Playwright Memory Accumulation With Multiple SPA Platforms

**What goes wrong:** The v1.0 `PlatformScanner.fetch_spa()` launches a Playwright browser context per call. With 3 platforms this was manageable. The 13 new platforms add at minimum Gumroad and potentially JVZoo as Playwright-required. If `asyncio.gather()` in `run_all_scanners()` launches Playwright for 3+ platforms across 5 niches simultaneously, that is 15+ concurrent browser contexts. Each Playwright context uses 150–300MB RAM. 15 contexts = 2.25–4.5GB RAM — OOM territory on standard servers.

**Prevention:**
- Add `PLAYWRIGHT_SEMAPHORE = asyncio.Semaphore(3)` as a module-level constant in `scanner.py` (max 3 concurrent Playwright instances system-wide).
- All `fetch_spa()` calls must acquire this semaphore before launching a browser context and release it on exit.
- This change must be made before any new Playwright-required scanner is added to `SCANNER_MAP`.
- Classify platforms as Playwright-required vs. httpx-only explicitly — minimize the Playwright set.

**Phase:** Phase 1 infrastructure. Required before Gumroad or any confirmed Playwright-required scanner is integrated.

---

### Pitfall 13: `schema_drift` Alert Conflates Too Many Failure Modes

**What goes wrong:** The v1.0 health monitor fires `alert='schema_drift'` for any scanner returning `[]`. With 13 new platforms, the failure modes multiply: true HTML structure change, bot detection / IP ban (Cloudflare 403, Incapsula challenge), no public marketplace (permanent expected empty for Category D), platform down (503), network timeout, OAuth token expired (Product Hunt API), per-platform rate limit triggered (AppSumo 429). All of these currently produce the same `schema_drift` alert.

**Why it happens:** The `schema_drift` label was appropriate for v1.0 where the only failure mode was HTML structure change. It is too generic for a 16-platform system.

**Consequences:** Alert fatigue. Operations team receives identical alerts for bot blocks, platform downtime, and expected-empty platforms. Real schema drifts go uninvestigated.

**Prevention:**
- Extend the alert taxonomy: `bot_detected` (403 + bot protection headers), `platform_down` (503/timeout), `auth_required` (401 without bot headers), `empty_marketplace` (expected for Category D), `rate_limited` (429), `schema_drift` (200 + no parseable products).
- Scanners should return a typed `ScanResult` (not just `list[Product]`) so the health monitor receives the failure reason along with the product list.
- For Category D platforms, configure the health monitor to expect 0 products and suppress all alerts for those platform_ids.

**Phase:** Phase 2 of v2.0 implementation, after the first wave of scanners is operational and failure modes are understood empirically.

---

## Minor Pitfalls

---

### Pitfall 14: Config YAML Complexity Explosion — 13 New Platform Entries Per Niche

**What goes wrong:** `config.yaml` currently has each niche specifying which platforms to scan with a `platform_slug` value per platform. With 13 new platforms, each niche entry grows from 3 lines to 16. For 5 niches, the config grows from ~20 platform-slug mappings to ~80. Finding the correct `platform_slug` per niche per platform requires manual research on each platform's category taxonomy.

**Prevention:**
- Introduce a `default_platforms:` section at the config root level. Niches inherit all platforms unless they explicitly opt out.
- For platforms where niche filtering does not apply (Product Hunt, AppSumo), use a sentinel value (`platform_slug: "all"`) that the scanner handles by ignoring niche filtering.
- Create `docs/platform-niche-slug-map.md` documenting the mapping from each MIS niche to its slug per platform. This is research work, not coding work — budget time for it.

**Phase:** Phase 1 config design before writing scanner code.

---

### Pitfall 15: Skool Community Gating — Different From Teachable/Kajabi

**What goes wrong:** Skool (`skool.com`) is more severely gated than Kajabi or Teachable. Skool communities are explicitly private by design. Unlike Teachable (which has public course landing pages) or Kajabi (which has public sales pages), Skool's community content is entirely behind a join wall.

The only public data on Skool is the community preview card (community name, member count, description, price to join) available on `skool.com/communities`. Member count is the only useful ranking signal, and it is a size metric, not a quality or sales ranking.

**Prevention:**
- If a Skool scanner is built at all, scope it to `skool.com/communities` sorted by member count. `rank` = positional in directory, `rank_type: "directory_positional_by_members"`.
- Store member count in the `rating` field (float) for lack of a better field in the existing schema.
- Mark `confidence_score: 0.3` for all Skool products in dossier generation — the data has low intelligence value compared to an actual product marketplace.
- If the communities directory requires login beyond the first page, defer Skool entirely.

**Phase:** Pre-build classification decision. Build only if the communities directory is confirmed publicly pageable without authentication.

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Pre-build platform classification | Category D platforms permanently returning empty data | Manual verification before writing any scanner: Does a public marketplace URL exist? |
| Cross-platform rank normalization | `rank` field semantically incompatible across platforms | Resolve schema before writing any scanner; add `rank_type` to platforms table |
| `SCANNER_MAP` registration | New scanner built but never called in production | Integration test asserting SCANNER_MAP keys match expected platform list |
| Platform ID assignment (IDs 4–16) | Collisions or scanner/DB constant mismatch | Central `mis/platform_ids.py`; startup validation assertion |
| Udemy scanner | Cloudflare Enterprise blocks httpx + React SPA | Use undocumented JSON API (`/api-2.0/courses/`) instead of HTML |
| JVZoo scanner | Incapsula bot detection — different from Cloudflare | Test access before building; residential proxy; specific `bot_detected` alert |
| Product Hunt scanner | Daily rank reset makes rank field semantically wrong | GraphQL API + OAuth; `rank_date` dimension; unified ranking uses "peak rank ever" |
| AppSumo scanner | Aggressive per-endpoint rate limiting breaks parallel scan | Per-platform concurrency limiter; serialize AppSumo requests across niches |
| Gumroad scanner | Discover page is React infinite scroll, not SSR | Playwright with scroll loop; rank from card position or wishlist count |
| Brazilian platforms (Eduzz, Monetizze, PerfectPay, Braip) | Post-rebranding domain/structure changes in 2023–2025 | Manual URL verification before implementation |
| Multiple Playwright-required platforms | 15+ concurrent browser contexts OOM on standard server | Global semaphore limiting concurrent Playwright instances to max 3 |
| `schema_drift` alert noise across 16 platforms | Non-drift failures (bot block, 503, expected empty) all look the same | Typed failure taxonomy; expected-empty classification for Category D |
| Price normalization (Udemy sale prices, multi-currency) | Sale prices and multi-currency corrupt price intelligence | Capture original price; store `currency_code`; flag free products explicitly |
| Config YAML complexity | 80+ platform-slug mappings hard to maintain manually | Default platforms at config root; `platform_slug: "all"` sentinel |

---

## Platform Classification Summary

| Platform | Public Marketplace | Rendering | Bot Protection | Rank Signal | Auth Required |
|----------|-------------------|-----------|----------------|-------------|---------------|
| Eduzz | Verify first | SSR likely | Low | Positional | No |
| JVZoo | Yes | SSR | Incapsula | EPC (float) | No |
| Udemy | Yes | React SPA | Cloudflare Enterprise | Enrollment count | No (API path) |
| Product Hunt | Yes (daily reset) | SSR + React | Low | Daily upvotes | OAuth (API) |
| AppSumo | Yes | SSR | Moderate (rate limiting) | Positional | No |
| Gumroad | Yes (discover) | React SPA | Low | Pageviews / position | No |
| Kajabi | No | N/A | N/A | N/A | N/A |
| Teachable | No | N/A | N/A | N/A | N/A |
| Skool | Gated (limited preview) | SSR (preview only) | Low | Member count | No (preview only) |
| Stan Store | No | N/A | N/A | N/A | N/A |
| Monetizze | Verify first | SSR likely | Low | Positional | No |
| PerfectPay | Verify first | SSR likely | Low | Positional | No |
| Braip | Verify first | SSR likely | Low | Positional | No |

**Category D (no marketplace — defer or alternative strategy):** Kajabi, Teachable, Stan Store, and likely Skool.

**Effective buildable scanners in v2.0:** 9 confirmed (Eduzz, JVZoo, Udemy, Product Hunt, AppSumo, Gumroad, Monetizze, PerfectPay, Braip) — pending pre-build URL verification for the 4 Brazilian platforms.

---

## Sources

- v1.0 codebase direct read: `mis/scanners/clickbank.py`, `mis/scanners/hotmart.py`, `mis/scanners/kiwify.py`, `mis/scanner.py` — HIGH confidence for integration patterns and existing contracts
- Kajabi, Teachable, Skool, Stan Store marketplace status: HIGH confidence these are closed platforms — core business model is SaaS/community tooling, not open marketplace
- Udemy undocumented API path (`/api-2.0/courses/`): MEDIUM confidence — endpoint format from training data (August 2025); must verify before implementation
- JVZoo Incapsula protection: MEDIUM confidence — based on known Imperva deployment patterns for high-scraping-incentive affiliate marketplaces
- Product Hunt GraphQL API (`api.producthunt.com/v2/api/graphql`): MEDIUM confidence on current availability and OAuth requirements
- Gumroad Discover page CSR rendering: MEDIUM confidence — based on Gumroad's React architecture; verify with manual inspection before building
- AppSumo rate limiting behavior: MEDIUM confidence — based on known patterns for deal aggregation sites with high scraping incentive
- Cloudflare Enterprise on Udemy: HIGH confidence — widely documented across community reports

---

*Confidence note: Web search and Bash were unavailable during this research session. All platform-specific details (exact URLs, current bot protection tier, API endpoint availability) must be manually verified before implementation begins. The classification table above should be treated as a starting hypothesis requiring pre-build validation, not ground truth.*
