# Technology Stack

**Project:** Market Intelligence System (MIS) — MEGABRAIN Module
**Researched:** 2026-03-14
**Overall Confidence:** MEDIUM (FastAPI/PostgreSQL/Redis verified via official docs; scraping libs and scheduler versions from training data, flagged explicitly)

---

## Recommended Stack

### Core Framework

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Python | 3.11+ | Runtime | Already used by MEGABRAIN; 3.11 has best perf/stability balance. Avoid 3.12 for now — minor ecosystem gaps with some scraping libs. |
| FastAPI | 0.111+ | REST API + dashboard backend | Verified: high-performance async, auto-generates OpenAPI docs, native Pydantic validation. Ideal for serving intelligence data to the frontend. |
| Pydantic v2 | 2.x | Data models + validation | FastAPI dependency; v2 is 5-50x faster than v1 for validation-heavy pipelines. Use for all scraped data schemas. |

### Scraping Layer

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Playwright (Python) | 1.40+ | JS-rendered pages (Hotmart, Kiwify, Eduzz, ClickBank) | MEDIUM confidence. Industry standard for SPA scraping. Handles login flows, dynamic content, anti-bot challenges better than Selenium. Async-native. |
| httpx | 0.27+ | Static HTML pages + API calls (YouTube Data API, Reddit API) | MEDIUM confidence. Async HTTP client, drop-in replacement for `requests` with native `async/await`. Use for pages that don't need JS execution — much faster than Playwright. |
| BeautifulSoup4 | 4.12+ | HTML parsing after fetch | MEDIUM confidence. Stable, battle-tested. Pair with `lxml` parser for speed. Do NOT use `html.parser` — 3x slower on large pages. |
| PRAW | 7.7+ | Reddit API official wrapper | MEDIUM confidence. Official Reddit API access — correct way to pull subreddit posts/comments. Reddit's API has 100 req/min rate limit on free tier. |
| youtube-data-api | via google-api-python-client 2.x | YouTube search + comments | MEDIUM confidence. Official Google client. YouTube Data API v3 quotas: 10,000 units/day free. Comment scraping = 1 unit each. Plan carefully. |
| pytrends | 4.9+ | Google Trends data | LOW confidence — version from training data. Unofficial Google Trends client. No official API exists. Google can block it — add exponential backoff. |
| Scrapy | 2.11+ | High-volume structured scraping (JVZoo, AppSumo, Product Hunt) | MEDIUM confidence. Best for multi-page crawls with built-in rate limiting, item pipelines, and retry logic. Use for platforms with pagination patterns. |

### Data Pipeline & Scheduling

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| APScheduler | 3.10+ | Hourly job scheduling | MEDIUM confidence. Lightweight, no external dependencies, runs in-process. Perfect for hourly radar cycle without needing Celery's complexity. Use `AsyncIOScheduler` with `AsyncIOExecutor`. |
| SQLAlchemy | 2.0+ | ORM + database abstraction | MEDIUM confidence. SQLAlchemy 2.0 has native async support. Lets you start with SQLite locally and migrate to PostgreSQL in prod without changing queries. |

**Why NOT Celery:** Celery requires Redis/RabbitMQ as broker AND result backend, adds ~200MB overhead, and is designed for distributed workloads. For a single-machine hourly pipeline, APScheduler is sufficient and dramatically simpler. Revisit Celery only if scraping jobs need to scale to multiple workers across machines.

**Why NOT Prefect/Airflow:** Prefect and Airflow are designed for complex DAG orchestration with UI visibility. For this project's scope (hourly cron + simple pipeline), APScheduler is 90% less setup with equivalent results.

### Database

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| SQLite | 3.45+ (stdlib) | Development + single-user prod | Verified: SQLite supports up to 281TB, ACID-compliant, zero-config. For a single-user intelligence system running locally, SQLite is sufficient. No server process needed — matches MEGABRAIN's file-based philosophy. |
| PostgreSQL | 16+ | Production / multi-user deployment | Verified: Best-in-class for analytics with JSONB support, GIN indexes for full-text search on scraped content, parallel query execution. Migrate from SQLite to PostgreSQL when concurrent users or data volume demands it. |
| Redis | 7.x | Rate-limit state, job deduplication, short-term cache | Verified: In-memory key-value store. Use it specifically for: (1) storing last-crawled timestamps per source to avoid duplicate scrapes, (2) caching API responses to avoid re-fetching within the same hour, (3) Celery broker if you ever scale. Optional for MVP — SQLite can serve the same role at smaller scale. |

**Recommended progression:** Start with SQLite-only (zero ops overhead). Add Redis when rate-limit coordination becomes complex. Add PostgreSQL when deploying to a server or sharing with a team.

### AI/LLM Integration

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| openai (SDK) | 1.x | Dossier generation, copy analysis, pain synthesis | MEDIUM confidence. MEGABRAIN already uses OpenAI for pipeline processing. Use `gpt-4o-mini` for bulk analysis (cheap, fast) and `gpt-4o` for final dossier synthesis. Structured outputs via `response_format={"type": "json_object"}` for reliable data extraction. |
| anthropic (SDK) | 0.28+ | Alternative for long-context analysis | LOW confidence — version from training data. Claude's 200K context window makes it better than GPT-4 for analyzing full sales pages + all reviews in a single prompt. Use selectively for product dossier generation where full context matters. |

**Why NOT LangChain:** LangChain adds abstraction overhead that doesn't pay off for this use case. Direct SDK calls to OpenAI/Anthropic are simpler, easier to debug, and better aligned with MEGABRAIN's existing pattern (raw API calls in `extract_*.py` scripts). LangChain is valuable for RAG pipelines — not needed here.

### Dashboard Frontend

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| FastAPI + Jinja2 | bundled | Server-side rendered dashboard | MEDIUM confidence. For a single-user internal tool, SSR with Jinja2 templates served by FastAPI eliminates a separate frontend build system. Much less complexity than a React SPA. |
| HTMX | 1.9+ | Dynamic UI updates without a JS framework | MEDIUM confidence. Lets you add real-time product table updates, filter controls, and dossier rendering with minimal JavaScript. Pairs perfectly with FastAPI/Jinja2. Avoids React/Vue build complexity for an internal tool. |
| Tailwind CSS (CDN) | 3.x | Styling | LOW confidence. Use via CDN (no build step needed). Fast to prototype a clean dashboard. For an internal tool, CDN-loaded Tailwind is entirely sufficient. |
| Chart.js | 4.x | Trend charts, scoring charts | LOW confidence — version from training. Lightweight charting library loaded via CDN. No build step, works with HTMX. Use for Google Trends graphs and product ranking charts. |

**Why NOT Streamlit:** Streamlit is excellent for data science notebooks but generates poor UX for navigation-heavy dashboards (multiple products, dossier views, filter panels). Its state management becomes painful. FastAPI+HTMX gives full control at similar code volume.

**Why NOT React/Next.js:** The project is Python-first and single-user. Adding a Node.js frontend build pipeline creates unnecessary overhead. HTMX + FastAPI achieves 95% of the UX with 20% of the complexity.

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| tenacity | 8.x | Retry logic with exponential backoff | All HTTP calls to external platforms — rate limits are guaranteed to hit |
| fake-useragent | 1.4+ | Rotate User-Agent strings | All Playwright/httpx scrapers — reduces bot detection |
| loguru | 0.7+ | Structured logging | Replace `print()` in all pipeline scripts — disk + stdout, rotation, JSON format |
| python-dotenv | 1.0+ | Environment variable loading | `.env` file support — consistent with MEGABRAIN pattern |
| Pydantic-settings | 2.x | Typed config management | Load and validate all config from env vars with type safety |
| aiohttp | 3.9+ | Async HTTP when httpx not sufficient | Only if httpx proves insufficient for specific cases (e.g., streaming responses) |
| Jinja2 | 3.1+ | Template rendering | FastAPI dependency — already included |
| WeasyPrint | 60+ | PDF dossier export | Render HTML templates to PDF — use for downloadable product dossiers |

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Browser automation | Playwright | Selenium | Playwright is 3x faster, native async, better anti-bot handling, smaller API surface |
| HTTP client | httpx | requests | `requests` is synchronous — blocks the event loop in async pipelines |
| Scheduler | APScheduler | Celery | Celery requires message broker, adds ops complexity for single-machine use |
| Scheduler | APScheduler | Prefect/Airflow | Prefect/Airflow are overengineered for hourly single-machine jobs |
| Database (dev) | SQLite | PostgreSQL | SQLite requires zero ops; migrate to PG when actually needed |
| Dashboard | FastAPI+HTMX | Streamlit | Streamlit UX degrades on multi-view dashboards; poor control over layout |
| Dashboard | FastAPI+HTMX | React SPA | React adds Node.js build pipeline — not justified for internal single-user tool |
| LLM orchestration | Direct SDK | LangChain | LangChain abstraction adds debug complexity without benefit for direct API calls |
| Reddit | PRAW | Playwright scrape | PRAW is the official API wrapper; official API = no ToS violation, structured data |
| Google Trends | pytrends | Playwright scrape | pytrends is cleaner; Playwright on Trends is fragile |

---

## Anti-Recommendations (Explicit Do-Nots)

| Technology | Why to Avoid |
|------------|-------------|
| Selenium | Deprecated in favor of Playwright for Python; slower, no async |
| Scrapy-Splash | Extra Docker dependency for JS rendering; Playwright is simpler and more capable |
| Beautiful Soup with html.parser | Use `lxml` parser — 3x faster on large product pages |
| SQLite in multi-threaded write mode | SQLite has write-locking issues under concurrent writes — use WAL mode (`PRAGMA journal_mode=WAL`) or switch to PostgreSQL |
| requests library (sync) | Blocks async event loop; use httpx instead |
| LangChain | Unnecessary abstraction; direct OpenAI/Anthropic SDK calls are cleaner for this use case |
| Celery (at MVP stage) | Overkill for single-machine hourly jobs; adds Redis/RabbitMQ ops overhead |
| React/Vue SPA | Adds Node.js build pipeline complexity for an internal single-user dashboard |
| Scrapy for JS-rendered pages | Scrapy is HTML-first; don't force JS execution through Scrapy-Splash — use Playwright |

---

## Integration with MEGABRAIN

The MIS plugs into MEGABRAIN as a module under `core/intelligence/` or as a sibling module:

```
MEGABRAIN/
├── core/
│   └── intelligence/       # Existing Python pipeline scripts
├── mis/                    # NEW: Market Intelligence System
│   ├── scrapers/           # Per-platform scraper modules
│   ├── pipeline/           # APScheduler jobs
│   ├── analysis/           # LLM analysis prompts + runners
│   ├── models/             # SQLAlchemy models
│   ├── api/                # FastAPI app
│   └── dashboard/          # Jinja2 templates + static
```

**Integration points:**
- Shares `.env` / environment config with MEGABRAIN
- Reads/writes to SQLite (or PostgreSQL) — separate DB from MEGABRAIN's JSON-file state
- Dossiers exported as YAML/JSON can be consumed by MEGABRAIN's existing knowledge pipeline
- JARVIS agent can invoke MIS via CLI or HTTP endpoint

---

## Installation

```bash
# Core runtime
pip install fastapi[standard] pydantic pydantic-settings sqlalchemy

# Scraping
pip install playwright httpx beautifulsoup4 lxml scrapy praw
pip install google-api-python-client pytrends

# Install Playwright browsers (one-time)
playwright install chromium

# Scheduling
pip install apscheduler

# LLM
pip install openai anthropic

# Utilities
pip install tenacity fake-useragent loguru python-dotenv weasyprint

# Dev
pip install pytest httpx pytest-asyncio
```

```bash
# For Redis (optional, for rate-limit state at scale)
# Install Redis server separately, then:
pip install redis
```

---

## Confidence Summary

| Component | Confidence | Source |
|-----------|------------|--------|
| FastAPI + Pydantic | HIGH | Official fastapi.tiangolo.com docs verified |
| PostgreSQL for analytics | HIGH | Official postgresql.org docs verified |
| SQLite for local dev | HIGH | Official sqlite.org docs verified |
| Redis as cache/broker | HIGH | Official redis.io docs verified |
| Playwright (concept) | MEDIUM | Training data; official docs blocked during research |
| httpx over requests | MEDIUM | Training data; well-established community consensus |
| APScheduler over Celery | MEDIUM | Training data; architecture reasoning sound |
| PRAW for Reddit | MEDIUM | Training data; Reddit's official Python wrapper |
| pytrends | LOW | Training data; unofficial library, version unverified |
| HTMX + Jinja2 for dashboard | MEDIUM | Training data; pattern well-established in Python community |
| youtube-data-api quotas | MEDIUM | Training data; quota numbers stable over years |
| Playwright version 1.40+ | LOW | Training data; version unverified — check pypi.org/project/playwright |
| APScheduler version 3.10+ | LOW | Training data; version unverified — check pypi.org/project/apscheduler |
| WeasyPrint for PDF | LOW | Training data; known to have system-level dependencies (libcairo, libpango) |

---

## Version Verification Checklist

Before building, verify current versions for LOW/MEDIUM confidence items:

- [ ] `pip index versions playwright` — confirm 1.40+
- [ ] `pip index versions apscheduler` — confirm 3.x stable (v4 is in beta as of training cutoff)
- [ ] `pip index versions pytrends` — confirm active maintenance
- [ ] Check APScheduler docs — v4 (AsyncIO-native) may be stable by now; if so, prefer v4 API
- [ ] Check Reddit API ToS — free tier rate limits may have changed since 2023 changes

---

## Sources

- FastAPI official documentation: https://fastapi.tiangolo.com/ (verified 2026-03-14)
- PostgreSQL about page: https://www.postgresql.org/about/ (verified 2026-03-14)
- SQLite about page: https://www.sqlite.org/about.html (verified 2026-03-14)
- Redis documentation: https://redis.io/docs/latest/get-started/ (verified 2026-03-14)
- All other library recommendations: training data (knowledge cutoff August 2025) — see confidence flags above
