# Technology Stack

**Project:** Market Intelligence System (MIS) — v2.0 Platform Expansion
**Researched:** 2026-03-16
**Scope:** NEW capabilities only for 13 additional platforms. Do NOT re-research the existing v1.0 stack.
**Overall Confidence:** MEDIUM — web tools unavailable during research; findings based on training data (cutoff August 2025) cross-referenced with existing codebase patterns.

---

## Context: What Already Exists (Do Not Change)

The following is **validated and shipped in v1.0**. Do not re-evaluate:

```
httpx[http2]>=0.28.1          # SSR fetch + JSON/GraphQL APIs
playwright>=1.58.0            # SPA rendering
playwright-stealth>=2.0.2     # Anti-bot fingerprint suppression
tenacity>=9.1.4               # Retry with exponential backoff
structlog>=25.5.0             # Structured JSON logging
fake-useragent>=2.2.0         # User-Agent rotation
sqlite-utils>=3.39            # SQLite ORM-lite
apscheduler>=3.11.2           # AsyncIOScheduler for hourly jobs
PyYAML>=6.0.3                 # config.yaml parsing
python-dotenv>=1.2.1          # .env loading
beautifulsoup4>=4.12.3        # HTML parsing
lxml>=5.0.0                   # Fast HTML/XML parser (bs4 backend)
anthropic>=0.79.0             # claude-sonnet-4-6 for LLM tasks
markdownify>=0.12.0           # HTML -> Markdown for LLM consumption
```

**BaseScraper** provides: `fetch()` (httpx GET/POST), `fetch_spa()` (Playwright+stealth), rate limiting,
proxy rotation, retry. All new scanners subclass `PlatformScanner` which composes `BaseScraper`.

---

## Platform Integration Analysis: The 13 New Platforms

### Classification by Integration Method

| Platform | Region | Integration Method | Auth Required | Playwright Needed | Confidence |
|----------|--------|-------------------|---------------|-------------------|------------|
| **Eduzz** | BR | httpx SSR HTML | No | No | MEDIUM |
| **Monetizze** | BR | httpx SSR HTML | No | No | MEDIUM |
| **PerfectPay** | BR | httpx SSR HTML | No | Possibly | LOW |
| **Braip** | BR | httpx SSR HTML | No | No | LOW |
| **JVZoo** | US | httpx SSR HTML (no-auth) or REST API (affiliate key) | Optional | No | MEDIUM |
| **Udemy** | Global | Public REST API (Affiliate) | API key + ClientID | No | HIGH |
| **Product Hunt** | US | Public GraphQL API | Bearer token (free) | No | HIGH |
| **AppSumo** | US | httpx SSR or SPA | No | Possibly | MEDIUM |
| **Gumroad** | US | httpx SSR HTML (/discover) | No | No | MEDIUM |
| **Kajabi** | US | No public marketplace | — | — | MEDIUM |
| **Teachable** | US | httpx SSR HTML (if marketplace page exists) | No | No | LOW |
| **Skool** | US | Playwright (React SPA) | No | Yes | MEDIUM |
| **Stan Store** | US | Playwright (likely SPA) | No | Likely | LOW |

---

## Detailed Platform Integration Approach

### Group 1: Public REST / GraphQL APIs (Zero New Libraries)

#### Udemy Affiliate API
- **Endpoint:** `https://www.udemy.com/api-2.0/courses/` with `?ordering=highest-rated&subcategory={slug}`
- **Auth:** HTTP Basic Auth with `{ClientID}:{ClientSecret}` — requires free affiliate account signup at udemy.com/affiliate
- **Response:** JSON with `title`, `url`, `price`, `rating`, `num_reviews`, `primary_subcategory`
- **New library needed:** None — httpx Basic Auth via `httpx.BasicAuth(client_id, secret)` works natively
- **Env vars needed:** `UDEMY_CLIENT_ID`, `UDEMY_CLIENT_SECRET`
- **Rate limit:** ~500 requests/hour per token (MEDIUM confidence — verify on signup)
- **Ranking signal:** `num_reviews * rating` as proxy for bestseller rank; Udemy does not expose a
  direct "bestseller score" in the public API

#### Product Hunt API (GraphQL)
- **Endpoint:** `https://api.producthunt.com/v2/api/graphql`
- **Auth:** Bearer token — Developer Token from producthunt.com/v2/oauth/applications (free registration,
  no approval needed for read-only access)
- **New library needed:** None — same POST GraphQL pattern already used in `ClickBankScanner._post_graphql()`
- **Env vars needed:** `PRODUCT_HUNT_API_TOKEN`
- **Query pattern:** `posts(order: VOTES, after: null, first: 50)` filtered by topic
- **Rate limit:** 900 req/min (generous) — MEDIUM confidence
- **Ranking signal:** `votesCount` descending

#### JVZoo Marketplace
- **No-auth path (recommended):** `https://www.jvzoo.com/marketplace/search?q={keyword}&sort=bestsellers`
  — SSR HTML, publicly accessible, parseable with BeautifulSoup4
- **API path (optional):** `https://www.jvzoo.com/api/listproducts` — requires affiliate account and
  API key; unlocks conversion rate data
- **Recommended approach:** SSR HTML scraping — avoids mandatory account requirement. Degrade to
  positional rank if conversion rate is unavailable.
- **New library needed:** None
- **Env vars needed:** `JVZOO_API_KEY` (optional — degrade gracefully without it)

#### Gumroad Discover
- **URL:** `https://gumroad.com/discover?sort=hot&query={keyword}`
- **Rendering:** SSR HTML (Gumroad is a simpler platform; training data confirms SSR pages)
- **API note:** Gumroad OAuth API (`https://api.gumroad.com/v2/products`) only returns the
  authenticated user's own products — not useful for marketplace scanning
- **New library needed:** None
- **Ranking signal:** Positional rank on "hot" sort

---

### Group 2: SSR HTML — httpx Sufficient (No New Libraries)

#### Eduzz
- **URL:** `https://eduzz.com/marketplace?categoria={slug}`
- **Rendering:** SSR HTML — BR platforms of this generation typically use server-side rendering
- **Parser:** BeautifulSoup4 with `lxml` (already in stack)
- **New library needed:** None
- **Ranking signal:** Positional rank from listing order (Eduzz does not expose a numeric gravity score)
- **Confidence:** MEDIUM — verify by fetching and checking for JS hydration markers before building parser

#### Monetizze
- **URL:** `https://monetizze.com.br/marketplace` with category filter
- **Rendering:** SSR HTML
- **Parser:** BeautifulSoup4 with `lxml`
- **New library needed:** None
- **Ranking signal:** Positional rank

#### Braip
- **URL:** `https://braip.com/marketplace`
- **Rendering:** Assumed SSR (Braip is a smaller BR platform; unlikely to use heavy SPA stack)
- **New library needed:** None
- **Confidence:** LOW — verify rendering empirically before building parser

#### Teachable
- **Architecture concern:** Teachable courses live on individual creator subdomains
  (e.g. `mycourse.teachable.com`), not a unified public marketplace like Hotmart. There is no canonical
  `teachable.com/marketplace` browse page.
- **Fallback:** If Teachable has a "featured courses" or "top courses" editorial page at teachable.com,
  scrape that. If not, skip for v2.0.
- **Recommendation:** Deprioritize. Verify existence of a rankable listing page before allocating a
  platform ID. If no page exists, mark as Out of Scope for v2.0.
- **Confidence:** LOW

#### PerfectPay
- **URL:** `https://perfectpay.com.br` — marketplace URL uncertain
- **Rendering:** Unknown — assume SSR first, fall back to `fetch_spa()` if empty
- **New library needed:** None
- **Confidence:** LOW — verify URL and rendering method before implementing

---

### Group 3: React SPAs — Playwright Required (Already in Stack)

#### Skool
- **URL:** `https://www.skool.com/discover`
- **Rendering:** React SPA — page is client-side rendered; httpx returns a shell HTML
- **Approach:** `fetch_spa()` (Playwright + stealth) — already implemented in BaseScraper
- **New library needed:** None — `fetch_spa()` already handles this
- **Ranking signal:** Member count or activity score from discover feed
- **Risk:** CAPTCHA exposure — stealth plugin + 3.0s domain delay should mitigate

#### AppSumo
- **URL:** `https://appsumo.com/browse/?sort=most-liked`
- **Rendering:** AppSumo uses Next.js — may be SSR-rendered (Next.js supports SSR) or client-hydrated.
  Try `fetch()` first; fall back to `fetch_spa()` if content is empty.
- **New library needed:** None
- **Ranking signal:** `most-liked` or `trending` sort parameter

#### Stan Store
- **URL:** `https://stan.store/explore` (if public explore page exists — verify)
- **Rendering:** Likely React SPA (Stan Store is a modern creator platform)
- **Approach:** `fetch_spa()` via Playwright
- **New library needed:** None
- **Confidence:** LOW — Stan Store is a newer platform; verify public listing page exists and check
  for bot detection before implementing

---

### Group 4: Skip for v2.0

#### Kajabi
- **Architecture:** Kajabi is a creator-owned site builder, not a unified marketplace. There is no
  `kajabi.com/marketplace` browse page analogous to Hotmart or ClickBank.
- **Affiliate program:** Kajabi's affiliate marketplace is gated behind login — not publicly scrapeable.
- **Decision:** **Skip for v2.0.** No public listing page provides rankable product data without auth.
  Document as a known gap. Revisit in v3.0 only if a public directory emerges.
- **Confidence:** MEDIUM — based on Kajabi's product architecture as a hosted course platform

---

## Stack Additions for v2.0

### New Python Libraries: Zero

All 13 platforms can be integrated using the **existing library stack**. No new pip packages are required.

| Pattern | Existing Tool |
|---------|--------------|
| REST API with Basic Auth (Udemy) | `httpx.BasicAuth` — built into httpx |
| GraphQL API with Bearer token (Product Hunt) | `httpx` POST — same `_post_graphql()` pattern as ClickBank |
| SSR HTML (Eduzz, Monetizze, JVZoo, Gumroad, Braip) | `httpx` + `beautifulsoup4` + `lxml` |
| React SPA (Skool, Stan Store, AppSumo fallback) | `playwright` + `playwright-stealth` |
| XML responses (JVZoo API path, if taken) | stdlib `xml.etree.ElementTree` — no pip install |

### New Environment Variables (Add to .env)

```bash
# Udemy Affiliate API (required for Udemy scanner — get at udemy.com/affiliate)
UDEMY_CLIENT_ID=
UDEMY_CLIENT_SECRET=

# Product Hunt API (required for Product Hunt scanner — get at producthunt.com/v2/oauth/applications)
PRODUCT_HUNT_API_TOKEN=

# JVZoo API (optional — enables conversion rate data; scanner degrades gracefully without)
JVZOO_API_KEY=
```

### DOMAIN_DELAYS Extension in base_scraper.py

The `DOMAIN_DELAYS` dict must be extended. Existing entries are untouched:

```python
# ADD to DOMAIN_DELAYS in mis/base_scraper.py
"eduzz.com": 2.5,
"monetizze.com.br": 2.5,
"perfectpay.com.br": 2.5,
"braip.com": 2.5,
"jvzoo.com": 2.0,
"www.udemy.com": 1.5,         # API endpoint — generous rate limit
"api.producthunt.com": 1.0,   # 900 req/min — conservative floor
"appsumo.com": 3.0,           # Next.js — conservative until rendering confirmed
"gumroad.com": 2.0,
"www.skool.com": 3.0,         # React SPA + CAPTCHA risk
"stan.store": 3.0,
```

### SCANNER_MAP Extension in scanner.py

```python
# ADD to SCANNER_MAP in mis/scanner.py run_all_scanners()
"eduzz": EduzzScanner,
"monetizze": MonetizzeScanner,
"perfectpay": PerfectPayScanner,
"braip": BraipScanner,
"jvzoo": JVZooScanner,
"udemy": UdemyScanner,
"producthunt": ProductHuntScanner,
"appsumo": AppSumoScanner,
"gumroad": GumroadScanner,
"skool": SkoolScanner,
"stanstore": StanStoreScanner,
# teachable: pending — verify marketplace page exists
# kajabi: skip v2.0 — no public marketplace
```

---

## Platform ID Allocation for v2.0

Current IDs: 1=Hotmart, 2=ClickBank, 3=Kiwify. New allocations:

| ID | Platform | Status |
|----|----------|--------|
| 4 | Eduzz | Implement |
| 5 | JVZoo | Implement |
| 6 | Udemy | Implement |
| 7 | Product Hunt | Implement |
| 8 | AppSumo | Implement |
| 9 | Gumroad | Implement |
| 10 | Skool | Implement |
| 11 | Stan Store | Implement |
| 12 | Monetizze | Implement |
| 13 | PerfectPay | Implement |
| 14 | Braip | Implement |
| 15 | Teachable | Pending — verify marketplace page |
| 16 | Kajabi | Skip v2.0 — no public marketplace |

---

## Scanner Implementation Patterns for New Platforms

### Pattern A: REST API with Basic Auth (Udemy model)

```python
class UdemyScanner(PlatformScanner):
    async def scan_niche(self, niche_slug, platform_slug, niche_id=0):
        import os
        client_id = os.environ.get("UDEMY_CLIENT_ID")
        client_secret = os.environ.get("UDEMY_CLIENT_SECRET")
        if not client_id or not client_secret:
            log.warning("udemy_scanner.missing_credentials")
            return []
        # httpx GET with Basic Auth — no new libraries needed
        # ... params, parse JSON, return list[Product]
```

### Pattern B: GraphQL API with Bearer Token (Product Hunt model)

Identical to `ClickBankScanner._post_graphql()` — POST JSON body to GraphQL endpoint via httpx,
add `Authorization: Bearer {token}` header. Copy the method verbatim, change the URL and query.

### Pattern C: SSR HTML (Eduzz, Monetizze, Braip, JVZoo, Gumroad model)

Identical to `HotmartScanner` pattern — `fetch()` + BeautifulSoup4 parsing + multi-selector fallback
+ `alert="schema_drift"` log on parse failure + return `[]` on any unrecoverable error.

### Pattern D: SPA with Playwright (Skool, Stan Store, AppSumo model)

Use `fetch_spa()` from `PlatformScanner` (delegated to `BaseScraper`). No new base class code needed.
Parse the rendered HTML with BeautifulSoup4 as normal.

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Product Hunt data | GraphQL API (free token) | HTML scraping | API gives structured `votesCount`; HTML parsing is fragile |
| Udemy data | Official Affiliate API | HTML scraping | Official API stable and rate-limited; scraping Udemy HTML likely violates ToS |
| JVZoo data | SSR HTML (no auth) | JVZoo REST API (account required) | API requires vendor account; public SSR marketplace gives same data without auth |
| Kajabi coverage | Skip v2.0 | Scrape individual creator pages | No unified marketplace; individual pages require an external seed list |
| GraphQL client | Raw httpx POST | `gql` library | `gql` adds a dependency for zero functional gain; ClickBank proves raw POST is sufficient |
| XML parsing (JVZoo API) | stdlib `xml.etree.ElementTree` | `xmltodict` | stdlib covers simple XML; avoids a dependency |
| AppSumo rendering | Try httpx first, fall back to Playwright | Playwright always | Next.js can render SSR; try the cheaper path before committing to browser automation |

---

## What NOT to Add

| Library | Reason to Avoid |
|---------|----------------|
| `scrapy` | Decided against in v1.0; mixing Scrapy with PlatformScanner/BaseScraper creates two incompatible paradigms |
| `selenium` | Playwright already covers all SPA rendering needs; Selenium has no async support |
| `requests` | Synchronous — blocks the event loop; httpx is already present |
| `gql` | Python GraphQL client; raw POST via httpx is sufficient (ClickBank scanner proves this) |
| `xmltodict` | stdlib `xml.etree.ElementTree` covers any JVZoo XML parsing needed |
| `aiofiles` | No async file I/O needed in scanners |
| `redis` | Deferred to v3.0; SQLite WAL mode handles concurrent reads at this scale |
| `celery` | APScheduler covers all scheduling needs; no distributed workers needed |
| `pydantic` | Not in current stack; sqlite-utils + Python dataclasses cover all data needs |

---

## Confidence Assessment

| Platform / Claim | Confidence | Notes |
|-----------------|------------|-------|
| Udemy has a public Affiliate API | HIGH | Well-documented, stable for years; Basic Auth pattern is standard |
| Product Hunt has a public GraphQL API | HIGH | PH API v2 is publicly documented; verify read-only token requirements |
| Existing stack covers all integration patterns | HIGH | Verified against v1.0 codebase — BaseScraper, Playwright, BeautifulSoup4 all present and working |
| Eduzz/Monetizze are SSR HTML | MEDIUM | BR platforms of this generation typically use SSR; must verify empirically |
| JVZoo SSR marketplace is scrapeable | MEDIUM | JVZoo marketplace has been publicly accessible historically; verify current structure |
| Gumroad /discover is SSR | MEDIUM | Gumroad is a simpler platform; training data suggests SSR rendering |
| Skool Discover is a React SPA | MEDIUM | Skool uses modern React stack; likely needs Playwright — verify before committing |
| AppSumo rendering method | MEDIUM | Next.js app — may be SSR; try httpx first before falling back to Playwright |
| Kajabi has no public marketplace | MEDIUM | Based on Kajabi's hosted site-builder architecture; verify before finalizing skip |
| PerfectPay / Braip / Stan Store rendering | LOW | Less well-known platforms; rendering method must be verified empirically |
| Teachable has a rankable marketplace page | LOW | Creator-subdomain architecture makes a unified listing page unlikely |

---

## Verification Checklist (Run Before Implementation)

For each LOW/MEDIUM confidence platform, perform this check before writing the scanner:

```bash
# 1. Fetch the candidate listing URL with httpx
python -c "
import httpx, asyncio
async def check(url):
    async with httpx.AsyncClient(follow_redirects=True) as c:
        r = await c.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        print(r.status_code, len(r.text), 'hydration' in r.text.lower())
asyncio.run(check('https://eduzz.com/marketplace'))
"
# If content is empty or contains only hydration markers -> needs Playwright (fetch_spa)
# If content has product HTML -> httpx sufficient
```

This takes 2 minutes per platform and prevents building the wrong integration method.

---

## Sources

- Existing codebase: `mis/base_scraper.py`, `mis/scanners/clickbank.py`, `mis/scanners/hotmart.py`,
  `mis/scanner.py`, `mis/requirements.txt` — verified 2026-03-16
- Udemy Affiliate API: training data (knowledge cutoff August 2025) — HIGH confidence, API stable for years
- Product Hunt API v2: training data — HIGH confidence, publicly documented
- Platform rendering methods (non-API): training data — MEDIUM/LOW confidence as noted per-platform
- **Important:** WebSearch and WebFetch tools were unavailable during this research session. All
  platform-specific claims derive from training data. Run the verification checklist above before
  implementing each scanner to confirm rendering method and URL structure.
