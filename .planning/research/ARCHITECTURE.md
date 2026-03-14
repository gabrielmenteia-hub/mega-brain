# Architecture Patterns: Market Intelligence System

**Domain:** Web scraping + data pipeline + AI analysis + dashboard
**Researched:** 2026-03-14
**Overall confidence:** HIGH (mature domain, well-established patterns)

---

## Recommended Architecture

### High-Level: Layered Pipeline with Shared Storage

```
┌─────────────────────────────────────────────────────────────────┐
│                         INGESTION LAYER                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Platform     │  │ Trend/Social │  │ Ad Spy               │  │
│  │ Scrapers     │  │ Scrapers     │  │ Scrapers             │  │
│  │ (Hotmart,    │  │ (G.Trends,  │  │ (Ad comments,        │  │
│  │  ClickBank,  │  │  Reddit,    │  │  FB ads library)     │  │
│  │  etc.)       │  │  YouTube)   │  │                      │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
└─────────┼─────────────────┼──────────────────────┼─────────────┘
          │                 │                      │
          ▼                 ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                     QUEUE / SCHEDULER                           │
│  APScheduler (cron jobs) + in-memory task queue                 │
│  - Platform scrapers: daily/6h cycle                            │
│  - Trend radar: hourly cycle                                     │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                       STORAGE LAYER                             │
│  ┌─────────────────────┐    ┌───────────────────────────────┐  │
│  │ SQLite / PostgreSQL  │    │ File Store                    │  │
│  │ - raw_products       │    │ /artifacts/mis/               │  │
│  │ - pain_signals       │    │  - raw HTML snapshots         │  │
│  │ - dossiers           │    │  - generated PDFs             │  │
│  │ - trend_snapshots    │    │  - dossier JSONs              │  │
│  └─────────────────────┘    └───────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     AI ANALYSIS LAYER                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Analysis Pipeline (Python)                               │  │
│  │  - copy_analyzer.py     (sales page extraction)         │  │
│  │  - pain_synthesizer.py  (Reddit/Quora/YT clustering)    │  │
│  │  - dossier_generator.py (LLM orchestration via SDK)     │  │
│  │  - trend_reporter.py    (hourly pain report)            │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SERVING LAYER                              │
│  ┌──────────────────────┐   ┌────────────────────────────────┐ │
│  │ FastAPI REST API      │   │ Web Dashboard (Next.js / lite) │ │
│  │ /products, /dossiers  │◄──│ Product rankings, pain cards,  │ │
│  │ /pain-reports         │   │ dossier viewer, alerts         │ │
│  └──────────────────────┘   └────────────────────────────────┘ │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ MEGABRAIN CLI Bridge                                     │  │
│  │  - mis_agent.py  → calls FastAPI or reads DB directly    │  │
│  │  - Exposes /mis-briefing slash command                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Boundaries

| Component | Responsibility | Communicates With | Technology |
|-----------|---------------|-------------------|------------|
| **Platform Scrapers** | Fetch product listings from Hotmart, Kiwify, Eduzz, ClickBank, JVZoo, Udemy, Teachable, Product Hunt, AppSumo | Writes to DB raw_products table | Python + httpx/playwright |
| **Trend/Social Scrapers** | Hourly collection from Google Trends, Reddit, Quora, YouTube | Writes to DB pain_signals table | Python + httpx + PRAW (Reddit) |
| **Ad Spy Scrapers** | Collect ad creatives and comment sentiment from public ad libraries | Writes to DB ad_signals table | Python + playwright |
| **Scheduler** | Triggers scrapers on cron schedules; manages rate limits and retries | Calls all scraper modules | APScheduler |
| **Storage Layer** | Single source of truth for all raw and processed data | Read/written by all layers | SQLite (dev) / PostgreSQL (prod) + filesystem |
| **Analysis Pipeline** | LLM-powered transformation: raw data → structured insights → dossiers | Reads DB, writes dossiers back to DB + filesystem | Python + Anthropic/OpenAI SDK |
| **FastAPI Server** | REST endpoints consumed by dashboard and CLI bridge | Reads DB | Python + FastAPI + Uvicorn |
| **Web Dashboard** | Visual consumption of products, dossiers, pain reports | Calls FastAPI | Streamlit (fast) OR Next.js (polished) |
| **MEGABRAIN Bridge** | Exposes MIS as a slash command / agent within existing MEGABRAIN | Calls FastAPI or reads DB | Python module in core/intelligence/ |

---

## Data Flow

### Flow 1: Product Discovery (Platform Scrapers)

```
Scheduler (daily/6h)
  → Platform Scraper (e.g. hotmart_scraper.py)
    → HTTP request to platform listing page
    → HTML parse → extract product metadata
    → Deduplicate against DB
    → INSERT raw_products (name, platform, url, price, rank, niche, captured_at)
  → Trigger: if new_products_found → enqueue product_spy_job(product_id)
```

### Flow 2: Product Espionage (Deep Scrape)

```
product_spy_job(product_id)
  → Fetch sales page HTML → store in filesystem /artifacts/mis/raw/
  → copy_analyzer.py:
      - Extract headlines, bullets, price anchors, CTA text
      - LLM: "Summarize this sales page structure and main arguments"
      - Store structured JSON in DB dossier_data
  → review_scraper.py:
      - Scrape Hotmart reviews / Trustpilot / app store if applicable
      - LLM: "Extract top praise and top objections from these reviews"
      - Store in DB dossier_data
  → dossier_generator.py:
      - Assemble all data: metadata + copy analysis + reviews + ad data
      - LLM: "Generate complete product dossier as structured JSON"
      - Store final dossier in DB dossiers table
      - Export PDF to /artifacts/mis/dossiers/{product_id}.pdf
      - Trigger alert: new_dossier_ready
```

### Flow 3: Pain Radar (Hourly)

```
Scheduler (every 1h)
  → For each configured niche:
      → google_trends_fetcher.py → INSERT trend_snapshots
      → reddit_scraper.py (PRAW) → INSERT pain_signals (source=reddit)
      → quora_scraper.py → INSERT pain_signals (source=quora)
      → youtube_scraper.py (Data API) → INSERT pain_signals (source=youtube)
  → trend_reporter.py:
      - Aggregate all pain_signals from last 1h window
      - LLM: "Identify top 10 pains/desires from these signals, cluster by theme"
      - INSERT pain_report (hour_window, niche, top_pains JSON)
  → Dashboard polling picks up new report automatically
```

### Flow 4: Dashboard Consumption

```
User opens dashboard
  → Browser → FastAPI GET /products?niche=X&sort=rank
  → FastAPI queries DB → returns JSON
  → Browser renders product ranking table

User clicks product
  → Browser → FastAPI GET /dossiers/{product_id}
  → FastAPI returns dossier JSON
  → Browser renders dossier view

Dashboard polls every 5min
  → FastAPI GET /pain-reports/latest
  → Returns most recent hourly report per niche
```

### Flow 5: MEGABRAIN CLI Bridge

```
User types /mis-briefing in Claude Code
  → MEGABRAIN skill router detects keyword
  → mis_agent.py activated
  → Calls FastAPI /summary OR reads DB directly
  → Returns formatted markdown briefing to Claude conversation
```

---

## Suggested Build Order (Dependencies)

The system has clear dependency layers — each layer must exist before the next can function.

```
Phase 1: Foundation
  → Database schema (all tables, migrations)
  → Base scraper class (rate limiting, retry, logging)
  → APScheduler setup (skeleton with test job)
  Dependency: Nothing. Start here.

Phase 2: Platform Scrapers (Module 1)
  → Implement 3 BR scrapers (Hotmart, Kiwify, Eduzz)
  → Implement 5+ international scrapers
  → Scheduler integration
  Dependency: Phase 1 DB + base scraper

Phase 3: Trend/Social Scrapers (Module 3)
  → Google Trends (pytrends)
  → Reddit (PRAW)
  → YouTube Data API
  → Quora (httpx + parse)
  → Hourly scheduler job
  Dependency: Phase 1 DB + base scraper

Phase 4: AI Analysis Pipeline
  → copy_analyzer.py (needs scraped product pages)
  → pain_synthesizer.py (needs pain_signals data)
  → dossier_generator.py (needs all above)
  → trend_reporter.py (needs pain_signals)
  Dependency: Phase 2 + Phase 3 (needs data to analyze)

Phase 5: Serving Layer
  → FastAPI with endpoints for products, dossiers, pain reports
  → Web dashboard (Streamlit fastest path)
  Dependency: Phase 4 (needs data to display meaningfully)

Phase 6: MEGABRAIN Integration
  → mis_agent.py bridge
  → Slash command /mis-briefing
  → Alert hooks
  Dependency: Phase 5 API
```

**Critical path:** DB schema → Base scraper → Platform scrapers → Pain scrapers → AI pipeline → API → Dashboard → Integration

---

## Patterns to Follow

### Pattern 1: Collector / Processor Separation

**What:** Scrapers only collect raw data. AI analysis runs separately from a queue.
**When:** Always in this domain.
**Why:** Scraping and LLM calls have very different latencies, failure modes, and costs. Coupling them means a scrape failure breaks analysis and vice versa. Separating allows retry of either independently.

```
# Good: scraper writes raw, processor reads raw
def scrape_hotmart():
    html = fetch(url)
    db.insert("raw_products", {"html": html, "status": "raw", "url": url})

# Separate process/job:
def process_raw_products():
    rows = db.query("SELECT * FROM raw_products WHERE status = 'raw'")
    for row in rows:
        analysis = llm_analyze(row["html"])
        db.update("raw_products", row["id"], {"analysis": analysis, "status": "processed"})
```

### Pattern 2: Idempotent Upserts

**What:** Every scrape operation uses upsert (INSERT OR REPLACE / ON CONFLICT UPDATE) keyed on a stable identifier (URL hash, platform+product_id).
**When:** Always — scrapers run on schedules and will re-encounter the same products.
**Why:** Prevents duplicate rows. Allows tracking changes over time (price changes, rank changes).

```python
db.execute("""
    INSERT INTO raw_products (url_hash, platform, name, price, rank, captured_at)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(url_hash) DO UPDATE SET
        price = excluded.price,
        rank = excluded.rank,
        captured_at = excluded.captured_at
""", (url_hash, platform, name, price, rank, now()))
```

### Pattern 3: Rate Limit Budget per Source

**What:** Each scraper source has a configurable rate limit budget (requests/minute, delay between requests).
**When:** All HTTP scrapers.
**Why:** Google, Reddit, YouTube all have rate limits. Platform sites block aggressive crawlers. A centralized budget per domain prevents all jobs from hammering simultaneously.

```python
RATE_LIMITS = {
    "reddit": {"rpm": 60, "delay": 1.0},      # PRAW default
    "youtube": {"rpm": 100, "delay": 0.6},     # Data API quota
    "google_trends": {"rpm": 10, "delay": 6.0}, # Aggressive anti-bot
    "hotmart": {"rpm": 20, "delay": 3.0},       # No official limit, be conservative
}
```

### Pattern 4: Status-Driven Processing Queue

**What:** DB rows carry a `status` field (raw → processing → processed → failed). The AI pipeline queries by status.
**When:** Any multi-step pipeline.
**Why:** Simple, durable queue without Redis/Celery overhead. Works well at this scale. Failed items are visible and retryable.

```
raw_products.status:
  "raw"        → scraped, not yet analyzed
  "processing" → claimed by analysis job
  "processed"  → dossier generated
  "failed"     → analysis failed (error_message stored)
  "skipped"    → not relevant to current niches
```

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Scraping and LLM in the Same Synchronous Job

**What:** Calling the LLM API directly inside the scraper loop.
**Why bad:** LLM calls are expensive (time + money). If one fails, the whole scrape batch fails. If rate-limited on LLM, scraping also stalls.
**Instead:** Write raw data to DB, run AI pipeline as a separate job that processes the queue.

### Anti-Pattern 2: One Scraper Module for All Platforms

**What:** A single `scraper.py` with if/elif branches for each platform.
**Why bad:** Platforms have radically different structures. One change (site redesign on Hotmart) breaks the entire module. Testing becomes impossible.
**Instead:** One file per platform (`hotmart_scraper.py`, `clickbank_scraper.py`), all extending a common `BaseScraper` class.

### Anti-Pattern 3: Storing Full HTML in DB

**What:** Inserting raw HTML (can be 500KB+) into database rows.
**Why bad:** Database bloat. SQLite degrades significantly at large blob sizes. Queries slow down.
**Instead:** Store HTML on filesystem (`/artifacts/mis/raw/{url_hash}.html`), store only the path in DB.

### Anti-Pattern 4: Tight Coupling to MEGABRAIN Internals

**What:** MIS modules directly importing from MEGABRAIN core modules, writing to MEGABRAIN's own DB tables.
**Why bad:** Changes to MEGABRAIN break MIS and vice versa. Makes MIS untestable in isolation.
**Instead:** MIS has its own DB (`mis.db`), its own artifact directory (`/artifacts/mis/`). MEGABRAIN bridge module (`mis_agent.py`) is the ONLY integration point — it reads from MIS API/DB and speaks MEGABRAIN language.

### Anti-Pattern 5: Polling for Dashboard Updates via Full Page Refresh

**What:** Dashboard reloads entire page every N seconds to show new data.
**Why bad:** Jarring UX. Re-runs all queries. If Streamlit, causes full component re-render.
**Instead:** Streamlit's `st.rerun()` with a controlled interval or FastAPI SSE for real-time updates.

---

## Component Dependency Map (for Build Order)

```
mis.db (schema)
      │
      ├─→ BaseScraper
      │         │
      │         ├─→ PlatformScrapers (Hotmart, ClickBank, etc.)
      │         │         │
      │         │         └─→ product_spy_job
      │         │                   │
      │         └─→ TrendScrapers   │
      │                   │         │
      │                   ▼         ▼
      │             pain_signals  raw_products (status=raw)
      │                   │         │
      │                   └────┬────┘
      │                        ▼
      │                  Analysis Pipeline
      │                  (copy_analyzer,
      │                   pain_synthesizer,
      │                   dossier_generator,
      │                   trend_reporter)
      │                        │
      │                        ▼
      │                  dossiers, pain_reports
      │                        │
      │              ┌─────────┴─────────┐
      │              ▼                   ▼
      │         FastAPI Server     MEGABRAIN Bridge
      │              │
      │              ▼
      │         Web Dashboard
      │
      └─→ APScheduler (wires all jobs)
```

---

## Scalability Considerations

| Concern | At 10 niches / daily | At 50 niches / hourly | At 200+ niches / real-time |
|---------|---------------------|----------------------|---------------------------|
| Storage | SQLite + filesystem fine | PostgreSQL recommended | PostgreSQL + S3 for artifacts |
| Scraping throughput | Sequential fine | Async with asyncio/httpx | Distributed workers (Celery) |
| AI analysis cost | Batch nightly | Batch hourly, filter what matters | Cache aggressively, batch-summarize |
| Dashboard performance | Streamlit fine | Streamlit with DB indexes | Next.js + API pagination |
| Scheduler | APScheduler in-process | APScheduler in-process | Celery Beat or Airflow |

**For this project (single user, 8 platforms, hourly radar, 3-5 niches):** SQLite + APScheduler + Streamlit is the right call. No distributed systems needed.

---

## Integration with Existing MEGABRAIN

```
MEGABRAIN/
├── core/
│   └── intelligence/
│       └── mis_agent.py          ← NEW: Bridge module
├── artifacts/
│   └── mis/                      ← NEW: MIS artifact store
│       ├── raw/                  ← HTML snapshots
│       └── dossiers/             ← Generated PDFs
├── mis/                          ← NEW: MIS package root
│   ├── db/
│   │   ├── schema.sql
│   │   └── mis.db                ← gitignored (L3 data)
│   ├── scrapers/
│   │   ├── base.py
│   │   ├── platforms/
│   │   │   ├── hotmart.py
│   │   │   ├── kiwify.py
│   │   │   └── ...
│   │   └── signals/
│   │       ├── google_trends.py
│   │       ├── reddit.py
│   │       └── youtube.py
│   ├── analysis/
│   │   ├── copy_analyzer.py
│   │   ├── pain_synthesizer.py
│   │   ├── dossier_generator.py
│   │   └── trend_reporter.py
│   ├── api/
│   │   └── server.py             ← FastAPI
│   ├── dashboard/
│   │   └── app.py                ← Streamlit
│   ├── scheduler.py              ← APScheduler entry point
│   └── config.py                 ← Niches, rate limits, keys
```

The `mis_agent.py` in `core/intelligence/` is the only file that crosses the boundary between MIS and MEGABRAIN. It can be activated by the existing MEGABRAIN skill router via keyword detection.

---

## Key Architecture Decisions

| Decision | Recommended | Rationale |
|----------|-------------|-----------|
| Queue mechanism | DB status column | No Redis overhead needed at this scale; SQLite is sufficient; visible and debuggable |
| Scheduler | APScheduler (in-process) | Simple, Python-native, handles cron + interval; no broker needed |
| Storage | SQLite (dev) → PostgreSQL (if scaling) | SQLite zero-config is right for solo user; migration path clear |
| Artifact store | Filesystem /artifacts/mis/ | HTML/PDF blobs don't belong in a relational DB |
| Dashboard framework | Streamlit | Python-native, fastest to ship, no JS needed, handles polling |
| API layer | FastAPI | Needed for MEGABRAIN bridge and future extensibility; Streamlit could read DB directly in pinch |
| Scraper base | httpx (async) + Playwright (JS-heavy sites) | httpx for most; Playwright only when JS rendering required (Hotmart SPA) |
| Integration boundary | mis_agent.py only | Prevents tight coupling; MIS is independently runnable |

---

## Sources

- Architecture patterns based on well-established Python data pipeline conventions (ETL/ELT patterns)
- APScheduler documentation: https://apscheduler.readthedocs.io/
- FastAPI documentation: https://fastapi.tiangolo.com/
- Streamlit documentation: https://docs.streamlit.io/
- PRAW (Reddit API): https://praw.readthedocs.io/
- pytrends (Google Trends): https://github.com/GeneralMills/pytrends
- Confidence: HIGH for structural patterns (mature domain); MEDIUM for specific library choices (verify versions before implementing)
