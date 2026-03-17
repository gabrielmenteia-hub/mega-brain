# Phase 16: International High-Friction - Research

**Researched:** 2026-03-17
**Domain:** Web scraping com bot detection mitigation + Playwright SPA navigation
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### JVZooScanner (SCAN-INTL-03)
- Tentar fetch() com headers anti-bot (User-Agent, Accept-Language, Referer) antes de qualquer fallback
- Se Incapsula bloquear (status 403/503 ou HTML com "incapsula"), retornar `[]` + `log.warning(alert='bot_detected')`
- NAO usar Playwright para JVZoo — evitar consumo desnecessario de PLAYWRIGHT_SEMAPHORE
- Platform ID: 10 (de `_006_v2_platforms.py`)
- Extrair: title, price, niche/category, url, rank (se disponivel)

#### GumroadScanner (SCAN-INTL-04)
- Usar `fetch_spa()` do BaseScraper (Playwright + playwright-stealth ja integrado)
- Scroll loop: rolar ate o fim da pagina ou ate atingir limit de produtos
- URL alvo: pagina discover do Gumroad filtrada por categoria/niche
- Platform ID: 11
- Extracao via `page.query_selector_all()` apos scroll completo

#### AppSumoScanner (SCAN-INTL-05)
- SSR-first: tentar `fetch()` — AppSumo renderiza HTML estatico em muitos endpoints
- Se fetch() retornar HTML sem produtos (JS-only), fallback para `fetch_spa()`
- Respeitar `PLAYWRIGHT_SEMAPHORE` global (limit=3) — CRITICO para evitar OOM
- Platform ID: 12
- Extrair: title, price (deal price), category, url

#### PLAYWRIGHT_SEMAPHORE Global (nova infraestrutura)
- Adicionar `PLAYWRIGHT_SEMAPHORE = asyncio.Semaphore(3)` em `mis/base_scraper.py`
- Toda chamada a `fetch_spa()` deve adquirir este semaphore antes de lancar Playwright
- Semaphore atual por-dominio (`_SEMAPHORE dict` com `Semaphore(1)`) MANTIDO para controle de rate limiting HTTP
- `PLAYWRIGHT_SEMAPHORE` e ADICIONAL e global — controla concorrencia de contextos Playwright

#### Estrutura de Testes (padrao Phase 14)
- 6 testes por scanner (padrao estabelecido em Phase 14)
- Fixtures em `mis/tests/fixtures/{platform}/` — HTML/JSON estatico para mocking
- Testar: scan normal, fallback bot_detected, fallback marketplace_unavailable, dados vazios, limite de produtos, campos obrigatorios presentes

#### Fallback Pattern (padrao das phases anteriores)
- Bot detection / bloqueio -> `return []` + `log.warning(alert='bot_detected')`
- Plataforma indisponivel -> `return []` + `log.warning(alert='marketplace_unavailable')`
- Credenciais faltando -> NAO se aplica (essas plataformas sao publicas)

#### Config e SCANNER_MAP
- Adicionar `jvzoo`, `gumroad`, `appsumo` ao `SCANNER_MAP` em `mis/scanner.py` (funcao `run_all_scanners`)
- Seguir padrao de `product_hunt.py` e `udemy.py` para estrutura do scanner
- Usar `DOMAIN_DELAYS` dict em `base_scraper.py` para rate limits por dominio

### Claude's Discretion
- Estrategia exata de scroll para Gumroad (por scroll steps ou IntersectionObserver wait)
- Parsing de precos (deal price vs regular price no AppSumo)
- Numero exato de itens por scroll page no Gumroad
- Estrutura interna dos fixtures (pode ser HTML real capturado ou sintetico)

### Deferred Ideas (OUT OF SCOPE)
- Login autenticado no JVZoo para acessar rankings de afiliados — outro phase
- Webhook notification quando bot_detected persiste por N dias — backlog
- Proxy rotation para contornar Incapsula permanente — backlog
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SCAN-INTL-03 | `JVZooScanner` varre marketplace JVZoo por nicho (com contorno Incapsula ou fallback SSR) | JVZooMarket.com confirmado SSR; URL pattern verificada: `/listings?category={id}&start={offset}`; deteccao Incapsula via status 403/503 ou corpo "incapsula" |
| SCAN-INTL-04 | `GumroadScanner` varre `gumroad.com/discover` por nicho ordenado por popular | Discover page confirmada SPA com scroll infinito; `fetch_spa()` + loop de scroll com `page.evaluate` e `page.query_selector_all()` e o padrao correto |
| SCAN-INTL-05 | `AppSumoScanner` varre `appsumo.com/products` por nicho (SSR-first, Playwright fallback) | `/browse/` confirmado SSR com JSON embutido em `<script>`; URL pattern categoria: `/software/{category}/`; PLAYWRIGHT_SEMAPHORE(3) critico para evitar OOM |
</phase_requirements>

---

## Summary

Phase 16 integra tres plataformas internacionais de alta friccao — JVZoo, Gumroad e AppSumo — seguindo exatamente o padrao de scanner estabelecido nas Phases 14 e 15. A principal diferenca tecnica em relacao as phases anteriores e a necessidade de PLAYWRIGHT_SEMAPHORE global (nova infraestrutura em `base_scraper.py`) e estrategias de mitigacao de bot detection (JVZoo/Incapsula).

O codebase ja fornece toda a infraestrutura necessaria: `BaseScraper.fetch()` com headers anti-bot via `fake_useragent`, `BaseScraper.fetch_spa()` com `playwright-stealth` integrado, pattern de semaphore por dominio, e o padrao de 6 testes + fixtures estabelecido nas phases anteriores. O trabalho desta phase e essencialmente "aplicar o padrao ja conhecido" com as particularidades de cada plataforma.

A maior incerteza tecnica e o JVZoo — a investigacao confirmou que `jvzoomarket.com` e SSR (nao requer Playwright), mas o Incapsula pode bloquear mesmo com headers realistas. A estrategia correta e: tentar fetch() com headers completos, detectar bloqueio pelo status HTTP ou pelo corpo da resposta, e degradar graciosamente com `bot_detected`.

**Primary recommendation:** Implementar em dois planos — 16-01 (JVZooScanner isolado, maior incerteza de bot detection) e 16-02 (GumroadScanner + AppSumoScanner + PLAYWRIGHT_SEMAPHORE + wiring).

---

## Standard Stack

### Core (ja instalado no projeto)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| playwright | >=1.40 | Browser automation para SPAs (Gumroad) | Ja em uso no BaseScraper.fetch_spa() |
| playwright-stealth | >=1.0 | Supressao de fingerprints de automacao | Ja integrado no fetch_spa() |
| httpx | >=0.27 | HTTP async para SSR pages (JVZoo, AppSumo) | Ja em uso no BaseScraper.fetch() |
| fake-useragent | >=1.4 | Rotacao de User-Agent realistas | Ja em uso no _build_headers() |
| respx | >=0.21 | Mock de chamadas HTTP nos testes | Ja em uso nos testes de Phase 15 |
| structlog | >=23.x | Logging estruturado JSON | Ja configurado em base_scraper.py |
| pytest-asyncio | >=0.23 | Suporte async nos testes | Ja em uso em toda a suite |

### Nenhuma dependencia nova necessaria
Todas as dependencias desta phase ja estao instaladas. O unico codigo novo de infraestrutura e o `PLAYWRIGHT_SEMAPHORE` em `base_scraper.py`.

---

## Architecture Patterns

### Estrutura de Arquivos desta Phase
```
mis/
├── scanners/
│   ├── jvzoo.py          # NOVO — JVZooScanner (fetch() only, sem Playwright)
│   ├── gumroad.py        # NOVO — GumroadScanner (fetch_spa() + scroll loop)
│   └── appsumo.py        # NOVO — AppSumoScanner (SSR-first, fetch_spa() fallback)
├── tests/
│   ├── test_jvzoo_scanner.py    # NOVO — 6 testes
│   ├── test_gumroad_scanner.py  # NOVO — 6 testes
│   ├── test_appsumo_scanner.py  # NOVO — 6 testes
│   └── fixtures/
│       ├── jvzoo/
│       │   └── listings_category1.html  # HTML sintetico de produtos JVZoo
│       ├── gumroad/
│       │   └── discover_marketing.html  # HTML pos-scroll Gumroad
│       └── appsumo/
│           └── browse_software.html     # HTML SSR AppSumo com JSON embutido
└── base_scraper.py       # MODIFICADO — adicionar PLAYWRIGHT_SEMAPHORE
```

### Pattern 1: PLAYWRIGHT_SEMAPHORE em base_scraper.py
**O que e:** Semaphore global que limita a 3 o numero de contextos Playwright simultaneos.
**Quando usar:** Toda chamada a `fetch_spa()` deve adquirir este semaphore.
**Por que 3:** Cada contexto Playwright usa ~50-100MB RAM. Com 5 nichos em paralelo, sem limite ocorreria OOM em maquinas com 8GB RAM.

```python
# Em mis/base_scraper.py — adicionar apos _SEMAPHORE dict
PLAYWRIGHT_SEMAPHORE = asyncio.Semaphore(3)

# Em fetch_spa() — adquirir ANTES de async_playwright()
async def fetch_spa(self, url: str) -> str:
    domain = httpx.URL(url).host
    delay = DOMAIN_DELAYS.get(domain, DEFAULT_DELAY)

    async with self._get_semaphore(domain):       # semaphore por dominio (rate limit)
        async with PLAYWRIGHT_SEMAPHORE:           # semaphore global (OOM prevention)
            async with async_playwright() as pw:
                # ... resto igual ao atual
```

**CRITICO:** O semaphore por dominio (`_SEMAPHORE`) e mantido intacto para rate limiting HTTP.
O `PLAYWRIGHT_SEMAPHORE` e adicional e controla apenas concorrencia de instancias Playwright.

### Pattern 2: JVZooScanner — fetch() com deteccao Incapsula
**O que e:** Scanner SSR-only que usa `self.fetch()` herdado e detecta bloqueio Incapsula.
**URL verificada:** `https://www.jvzoomarket.com/listings?category={category_id}&start={offset}&sort=sales`
**Deteccao de bloqueio:**

```python
async def scan_niche(self, niche_slug, platform_slug, niche_id=0):
    url = f"https://www.jvzoomarket.com/listings?category={platform_slug}&sort=sales"
    try:
        html = await self.fetch(url)
    except ScraperError as exc:
        log.warning("jvzoo_scanner.bot_detected", alert="bot_detected", ...)
        return []

    # Detectar bloqueio Incapsula no corpo HTML (mesmo com status 200)
    if "incapsula" in html.lower() or "incident id" in html.lower():
        log.warning("jvzoo_scanner.bot_detected", alert="bot_detected", ...)
        return []

    # Parsing HTML com BeautifulSoup ou lxml
    ...
```

**Selectors verificados em jvzoomarket.com:**
- Produto URL: `a[href*="/productlibrary/marketframe?pid="]`
- Titulo: texto do link de produto
- Preco: texto com padrao `$XX.XX`
- Rank: posicao na lista (1-based), ou "X Sold" para rank por vendas

### Pattern 3: GumroadScanner — fetch_spa() com scroll loop
**O que e:** Scanner SPA que usa Playwright para navegar o discover page com scroll infinito.
**URL base verificada:** `https://gumroad.com/discover`
**Parametros de categoria:** `?sort=most_reviewed&tags={tag}` ou `?sort=popular`

```python
# GumroadScanner NAO usa self.fetch_spa() diretamente —
# precisa de acesso ao `page` object para scroll loop.
# Deve usar fetch_spa() como base ou implementar Playwright diretamente via self._base

async def _scan_with_scroll(self, url: str, limit: int = 50) -> str:
    """Navega URL via Playwright com scroll loop ate {limit} produtos ou fim da pagina."""
    async with PLAYWRIGHT_SEMAPHORE:  # importado de mis.base_scraper
        async with async_playwright() as pw:
            browser = await pw.chromium.launch()
            page = await browser.new_page()
            await _PlaywrightStealth().apply_stealth_async(page)
            await page.goto(url, wait_until="networkidle")

            # Scroll loop — estrategia por steps fixos
            prev_height = 0
            for _ in range(20):  # max 20 scrolls
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(1500)  # aguarda carregamento
                new_height = await page.evaluate("document.body.scrollHeight")
                if new_height == prev_height:
                    break  # fim da pagina
                prev_height = new_height

            content = await page.content()
            await browser.close()
    return content
```

**Seletores Gumroad Discover (baseado em estrutura conhecida):**
- Cards de produto: `[data-component-name="DiscoverProduct"]` ou similar
- Titulo: `h3`, `[data-testid="product-name"]`
- Preco: elemento com texto de preco (gratis ou valor)
- URL: `a[href*="gumroad.com/l/"]` ou `a[href*=".gumroad.com/l/"]`

**NOTA:** Os seletores exatos do Gumroad Discover devem ser inspecionados no HTML real capturado. Usar fixtures HTML sinteticas que reflitam a estrutura atual.

### Pattern 4: AppSumoScanner — SSR-first com fallback Playwright
**O que e:** Scanner que tenta SSR primeiro (mais rapido, sem Playwright) e faz fallback.
**URL verificada:** `https://appsumo.com/browse/` com categorias como `/software/marketing-sales/`
**Estrutura SSR confirmada:** JSON embutido em `<script>` tag, HTML com produto cards semanticos.

```python
async def scan_niche(self, niche_slug, platform_slug, niche_id=0):
    url = f"https://appsumo.com/browse/software/{platform_slug}/"
    try:
        html = await self.fetch(url)
        products = self._parse_html(html)
        if products:
            return products
        # HTML recebido mas sem produtos — possivel JS-only rendering
        log.info("appsumo_scanner.ssr_empty_fallback", niche=niche_slug)
    except ScraperError:
        log.info("appsumo_scanner.fetch_failed_fallback", niche=niche_slug)

    # Fallback: Playwright
    try:
        html = await self.fetch_spa(url)
        return self._parse_html(html)
    except Exception as exc:
        log.warning("appsumo_scanner.marketplace_unavailable",
                    alert="marketplace_unavailable", ...)
        return []
```

**Parsing AppSumo:**
- JSON embutido: `<script>` com dados de produto (JSON-LD ou window.__NEXT_DATA__)
- HTML fallback: `a[href*="/products/"]` para links de produto
- Preco: deal price exibido como `$XX/lifetime` ou `$XX`
- Categoria: path-based no URL ou metadata

### Anti-Patterns a Evitar
- **Usar Playwright para JVZoo:** Desperdicaria PLAYWRIGHT_SEMAPHORE slots sem necessidade. JVZoo e SSR, `fetch()` e suficiente.
- **Scroll loop sem limite:** Sem `max_scrolls`, pode rodar indefinidamente em paginas com muitos produtos.
- **Abrir async_playwright() sem PLAYWRIGHT_SEMAPHORE:** Causa OOM com 5 nichos em paralelo.
- **Raise excecao em vez de retornar []:** Quebraria `run_all_scanners()` que usa `return_exceptions=True`. Sempre retornar `[]` + log.warning.
- **Nao adquirir PLAYWRIGHT_SEMAPHORE antes do semaphore por dominio:** A ordem deve ser: dominio semaphore DENTRO do PLAYWRIGHT_SEMAPHORE para evitar deadlock.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| User-Agent rotation | Lista manual de UAs hardcoded | `fake_useragent.UserAgent()` (ja em _build_headers()) | fake_useragent tem banco de dados atualizado de UAs reais |
| Playwright stealth | CSS/JS customizado para esconder automacao | `playwright-stealth` (ja em fetch_spa()) | Cobre dezenas de fingerprints que seriam esquecidos manualmente |
| HTTP retry com backoff | Loop manual try/except | `tenacity` com `@retry` (ja em fetch()) | Implementa jitter, backoff exponencial, e limite de tentativas corretamente |
| Playwright concorrencia | Thread pool ou semaforo caseiro | `asyncio.Semaphore(3)` em nivel de modulo | Padrao asyncio nativo, sem overhead de threads |
| HTML parsing | Regex em HTML | `BeautifulSoup` ou `lxml` (ja dependencias do projeto) | HTML e irregular; regex falha em edge cases |

**Key insight:** O codebase ja tem toda a infraestrutura anti-bot. O trabalho e configurar e usar corretamente — nao reinventar.

---

## Common Pitfalls

### Pitfall 1: Incapsula retorna 200 com pagina de bloqueio
**O que da errado:** Incapsula frequentemente retorna HTTP 200 com uma pagina HTML de desafio, nao 403. O scanner parseia HTML vazio e retorna `[]` sem logar `bot_detected`.
**Por que acontece:** Bot detection de geracao atual usa "soft blocks" — retorna pagina aparentemente normal para nao revelar que o bot foi detectado.
**Como evitar:** Verificar `"incapsula" in html.lower()` E `"incident id" in html.lower()` alem do status HTTP.
**Warning signs:** Scanner retorna `[]` consistentemente sem `bot_detected` no log.

### Pitfall 2: Gumroad scroll loop nao detecta fim de pagina corretamente
**O que da errado:** `document.body.scrollHeight` nao muda entre scrolls mas produtos continuam carregando assincronamente. Ou: pagina e infinita mas scanner para cedo.
**Por que acontece:** SPAs com virtual scroll ou lazy loading tem comportamento nao-linear de altura.
**Como evitar:** Combinar verificacao de altura com contagem de elementos (`page.query_selector_all()`). Se contagem nao aumentou em 2 scrolls consecutivos, parar.
**Warning signs:** Scanner retorna sempre o mesmo numero de produtos (ex: sempre 20 — apenas o primeiro batch).

### Pitfall 3: PLAYWRIGHT_SEMAPHORE adquirido dentro do semaphore por dominio
**O que da errado:** Deadlock potencial. Se todos os 3 slots do PLAYWRIGHT_SEMAPHORE estao ocupados e cada coroutine esta esperando pelo semaphore de dominio que esta bloqueado por outra coroutine esperando PLAYWRIGHT_SEMAPHORE.
**Por que acontece:** A ordem de aquisicao de locks importa para prevenir deadlock.
**Como evitar:** Adquirir PLAYWRIGHT_SEMAPHORE ANTES do semaphore por dominio. No fetch_spa() modificado: `async with PLAYWRIGHT_SEMAPHORE: async with self._get_semaphore(domain):`.
**Warning signs:** Testes travando sem timeout em concorrencia.

### Pitfall 4: AppSumo __NEXT_DATA__ vs JSON-LD
**O que da errado:** AppSumo usa Next.js. O JSON de produtos pode estar em `window.__NEXT_DATA__` (estrutura Next.js) ou em JSON-LD. Essas estruturas sao diferentes.
**Por que acontece:** AppSumo SSR com Next.js embute dados em `<script id="__NEXT_DATA__" type="application/json">`.
**Como evitar:** Tentar `json.loads(soup.find("script", id="__NEXT_DATA__").string)` primeiro. Fallback para JSON-LD (`script[type="application/ld+json"]`). Fallback final para CSS selectors em HTML.
**Warning signs:** `json.JSONDecodeError` ao tentar parsear `<script>` tag errada.

### Pitfall 5: JVZoo category IDs hardcoded vs slugs
**O que da errado:** JVZooMarket usa IDs numericos de categoria (ex: `?category=84` para "Affiliate Marketing"). Usar slugs textuais nao funciona.
**Por que acontece:** URL verificada: `https://www.jvzoomarket.com/productlibrary/listings?category=84`
**Como evitar:** O `platform_slug` no config.yaml deve conter o ID numerico da categoria JVZoo (ex: `jvzoo: "84"` para marketing). Documentar o mapeamento nos comentarios do config.

---

## Code Examples

### Modificacao em base_scraper.py — PLAYWRIGHT_SEMAPHORE
```python
# Adicionar apos _SEMAPHORE dict (linha ~48 do base_scraper.py atual)
PLAYWRIGHT_SEMAPHORE = asyncio.Semaphore(3)

# fetch_spa() modificado — ordem de aquisicao: PLAYWRIGHT_SEMAPHORE -> dominio
async def fetch_spa(self, url: str) -> str:
    domain = httpx.URL(url).host
    delay = DOMAIN_DELAYS.get(domain, DEFAULT_DELAY)

    async with PLAYWRIGHT_SEMAPHORE:                  # NOVO: global Playwright limit
        async with self._get_semaphore(domain):       # existente: per-domain rate limit
            async with async_playwright() as pw:
                selected = self._select_proxy()
                browser = await pw.chromium.launch(
                    proxy={"server": selected} if selected else None
                )
                try:
                    page = await browser.new_page()
                    await _PlaywrightStealth().apply_stealth_async(page)
                    await page.goto(url, wait_until="networkidle")
                    content = await page.content()
                finally:
                    await browser.close()
        await asyncio.sleep(delay)
        return content
```

### Estrutura do JVZooScanner
```python
# Source: padrao product_hunt.py + udemy.py (Phases 15)
from mis.scanner import PlatformScanner, Product
from mis.platform_ids import JVZOO_PLATFORM_ID
from mis.exceptions import ScraperError

JVZOO_BASE_URL = "https://www.jvzoomarket.com"

class JVZooScanner(PlatformScanner):
    async def scan_niche(self, niche_slug, platform_slug, niche_id=0):
        url = f"{JVZOO_BASE_URL}/listings?category={platform_slug}&sort=sales"
        try:
            html = await self.fetch(url)
        except ScraperError:
            log.warning("jvzoo_scanner.bot_detected", alert="bot_detected",
                        niche=niche_slug)
            return []

        if "incapsula" in html.lower() or "incident id" in html.lower():
            log.warning("jvzoo_scanner.bot_detected", alert="bot_detected",
                        niche=niche_slug, reason="incapsula_challenge_page")
            return []

        return self._parse_listings(html, niche_id)
```

### Fixture HTML sintetica para JVZoo (mis/tests/fixtures/jvzoo/listings_category84.html)
```html
<!-- Sintetico — reflete estrutura verificada em jvzoomarket.com -->
<html>
<body>
  <div class="product-listing">
    <a href="/productlibrary/marketframe?pid=12345">Email Marketing Pro 2026</a>
    <span class="price">$47.00</span>
    <span class="sales">280 Sold</span>
  </div>
  <div class="product-listing">
    <a href="/productlibrary/marketframe?pid=67890">Traffic Dominator Suite</a>
    <span class="price">$97.00</span>
    <span class="sales">142 Sold</span>
  </div>
</body>
</html>
```

### Estrutura de testes (6 testes por scanner — padrao Phase 15)
```python
# Padrao replicado de test_udemy_scanner.py e test_product_hunt_scanner.py
# Testes 1-2 (RED ate implementacao): test_happy_path, test_field_types
# Testes 3-4 (GREEN desde Wave 0): test_bot_detected, test_empty_results
# Testes 5-6 (GREEN): test_upsert_no_duplicates, test_is_stale

# Para JVZoo — test_bot_detected usa respx mock:
respx.get("https://www.jvzoomarket.com/listings").mock(
    return_value=Response(403)
)
# OU respx retorna HTML com "incapsula" no corpo

# Para Gumroad/AppSumo — sem respx (usam Playwright), mock via monkeypatch
# em fetch_spa() ou fixture HTML diretamente em _parse_html()
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Semaphore por dominio para Playwright | PLAYWRIGHT_SEMAPHORE global adicional | Esta phase | Previne OOM com multiplos nichos em paralelo |
| fetch_spa() simples (goto + content) | fetch_spa() com scroll loop (para Gumroad) | Esta phase | Necessario para paginas com infinite scroll |
| SSR-only | SSR-first com Playwright fallback (AppSumo) | Esta phase | Mais eficiente — evita Playwright quando SSR funciona |

**Padrao consolidado de scanner neste codebase:**
- `PlatformScanner` via composicao com `BaseScraper` (nao heranca direta)
- `self.fetch()` delega para `self._base.fetch()` com retry + rate limit
- `self.fetch_spa()` delega para `self._base.fetch_spa()` com stealth
- Sempre retornar `[]` com `log.warning(alert='...')` em vez de raise
- 6 testes + fixtures estaticas em `mis/tests/fixtures/{platform}/`
- Platform ID importado de `mis.platform_ids`

---

## Open Questions

1. **Seletores CSS exatos do Gumroad Discover**
   - O que sabemos: pagina e SPA com scroll infinito; URL base `gumroad.com/discover`; parametros `?sort=most_reviewed&tags={tag}` confirmados
   - O que e incerto: seletores CSS exatos dos cards de produto (classes podem mudar com deploys)
   - Recomendacao: criar fixture HTML sintetica conservadora com seletores simples (`[data-component-name]` ou `h3 + preco + a`); ajustar se testes quebrarem

2. **Mapeamento JVZoo category IDs por nicho**
   - O que sabemos: URL usa `?category=84` (numerico); categoria 84 = "Affiliate Marketing / E-Commerce"
   - O que e incerto: IDs exatos para nichos "emagrecimento" e "financas-pessoais" (JVZoo e focado em MMO/software, pode nao ter equivalentes)
   - Recomendacao: usar categoria generica `84` (Affiliate Marketing) para todos os nichos como slug padrao; documentar limitacao no config.yaml

3. **AppSumo __NEXT_DATA__ vs JSON-LD vs CSS selectors**
   - O que sabemos: pagina `/browse/` e SSR com JSON embutido em `<script>`; estrutura Next.js confirmada
   - O que e incerto: se o JSON util esta em `__NEXT_DATA__` (Next.js) ou em JSON-LD separado
   - Recomendacao: tentar `__NEXT_DATA__` primeiro (mais estruturado), fallback para CSS selectors em HTML diretamente

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest + pytest-asyncio |
| Config file | `pytest.ini` ou `pyproject.toml` (ja configurado no projeto) |
| Quick run command | `pytest mis/tests/test_jvzoo_scanner.py mis/tests/test_gumroad_scanner.py mis/tests/test_appsumo_scanner.py -x` |
| Full suite command | `pytest mis/tests/ -x` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SCAN-INTL-03 | JVZooScanner retorna produtos ou bot_detected | unit | `pytest mis/tests/test_jvzoo_scanner.py -x` | Wave 0 |
| SCAN-INTL-03 | JVZoo HTTP 403 -> alert='bot_detected' | unit | `pytest mis/tests/test_jvzoo_scanner.py::test_bot_detected -x` | Wave 0 |
| SCAN-INTL-03 | JVZoo corpo "incapsula" -> alert='bot_detected' | unit | `pytest mis/tests/test_jvzoo_scanner.py::test_incapsula_body -x` | Wave 0 |
| SCAN-INTL-04 | GumroadScanner retorna produtos via scroll | unit | `pytest mis/tests/test_gumroad_scanner.py -x` | Wave 0 |
| SCAN-INTL-04 | Gumroad empty page -> result == [] | unit | `pytest mis/tests/test_gumroad_scanner.py::test_empty_results -x` | Wave 0 |
| SCAN-INTL-05 | AppSumoScanner SSR-first retorna produtos | unit | `pytest mis/tests/test_appsumo_scanner.py -x` | Wave 0 |
| SCAN-INTL-05 | AppSumo OOM prevention: PLAYWRIGHT_SEMAPHORE(3) | unit | `pytest mis/tests/test_base_scraper_semaphore.py -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest mis/tests/test_jvzoo_scanner.py mis/tests/test_gumroad_scanner.py mis/tests/test_appsumo_scanner.py -x`
- **Per wave merge:** `pytest mis/tests/ -x`
- **Phase gate:** Full suite green antes de `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `mis/tests/test_jvzoo_scanner.py` — 6 testes SCAN-INTL-03 (RED/GREEN mix)
- [ ] `mis/tests/test_gumroad_scanner.py` — 6 testes SCAN-INTL-04 (RED/GREEN mix)
- [ ] `mis/tests/test_appsumo_scanner.py` — 6 testes SCAN-INTL-05 (RED/GREEN mix)
- [ ] `mis/tests/fixtures/jvzoo/listings_category84.html` — fixture HTML sintetica JVZoo
- [ ] `mis/tests/fixtures/gumroad/discover_marketing.html` — fixture HTML sintetica Gumroad pos-scroll
- [ ] `mis/tests/fixtures/appsumo/browse_software.html` — fixture HTML SSR AppSumo com JSON embutido

---

## Sources

### Primary (HIGH confidence)
- Codebase direto: `mis/base_scraper.py` — fetch(), fetch_spa(), _SEMAPHORE, DOMAIN_DELAYS, _build_headers()
- Codebase direto: `mis/scanners/product_hunt.py` — estrutura canonica de scanner a ser replicada
- Codebase direto: `mis/scanners/udemy.py` — padrao de fallback e log.warning(alert=...)
- Codebase direto: `mis/scanner.py` — PlatformScanner ABC, Product dataclass, SCANNER_MAP, run_all_scanners()
- Codebase direto: `mis/platform_ids.py` — JVZOO=10, GUMROAD=11, APPSUMO=12 confirmados
- Codebase direto: `mis/tests/test_product_hunt_scanner.py` + `test_udemy_scanner.py` — padrao de 6 testes
- WebFetch verificado: `jvzoomarket.com/listings?category=1` — URL pattern SSR confirmada, selectors verificados
- WebFetch verificado: `appsumo.com/browse/` — SSR confirmado com JSON embutido em script tag, estrutura Next.js

### Secondary (MEDIUM confidence)
- WebSearch verificado: Playwright asyncio.Semaphore(3) padrao para OOM prevention — multiplas fontes tecnicas concordam com limite 3-5 contextos simultaneos
- WebSearch verificado: Incapsula deteccao via status 403/503 OU corpo HTML com "incapsula"/"incident id"
- WebSearch verificado: Gumroad discover URL `gumroad.com/discover` com parametros `sort=` e `tags=`

### Tertiary (LOW confidence)
- Seletores CSS exatos do Gumroad Discover — nao verificados diretamente (SPA nao renderizou via WebFetch)
- Mapeamento exato de category IDs JVZoo para nichos BR (marketing, emagrecimento, financas)
- Estrutura exata do `__NEXT_DATA__` do AppSumo (confirmado Next.js SSR, estrutura interna nao inspecionada)

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — todo o stack ja esta no codebase e funcionando
- Architecture patterns: HIGH — padrao de scanner estabelecido e replicavel; PLAYWRIGHT_SEMAPHORE e padrao asyncio canonico
- Pitfalls: HIGH — Incapsula soft-block e OOM sem semaphore sao pitfalls documentados e verificados
- Seletores CSS Gumroad: LOW — SPA nao inspecionavel via WebFetch; fixtures devem ser conservadoras

**Research date:** 2026-03-17
**Valid until:** 2026-04-17 (plataformas SSR estaveis; Gumroad SPA pode mudar seletores mais rapido)
