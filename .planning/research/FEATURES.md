# Feature Landscape — Market Intelligence System (MIS)

**Domain:** Market intelligence / product spy / competitive research (infoproducts focus)
**Researched:** 2026-03-14
**Confidence note:** Research based on training knowledge (cutoff Aug 2025) of tools: SimilarWeb, SEMrush, Ahrefs, SpyFu, iSpionage, AdSpy, BigSpy, PowerAdSpy, Hotmart ranking pages, ClickBank marketplace. WebSearch and Bash were unavailable in this research session — mark stack-specific findings for validation. Core competitive intelligence features are MEDIUM-HIGH confidence (stable domain).

---

## Table Stakes

Features users expect. Missing = product feels incomplete or unusable vs. existing tools.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Product ranking list (best-sellers) | Core output of any "spy" tool — users want to know what's winning | Med | Already exists in Hotmart's public ranking pages; scraping needed for Kiwify/Eduzz |
| Multi-platform coverage | Single-platform tools feel limited; users want cross-marketplace signal | High | Each platform = separate scraper or API adapter |
| Niche/category filtering | Without filtering, rankings are noise — users work in specific niches | Low | Config-driven; list of 3–5 niches per user |
| Sales page / copy extraction | Core of product espionage — see what angles they use | Med | HTML scraping + LLM analysis |
| Pricing & offer structure extraction | Price, bonuses, guarantees, upsells — fundamental to competitive modeling | Med | Scraping + structured extraction |
| Ad intelligence (creatives + copy) | Ad spy is a core job-to-be-done for anyone running paid traffic | High | Meta Ad Library (public), TikTok Creative Center, Google Ads Transparency |
| Review aggregation | Customers reveal true pain points in reviews — voice of customer mining | Med | Scraping Hotmart/product pages + external review sites |
| Trend signal for niches | Google Trends is the minimum bar every market researcher checks | Low | Google Trends API (public, rate-limited) |
| Dashboard / visual interface | Raw data without UI means only engineers can use it | High | Web dashboard — table + detail views |
| Automated periodic refresh | Manual refresh defeats the purpose; users expect data to stay current | Med | Scheduler (cron/Celery) for each module |
| Alert on new top product | Proactive notification = core workflow for active marketers | Low | Threshold-based trigger on ranking change |
| Exportable dossier (PDF or structured) | Users need to share/reference findings outside the tool | Med | PDF generation from structured data |

---

## Differentiators

Features that set this product apart. Not expected from generic tools, but high value for infoproduct marketers.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Hourly pain/desire radar | No current tool does real-time hourly VOC (voice of customer) aggregation across Reddit + Quora + YouTube + ad comments | High | Multi-source aggregation + LLM synthesis; genuinely rare |
| Brazilian platform coverage (Hotmart/Kiwify/Eduzz) | SimilarWeb/SEMrush are gringa-first; no English tool covers BR infoproduct market well | High | Requires Portuguese NLP + BR-specific scrapers |
| AI-generated product dossier | Most tools show raw data; generating a structured "why is this winning" narrative via LLM is rare | Med | LLM synthesis over collected data → structured output |
| MEGABRAIN integration | Dossiers feed directly into DNA/agent framework for product modeling — no other tool has this pipeline | Low (integration) / High (upstream) | Unique to this system |
| Ad comment sentiment mining | AdSpy/BigSpy show ad creatives but not the audience comments revealing pain/desire — this adds a layer | High | Requires accessing FB/Instagram comment threads on public ads (TOS-sensitive) |
| Competitor trajectory tracking | Not just what's ranking now, but trend over time — rising vs. declining products | Med | Time-series storage + delta calculation |
| Cross-platform product matching | Same product selling on Hotmart AND ClickBank — deduplicate and merge signals | Med | Fingerprinting / fuzzy matching by product name + author |
| LLM-generated "model this" brief | Given a winning product dossier, generate a "how to model this for your market" action plan | Med | Prompt engineering over dossier data |

---

## Anti-Features

Features to explicitly NOT build in v1.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Full SEO intelligence (keyword rankings, backlinks, domain authority) | This is SEMrush/Ahrefs territory — enormous scope, high infra cost, not the job-to-be-done for infoproduct marketers | Use Google Trends for search signal only; don't build a keyword rank tracker |
| Social media follower/engagement tracking | Influencer analytics is a separate product category (HypeAuditor, etc.) | Capture only ad data from public ad libraries |
| Automated product creation | Out of scope per PROJECT.md; also creates legal/quality liability | Generate dossiers and briefs — creation stays with the user |
| Payment platform integration (selling) | Out of scope per PROJECT.md | N/A |
| Private group / DM monitoring | Technically blocked by TOS (Facebook groups, Discord, etc.) | Use public Reddit threads, public forum posts |
| Real-time (sub-minute) monitoring | Engineering cost is disproportionate; hourly is sufficient for market intelligence | Hourly scheduler is the right granularity |
| Buyer PII collection | Illegal in BR (LGPD) and globally (GDPR) | Only aggregate/public data |
| White-label / multi-tenant SaaS | Premature — adds auth complexity, billing, isolation before product is validated | Single-user tool integrated with MEGABRAIN |
| Mobile app | Added infra/store complexity; target user is desktop power user | Responsive web dashboard is sufficient |

---

## Feature Dependencies

```
Product ranking list (Scanner)
    → Triggers: Alert on new top product
    → Required by: Product dossier generation
    → Required by: Competitor trajectory tracking

Sales page / copy extraction (Espionage)
    → Requires: Product ranking list (to know which products to spy)
    → Required by: AI-generated product dossier

Pricing & offer structure extraction
    → Requires: Product ranking list
    → Required by: AI-generated product dossier

Ad intelligence
    → Requires: Product ranking list (to find ads for specific products)
    → Required by: AI-generated product dossier

Review aggregation
    → Requires: Product ranking list
    → Required by: Hourly pain/desire radar (reviews as a signal source)
    → Required by: AI-generated product dossier

Hourly pain/desire radar (Radar)
    → Requires: Niche/category config
    → Requires: Multi-source connectors (Trends, Reddit, Quora, YouTube)
    → Required by: AI-generated market pain report

Dashboard / visual interface
    → Requires: All data modules to have structured outputs
    → Required by: Exportable dossier (PDF rendering)

AI-generated product dossier
    → Requires: Copy extraction + ad intelligence + review aggregation + pricing
    → Required by: MEGABRAIN integration (DNA/agent pipeline)
    → Required by: LLM "model this" brief
```

---

## MVP Recommendation

The minimum set that delivers the core value proposition ("map of what's selling and why"):

**Prioritize (build in v1):**

1. Product ranking scanner — Hotmart (BR) + ClickBank (international) only. Two platforms is sufficient for validation.
2. Niche/category filtering — essential to make rankings useful.
3. Sales page / copy extraction — the highest-signal espionage output.
4. Pricing & offer structure extraction — fast win, structured scraping.
5. Review aggregation — voice of customer, feeds dossier quality.
6. AI-generated product dossier — the differentiating output; this is the product.
7. Basic web dashboard — table view + dossier detail page.

**Add in v2 (after validation):**

8. Ad intelligence (Meta Ad Library) — high value but TOS-sensitive, needs careful implementation.
9. Hourly pain/desire radar — highest technical complexity; validate demand first.
10. Alert on new top product — depends on scheduler reliability.
11. Competitor trajectory tracking — requires historical data, needs v1 to run for weeks first.

**Defer:**

- Full multi-platform coverage (Kiwify, Eduzz, JVZoo, Udemy, Teachable, Product Hunt, AppSumo): Add after core loop is validated on 2 platforms.
- Cross-platform product matching: Needs multi-platform data first.
- LLM "model this" brief: Nice-to-have enhancement on top of dossier.
- Ad comment sentiment mining: TOS risk + high complexity; defer to v3.

---

## Competitive Positioning Notes

**What existing tools do well that we should not try to match:**

- SimilarWeb: Web traffic estimation at scale (requires massive data infrastructure — petabytes of panel data). Not replicable.
- SEMrush/Ahrefs: Backlink databases + keyword rank tracking (billions of indexed pages). Not replicable.
- AdSpy/BigSpy: Massive indexed ad databases with search/filter across millions of ads. We target specific product ads, not the full ad universe.

**Our defensible angle:**

None of the above tools care about BR infoproduct platforms (Hotmart/Kiwify/Eduzz). None generate structured AI dossiers optimized for product modeling. None integrate into a personal knowledge/agent system like MEGABRAIN. The hourly pain radar with LLM synthesis is also genuinely novel.

---

## Sources

**Confidence: MEDIUM** — Based on training knowledge (stable domain, tools unchanged in core feature sets since 2022–2024). Specific feature lists for SimilarWeb, SEMrush, Ahrefs, AdSpy, BigSpy, SpyFu, iSpionage, Hotmart rankings, and ClickBank marketplace are well-documented in the training corpus. No live verification was possible in this session (WebSearch/Bash denied). Recommend spot-checking:
- https://www.similarweb.com/features/ (traffic intelligence feature list)
- https://www.semrush.com/features/ (competitive research features)
- https://adspy.com (ad intelligence features)
- https://bigspy.com (ad spy features)
- https://www.spyfu.com (PPC/SEO competitor research)
- https://hotmart.com/pt-br/marketplace (BR ranking pages — public)
- https://accounts.clickbank.com/marketplace.htm (ClickBank marketplace ranking — public)
