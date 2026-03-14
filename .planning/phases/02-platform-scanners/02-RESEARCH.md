# Phase 2: Platform Scanners - Research

**Researched:** 2026-03-14
**Domain:** Web scraping (Playwright XHR interception + httpx), ClickBank REST API, APScheduler cron jobs, SQLite upsert, schema drift detection
**Confidence:** HIGH (architecture, patterns, testing) / MEDIUM (Hotmart XHR endpoint shape — requires live inspection)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Cobertura de Plataformas:**
- Plataformas: Hotmart (BR, SPA), ClickBank (gringa, API oficial) e Kiwify (BR, SSR)
- Kiwify: httpx suficiente (SSR, sem anti-bot significativo) — implementar primeiro para validar o PlatformScanner pattern
- ClickBank: usar API oficial com gravity score — mais estável que scraping HTML
- Hotmart: scraping público apenas, sem autenticação, sem credenciais de conta
- Jobs separados por plataforma no APScheduler — falha de uma não afeta as demais

**Dados Coletados por Produto:**
- Campos obrigatórios: `external_id`, `title`, `url`, `platform_id`, `niche_id`, `rank`
- Campos adicionais (todos nullable): `price` (float), `commission_pct` (float), `rating` (float), `thumbnail_url` (str)
- Thumbnail: salvar só URL remota — não fazer download local
- Nova migration `_002_product_enrichment.py` para adicionar colunas à tabela `products` existente

**Deduplication e Upsert:**
- `external_id` por plataforma: slug da URL para Hotmart, ID da API para ClickBank, researcher define para Kiwify
- Estratégia: upsert por `external_id` — atualiza rank/score/price/updated_at, não duplica
- Preservar dados antigos quando drift detectado — nunca sobrescrever com resultado vazio

**Volume de Coleta:**
- Top 10 a 50 produtos por nicho por plataforma (não mínimo — é o alvo real)
- `max_products_per_niche: 50` configurável no config.yaml

**Abordagem Hotmart:**
- Playwright + interceptar requisições XHR/GraphQL — dados estruturados do backend
- Anti-bot: researcher testa ao vivo e reporta necessidade de configuração extra

**Abordagem Kiwify:**
- SSR — httpx suficiente
- Marketplace público navegável por categoria

**Arquitetura dos Scrapers:**
- Hierarquia: `PlatformScanner(BaseScraper)` como classe base intermediária
- Método abstrato: `scan_niche(niche_slug: str) -> list[Product]`
- `mis/scanner.py`: contém `PlatformScanner` + `run_all_scanners(config)`
- `mis/scanners/`: subpackage com `hotmart.py`, `clickbank.py`, `kiwify.py`, `__init__.py`
- `Product`: dataclass com todos os campos possíveis, opcionais como `Optional[]`
- Persistência fora do scraper: `ProductRepository` ou `upsert_product()` em arquivo separado
- `run_all_scanners()`: `asyncio.gather()` paralelo com `return_exceptions=True`

**Config.yaml Extensão:**
```yaml
niches:
  - slug: emagrecimento
    name: Emagrecimento
    platforms:
      hotmart: saude-e-fitness
      clickbank: health
      kiwify: saude
```
- Nicho sem bloco `platforms`: skip + warning via structlog
- Validação: typos de plataforma lançam `ValueError`; pelo menos uma plataforma mapeada
- Novos settings: `max_products_per_niche: 50`, `scan_schedule: "0 3 * * *"`, `parallel_scanners: true`

**Schema Drift Detection:**
- Fallback selectors/endpoints hardcoded no scraper em lista ordenada
- Sequência: primary → fallbacks → alerta via structlog com `alert='schema_drift'`
- Payload: platform + nicho, selector/endpoint que falhou, timestamp último run bem-sucedido, URL tentada
- Integrar ao health_monitor como canary check DB-based (não live request)
- Canary: `SELECT MAX(updated_at) FROM products WHERE platform_id = ?` — se > 25h, dispara alerta
- Dados antigos preservados quando 0 produtos retornados

**Testes:**
- Fixtures HTML/JSON gravadas ao vivo (uma vez) → commitadas → testes sempre usam fixtures
- Localização: `mis/tests/fixtures/` organizado por plataforma (`hotmart/`, `clickbank/`, `kiwify/`)
- Mock httpx via respx; Playwright: mock do `fetch_spa()` retornando HTML da fixture
- Testes completos: scraper + upsert no DB (DB real em `tmp_path`)
- 5 testes mínimos por scraper (happy path, tipos, fallback selector, drift alert, upsert)

### Claude's Discretion
- Horário default do job diário (dentro da janela de madrugada)
- Implementação interna do ProductRepository (classe vs funções)
- Formato do external_id para Kiwify e ClickBank (researcher confirma o campo estável)
- Algoritmo de detecção de 0 produtos (threshold, timeout handling)

### Deferred Ideas (OUT OF SCOPE)
- Kiwify estava inicialmente fora do escopo — incluída por decisão do usuário
- JVZoo, Eduzz, Udemy, Product Hunt, AppSumo — v2
- Histórico de evolução de ranking (tabela de snapshots) — ADV-03
- Proxy residencial e configuração avançada de stealth para Cloudflare — Pre-Phase 3
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SCAN-01 | Sistema varre e rankeia produtos mais vendidos na Hotmart por nicho configurado | Playwright XHR interception, PlatformScanner pattern, upsert_product() |
| SCAN-02 | Sistema varre e rankeia produtos mais vendidos na Kiwify por nicho configurado | httpx SSR scraping, BeautifulSoup/lxml parsing, PlatformScanner pattern |
| SCAN-03 | Sistema varre e rankeia produtos com maior gravity score no ClickBank por nicho | ClickBank REST API v1.3 com API Key header, gravity score endpoint |
| SCAN-04 | Ranking é atualizado automaticamente em ciclo periódico (diário) | APScheduler CronTrigger, `register_scanner_jobs()`, `run_all_scanners()` |
</phase_requirements>

---

## Summary

Phase 2 constrói três scrapers de plataforma sobre o `BaseScraper` já existente, todos convergindo para a mesma tabela `products` via upsert. A arquitetura é bem determinada pelo CONTEXT.md, restando à pesquisa confirmar: (a) que a API pública do ClickBank existe e requer apenas API Key própria (confirmado), (b) o padrão canônico de intercepcão XHR com Playwright async (confirmado com código), (c) que Kiwify é SSR e httpx suficiente (confirmado), e (d) como sqlite-utils executa upsert com chave composta (confirmado).

O maior risco técnico é Hotmart: por ser SPA com XHR/GraphQL, os endpoints exatos e a forma do JSON retornado **devem ser auditados ao vivo** antes de escrever o scraper. O CONTEXT.md já reconhece isso (blocker Pre-Phase 2 no STATE.md). A estratégia recomendada é: implementar Kiwify primeiro (valida o pattern), depois ClickBank (API estável), depois Hotmart (requer inspeção live).

ClickBank marketplace público (https://www.clickbank.com/view-marketplace/) não expõe um endpoint de listagem via API pública/anônima. A API REST v1.3 documentada é orientada a conta (orders, analytics, products CRUD para seus próprios produtos). Para busca de produtos de afiliados por categoria com gravity score, o caminho é scraping do marketplace web — não existe endpoint REST público de busca por categoria com gravity.

**Primary recommendation:** Implementar na ordem Kiwify → ClickBank (scraping marketplace) → Hotmart (XHR intercept), com audit live obrigatória antes de Hotmart.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| httpx | >=0.28.1 | Fetch SSR pages e endpoints (Kiwify, ClickBank) | Já em requirements.txt, async nativo |
| playwright | >=1.58.0 | Renderizar SPA Hotmart + interceptar XHR | Já em requirements.txt, suporta `page.on('response')` |
| playwright-stealth | >=2.0.2 | Suprimir fingerprints anti-bot no Playwright | Já em requirements.txt, integrado no BaseScraper |
| BeautifulSoup4 / lxml | latest | Parsear HTML SSR (Kiwify) | Padrão de scraping HTML |
| respx | >=0.21.0 | Mock httpx em testes unitários | Já em requirements-dev.txt |
| sqlite-utils | >=3.39 | Upsert no DB SQLite | Já em requirements.txt, pattern estabelecido |
| APScheduler | >=3.11.2 | CronTrigger para jobs diários | Já em requirements.txt, singleton get_scheduler() |
| structlog | >=25.5.0 | Logging JSON com `alert=` field | Já em requirements.txt, padrão estabelecido |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| BeautifulSoup4 | >=4.12 | Parsing HTML Kiwify/ClickBank | SSR + fallback selectors |
| lxml | latest | Parser mais rápido para bs4 | Volumes maiores de HTML |
| dataclasses (stdlib) | built-in | Product dataclass | Já disponível, zero dependência |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| BeautifulSoup4 | lxml direto | lxml mais rápido mas API menos ergonômica |
| Playwright XHR intercept | Selenium | Playwright tem API async nativa e `page.on()` mais limpa |
| sqlite-utils upsert | SQL manual INSERT OR REPLACE | sqlite-utils mais conciso e mantém FKs |

**Installation:**
```bash
pip install beautifulsoup4 lxml
```
(Todas as outras dependências já estão em requirements.txt)

---

## Architecture Patterns

### Recommended Project Structure
```
mis/
├── scanner.py           # PlatformScanner base + run_all_scanners()
├── scanners/
│   ├── __init__.py
│   ├── hotmart.py       # HotmartScanner(PlatformScanner)
│   ├── clickbank.py     # ClickBankScanner(PlatformScanner)
│   └── kiwify.py        # KiwifyScanner(PlatformScanner)
├── product_repository.py  # upsert_product(), get_products_by_niche()
├── migrations/
│   ├── _001_initial.py    # existente
│   └── _002_product_enrichment.py  # nova: rank, commission_pct, rating, thumbnail_url, updated_at
└── tests/
    ├── fixtures/
    │   ├── hotmart/       # response_saude_page1.json, response_mkt_page1.json
    │   ├── clickbank/     # marketplace_health.html, marketplace_mktg.html
    │   └── kiwify/        # catalog_saude.html, catalog_mktg.html
    ├── test_hotmart_scanner.py
    ├── test_clickbank_scanner.py
    ├── test_kiwify_scanner.py
    └── test_scanner_jobs.py
```

### Pattern 1: PlatformScanner Abstract Base

```python
# mis/scanner.py
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
import structlog

from .base_scraper import BaseScraper

log = structlog.get_logger()

@dataclass
class Product:
    external_id: str
    title: str
    url: str
    platform_id: int
    niche_id: int
    rank: int
    price: Optional[float] = None
    commission_pct: Optional[float] = None
    rating: Optional[float] = None
    thumbnail_url: Optional[str] = None


class PlatformScanner(BaseScraper, ABC):
    """Abstract base for platform-specific scanners."""

    @abstractmethod
    async def scan_niche(self, niche_slug: str, platform_slug: str) -> list[Product]:
        """Scan one niche/category. Returns empty list on failure, never raises."""
        ...


async def run_all_scanners(config: dict) -> dict[str, list[Product]]:
    """Run all enabled scanners in parallel. Failure in one does not cancel others."""
    from .scanners.hotmart import HotmartScanner
    from .scanners.clickbank import ClickBankScanner
    from .scanners.kiwify import KiwifyScanner

    scanners = {
        "hotmart": HotmartScanner(),
        "clickbank": ClickBankScanner(),
        "kiwify": KiwifyScanner(),
    }
    results = {}
    for niche in config["niches"]:
        platforms_cfg = niche.get("platforms", {})
        if not platforms_cfg:
            log.warning("scanner.niche.no_platforms", niche=niche["slug"])
            continue
        tasks = {
            platform: scanner.scan_niche(niche["slug"], platforms_cfg[platform])
            for platform, scanner in scanners.items()
            if platform in platforms_cfg
        }
        gathered = await asyncio.gather(*tasks.values(), return_exceptions=True)
        for platform, result in zip(tasks.keys(), gathered):
            if isinstance(result, Exception):
                log.error("scanner.platform.failed", platform=platform, error=str(result))
            else:
                results.setdefault(platform, []).extend(result)
    return results
```

### Pattern 2: Playwright XHR Interception (Hotmart)

```python
# mis/scanners/hotmart.py — padrão de intercepção XHR
import json
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

HOTMART_SELECTORS = [
    # primary — confirmar via inspeção live antes de implementar
    "https://api.hotmart.com/product/v3/search",   # hipótese: endpoint REST
    # fallback 1
    "https://api.hotmart.com/marketplace/products",
]

async def _fetch_hotmart_niche(niche_slug: str, category_slug: str) -> list[dict]:
    captured = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        await stealth_async(page)

        async def handle_response(response):
            # filtra por URL que contém keywords do endpoint esperado
            for selector in HOTMART_SELECTORS:
                if selector in response.url:
                    try:
                        body = await response.json()
                        captured.append(body)
                    except Exception:
                        pass

        page.on("response", handle_response)
        url = f"https://hotmart.com/pt-br/marketplace/produtos?category={category_slug}"
        await page.goto(url, wait_until="networkidle")
        await browser.close()

    return captured
```

**IMPORTANTE:** Os endpoints exatos do Hotmart (`HOTMART_SELECTORS`) são hipóteses que DEVEM ser auditados via DevTools antes de implementar. Esta é a tarefa de "inspeção live" marcada como blocker no STATE.md.

### Pattern 3: APScheduler CronTrigger para Jobs de Plataforma

```python
# mis/scheduler.py — adicionar register_scanner_jobs()
from apscheduler.triggers.cron import CronTrigger

def register_scanner_jobs(config: dict) -> None:
    """Register one APScheduler job per platform scanner."""
    from .scanners.hotmart import run_hotmart_scan
    from .scanners.clickbank import run_clickbank_scan
    from .scanners.kiwify import run_kiwify_scan

    scheduler = get_scheduler()
    scan_schedule = config.get("settings", {}).get("scan_schedule", "0 3 * * *")
    trigger = CronTrigger.from_crontab(scan_schedule)

    for job_id, func in [
        ("scanner_hotmart", run_hotmart_scan),
        ("scanner_clickbank", run_clickbank_scan),
        ("scanner_kiwify", run_kiwify_scan),
    ]:
        scheduler.add_job(
            func,
            trigger=trigger,
            args=[config],
            id=job_id,
            replace_existing=True,  # padrão estabelecido na Phase 1
        )
        log.info("scanner.job.registered", job_id=job_id, schedule=scan_schedule)
```

Default de horário recomendado: `"0 3 * * *"` (3h da manhã) — janela de menor tráfego, evita horário de pico das plataformas BR.

### Pattern 4: Upsert com sqlite-utils por external_id

```python
# mis/product_repository.py
from datetime import datetime, timezone
import sqlite_utils
from .scanner import Product


def upsert_product(db: sqlite_utils.Database, product: Product) -> None:
    """Insert or update a product row keyed by (platform_id, external_id)."""
    row = {
        "platform_id": product.platform_id,
        "niche_id": product.niche_id,
        "external_id": product.external_id,
        "title": product.title,
        "url": product.url,
        "rank": product.rank,
        "price": product.price,
        "commission_pct": product.commission_pct,
        "rating": product.rating,
        "thumbnail_url": product.thumbnail_url,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    # upsert_all com alter=True cria colunas novas automaticamente se necessário
    db["products"].upsert(row, pk=("platform_id", "external_id"), alter=True)
```

**Chave composta** `(platform_id, external_id)` garante que o mesmo `external_id` em plataformas diferentes não colide. O `alter=True` permite adicionar colunas sem migration explícita durante desenvolvimento, mas a migration `_002` deve ser criada para produção.

### Pattern 5: Schema Drift Detection com Fallback Selectors

```python
# Padrão dentro de cada scraper
SELECTORS_ORDERED = [
    ".product-card[data-product-id]",  # primary
    ".marketplace-item",               # fallback 1
    "[data-testid='product-item']",    # fallback 2
]

def _parse_with_fallbacks(html: str, platform: str, niche: str, url: str, last_ok: str | None) -> list[dict]:
    for selector in SELECTORS_ORDERED:
        results = _try_selector(html, selector)
        if results:
            return results

    # Todos os fallbacks falharam — emitir alerta de drift
    log.warning(
        "schema.drift.detected",
        alert="schema_drift",
        platform=platform,
        niche=niche,
        selectors_tried=SELECTORS_ORDERED,
        url=url,
        last_successful_run=last_ok,
    )
    return []  # retorna vazio — dados antigos no DB são preservados pelo upsert
```

### Pattern 6: Canary Check DB-based para Plataformas

```python
# mis/health_monitor.py — estender com canary de plataforma
async def run_platform_canary(db_path: str, platform_id: int, platform_name: str) -> bool:
    """Check if platform products were updated in last 25 hours. DB-only, no live request."""
    import sqlite_utils
    from datetime import datetime, timezone, timedelta

    db = sqlite_utils.Database(db_path)
    threshold = (datetime.now(timezone.utc) - timedelta(hours=25)).isoformat()
    rows = list(db.execute(
        "SELECT MAX(updated_at) as last_update FROM products WHERE platform_id = ?",
        [platform_id]
    ).fetchall())

    last_update = rows[0][0] if rows else None
    if not last_update or last_update < threshold:
        log.warning(
            "health.platform.stale",
            alert="platform_data_stale",
            platform=platform_name,
            last_update=last_update,
            threshold_hours=25,
        )
        return False

    log.info("health.platform.ok", platform=platform_name, last_update=last_update)
    return True
```

### Pattern 7: Migration _002 para Novos Campos

```python
# mis/migrations/_002_product_enrichment.py
def run_migration_002(db_path: str) -> None:
    """Add enrichment columns to products table. Idempotent."""
    import sqlite_utils
    db = sqlite_utils.Database(db_path)
    existing = {col.name for col in db["products"].columns}
    new_cols = {
        "rank": int,
        "commission_pct": float,
        "rating": float,
        "thumbnail_url": str,
        "updated_at": str,
    }
    for col_name, col_type in new_cols.items():
        if col_name not in existing:
            db["products"].add_column(col_name, col_type)
```

### Anti-Patterns to Avoid

- **Não usar `INSERT OR REPLACE`:** substitui a linha inteira, perde dados de colunas não fornecidas. Usar `upsert()` do sqlite-utils que faz PATCH semântico.
- **Não lançar exceção em scan_niche() quando drift:** retornar lista vazia + logar alerta. Dados antigos ficam intactos no DB.
- **Não fazer download de thumbnail:** salvar apenas `thumbnail_url` como string. Download pertence a uma fase futura.
- **Não compartilhar estado entre plataformas em run_all_scanners():** `asyncio.gather(return_exceptions=True)` garante isolamento; cada plataforma tem seu próprio job APScheduler.
- **Não usar `asyncio_mode = strict` sem marcar testes com `@pytest.mark.asyncio`:** o projeto usa `asyncio_mode = auto` no pytest.ini (Phase 1), manter.
- **Não fazer request live no canary de plataforma:** canary deve consultar apenas o DB (`updated_at`) — o request live fica no scraper regular.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Mock de httpx em testes | Monkey-patch manual | respx (já em requirements-dev.txt) | respx integra com pytest fixture, assert_all_called automático |
| Deduplicação de produtos | Hash comparison manual | sqlite-utils `upsert(pk=...)` | Lida com concorrência e colisões de chave corretamente |
| Parsing de cron expression | Parser próprio | `CronTrigger.from_crontab()` do APScheduler | Suporte completo a todos os campos cron |
| Retry em requests do scraper | Loop `for i in range(3)` | tenacity (já em BaseScraper.fetch()) | Edge cases de retry são numerosos; tenacity já está integrado |
| Logging estruturado | `print()` com dicts | structlog (já configurado) | `alert=` field machine-readable, padrão do projeto |
| Suprimir fingerprints do Playwright | Configurar manualmente | playwright-stealth (já em BaseScraper.fetch_spa()) | Cobre 20+ fingerprints que detecção anti-bot verifica |

**Key insight:** O projeto Phase 1 já estabeleceu todos os primitivos — a Phase 2 **compõe** esses primitivos, não os reinventa.

---

## Common Pitfalls

### Pitfall 1: ClickBank não tem API pública de marketplace
**What goes wrong:** Developer assume que a API REST v1.3 do ClickBank retorna produtos de outros vendedores por categoria com gravity score.
**Why it happens:** A documentação da API foca em CRUD dos seus próprios produtos. O marketplace de afiliados é uma UI web separada.
**How to avoid:** Scraping do marketplace web `https://www.clickbank.com/view-marketplace/` com httpx (a página é Next.js SSR, mas dados iniciais estão no HTML). Filtrar por categoria via URL params (requerem inspeção live para confirmar formato exato).
**Warning signs:** API retorna 401 ou dados vazios sem niche filtering.

### Pitfall 2: Hotmart endpoint XHR desconhecido sem inspeção live
**What goes wrong:** Scraper implementado com endpoint hipotético que nunca funciona.
**Why it happens:** Hotmart é SPA — endpoint de busca de marketplace não está documentado publicamente.
**How to avoid:** Antes de escrever `hotmart.py`, abrir DevTools → Network → XHR/Fetch, navegar em `https://hotmart.com/pt-br/marketplace/produtos?category=saude-e-fitness`, identificar o request que retorna lista de produtos, verificar URL, headers e payload. Commitar a fixture do response real.
**Warning signs:** `captured = []` ao final do `page.on('response')` loop.

### Pitfall 3: Upsert sem chave composta gera duplicatas cross-platform
**What goes wrong:** `external_id` de produto Kiwify colide com `external_id` de produto Hotmart.
**Why it happens:** `external_id` é único por plataforma, não globalmente.
**How to avoid:** Sempre usar `pk=("platform_id", "external_id")` no upsert.
**Warning signs:** `UNIQUE constraint failed: products.external_id`.

### Pitfall 4: APScheduler job registrado mas event loop não compartilhado
**What goes wrong:** Job não executa mesmo com scheduler rodando.
**Why it happens:** `AsyncIOScheduler` precisa do mesmo event loop que o código async principal.
**How to avoid:** Usar `get_scheduler()` singleton (já estabelecido na Phase 1). Registrar jobs antes de `start_scheduler()`. Em testes, verificar registro do job sem executar o scheduler.
**Warning signs:** Job aparece em `scheduler.get_jobs()` mas callback nunca chamado.

### Pitfall 5: Fixture não representa a estrutura real
**What goes wrong:** Testes passam com fixture, mas scraper falha em produção.
**Why it happens:** Fixture gravada de URL errada ou processada manualmente.
**How to avoid:** Gravar fixtures diretamente do response ao vivo usando `response.body()` (Playwright) ou `response.content` (httpx). Commitar o arquivo binário/JSON exato sem modificação.
**Warning signs:** Campos ausentes na fixture que existem em produção.

### Pitfall 6: Schema drift alert com 0 produtos sobrescreve DB
**What goes wrong:** Scraper falha silenciosamente com lista vazia, upsert não roda mas dados antigos são perdidos em outro caminho.
**Why it happens:** Lógica de "se vazio, skip upsert" não implementada.
**How to avoid:** No `ProductRepository.save_batch()`, verificar `if not products: return` antes do loop de upsert. Logar `zero_products_detected` sempre que isso acontecer.
**Warning signs:** `SELECT COUNT(*) FROM products WHERE platform_id = ?` retorna 0 após um job que deveria ter encontrado dados.

---

## Code Examples

### Teste de Scraper com respx (Kiwify/ClickBank SSR)
```python
# Source: respx official guide (lundberg.github.io/respx/guide/)
import pytest
import respx
from httpx import Response

@pytest.mark.asyncio
async def test_kiwify_happy_path(tmp_path):
    fixture = (Path(__file__).parent / "fixtures/kiwify/catalog_saude.html").read_bytes()

    with respx.mock(assert_all_called=True) as mock:
        mock.get("https://www.kiwify.com.br/marketplace?category=saude").mock(
            return_value=Response(200, content=fixture)
        )
        async with KiwifyScanner() as scanner:
            products = await scanner.scan_niche("emagrecimento", "saude")

    assert len(products) >= 10
    for p in products:
        assert p.external_id is not None
        assert isinstance(p.rank, int)
        assert p.platform_id == KIWIFY_PLATFORM_ID
```

### Teste de Fallback Selector e Drift Alert
```python
@pytest.mark.asyncio
async def test_drift_alert_emitted_when_all_selectors_fail(tmp_path, caplog):
    broken_html = b"<html><body>maintenance mode</body></html>"

    with respx.mock():
        respx.get(...).mock(return_value=Response(200, content=broken_html))
        async with KiwifyScanner() as scanner:
            products = await scanner.scan_niche("emagrecimento", "saude")

    assert products == []
    # Verificar que alert='schema_drift' foi emitido no structlog
    assert any("schema_drift" in record.message for record in caplog.records)
```

### Teste de Upsert sem Duplicatas
```python
def test_upsert_no_duplicates(db_path):
    from mis.db import get_db, run_migrations
    from mis.product_repository import upsert_product
    from mis.migrations._002_product_enrichment import run_migration_002

    run_migrations(db_path)
    run_migration_002(db_path)
    db = get_db(db_path)

    product = Product(external_id="kiwify-abc123", title="Curso X", url="https://...",
                      platform_id=3, niche_id=1, rank=1, price=97.0)
    upsert_product(db, product)
    upsert_product(db, product._replace(rank=2))  # re-run com rank atualizado

    rows = list(db["products"].rows_where("external_id = ?", ["kiwify-abc123"]))
    assert len(rows) == 1
    assert rows[0]["rank"] == 2
```

### APScheduler CronTrigger — Verificar Registro sem Executar
```python
def test_scanner_jobs_registered(temp_config_yaml):
    from mis.scheduler import get_scheduler, stop_scheduler, register_scanner_jobs
    config = load_config(Path(temp_config_yaml))
    register_scanner_jobs(config)
    scheduler = get_scheduler()
    job_ids = {job.id for job in scheduler.get_jobs()}
    assert "scanner_hotmart" in job_ids
    assert "scanner_clickbank" in job_ids
    assert "scanner_kiwify" in job_ids
    stop_scheduler()
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Selenium para SPAs | Playwright + stealth_async | 2021-2023 | Async nativo, fingerprint suppression built-in |
| requests síncrono | httpx async | 2020+ | HTTP/2, asyncio nativo |
| SQL raw INSERT OR REPLACE | sqlite-utils upsert(pk=...) | 2019+ | Semântica PATCH, não substitui linha inteira |
| Page scraping para gravity score | API REST (quando disponível) | Sempre preferível | Mais estável que HTML parsing |
| ClickBank API para marketplace | Scraping web marketplace | Permanente | API oficial não expõe busca pública por gravity/categoria |

**Deprecated/outdated:**
- `asyncio_mode = strict` em pytest.ini: o projeto já usa `auto`, não mudar.
- APScheduler 4.x: o projeto usa 3.x (`AsyncIOScheduler`). APScheduler 4.x tem API completamente diferente — não misturar documentação entre versões.

---

## Open Questions

1. **Hotmart XHR endpoint shape**
   - What we know: Hotmart é SPA Vue/React, carrega produtos via XHR ou GraphQL. `api.hotmart.com` existe mas documentação não é pública.
   - What's unclear: URL exata do endpoint, parâmetros de paginação, formato do JSON de resposta, campos de rank/score presentes.
   - Recommendation: **Ação obrigatória no Wave 0 do Plan 02-01**: abrir hotmart.com/pt-br/marketplace no browser, ativar DevTools → Network → XHR/Fetch, navegar por categoria e identificar o request. Gravar response como fixture. Só então implementar o scraper.

2. **ClickBank marketplace — URL params por categoria**
   - What we know: `https://www.clickbank.com/view-marketplace/` é Next.js SSR. Gravity score e categoria são visíveis.
   - What's unclear: Formato exato do URL parameter para filtrar por categoria (ex: `?cat=health` ou `/health/`). Se dados de gravity estão no SSR HTML inicial ou carregados via XHR.
   - Recommendation: Inspecionar via httpx GET com Accept: `text/html` e verificar se dados estão no HTML. Se não, identificar XHR com Playwright.

3. **Kiwify external_id estável**
   - What we know: Kiwify é SSR, estrutura mais simples.
   - What's unclear: O campo mais estável para external_id — pode ser slug da URL, ID em atributo data-, ou outro.
   - Recommendation: Usar slug da URL do produto como external_id (padrão Hotmart). Gravar fixture live e confirmar estrutura HTML antes de implementar parser.

4. **ClickBank gravity score disponível sem login**
   - What we know: Marketplace é público para browsing.
   - What's unclear: Se gravity score aparece no HTML sem autenticação de afiliado.
   - Recommendation: Testar com httpx GET anônimo no plan 02-02. Se gravity não aparecer sem login, usar rank posicional como score (posição na lista de "top products" por categoria).

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.x + pytest-asyncio 0.24.x |
| Config file | `mis/pytest.ini` (asyncio_mode = auto, testpaths = tests, timeout = 10) |
| Quick run command | `cd mis && python -m pytest tests/test_kiwify_scanner.py -x -q` |
| Full suite command | `cd mis && python -m pytest tests/ -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SCAN-01 | HotmartScanner.scan_niche() retorna lista com campos obrigatórios | unit + fixture | `pytest tests/test_hotmart_scanner.py -x` | ❌ Wave 0 |
| SCAN-01 | Hotmart fallback selector usado quando primary falha | unit + fixture | `pytest tests/test_hotmart_scanner.py::test_fallback_selector -x` | ❌ Wave 0 |
| SCAN-01 | Hotmart drift alert emitido quando todos selectors falham | unit + fixture | `pytest tests/test_hotmart_scanner.py::test_drift_alert -x` | ❌ Wave 0 |
| SCAN-01 | Hotmart upsert: re-run atualiza rank sem duplicar | integration (DB real) | `pytest tests/test_hotmart_scanner.py::test_upsert_no_dup -x` | ❌ Wave 0 |
| SCAN-02 | KiwifyScanner.scan_niche() retorna >= 10 produtos com campos obrigatórios | unit + fixture | `pytest tests/test_kiwify_scanner.py::test_happy_path -x` | ❌ Wave 0 |
| SCAN-02 | Kiwify campos tipados: price é float, rank é int | unit + fixture | `pytest tests/test_kiwify_scanner.py::test_field_types -x` | ❌ Wave 0 |
| SCAN-02 | Kiwify fallback selector e drift alert | unit + fixture | `pytest tests/test_kiwify_scanner.py::test_drift_alert -x` | ❌ Wave 0 |
| SCAN-02 | Kiwify upsert sem duplicatas | integration (DB real) | `pytest tests/test_kiwify_scanner.py::test_upsert -x` | ❌ Wave 0 |
| SCAN-03 | ClickBankScanner.scan_niche() retorna produtos com gravity score (rank) | unit + fixture | `pytest tests/test_clickbank_scanner.py::test_happy_path -x` | ❌ Wave 0 |
| SCAN-03 | ClickBank campos tipados + gravity como float/rank como int | unit + fixture | `pytest tests/test_clickbank_scanner.py::test_field_types -x` | ❌ Wave 0 |
| SCAN-03 | ClickBank fallback selector e drift alert | unit + fixture | `pytest tests/test_clickbank_scanner.py::test_drift_alert -x` | ❌ Wave 0 |
| SCAN-03 | ClickBank upsert sem duplicatas | integration (DB real) | `pytest tests/test_clickbank_scanner.py::test_upsert -x` | ❌ Wave 0 |
| SCAN-04 | register_scanner_jobs() registra 3 jobs no APScheduler | unit | `pytest tests/test_scanner_jobs.py::test_jobs_registered -x` | ❌ Wave 0 |
| SCAN-04 | Job usa CronTrigger com schedule do config.yaml | unit | `pytest tests/test_scanner_jobs.py::test_cron_trigger -x` | ❌ Wave 0 |
| SCAN-04 | Canary DB-based alerta quando updated_at > 25h | unit (DB real) | `pytest tests/test_scanner_jobs.py::test_platform_canary_stale -x` | ❌ Wave 0 |
| SCAN-04 | run_all_scanners() com return_exceptions=True não cancela outras plataformas | unit | `pytest tests/test_scanner_jobs.py::test_partial_failure -x` | ❌ Wave 0 |

### Abordagem de Mock por Tipo de Scraper

**KiwifyScanner e ClickBankScanner (httpx):**
- Usar `respx.mock` como context manager ou fixture `respx_mock`
- Fixtures em `mis/tests/fixtures/kiwify/` e `mis/tests/fixtures/clickbank/`
- Mock retorna `Response(200, content=fixture_bytes)`
- NÃO fazer requests reais em testes unitários

**HotmartScanner (Playwright):**
- Mock do método `fetch_spa()` herdado do BaseScraper via `unittest.mock.AsyncMock`
- `fetch_spa()` retorna HTML da fixture em vez de navegar ao vivo
- Playwright NÃO é instanciado nos testes unitários — apenas o parser é testado
- Alternativa: monkeypatch em `page.on('response')` para retornar fixture JSON

**Testes de integração (upsert no DB):**
- Usar fixture `db_path` existente em conftest.py (DB real em `tmp_path`)
- Rodar migration `_001` + `_002` no fixture antes do teste
- Verificar com `db["products"].rows_where(...)` — sem mock de DB

**Testes de APScheduler:**
- NÃO iniciar o scheduler (`start_scheduler()`) nos testes
- Apenas verificar `scheduler.get_jobs()` após `register_scanner_jobs()`
- Verificar trigger type e schedule do job registrado
- Usar `stop_scheduler()` no teardown para reset do singleton

**Verificar schema drift:**
```python
import logging

def test_drift_alert_emitted(caplog):
    with caplog.at_level(logging.WARNING):
        # chamar scraper com HTML sem nenhum selector reconhecido
        ...
    assert any("schema_drift" in r.message for r in caplog.records)
```
Nota: structlog com JSONRenderer não escreve no caplog padrão do Python. Usar `structlog.testing.capture_logs()` em vez de `caplog`:
```python
from structlog.testing import capture_logs

def test_drift_alert_structlog():
    with capture_logs() as cap:
        products = _parse_with_fallbacks("<html>broken</html>", ...)
    assert any(e.get("alert") == "schema_drift" for e in cap)
```

### Sampling Rate
- **Por task commit:** `cd mis && python -m pytest tests/test_{module_atual}_scanner.py -x -q`
- **Por wave merge:** `cd mis && python -m pytest tests/ -q`
- **Phase gate:** Full suite verde antes de `/gsd:verify-work`

### Wave 0 Gaps (criados antes de qualquer implementação)

- [ ] `mis/tests/fixtures/kiwify/catalog_saude.html` — gravar ao vivo (Kiwify SSR)
- [ ] `mis/tests/fixtures/kiwify/catalog_mkt.html` — gravar ao vivo
- [ ] `mis/tests/fixtures/clickbank/marketplace_health.html` — gravar ao vivo
- [ ] `mis/tests/fixtures/clickbank/marketplace_mktg.html` — gravar ao vivo
- [ ] `mis/tests/fixtures/hotmart/` — gravar JSON do XHR ao vivo (requer inspeção live primeiro)
- [ ] `mis/migrations/_002_product_enrichment.py` — nova migration antes de qualquer upsert
- [ ] `mis/scanner.py` — Product dataclass + PlatformScanner + run_all_scanners()
- [ ] `mis/scanners/__init__.py` — subpackage
- [ ] `mis/product_repository.py` — upsert_product()
- [ ] `mis/tests/test_hotmart_scanner.py` — 5 testes mínimos (RED antes de implementar)
- [ ] `mis/tests/test_clickbank_scanner.py` — 5 testes mínimos (RED antes de implementar)
- [ ] `mis/tests/test_kiwify_scanner.py` — 5 testes mínimos (RED antes de implementar)
- [ ] `mis/tests/test_scanner_jobs.py` — testes de SCAN-04 (RED antes de implementar)
- [ ] `mis/requirements.txt` — adicionar `beautifulsoup4` e `lxml`

---

## Sources

### Primary (HIGH confidence)
- `mis/base_scraper.py` — padrões fetch(), fetch_spa(), DOMAIN_DELAYS, stealth_async
- `mis/scheduler.py` — get_scheduler() singleton, replace_existing=True pattern
- `mis/health_monitor.py` — run_canary_check(), register_canary_job(), structlog alert pattern
- `mis/db.py` + `mis/migrations/_001_initial.py` — get_db(), products schema
- `mis/tests/conftest.py` — db_path fixture, temp_config_yaml pattern
- `mis/pytest.ini` — asyncio_mode = auto, testpaths = tests, timeout = 10
- [sqlite-utils Python API docs](https://sqlite-utils.datasette.io/en/stable/python-api.html) — upsert() semântica com pk composto
- [respx guide](https://lundberg.github.io/respx/guide/) — respx_mock fixture, async context manager pattern
- [APScheduler 3.x cron docs](https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html) — CronTrigger.from_crontab()
- [Playwright scrapfly guide](https://scrapfly.io/blog/answers/how-to-capture-xhr-requests-playwright) — page.on('response') pattern

### Secondary (MEDIUM confidence)
- [ClickBank API support docs](https://support.clickbank.com/en/articles/10535400-clickbank-apis) — confirmação que API não expõe marketplace público por categoria
- [ClickBank marketplace](https://www.clickbank.com/view-marketplace/) — Next.js SSR, gravity score e rank visíveis publicamente

### Tertiary (LOW confidence — requer inspeção live)
- Hotmart XHR endpoint URL e JSON schema — hipótese não verificável sem browser ao vivo
- ClickBank marketplace URL params por categoria — formato exato requer teste ao vivo
- Kiwify HTML structure — estrutura de cards e campo external_id requerem inspeção live

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — toda a stack já existe no projeto, apenas beautifulsoup4/lxml são novidade
- Architecture: HIGH — padrões determinados pelo CONTEXT.md + codebase existente
- Hotmart endpoint: LOW — requer inspeção live obrigatória antes de implementar
- ClickBank marketplace scraping: MEDIUM — SSR confirmado, URL params requerem validação
- Kiwify: MEDIUM — SSR confirmado, estrutura HTML requer gravar fixture ao vivo
- Pitfalls: HIGH — baseados em codebase real e padrões estabelecidos
- Testing patterns: HIGH — respx + structlog.testing + db_path fixture todos verificados

**Research date:** 2026-03-14
**Valid until:** 2026-04-14 (plataformas web mudam frequentemente — re-auditar fixtures antes de cada sprint)

---

## RESEARCH COMPLETE

**Phase:** 02 - Platform Scanners
**Confidence:** HIGH (stack/architecture) / MEDIUM (ClickBank/Kiwify URLs) / LOW (Hotmart XHR endpoint)

### Key Findings

- **ClickBank não tem API pública de marketplace:** A API REST v1.3 é para gerenciar seus próprios produtos. Para buscar produtos de afiliados por categoria com gravity score, é necessário scraping do marketplace web — não existe endpoint público de busca.
- **Hotmart requer inspeção live obrigatória:** Os endpoints XHR/GraphQL não são documentados. O scraper de Hotmart DEVE ser precedido por uma sessão de DevTools para identificar e gravar o endpoint real e fixture do response.
- **Ordem de implementação recomendada:** Kiwify (valida pattern, mais simples) → ClickBank (SSR, gravity) → Hotmart (XHR, maior risco).
- **Upsert com pk composto:** `(platform_id, external_id)` previne colisões cross-platform. `sqlite-utils upsert(pk=(...), alter=True)` é o mecanismo correto.
- **structlog.testing.capture_logs():** Necessário para testar alertas de schema drift, pois o JSONRenderer do structlog não escreve no caplog padrão do pytest.

### File Created
`C:/Users/Gabriel/MEGABRAIN/.planning/phases/02-platform-scanners/02-RESEARCH.md`

### Confidence Assessment
| Area | Level | Reason |
|------|-------|--------|
| Standard Stack | HIGH | Toda a stack já existe no projeto; apenas bs4/lxml são novidade |
| Architecture | HIGH | Determinada pelo CONTEXT.md + padrões Phase 1 já implementados |
| Kiwify/ClickBank Scraping | MEDIUM | SSR confirmado; URL params e HTML structure requerem fixture ao vivo |
| Hotmart XHR Endpoint | LOW | Endpoint não documentado publicamente; inspeção live é pré-requisito |
| Testing Patterns | HIGH | respx, structlog.testing, db_path fixture todos verificados em fontes primárias |

### Open Questions
1. Hotmart: qual é o URL exato do endpoint XHR/GraphQL e o schema do JSON retornado?
2. ClickBank: o gravity score aparece no HTML SSR sem autenticação? Qual o formato do param de categoria?
3. Kiwify: qual campo é o external_id mais estável (slug da URL vs atributo data-id)?

### Ready for Planning
Research completo. O planner pode criar PLAN.md para os três planos (02-01 Kiwify+base, 02-02 ClickBank, 02-03 Hotmart+jobs). O blocker de inspeção live do Hotmart deve ser Wave 0 obrigatório no Plan 02-03.
