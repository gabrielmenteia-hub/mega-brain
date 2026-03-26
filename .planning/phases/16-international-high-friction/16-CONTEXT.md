# Phase 16: International High-Friction - Context

**Gathered:** 2026-03-17
**Status:** Ready for planning
**Source:** Derived from codebase analysis (discuss-phase skipped by user)

<domain>
## Phase Boundary

Três plataformas internacionais de alta fricção (bot detection / SPA rendering) integradas:
- **JVZoo** (Incapsula bot detection) — fetch() com headers customizados ou fallback gracioso
- **Gumroad** (SPA/infinite scroll) — Playwright scroll loop via fetch_spa()
- **AppSumo** (SSR-first, Playwright fallback) — PLAYWRIGHT_SEMAPHORE global limita 3 contextos

Criação de playbooks e dossiers está fora do escopo.

</domain>

<decisions>
## Implementation Decisions

### JVZooScanner (SCAN-INTL-03)
- Tentar fetch() com headers anti-bot (User-Agent, Accept-Language, Referer) antes de qualquer fallback
- Se Incapsula bloquear (status 403/503 ou HTML com "incapsula"), retornar `[]` + `log.warning(alert='bot_detected')`
- NÃO usar Playwright para JVZoo — evitar consumo desnecessário de PLAYWRIGHT_SEMAPHORE
- Platform ID: 10 (de `_006_v2_platforms.py`)
- Extrair: title, price, niche/category, url, rank (se disponível)

### GumroadScanner (SCAN-INTL-04)
- Usar `fetch_spa()` do BaseScraper (Playwright + playwright-stealth já integrado)
- Scroll loop: rolar até o fim da página ou até atingir limit de produtos
- URL alvo: página discover do Gumroad filtrada por categoria/niche
- Platform ID: 11
- Extração via `page.query_selector_all()` após scroll completo

### AppSumoScanner (SCAN-INTL-05)
- SSR-first: tentar `fetch()` — AppSumo renderiza HTML estático em muitos endpoints
- Se fetch() retornar HTML sem produtos (JS-only), fallback para `fetch_spa()`
- Respeitar `PLAYWRIGHT_SEMAPHORE` global (limit=3) — CRÍTICO para evitar OOM
- Platform ID: 12
- Extrair: title, price (deal price), category, url

### PLAYWRIGHT_SEMAPHORE Global (nova infraestrutura)
- Adicionar `PLAYWRIGHT_SEMAPHORE = asyncio.Semaphore(3)` em `mis/base_scraper.py`
- Toda chamada a `fetch_spa()` deve adquirir este semaphore antes de lançar Playwright
- Semaphore atual por-domínio (`_SEMAPHORE dict` com `Semaphore(1)`) MANTIDO para controle de rate limiting HTTP
- `PLAYWRIGHT_SEMAPHORE` é ADICIONAL e global — controla concorrência de contextos Playwright

### Estrutura de Testes (padrão Phase 14)
- 6 testes por scanner (padrão estabelecido em Phase 14)
- Fixtures em `mis/tests/fixtures/{platform}/` — HTML/JSON estático para mocking
- Testar: scan normal, fallback bot_detected, fallback marketplace_unavailable, dados vazios, limite de produtos, campos obrigatórios presentes

### Fallback Pattern (padrão das phases anteriores)
- Bot detection / bloqueio → `return []` + `log.warning(alert='bot_detected')`
- Plataforma indisponível → `return []` + `log.warning(alert='marketplace_unavailable')`
- Credenciais faltando → NÃO se aplica (essas plataformas são públicas)

### Config e SCANNER_MAP
- Adicionar `jvzoo`, `gumroad`, `appsumo` ao `SCANNER_MAP` em `mis/scanner_runner.py` (ou equivalente)
- Seguir padrão de `product_hunt.py` e `udemy.py` para estrutura do scanner
- Usar `DOMAIN_DELAYS` dict em `base_scraper.py` para rate limits por domínio

### Claude's Discretion
- Estratégia exata de scroll para Gumroad (por scroll steps ou IntersectionObserver wait)
- Parsing de preços (deal price vs regular price no AppSumo)
- Número exato de itens por scroll page no Gumroad
- Estrutura interna dos fixtures (pode ser HTML real capturado ou sintético)

</decisions>

<specifics>
## Specific Ideas

- PLAYWRIGHT_SEMAPHORE(3) é requisito de sucesso explícito no ROADMAP.md — não é opcional
- JVZoo tem Incapsula CDN — headers como `Accept-Encoding: gzip, deflate, br` e cookie jar podem ajudar a passar
- AppSumo tem estrutura SSR bem documentada — fetch() deve funcionar para a maioria dos endpoints
- Seguir exatamente o mesmo padrão de `product_hunt.py` (Phase 15) como referência de estrutura

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `mis/base_scraper.py` → `fetch()` + `fetch_spa()` + `_SEMAPHORE` per-domain + `DOMAIN_DELAYS`
- `mis/scanners/product_hunt.py` → referência de estrutura para scanner público sem auth
- `mis/scanners/udemy.py` → referência de scanner com fallback de credenciais
- `mis/migrations/_006_v2_platforms.py` → IDs: JVZoo=10, Gumroad=11, AppSumo=12

### Established Patterns
- Semaphore por domínio: `_SEMAPHORE[domain] = asyncio.Semaphore(1)` — manter intacto
- playwright-stealth já aplicado em `fetch_spa()` antes de `page.goto()`
- 6 testes + fixtures em `mis/tests/fixtures/{platform}/`
- `log.warning(alert='...')` para falhas não-excepcionais

### Integration Points
- `mis/scanner_runner.py` (ou SCANNER_MAP): adicionar jvzoo/gumroad/appsumo
- `mis/base_scraper.py`: adicionar `PLAYWRIGHT_SEMAPHORE = asyncio.Semaphore(3)`
- `mis/config.yaml`: adicionar opt-in slugs para cada plataforma (padrão Phase 14)

</code_context>

<deferred>
## Deferred Ideas

- Login autenticado no JVZoo para acessar rankings de afiliados — outro phase
- Webhook notification quando bot_detected persiste por N dias — backlog
- Proxy rotation para contornar Incapsula permanente — backlog

</deferred>

---

*Phase: 16-international-high-friction*
*Context gathered: 2026-03-17 (derived from codebase analysis)*
