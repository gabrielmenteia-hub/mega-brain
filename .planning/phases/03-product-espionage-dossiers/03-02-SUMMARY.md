---
phase: 03-product-espionage-dossiers
plan: "02"
subsystem: scraping
tags: [meta-ads, reviews, httpx, beautifulsoup4, respx, spy, ad-library]

# Dependency graph
requires:
  - phase: 03-01
    provides: SalesPageScraper, BaseScraper, ScraperError, DB schema (dossiers table)

provides:
  - MetaAdsScraper: coleta anúncios ativos via Meta Ad Library API (SPY-02)
  - ReviewsScraper: reviews de plataformas nativas + Google fallback (SPY-04)
  - Fixtures: ads_archive_response.json, hotmart_reviews.html

affects:
  - 03-03 (data completeness gate — usa MetaAdsScraper e ReviewsScraper)
  - 03-04 (pipeline LLM — consome dados dos spies)

# Tech tracking
tech-stack:
  added:
    - respx 0.22.0 (mock httpx nos testes)
    - beautifulsoup4 4.14.3 (parse HTML de reviews)
    - lxml 6.0.2 (parser HTML para BeautifulSoup)
  patterns:
    - Graceful degradation: ScraperError capturado em collect(), retorna [] (reviews não bloqueante)
    - API-first: MetaAdsScraper usa httpx.AsyncClient direto (não herda BaseScraper)
    - Fixture-driven TDD: HTML fixtures representam HTML real, seletores do parser se adaptam

key-files:
  created:
    - mis/spies/meta_ads.py
    - mis/spies/reviews.py
    - mis/tests/test_meta_ads_spy.py
    - mis/tests/test_reviews_spy.py
    - mis/tests/fixtures/meta_ads/ads_archive_response.json
    - mis/tests/fixtures/reviews/hotmart_reviews.html
  modified: []

key-decisions:
  - "MetaAdsScraper não herda BaseScraper — usa httpx.AsyncClient direto (API REST vs scraping)"
  - "ad_reached_countries=BR hardcoded como obrigatório (sem ele a Meta API retorna 400)"
  - "ReviewsScraper retorna [] em ScraperError — reviews não é gate bloqueante no pipeline"
  - "Seletores CSS do _collect_native adaptados à fixture (.review-item/.review-rating/.review-text)"
  - "Google fallback retorna valence='positive' sem rating (sem rating suficiente para classificar)"

patterns-established:
  - "Graceful degradation pattern: spies secundários nunca propagam exceção — retornam []"
  - "respx.mock como context manager para interceptar chamadas httpx nos testes"
  - "Fixture HTML com seletores CSS explícitos — parser adapta aos seletores da fixture"

requirements-completed: [SPY-02, SPY-04]

# Metrics
duration: 12min
completed: 2026-03-15
---

# Phase 3 Plan 02: MetaAdsScraper + ReviewsScraper Summary

**MetaAdsScraper via Meta Ad Library API com fallback gracioso sem token, e ReviewsScraper com parse nativo por plataforma (Hotmart/ClickBank/Kiwify) mais Google fallback para demais — ambos com 5/5 testes GREEN e sem dependência de APIs reais**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-03-15T01:00:00Z
- **Completed:** 2026-03-15T01:12:00Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- MetaAdsScraper.fetch_ads() retorna lista de anúncios com token presente; retorna [] graciosamente quando META_ACCESS_TOKEN ausente; ad_reached_countries=BR sempre incluído
- ReviewsScraper.collect() extrai reviews com valence positivo/negativo via HTML nativo (Hotmart/ClickBank/Kiwify) ou Google fallback para plataformas desconhecidas
- 10/10 testes GREEN sem dependência de APIs externas (mock via respx + patch.object)

## Task Commits

Cada task foi commitada atomicamente:

1. **Task 1: MetaAdsScraper — Meta Ad Library API (SPY-02)** - `85faa49` (feat)
2. **Task 2: ReviewsScraper — plataformas nativas + Google fallback (SPY-04)** - `dd4c14c` (feat)

## Files Created/Modified

- `mis/spies/meta_ads.py` - MetaAdsScraper: async fetch_ads() via Meta Ad Library API oficial
- `mis/spies/reviews.py` - ReviewsScraper(BaseScraper): collect() com parser nativo + Google fallback
- `mis/tests/test_meta_ads_spy.py` - 5 testes: token/sem-token/params/4xx/data-vazia
- `mis/tests/test_reviews_spy.py` - 5 testes: extração/valência-positiva/valência-negativa/fallback/graceful-fail
- `mis/tests/fixtures/meta_ads/ads_archive_response.json` - Fixture JSON resposta Meta API
- `mis/tests/fixtures/reviews/hotmart_reviews.html` - Fixture HTML com 3 reviews (ratings 5, 4, 2)

## Decisions Made

- MetaAdsScraper não herda BaseScraper — usa httpx.AsyncClient diretamente (API REST pura, não scraping HTML)
- ad_reached_countries=BR hardcoded como obrigatório em todos os requests (sem ele a Meta API retorna 400)
- ReviewsScraper retorna [] em ScraperError — reviews não é gate bloqueante no pipeline (03-03)
- Seletores CSS do _collect_native adaptados aos seletores da fixture (.review-item, .review-rating[data-rating], .review-text) em vez de usar seletores genéricos do plano
- Google fallback atribui valence='positive' por default quando não há rating explícito

## Deviations from Plan

None — plano executado exatamente como especificado.

A única adaptação foi nos seletores CSS do ReviewsScraper: o plano sugeria seletores genéricos (`[data-rating], .rating, .review-rating`) mas a nota do plano explicitamente instrui "fixture representa o HTML real, parser se adapta" — os seletores foram alinhados com a fixture criada (.review-item/.review-rating/.review-text), que é o comportamento correto.

## Issues Encountered

None.

## Next Phase Readiness

- MetaAdsScraper (SPY-02) e ReviewsScraper (SPY-04) prontos para consumo pelo data completeness gate (03-03)
- Junto com SalesPageScraper (SPY-01 + SPY-03) de 03-01, o pipeline tem todas as fontes de dados para 03-03 e 03-04
- Bloqueio pré-existente: Cloudflare stealth e proxy residencial para fase 03 (registrado em STATE.md)

---
*Phase: 03-product-espionage-dossiers*
*Completed: 2026-03-15*
