# Domain Pitfalls — Market Intelligence System (Web Scraping)

**Domain:** Market intelligence, competitive analysis, web scraping of infoproduct platforms
**Researched:** 2026-03-14
**Confidence:** MEDIUM (training data + domain expertise; web search unavailable in this session)

---

## Critical Pitfalls

Mistakes that cause rewrites, legal exposure, or total project failure.

---

### Pitfall 1: Assuming Platform HTML Structure Is Stable

**What goes wrong:** Hotmart, Kiwify, Eduzz, ClickBank, and JVZoo change their frontend markup frequently — sometimes weekly. CSS selectors and XPaths used to extract product data (titles, prices, affiliate rankings) break silently. The scraper keeps "working" but returns empty or garbage data. You only discover this when the dashboard shows stale data from 3 weeks ago.

**Why it happens:** Developers write scrapers against a snapshot of the HTML at build time and don't build detection for structural drift. There are no official APIs to fall back on, so every HTML change is a breaking change.

**Consequences:** Silent data corruption. Rankings show phantom products. Dossiers are generated from stale data. The entire intelligence value proposition collapses without the user noticing.

**Prevention:**
- Never rely on a single selector. Use multiple fallback selectors per data field (`h1 > span`, `[data-product-title]`, `meta[property="og:title"]`) with priority ordering.
- Add a schema integrity check after every scrape: if extracted fields hit > 30% null rate, trigger an alert and halt the run — do not persist bad data.
- Build a `scraper_health_monitor` module that runs a lightweight canary scrape on 3 known products after every deploy and compares field counts against baseline.
- Version-pin scraper configs (`hotmart_selectors_v3.yaml`) so rollback is possible when a platform updates.

**Warning signs:**
- Scraped product list length drops > 20% vs prior run
- Key fields (price, title, sales_rank) returning None at elevated rates
- Identical timestamps across many products (cached/stale response being parsed repeatedly)

**Phase:** Address in Phase 1 (Scanner de Produtos Campeões) before any dependent modules are built.

---

### Pitfall 2: Getting IP-Banned and Losing All Data Access

**What goes wrong:** Aggressive scraping cadence (no delays, no rotation, same User-Agent) triggers Cloudflare, Akamai, or platform-native bot detection. The scraper gets the IP permanently blocked. If you're running from a home IP or a single VPS, the entire system goes dark.

**Why it happens:** Developers focus on getting data fast and assume they can add throttling later. "Later" arrives as a ban email from the platform or a 403 wall.

**Consequences:** Complete data loss from that platform. Recovery requires proxy rotation infrastructure that wasn't budgeted. Hotmart in particular aggressively blocks scrapers — it has Cloudflare Enterprise on most endpoints.

**Prevention:**
- From day one, implement a `RateLimitedSession` wrapper with per-domain configurable delays (minimum 3–8 seconds between requests to same domain, with jitter).
- Rotate User-Agent strings from a pool of realistic browser fingerprints (not just UA strings — include `Accept-Language`, `Accept-Encoding`, `Sec-Fetch-*` headers that match real browsers).
- Use residential proxy rotation for platforms with known aggressive detection (Hotmart, ClickBank). Datacenter proxies are detected trivially by these platforms.
- Implement exponential backoff on 429 and 503 responses. Never retry immediately.
- For Cloudflare-protected sites, use Playwright/Puppeteer with stealth mode (`playwright-stealth` or `undetected-chromedriver`) rather than raw HTTP requests.
- Store cookies per session and reuse them across requests within a session.

**Warning signs:**
- HTTP 403 responses increasing
- Cloudflare challenge pages being returned (HTML contains `cf-browser-verification` or `Checking your browser`)
- Response time drops to < 50ms (CDN edge returning cached block, not real content)

**Phase:** Address in Phase 1 before any production scraping begins. This is infrastructure, not a feature.

---

### Pitfall 3: Violating Terms of Service in Ways That Create Legal Exposure

**What goes wrong:** Scraping product pricing data, affiliate commissions, or private marketplace rankings from platforms that explicitly prohibit it in their ToS. More critically: scraping user reviews that contain PII, or scraping competitor ad spend data from Meta Ad Library in ways that violate Meta's ToS.

**Why it happens:** Developers assume "public page = legal to scrape." Courts and platforms disagree on where this line is.

**Consequences:** DMCA notices, account termination (losing any legitimate platform accounts), or in extreme cases cease-and-desist from platforms. In Brazil, LGPD creates additional liability if any user-identifiable data (review author names, email fragments) is stored.

**Prevention:**
- Define explicitly what is in-scope for collection: product metadata (title, price, category, public rating aggregate) = OK. User review content with identifiable author names = strip or anonymize before storage. Personal data of buyers = never collected (already in project Out of Scope).
- Review each target platform's `robots.txt` and respect `Disallow` directives for non-public paths.
- Store a legal review checklist per platform in the repo (`docs/legal/platform_review.md`). Mark confidence level per platform.
- Never store scraped data beyond what's needed for the current analysis window (rolling 90-day retention max).

**Warning signs:**
- Scraping paths that require login (authenticated marketplace dashboards) — these have stronger ToS protections.
- Extracting data from pages with explicit copyright notices on rankings (ClickBank's "Top Products" may be classified as proprietary rankings, not public data).

**Phase:** Legal review must happen in Phase 0 (pre-build). Do not start scraping until per-platform risk matrix is documented.

---

### Pitfall 4: Building Hourly Pipelines Without Idempotency

**What goes wrong:** The hourly Radar de Dores pipeline runs, fails midway (API timeout, bad proxy), and on the next run re-processes everything from scratch, creating duplicate entries in the database. Or worse: it fails silently and cron keeps retrying, creating 6 copies of the same Google Trends snapshot with the same timestamp.

**Why it happens:** Pipelines are built quickly without thinking about failure modes. "Happy path only" architectures work in demos.

**Consequences:** Database bloat, corrupted trend analysis (duplicates inflate term frequency counts), alerts firing on data that was already processed, and AI analysis generating dossiers from stale/duplicate inputs.

**Prevention:**
- Every pipeline run must be idempotent: identify each run by `(source, timestamp_bucket, query)` as a composite key. If a record with that key already exists, skip — do not re-insert.
- Use a `pipeline_runs` table or file-based checkpoint store. Mark runs as `STARTED`, `PARTIAL`, `COMPLETED`, `FAILED`. On restart, resume from last checkpoint.
- Implement a "deduplication window" in the analysis layer: when aggregating trends, deduplicate by (source, content_hash, hour_bucket) before counting.
- For Google Trends specifically: the API returns relative values (0-100 index), not absolute counts. Running hourly and naively averaging will produce wrong trend curves if any run fails. Store raw snapshots with exact timestamps; compute trends during the analysis phase, not during collection.

**Warning signs:**
- Row counts in trend tables growing faster than expected
- Duplicate timestamps in the `runs` log
- Dashboard showing sudden spikes in term frequency that correlate with pipeline restarts

**Phase:** Address in Phase 3 (Radar de Dores). This is the highest-frequency pipeline and the most likely to have reliability issues.

---

### Pitfall 5: Treating Google Trends Data as Absolute Search Volume

**What goes wrong:** Google Trends returns a relative index (0–100), not absolute search counts. Comparing two different queries run at different times produces meaningless results. Many projects build "trending topics" dashboards on top of this without understanding the data semantics, leading to completely wrong conclusions.

**Why it happens:** The Trends API is easy to use but its output semantics are non-obvious. The index is relative to the peak in the time window, not across windows.

**Consequences:** "Trending" reports show topics as hot that are actually flat, or vice versa. The intelligence output misleads the user into modeling products for non-existent demand.

**Prevention:**
- Always include at least one "anchor" comparison term per query batch — a stable evergreen term in the niche (e.g., "curso online") so relative values can be normalized across runs.
- Document the data semantics in the dashboard UI: display "relative interest score" not "search volume."
- Use the `pytrends` library (Python); be aware it uses Google's unofficial API and breaks periodically. Build a fallback that detects `429 Too Many Requests` from Google and backs off for 60+ minutes.
- Store raw response payloads alongside processed values so analysis can be re-run if semantics interpretation changes.

**Warning signs:**
- Values oscillating between 0 and 100 on consecutive hourly runs for the same query (this indicates the anchor term is too volatile)
- All terms returning 100 (means Google is normalizing to a single peak — batch the queries differently)

**Phase:** Address in Phase 3 design before implementation. The data model decision (how to store and compare) must be made before the first line of pipeline code.

---

### Pitfall 6: JavaScript-Heavy Sites Breaking HTTP-Only Scrapers

**What goes wrong:** Hotmart's marketplace, Kiwify's product pages, and Udemy's course listings all render critical data (prices, sales ranks, enrollment counts) via React/Vue client-side rendering. A simple `requests` + `BeautifulSoup` scraper will fetch the HTML shell with empty `<div id="app"></div>` and extract nothing.

**Why it happens:** Developers test scrapers on simple static pages first, then assume the same approach scales to all targets.

**Consequences:** All scrapers return empty datasets for the most important platforms. Discovery is often delayed because the scraper "runs successfully" — it just collects no data.

**Prevention:**
- Audit every target platform before writing any scraper code. Use browser DevTools → Network tab to determine if content is SSR or CSR. Check if a `View Page Source` (not Inspect) shows the product data.
- For CSR platforms, use Playwright (async) with browser contexts. Playwright is preferred over Selenium for this project because: async-native (better for pipeline integration), better Python support, actively maintained.
- Consider a hybrid approach: use raw HTTP for platforms that SSR their data (cheaper, faster, less detectable), use Playwright only where JS rendering is required.
- Be aware that Playwright instances are memory-hungry. Running 8 concurrent Playwright browsers will consume 2–4 GB RAM. Budget accordingly.

**Warning signs:**
- Scraped page HTML contains only `<div id="root">` or `<div id="app">` with no nested content
- Product field extraction returns 100% None/null
- Response time is < 100ms (getting edge-cached shell page, not rendered content)

**Phase:** Address in Phase 1 discovery/planning before any scraper implementation.

---

## Moderate Pitfalls

---

### Pitfall 7: Reddit and Quora API Deprecations and Paywalls

**What goes wrong:** Reddit's official API became heavily restricted in 2023 (rate limits, paid tiers). Quora has no public API. Projects that planned to use free API access for volume data scraping get cut off.

**Prevention:**
- For Reddit: use the official API with OAuth for moderate volume (up to 100 requests/minute on free tier). Do NOT use PRAW without respecting its built-in rate limiting. For higher volume, budget for the official paid API or use Pushshift archives where data freshness allows.
- For Quora: scraping the public search results page is the only non-API option. Use Playwright, scrape slowly (1 request per 10–15 seconds), and accept that Quora coverage will be lower quality than Reddit.
- Build the system so that if a source becomes unavailable, the rest of the pipeline degrades gracefully rather than failing completely.

**Phase:** Phase 3. Design source adapters with pluggable interface so sources can be disabled without cascading failures.

---

### Pitfall 8: YouTube Data API v3 Quota Exhaustion

**What goes wrong:** YouTube Data API v3 has a default quota of 10,000 units/day. A single search request costs 100 units. Running 10 niche queries per hour = 2,400 units/hour = quota exhausted in 4 hours.

**Prevention:**
- Request a quota increase from Google Cloud Console before building the YouTube module. Budget for this taking 1–2 weeks for approval.
- Cache search results aggressively. A query for "curso de tráfego pago" run at 10:00 AM does not need to be re-run at 11:00 AM — results change slowly. Cache for 6–12 hours.
- Only fetch video IDs from search, then batch-fetch statistics using `videos.list` (1 unit per batch of up to 50 videos) rather than `search.list` repeatedly.
- Use the `commentThreads.list` endpoint only for videos with high engagement relevance (views > threshold).

**Phase:** Phase 3. Quota architecture must be designed before YouTube integration is coded.

---

### Pitfall 9: Building the Dashboard Before the Data Pipeline Is Reliable

**What goes wrong:** Developer builds a beautiful React/Next.js dashboard in Phase 1. Then spends the rest of the project fighting to make the data pipeline actually produce clean, reliable data. The dashboard becomes a liability — every schema change requires frontend updates, and the frontend creates artificial pressure to "not break the API."

**Prevention:**
- Build and validate the data pipeline end-to-end first. Only start dashboard development when at least 2 data sources are producing reliable, consistent data for 48+ hours.
- Design the database schema for the pipeline's needs, not the dashboard's display needs. The dashboard adapts to the schema, not the reverse.
- Use a simple admin view (FastAPI auto-docs, or a Streamlit prototype) during pipeline development to inspect data without building production UI.

**Phase:** Dashboard is Phase N (final). Pipeline is Phase 1–3.

---

### Pitfall 10: Storing Raw Scraped Data Without a Retention and Cleanup Strategy

**What goes wrong:** The system scrapes hourly for 90 days. Without cleanup, the raw data store grows to tens of gigabytes. Queries slow down. The server runs out of disk. The developer discovers this at 2 AM when the pipeline crashes.

**Prevention:**
- Define retention tiers at design time: raw scraped pages (keep 7 days), extracted structured data (keep 90 days), aggregated trend reports (keep 1 year), generated dossiers (keep indefinitely).
- Implement automated cleanup jobs from day one. Do not "add it later."
- Use SQLite for development, but plan for PostgreSQL in production if data volume projections exceed 10 GB/year.

**Phase:** Phase 1 (data model design). Retention policy must be in the schema design, not added as an afterthought.

---

### Pitfall 11: AI Analysis Pipelines Generating Hallucinated Competitive Insights

**What goes wrong:** The AI dossier generation step receives incomplete or partially-null scraped data (because a scraper failed). The LLM fills in the gaps with plausible-sounding but fabricated competitive intelligence. The user acts on hallucinated data, launches a product based on non-existent demand signals, and loses money.

**Prevention:**
- Implement a data completeness gate before any AI analysis: if the input data for a dossier is missing more than N% of required fields, do not generate the dossier. Queue for retry when complete data is available.
- Add a `data_confidence_score` to every dossier output (0–1 scale based on field completeness and source freshness).
- Instruct the LLM explicitly via system prompt to flag when it's reasoning from incomplete data: "If a field is missing, say 'data unavailable' — do not infer or extrapolate."
- Store the exact source data used to generate each dossier alongside the dossier itself so the user can audit.

**Phase:** Phase 2 (Espionagem de Produto / dossier generation) and Phase 3 (trend analysis).

---

## Minor Pitfalls

---

### Pitfall 12: Not Handling Platform-Specific Currency and Locale Formatting

**What goes wrong:** Hotmart prices in BRL use `R$ 197,00` (comma as decimal separator). ClickBank prices are USD with `.` decimals. A naive price parser produces nonsense numbers when comparing across platforms.

**Prevention:** Build a currency normalizer that handles locale-specific formatting (Brazil uses `.` for thousands and `,` for decimals). Always store prices in a standardized format (e.g., cents as integer, plus explicit `currency_code` field). Never store prices as raw text strings.

**Phase:** Phase 1.

---

### Pitfall 13: Cron-Based Scheduling Instead of Queue-Based Pipeline Orchestration

**What goes wrong:** The hourly pipeline is triggered by cron. If the previous run is still executing when the next one fires, you get concurrent runs corrupting shared state, duplicating writes, or causing database locks.

**Prevention:** Use a task queue (Celery + Redis, or APScheduler with a singleton lock) to ensure only one pipeline run executes per source at a time. If a run is still active when the next is scheduled, skip the new trigger and log it.

**Phase:** Phase 3 (hourly Radar pipeline). Address in architecture design before implementation.

---

### Pitfall 14: Ignoring Seasonal and Time-Zone Effects in Trend Data

**What goes wrong:** Google Trends data is returned in the timezone of the account or the default (US Eastern). Brazilian market queries return data offset from the actual Brazilian behavior pattern. "Peak interest at 9 AM" in the Trends data might actually be 9 AM EST = 11 AM BRT, creating analysis errors.

**Prevention:** Always specify `geo='BR'` for Brazilian market queries in pytrends. Store all timestamps in UTC internally and convert to BRT (UTC-3) for display. Document timezone handling in the data model.

**Phase:** Phase 3.

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Platform scanners (Hotmart, Kiwify, ClickBank) | HTML structure instability + JS-rendered content | Playwright for CSR sites; schema drift alerts; fallback selectors |
| Espionagem de Produto (copy extraction) | Cloudflare/anti-bot blocking on landing pages | Residential proxy rotation; Playwright stealth mode; session cookie reuse |
| Google Trends radar (hourly) | Incorrect relative-vs-absolute data semantics; quota exhaustion | Anchor terms; normalized storage; pytrends rate limiting |
| Reddit/Quora scraping | API restrictions, Quora has no API | Rate-limited OAuth for Reddit; Playwright for Quora; graceful degradation |
| YouTube comments | Quota exhaustion (10K units/day default) | Request quota increase early; cache aggressively; batch API calls |
| AI dossier generation | Hallucinations from incomplete data | Data completeness gate; confidence scores; explicit LLM instructions |
| Dashboard development | Schema churn if built before pipeline stabilizes | Build pipeline first; use admin/debug view during development |
| Pipeline orchestration | Concurrent cron runs corrupting state | Queue-based orchestration with singleton locks from day one |

---

## Sources

- Domain knowledge: web scraping patterns for infoproduct platforms (training data, HIGH confidence for platform behavior patterns)
- Google Trends API semantics: pytrends documentation and known limitations (MEDIUM confidence — verify current quota limits)
- YouTube Data API v3 quota units: Google official documentation (MEDIUM confidence — quota policies change; verify at https://developers.google.com/youtube/v3/getting-started#quota)
- Reddit API restrictions: widely documented post-2023 API changes (HIGH confidence)
- Cloudflare detection evasion: established community knowledge (MEDIUM confidence — Cloudflare actively evolves detection)
- LGPD compliance for scraped data: Brazilian General Data Protection Law (HIGH confidence for general principles)

---

*Confidence note: Web search was unavailable during this research session. Findings are based on training data (cutoff August 2025). Platform-specific details (Hotmart/Kiwify anti-bot measures, current API quotas) should be re-verified before implementation.*
