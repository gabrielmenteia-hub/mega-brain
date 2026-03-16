# Feature Landscape

**Domain:** Market Intelligence System v2.0 — Platform Expansion (13 new platform scanners + cross-platform unified ranking)
**Researched:** 2026-03-16
**Supersedes:** Prior v1.0 FEATURES.md (dated 2026-03-14)
**Overall confidence:** MEDIUM — platform access method analysis based on training knowledge (cutoff Aug 2025) and codebase pattern analysis. WebSearch was unavailable. All access method claims must be verified against live platforms before writing scanner code.

---

## What Already Exists (v1.0 Baseline — Do Not Rebuild)

The `Product` dataclass in `mis/scanner.py` is the universal data contract across all platforms:

```
Mandatory: external_id, title, url, platform_id, niche_id, rank
Optional:  price, commission_pct, rating, thumbnail_url
```

`PlatformScanner` ABC: `scan_niche(niche_slug, platform_slug) -> list[Product]`
`BaseScraper`: `fetch()` (httpx, SSR/JSON), `fetch_spa()` (Playwright stealth)
`run_all_scanners()`: dispatches via `SCANNER_MAP` dict — new platforms register here
`save_batch_with_alerts()`: upserts products + triggers top-20 entry alerts
Dashboard `/ranking` route: already supports `?platform=` and `?niche=` filter params

Three established access patterns to follow as templates:

- **Pattern A: SSR HTML + BeautifulSoup** — Hotmart, Kiwify (positional rank)
- **Pattern B: Public JSON/GraphQL API without auth** — ClickBank (gravity score)
- **Pattern C: Public API with auth key** — not yet used; needed for Udemy and Product Hunt
- **Pattern D: Playwright SPA** — `fetch_spa()` is ready but no production scanner uses it yet

Every new scanner that registers in `SCANNER_MAP` automatically inherits for free:
top-20 entry alerts via `save_batch_with_alerts()`, schema drift detection + structlog
`alert='schema_drift'` pattern, rate limiting and proxy rotation via `BaseScraper`,
and health monitor canary checks (one new canary URL per scanner required).

---

## Table Stakes

Features that must ship in v2.0. Missing any = milestone goal unmet.

### New Platform Scanners

| Platform | Category | Access Method | Ranking Metric | Price Available? | Auth Required? | Complexity |
|----------|----------|---------------|----------------|-----------------|----------------|------------|
| Eduzz | BR infoproduct | Pattern A — SSR HTML | Positional (page order) | BRL — likely in HTML | No | Medium |
| Monetizze | BR infoproduct | Pattern A — SSR HTML | Positional | BRL + commission pct | No | Medium |
| JVZoo | EN affiliate marketplace | Pattern B — inspect network for JSON; fallback SSR | EPC or bestseller position | USD + commission pct | No (likely) | Medium |
| Product Hunt | EN tech/SaaS launches | Pattern C — official GraphQL API | `votesCount` (daily upvotes) | Not available | Yes: OAuth Bearer token | Low-Medium |
| Udemy | EN online courses | Pattern C — official affiliate REST API | `num_subscribers` (enrollment count) | USD | Yes: client_id + client_secret | Medium |
| Gumroad | EN creator economy | Pattern A — SSR HTML (`/discover?sort=popular`) | Positional under "popular" sort | USD (min price for PWYW) | No | Medium |
| AppSumo | EN software deals | Pattern A or D — try SSR first, fall back to Playwright | Positional / featured order | USD | No | Medium-High |
| Braip | BR infoproduct + physical | Pattern A — SSR HTML (if marketplace confirmed) | Positional | BRL | No | Medium-High |
| PerfectPay | BR infoproduct | Pattern A — SSR HTML (if marketplace confirmed) | Positional | BRL | No | Medium-High |
| Skool | EN community platform | Pattern D — Playwright SPA | Member count (weak proxy) | USD | No | High |

### Cross-Platform Unified Ranking View

| Feature | Why Needed | Complexity |
|---------|------------|------------|
| `/ranking/unified` dashboard route | Core v2.0 value: "what's winning in [niche] across all platforms" | Medium |
| Niche-first grouping (platform as badge/tag) | User mental model is niche-first; platform is secondary context | Medium |
| Normalized cross-platform rank score | `rank/total` within each platform; enables fair comparison across heterogeneous metrics | High |
| Platform coverage indicator per niche | "This niche: 7/10 platforms have data" — user knows completeness | Low |
| Multi-platform presence count per product | Products on 3+ platforms = strongest buy signal | Low |
| Sort axes: unified score, niche, price, platform count | Multiple use cases; unified score is the default | Low |

---

## Platform-by-Platform Access Analysis

### Tier 1: Official APIs (Cleanest, Most Stable)

**Product Hunt** — MEDIUM-HIGH confidence
- GraphQL API: `https://api.producthunt.com/v2/api/graphql`
- Free developer registration at `producthunt.com/v2/oauth/applications`
- Auth: Bearer token, stored as `PH_ACCESS_TOKEN` in `.env`
- Key fields: `name`, `tagline`, `url`, `votesCount`, `topics { name }`, thumbnail URL
- Ranking metric: `votesCount` — daily upvotes, natural popularity signal
- Price: NOT available (Product Hunt lists free and paid products together)
- Rate limit: documented, well-behaved
- Risk: Bearer token may expire; add graceful degradation on 401

**Udemy** — MEDIUM confidence
- REST API: `https://www.udemy.com/api-2.0/courses/`
- Free registration: `udemy.com/developers/affiliate/`
- Auth: `Authorization: Basic {base64(client_id:client_secret)}`
- Useful query params: `?ordering=enrollment&page_size=50&fields[course]=title,url,price,rating,num_subscribers,primary_category,image_480x270`
- Ranking metric: `num_subscribers` (enrollment count = best available public proxy for bestseller rank)
- Key fields: title, url, price (USD), rating, num_subscribers, primary_category, image_480x270
- Rate limit: 1000 requests/day free tier — sufficient for daily scan cycle
- Env vars needed: `UDEMY_CLIENT_ID`, `UDEMY_CLIENT_SECRET`
- Risk: Udemy TOS may restrict commercial use of affiliate API — verify before implementing
- Note: `num_subscribers` includes free promotional enrollments; label as "enrolled" not "sold" in dashboard

### Tier 2: SSR HTML Scraping (Same Pattern as Hotmart/Kiwify)

**Eduzz** — MEDIUM confidence
- Marketplace URL: `https://eduzz.com/marketplace` (or `/afiliados/marketplace` — verify live)
- Expected SSR rendering consistent with other BR infoproduct platforms
- Category filter: URL query param (verify exact param name with live inspection)
- Key fields: title, url, price (BRL), commission_pct (affiliate pages show this)
- Ranking metric: positional page order under default "bestseller" or "popular" sort
- commission_pct: high value field — Eduzz affiliate pages typically expose commission rate
- Selector strategy: follow Hotmart pattern (ordered selector list + schema_drift alert)

**Monetizze** — MEDIUM confidence
- Marketplace URL: `https://marketplace.monetizze.com.br/`
- SSR expected; category filter via URL param
- Key fields: title, url, price (BRL), commission_pct (usually visible on affiliate pages)
- Ranking metric: positional
- Same implementation pattern and risk profile as Eduzz

**Gumroad** — MEDIUM confidence
- Discover page: `https://gumroad.com/discover`
- Filter params: `?tags={tag}&sort=popular` or `?sort=best_sellers`
- SSR-rendered product cards (Gumroad is known for SSR, not SPA)
- Key fields: title, url, price (USD; handle "pay what you want" — store minimum price or 0.0), creator name, thumbnail
- Ranking metric: positional under "popular" sort
- commission_pct: NOT available at marketplace level (Gumroad affiliates are per-product, not discoverable here)

**AppSumo** — MEDIUM confidence
- URL: `https://appsumo.com/products/` with `?categories={slug}` filter
- Try `fetch()` first; if product cards absent from response, fall back to `fetch_spa()`
- Key fields: title, url, price (often lifetime deal one-time price), rating, review count
- Ranking metric: positional under "featured" or "popular" sort
- commission_pct: NOT applicable (AppSumo sells directly, not an affiliate marketplace)
- Risk: strong anti-bot measures common for deal/coupon sites; use maximum delay and proxy rotation

**JVZoo** — LOW confidence
- No documented public API found in training knowledge
- Marketplace: `https://www.jvzoo.com/marketplace`
- Likely approach: inspect network traffic for undocumented JSON endpoints (follow ClickBank pattern)
- Fallback: SSR HTML scraping of marketplace listing
- Key fields if found: title, url, EPC (earnings per click), commission_pct, conversion rate
- Ranking metric: EPC or "Top 10 Today" position
- Risk: site structure unknown without live inspection; plan for schema drift from day one

**PerfectPay** — LOW confidence
- Domain: `perfectpay.com.br`
- Marketplace existence: UNCONFIRMED — requires live URL check before implementation
- Check `https://perfectpay.com.br/marketplace` and `https://perfectpay.com.br/afiliados` live
- If marketplace found: SSR HTML, same BR pattern as Eduzz/Monetizze
- Decision gate: verify marketplace URL exists before allocating implementation time

**Braip** — LOW confidence
- Domain: `braip.com`
- Newer platform (circa 2022); marketplace discoverability uncertain
- Hybrid platform (digital + physical products); if product_type is detectable in HTML, surface it
- Decision gate: same as PerfectPay — verify live URL before planning implementation

### Tier 3: Blocked — No Public Marketplace

**Kajabi** — HIGH confidence (skip)
- White-label SaaS: each creator operates on their own `{name}.kajabi.com` subdomain
- No `kajabi.com/marketplace` or centralized product discovery page exists
- Implementing a scanner would require crawling thousands of creator subdomains — fragile and out of scope
- Decision: SKIP v2.0; mark as "no public marketplace" in platform registry

**Teachable** — HIGH confidence (skip)
- Same architecture as Kajabi: individual school URLs (`{school}.teachable.com`)
- No centralized discovery or ranking page
- Decision: SKIP v2.0

**Stan Store** — HIGH confidence (skip)
- Link-in-bio creator store tool (Linktree + Gumroad hybrid)
- No central marketplace, no product ranking page
- Decision: SKIP v2.0

**Skool** — MEDIUM confidence (deprioritize)
- `skool.com/communities` shows public communities with member counts and price
- SPA-rendered — requires `fetch_spa()` (Playwright, slow, higher resource cost)
- Data quality is lower signal: community member count is a weak proxy for product sales rank
- If included: community name, url, member count, price only — no deep scraping
- Decision: deprioritize; include only if timeline and Playwright cost allow after higher-priority scanners are done

---

## Differentiators

Features that make v2.0 meaningfully better than just "v1.0 with more rows in platforms table."

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Normalized cross-platform rank score | `percentile_rank = rank / total` enables "top product in [niche] regardless of platform" — the headline v2.0 value claim | High | Computed at query time in unified view; no schema change required |
| Multi-platform presence count per product | "This product appears in top-10 on 4 platforms" — strongest signal available in the system | Low | `COUNT(DISTINCT platform_id) WHERE rank <= 10` for a given product across platforms |
| Platform health badges in unified view | "Eduzz: last scanned 2h ago — OK | PerfectPay: schema drift" — user knows data freshness without leaving the page | Low | Surface existing `health_monitor` canary data in new template context |
| Per-platform canary checks for all new scanners | Broken scanners detected automatically, consistent with FOUND-04 pattern | Low | One canary URL per new scanner added to health_monitor |
| "New to top-20" alerts across all new platforms | `save_batch_with_alerts()` already handles this — new scanners inherit it for free | None (free) | Zero additional work; auto-inherited by registering in SCANNER_MAP |

---

## Anti-Features

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| KajabiScanner | No public marketplace; crawling thousands of creator subdomains is fragile and out of scope | Mark "no public marketplace" in platform registry comments |
| TeachableScanner | Same as Kajabi — no centralized discovery page | Skip entirely |
| Stan StoreScanner | No product ranking page or marketplace | Skip entirely |
| Currency normalization (BRL/USD to common unit) | Exchange rates are a moving target; adds maintenance debt and misleads when rates shift | Show prices with currency tag (BRL/USD); no conversion at any layer |
| Real-time scan trigger from dashboard UI | Bypasses APScheduler rate discipline; could trigger platform bans | Manual force-scan via CLI only (`python -m mis scan`); no dashboard button |
| Cross-platform product deduplication/merging | A product appearing on Hotmart AND ClickBank is STRONGER SIGNAL — merging would destroy this insight | Let products coexist with different `platform_id`; surface multi-platform count as a feature |
| Skool deep scraping (member lists, community content) | SPA + rate limits + ToS risk + low ROI vs complexity | If included: community name, url, member count, price only |
| Presenting Udemy `num_subscribers` as "sales" | Includes free promotional enrollments — not equivalent to paid sales; misleading | Label column "Enrolled" not "Sales" in dashboard; add tooltip explaining the metric |

---

## Feature Dependencies

```
All new scanners
  → Register class in SCANNER_MAP (mis/scanner.py)
  → Add platform row to DB platforms table (migration or seed script)
  → Add domain entry to DOMAIN_DELAYS in mis/base_scraper.py
  → Add canary check URL in health_monitor.py

Product Hunt scanner
  → PH_ACCESS_TOKEN in .env

Udemy scanner
  → UDEMY_CLIENT_ID + UDEMY_CLIENT_SECRET in .env

/ranking/unified dashboard route
  → New or extended query in dossier_repository.py for cross-platform view
  → Normalized rank computation (percentile: rank / COUNT per platform per niche)
  → New Jinja2 template: mis/web/templates/unified_ranking.html
  → New route file: mis/web/routes/unified_ranking.py, registered in web/app.py

Normalized score (unified view)
  → All scanners for target niche must have run at least once (cold start gap acceptable)
  → Graceful handling: platforms with 0 products for a niche simply don't appear (no error)

Platform health badges in unified view
  → health_monitor.py already returns status per platform
  → Pass health dict via route context into unified_ranking.html template
```

---

## MVP Recommendation for v2.0

**Phase order: low-friction BR platforms first → well-documented APIs → SPA platforms last → unified view as capstone.**

BR platforms share the exact SSR + BeautifulSoup pattern as Hotmart/Kiwify — fastest to implement,
highest market relevance for the target user. JVZoo follows ClickBank's network-inspection pattern.
Product Hunt and Udemy have clean APIs. AppSumo/Skool are higher-friction SPA targets. The unified
ranking view is the dashboard capstone and requires scanners to be operational first.

**Build in v2.0 (recommended order):**

1. EduzzScanner — SSR BR, lowest friction, high market relevance
2. MonetizzeScanner — SSR BR, same pattern
3. JVZooScanner — inspect network for JSON API first; fallback SSR HTML
4. Product Hunt Scanner — clean public GraphQL API, free OAuth token, tech/SaaS signal
5. UdemyScanner — official affiliate REST API, highest data quality for course niche
6. GumroadScanner — SSR, creator economy signal, price data available
7. AppSumoScanner — SSR or Playwright; software deals niche
8. BraipScanner — SSR BR; implement ONLY after live marketplace URL confirmed
9. PerfectPayScanner — SSR BR; implement ONLY after live marketplace URL confirmed
10. /ranking/unified — dashboard capstone; implement after at least 5 scanners are working

**Deprioritize or drop:**
- SkoolScanner — Playwright SPA, lower data quality, lower ROI vs complexity
- KajabiScanner — no public marketplace (hard skip)
- TeachableScanner — no public marketplace (hard skip)
- Stan StoreScanner — no public marketplace (hard skip)

---

## Cross-Platform Unified Ranking: Full Specification

The `/ranking/unified` view answers: "What products are winning in [niche] right now,
regardless of which platform they are on?"

### Columns to Expose

| Column | Source | Notes |
|--------|--------|-------|
| Unified rank | Computed: AVG(percentile_rank across all platforms where product appears) | Lower = better; sort ascending |
| Product title | `products.title` | Linked to `/dossier/{id}` if dossier exists |
| Platform(s) | `products.platform_id` → `platforms.name` | Color-coded badges |
| Platform count | COUNT(DISTINCT platform_id) for this product | "Appears on N platforms" — key signal |
| Niche | `products.niche_id` → `niches.name` | Primary filter axis |
| Price | `products.price` + currency tag | "R$ 197" or "USD 47" — no conversion |
| Rating | `products.rating` | NULL shown as "—" |
| Raw rank | `products.rank` per platform | Context: "ClickBank #3, Hotmart #7" |
| Dossier status | `dossiers.status` | "complete" / "pending" / "none" |
| Last scanned | `products.updated_at` | Flag stale > 25h |

### Normalization Formula

```
percentile_rank(product, platform, niche) =
    product.rank / COUNT(products WHERE platform_id = platform.id AND niche_id = niche.id)

unified_score(product) =
    AVG(percentile_rank) across all platforms where this product appears in that niche
```

- Lower score = better rank (0.0 = #1 of 1 product; 1.0 = last place)
- Single-platform products: `unified_score = percentile_rank` (no penalty for single-platform presence)
- Multi-platform products: average of their percentile ranks; multi-platform count shown separately

### UX Filters

- **Required filter: niche** — unified view without niche = noise across all niches; enforce in route
- **Optional filter: platform** — drill into single platform from unified view
- **Toggle: "Multi-platform only"** — show only products present on 2+ platforms (strongest signals)
- **Sort options:** unified_score (default), price, rating, last_scanned, platform_count

### New Files Required

```
mis/web/routes/unified_ranking.py      — new route file
mis/web/templates/unified_ranking.html — new Jinja2 template
mis/dossier_repository.py              — new function: list_unified_ranking()
mis/web/app.py                         — register unified_ranking router
```

---

## Sources

- Direct codebase analysis: `mis/scanner.py`, `mis/base_scraper.py`, `mis/scanners/hotmart.py`,
  `mis/scanners/clickbank.py`, `mis/scanners/kiwify.py`, `mis/web/routes/ranking.py` — HIGH confidence
- Product Hunt GraphQL API (public documentation, free developer tier) — MEDIUM-HIGH confidence
- Udemy Affiliate REST API (public documentation) — MEDIUM confidence; verify TOS before implementing
- Kajabi / Teachable / Stan Store "no public marketplace" finding — HIGH confidence (well-established
  platform architecture, stable characteristic since 2020+)
- BR platforms (Eduzz, Monetizze, PerfectPay, Braip) access patterns — MEDIUM confidence;
  live URL verification required before writing any scanner code
- JVZoo access method — LOW confidence; no public API documented; network inspection required
- AppSumo / Gumroad / Skool access patterns — MEDIUM confidence; spot-check live before implementing
- All scraping-based access method claims are subject to schema drift; design for it from day one
  using the existing schema_drift alert pattern already in place for Hotmart and Kiwify
