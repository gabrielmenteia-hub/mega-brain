# Phase 14: BR Scanners - Research

**Researched:** 2026-03-17
**Domain:** Brazilian infoproduct marketplace scraping (Eduzz, Monetizze, PerfectPay, Braip)
**Confidence:** MEDIUM — Braip confirmed SSR; Eduzz/Monetizze/PerfectPay require live inspection to confirm selectors; pattern and integration code confirmed HIGH via source reading

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **Fallback quando sem marketplace:** `scan_niche()` retorna `[]` + structlog emite `alert='marketplace_unavailable'`. Job APScheduler não falha. Dados antigos preservados no DB com `is_stale=True`. Upsert bem-sucedido reseta `is_stale=False` automaticamente.
- **Coluna is_stale:** Nova coluna `is_stale` (boolean, default `False`) na tabela `products` via migration `_007_is_stale.py`. Upsert seta `is_stale=False` on products arriving; scanner seta `is_stale=True` em todos produtos da plataforma+nicho quando retorna lista vazia.
- **Splitting:** 14-01 = EduzzScanner + MonetizzeScanner + migration _007_is_stale. 14-02 = PerfectPayScanner + BraipScanner.
- **6 testes por scanner** (5 padrão + 1 is_stale). is_stale dentro de cada `test_X_scanner.py`.
- **Fixtures HTML capturadas ao vivo** pelo researcher durante implementação, commitadas em `mis/tests/fixtures/eduzz/`, `monetizze/`, `perfectpay/`, `braip/`.
- Se PerfectPay ou Braip não tiverem marketplace público: testar **só o fallback** (retorno vazio + `is_stale=True`).
- **test_migration_007.py** para a nova migration (padrão do test_migration_006.py).
- Slugs de categoria descobertos via inspeção live. Config.yaml: opt-in por nicho, mesmo padrão hotmart/kiwify.
- Se plataforma não tiver categoria mapeada: skip com structlog warning (não falha o job).

### Claude's Discretion

- Estratégia de scraping (SSR vs SPA) por plataforma — researcher confirma via inspeção live.
- `external_id` convention por plataforma — researcher decide o campo mais estável.
- Horário default do job (dentro da madrugada).
- Implementação interna do reset de is_stale (update em batch vs por produto).

### Deferred Ideas (OUT OF SCOPE)

- Nenhum — discussão ficou dentro do escopo da Phase 14.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SCAN-BR-01 | `EduzzScanner` varre marketplace Eduzz por nicho e persiste top produtos por posição | Eduzz orbita.eduzz.com é SPA (JavaScript-required); fallback implementa `alert='marketplace_unavailable'`; padrão PlatformScanner de hotmart.py/kiwify.py reutilizado integralmente |
| SCAN-BR-02 | `MonetizzeScanner` varre marketplace Monetizze por nicho e persiste top produtos | Monetizze vitrine requer login (403 sem auth); scanner implementa fallback com `alert='marketplace_unavailable'`; `is_stale=True` em dados existentes quando lista vazia retornada |
| SCAN-BR-03 | `PerfectPayScanner` varre marketplace PerfectPay por nicho | PerfectPay não tem marketplace público — é plataforma de checkout; scanner implementa somente fallback (retorna `[]` + `alert='marketplace_unavailable'`) |
| SCAN-BR-04 | `BraipScanner` varre marketplace Braip por nicho | Braip tem marketplace público em `marketplace.braip.com` com dados SSR via `window.__NUXT__`; `hash` serve como external_id; URL de categoria: `/search?categorySlug={slug}` |
</phase_requirements>

---

## Summary

A pesquisa confirma que das 4 plataformas BR, apenas **Braip** possui marketplace público navegável sem autenticação (`marketplace.braip.com`). Os dados de produto são embutidos em `window.__NUXT__` (Nuxt.js SSR), com campo `hash` como external_id e URL de categoria via `?categorySlug={slug}`. O parsing via `window.__NUXT__` é diferente do BeautifulSoup puro — requer `json.loads` no conteúdo do script após `response.text`.

**Eduzz** migrou para `orbita.eduzz.com` (SPA React — "You need to enable JavaScript") e não expõe vitrine pública. **Monetizze** tem vitrine de afiliados atrás de login (403 sem auth). **PerfectPay** é plataforma de checkout sem marketplace centralizado — confirmado por documentação oficial.

O padrão de implementação é completamente mapeado via leitura dos arquivos fonte: `HotmartScanner` e `KiwifyScanner` são os templates de referência. A estrutura de 6 testes, a migration `_007_is_stale`, a integração com `run_all_scanners()` e `product_repository.upsert_product()` são todos patterns estabelecidos e verificados no código.

**Primary recommendation:** Implementar BraipScanner com parsing `window.__NUXT__` (HIGH confidence). Para Eduzz, Monetizze e PerfectPay: implementar scanner de fallback puro (retorna `[]` + `alert='marketplace_unavailable'` + sets `is_stale=True`) — nenhum marketplace público acessível sem autenticação foi confirmado.

---

## Standard Stack

### Core (Confirmed from source — HIGH confidence)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `httpx` | (existente) | HTTP client async para fetch SSR | Usado em todos scanners v1.0 |
| `BeautifulSoup4` + `lxml` | (existente) | Parse HTML para Braip (se estrutura HTML além do NUXT) | Padrão HotmartScanner/KiwifyScanner |
| `structlog` | (existente) | Logging estruturado com alert fields | `alert='schema_drift'`, `alert='marketplace_unavailable'` |
| `respx` | (existente) | Mock de requests httpx em testes | Usado em todos test_*_scanner.py |
| `pytest-asyncio` | (existente) | Testes async | Todos scanners são async |
| `sqlite_utils` | (existente) | DB operations na migration _007 | Padrão de todas migrations |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `json` (stdlib) | stdlib | Parse de `window.__NUXT__` para Braip | Necessário extrair dados do estado Nuxt |
| `re` (stdlib) | stdlib | Extract external_id de URLs | Padrão HotmartScanner |

### Installation

Sem novas dependências. Toda a stack já está instalada.

```bash
# Nenhum pip install necessário — todas dependências já presentes em v1.0
```

---

## Architecture Patterns

### Estrutura de Arquivos da Phase 14

```
mis/
├── scanners/
│   ├── __init__.py              # Registrar os 4 novos scanners (SCANNER_MAP em scanner.py)
│   ├── eduzz.py                 # EduzzScanner (fallback-only — sem marketplace público)
│   ├── monetizze.py             # MonetizzeScanner (fallback-only — vitrine com login)
│   ├── perfectpay.py            # PerfectPayScanner (fallback-only — checkout platform)
│   └── braip.py                 # BraipScanner (marketplace público — window.__NUXT__)
├── migrations/
│   └── _007_is_stale.py         # ADD COLUMN is_stale BOOLEAN DEFAULT 0 em products
├── platform_ids.py              # EDUZZ_PLATFORM_ID=4 etc. (JÁ EXISTE — não alterar)
├── product_repository.py        # Alterar upsert_product() p/ setar is_stale=False
│                                # + add mark_stale() p/ setar is_stale=True em batch
├── db.py                        # Adicionar import + chamada _run_007
├── scanner.py                   # Adicionar os 4 scanners em SCANNER_MAP
└── tests/
    ├── test_eduzz_scanner.py    # 6 testes (fallback-only: testes 1-4 com HTML vazio, + is_stale)
    ├── test_monetizze_scanner.py # 6 testes (fallback-only)
    ├── test_perfectpay_scanner.py # 6 testes (fallback-only)
    ├── test_braip_scanner.py    # 6 testes (NUXT parsing + is_stale)
    ├── test_migration_007.py    # 3-4 testes padrão _006
    └── fixtures/
        ├── eduzz/               # HTML fixtures (vazio — sem marketplace)
        ├── monetizze/           # HTML fixtures (vazio — vitrine com login)
        ├── perfectpay/          # HTML fixtures (vazio — checkout only)
        └── braip/               # catalog_<niche>.html com window.__NUXT__ real
```

### Pattern 1: PlatformScanner com Fallback Puro (Eduzz, Monetizze, PerfectPay)

**What:** Scanner que sempre retorna `[]` com `alert='marketplace_unavailable'` porque a plataforma não tem marketplace público.
**When to use:** Quando URL de marketplace não existe, retorna 404, ou requer autenticação.

```python
# Source: mis/scanners/hotmart.py (padrão adaptado)
class EduzzScanner(PlatformScanner):
    async def scan_niche(
        self,
        niche_slug: str,
        platform_slug: str,
        niche_id: int = 0,
    ) -> list[Product]:
        """Eduzz marketplace requires authentication — returns [] with alert."""
        log.warning(
            "eduzz_scanner.marketplace_unavailable",
            alert="marketplace_unavailable",
            niche=niche_slug,
            reason="Eduzz vitrine requires login — no public marketplace URL",
        )
        return []
```

### Pattern 2: BraipScanner via window.__NUXT__ (Braip)

**What:** Braip usa Nuxt.js com SSR. Dados de produto embutidos no HTML via `window.__NUXT__` como JSON. Parsing: encontrar o script tag, extrair JSON, navegar até `state.search.products`.
**When to use:** Plataforma com Nuxt.js SSR (dados no estado hidratado do lado servidor).

```python
# Source: Inspeção live de marketplace.braip.com (2026-03-17)
# Estrutura confirmada: window.__NUXT__ contém state.search.products
import json, re

def _extract_nuxt_products(html: str) -> list[dict]:
    """Extract product list from Nuxt.js __NUXT__ state embedded in HTML."""
    match = re.search(r'window\.__NUXT__\s*=\s*(\{.*?\});?\s*</script>', html, re.DOTALL)
    if not match:
        return []
    try:
        nuxt_data = json.loads(match.group(1))
        # Path: state -> search -> products (list of product dicts)
        return nuxt_data.get("state", {}).get("search", {}).get("products", [])
    except (json.JSONDecodeError, KeyError):
        return []
```

**Campos por produto no `window.__NUXT__`:**
```
hash          → external_id (e.g. "proown9j") — MAIS ESTÁVEL, não muda com renomeação
slug          → URL path (e.g. "braip-pages")
title         → nome do produto
price         → valor em centavos (2990 = R$ 29.90) — dividir por 100
src           → URL da imagem (thumbnail_url)
producerName  → nome do produtor
star          → rating float
totalRatings  → contagem de reviews
```

**URL de categoria Braip:**
```
Base: https://marketplace.braip.com/search
Parâmetro: ?categorySlug={slug}
Exemplos de slugs: encapsulados, livros, cursos-online, cosmeticos, mentorias
```

### Pattern 3: Migration _007_is_stale

**What:** Adiciona coluna `is_stale` BOOLEAN DEFAULT 0 na tabela `products`. Idempotente via checagem de colunas existentes.

```python
# Source: mis/migrations/_006_v2_platforms.py (padrão a replicar)
def run_migration_007(db_path: str) -> None:
    db = sqlite_utils.Database(db_path)
    if "products" in db.table_names():
        existing_cols = {col.name for col in db["products"].columns}
        if "is_stale" not in existing_cols:
            db["products"].add_column("is_stale", bool, not_null_default=False)
    db.conn.commit()
```

**Wire em db.py** (adicionar após `_run_006`):
```python
from .migrations._007_is_stale import run_migration_007 as _run_007
# ...dentro de run_migrations():
_run_007(db_path)
```

### Pattern 4: is_stale no upsert

**What:** `upsert_product()` deve setar `is_stale=False` no UPDATE. Nova função `mark_stale()` seta `is_stale=True` em batch por plataforma+nicho quando lista vazia.

```python
# Source: mis/product_repository.py (adaptação do upsert existente)

def mark_stale(db, platform_id: int, niche_id: int) -> None:
    """Mark all products for platform+niche as is_stale=True."""
    db.execute(
        "UPDATE products SET is_stale = 1 WHERE platform_id = ? AND niche_id = ?",
        [platform_id, niche_id],
    )

# No scanner, quando retornar lista vazia:
# mark_stale(db, PLATFORM_ID, niche_id)
```

### Pattern 5: Registro em run_all_scanners()

**What:** `scanner.py` tem SCANNER_MAP hardcoded. Adicionar os 4 novos scanners.

```python
# Source: mis/scanner.py linha 187-191 (padrão a replicar)
from .scanners.eduzz import EduzzScanner
from .scanners.monetizze import MonetizzeScanner
from .scanners.perfectpay import PerfectPayScanner
from .scanners.braip import BraipScanner

SCANNER_MAP = {
    "kiwify": KiwifyScanner,
    "hotmart": HotmartScanner,
    "clickbank": ClickBankScanner,
    "eduzz": EduzzScanner,       # NEW
    "monetizze": MonetizzeScanner, # NEW
    "perfectpay": PerfectPayScanner, # NEW
    "braip": BraipScanner,         # NEW
}
```

### Pattern 6: Config.yaml opt-in por nicho

**What:** Usuário adiciona bloco `eduzz:`, `monetizze:`, `braip:` etc. dentro do bloco `platforms` de cada nicho — mesmo padrão do hotmart/kiwify existente.

```yaml
# Source: mis/config.yaml (padrão existente)
niches:
  - name: "Emagrecimento"
    slug: "emagrecimento"
    platforms:
      hotmart: saude-e-fitness
      kiwify: saude
      braip: encapsulados          # NEW — slug de categoria Braip
      eduzz: saude-bem-estar       # NEW — slug de categoria Eduzz (a confirmar live)
      monetizze: saude             # NEW — slug de categoria Monetizze (a confirmar live)
```

### Anti-Patterns to Avoid

- **Não lançar exceção em scan_niche():** Sempre capturar exceções e retornar `[]` com log. O job APScheduler não pode ser interrompido.
- **Não usar `add_column` sem checar existência:** Migration deve verificar se coluna já existe antes de adicionar (idempotência).
- **Não hardcodar platform_id:** Importar de `mis.platform_ids` (EDUZZ_PLATFORM_ID=4, MONETIZZE_PLATFORM_ID=5, etc.).
- **Não esquecer `db.conn.commit()` após migration:** sqlite_utils não auto-commita em todos os paths (bug verificado na Phase 13).
- **Não parsear NUXT com BeautifulSoup:** O JSON está em um script tag inline — usar `re.search` + `json.loads`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| HTTP client com retry | Custom retry loop | `BaseScraper.fetch()` via `self.fetch()` | tenacity já configurado, 3 tentativas, exponential backoff |
| Upsert idempotente | INSERT + SELECT | `upsert_product()` em product_repository.py | UPDATE-then-INSERT pattern já testado e verde |
| Scan paralelo | asyncio manual | `run_all_scanners()` em scanner.py | `asyncio.gather(return_exceptions=True)` — falha isolada por plataforma |
| Rate limiting por domínio | Sleep manual | `DOMAIN_DELAYS` em base_scraper.py | Adicionar entradas para novos domínios |
| Alert de schema drift | Log customizado | `structlog.warning(alert='schema_drift')` | Padrão estabelecido em todos scanners v1.0 |
| Mock HTTP em testes | monkeypatch | `respx.mock` + `@respx.mock` | Padrão confirmado em test_hotmart e test_kiwify |

**Key insight:** O padrão de scanner está 100% estabelecido. Cada novo scanner é uma subclasse de `PlatformScanner` com um único método `scan_niche()`. A infraestrutura (retry, rate-limit, logging, upsert, scheduler) está pronta — apenas a lógica de parsing muda por plataforma.

---

## Marketplace Status por Plataforma (CONFIRMADO)

### Braip — Marketplace Público CONFIRMADO (HIGH confidence)

- **URL base:** `https://marketplace.braip.com/`
- **URL por categoria:** `https://marketplace.braip.com/search?categorySlug={slug}`
- **Rendering:** Nuxt.js SSR — produtos em `window.__NUXT__` no HTML
- **Acesso sem login:** SIM (confirmado por WebFetch direto)
- **external_id:** `hash` (e.g. `"proown9j"`) — campo estável
- **Campos disponíveis:** title, price (centavos), hash, slug, src (thumbnail), star, totalRatings
- **Slugs de categoria conhecidos:** `encapsulados`, `livros`, `cursos-online`, `cosmeticos`, `mentorias`
- **Slugs adicionais:** a confirmar via inspeção live do menu de categorias

### Eduzz — Sem Marketplace Público (HIGH confidence)

- **Situação:** Eduzz migrou toda operação para `orbita.eduzz.com` (SPA React). Resposta: "You need to enable JavaScript to run this app."
- **Vitrine de afiliados:** Acessível somente dentro do painel autenticado (menu lateral "Vitrine")
- **URLs testadas:** `eduzz.com/marketplace` (404), `eduzz.com/loja` (404), `orbita.eduzz.com/marketplace` (SPA vazia), `orbita.eduzz.com/affiliate/store` (SPA vazia)
- **Estratégia Phase 14:** Implementar fallback puro — `scan_niche()` retorna `[]` + `alert='marketplace_unavailable'`

### Monetizze — Vitrine Requer Autenticação (HIGH confidence)

- **Situação:** Vitrine de afiliados acessível somente via painel autenticado (`app.monetizze.com.br`). Acesso direto retorna 403.
- **Documentação oficial:** "acesse a aba Vitrine de Afiliação no menu lateral do painel" — requer conta ativa.
- **URL testada:** `app.monetizze.com.br/r/vitrine` retorna HTTP 403
- **Estratégia Phase 14:** Implementar fallback puro — `scan_niche()` retorna `[]` + `alert='marketplace_unavailable'`

### PerfectPay — Checkout Platform sem Marketplace (HIGH confidence)

- **Situação:** PerfectPay é plataforma de checkout e gestão de pagamentos. Não tem marketplace centralizado público.
- **Documentação oficial confirma:** Vitrine de produtos é funcionalidade interna para afiliados logados em `app.perfectpay.com.br`.
- **Estratégia Phase 14:** Implementar fallback puro — `scan_niche()` retorna `[]` + `alert='marketplace_unavailable'`

---

## Common Pitfalls

### Pitfall 1: window.__NUXT__ com JSON incompleto

**What goes wrong:** Nuxt.js pode serializar o estado em múltiplos scripts ou usar `__NUXT_DATA__` em versões mais recentes. Regex simples pode capturar apenas parte do JSON.
**Why it happens:** Nuxt 3 mudou o formato do estado hidratado de `window.__NUXT__` para `window.__NUXT_DATA__` (array de arrays) em versões recentes.
**How to avoid:** Criar fixture HTML real capturada ao vivo. Testar o regex contra a fixture antes de deployar. Ter fallback selector se `window.__NUXT__` falhar (tentar `window.__NUXT_DATA__`).
**Warning signs:** `json.JSONDecodeError` durante parse — logar como `alert='schema_drift'` e retornar `[]`.

### Pitfall 2: is_stale NÃO resetado no upsert existente

**What goes wrong:** `upsert_product()` atual não conhece o campo `is_stale`. Se migration _007 adiciona a coluna mas upsert não a seta, todos produtos que recebem update no rank ficam com `is_stale=NULL` ou valor residual.
**Why it happens:** `upsert_product()` faz UPDATE de campos fixos hardcoded — não tem `ALTER TABLE` awareness.
**How to avoid:** Adicionar `is_stale = 0` (False) no bloco `SET` do UPDATE em `upsert_product()`. E no INSERT também. Checar que migration já rodou antes de assumir que a coluna existe.
**Warning signs:** Testes de is_stale passam mas produtos na UI aparecem com stale=True mesmo após scan bem-sucedido.

### Pitfall 3: Braip paginação

**What goes wrong:** `window.__NUXT__` na primeira página retorna 12 produtos (`productMetaPerPage=12`). Chamadas sem paginação retornam apenas a primeira página.
**Why it happens:** Braip usa lazy loading / paginação server-side via query param.
**How to avoid:** Implementar loop de paginação via `?page={n}` até `productMetaLastPage`. Ou limitar ao topo (rank=1..N, onde N ≤ 12 por página, página 1 = top produtos). Documentar a decisão no código.
**Warning signs:** Scan retorna exatamente 12 produtos em todo niche — sem variação.

### Pitfall 4: DOMAIN_DELAYS não atualizado

**What goes wrong:** `BaseScraper.fetch()` usa `DOMAIN_DELAYS` para rate limiting. Domínios novos usam `DEFAULT_DELAY=2.0` (ok), mas sem entrada explícita o log não identifica o domínio com delay intencional.
**Why it happens:** `DOMAIN_DELAYS` em `base_scraper.py` só tem hotmart, kiwify, clickbank.
**How to avoid:** Adicionar entradas explícitas para `marketplace.braip.com` (e os demais) com 2.0s.

### Pitfall 5: run_all_scanners() não injeta niche_id para novos scanners

**What goes wrong:** `run_all_scanners()` tem lógica de `niche_id_map` que injeta niche_id resolvido após o scan. Scanners de fallback que retornam `[]` não precisam disso, mas se marcam `is_stale`, precisam do `niche_id` para o WHERE clause da query.
**Why it happens:** Scanners de fallback precisam de `niche_id` para `mark_stale(db, platform_id, niche_id)` mas recebem `niche_id=0` por default quando chamados sem o argumento.
**How to avoid:** Passar `niche_id` explicitamente na chamada de `scan_niche()` dentro de `run_all_scanners()`. Verificar que `_run_one()` passa o niche_id resolvido do `niche_id_map`.

---

## Code Examples

### Exemplo 1: BraipScanner — Extração via window.__NUXT__

```python
# Source: Análise de marketplace.braip.com (2026-03-17)
import json
import re
from mis.platform_ids import BRAIP_PLATFORM_ID
from mis.scanner import PlatformScanner, Product

BRAIP_MARKETPLACE_URL = "https://marketplace.braip.com/search"

def _parse_nuxt_products(html: str, niche_id: int) -> list[Product]:
    """Parse products from Braip's window.__NUXT__ state."""
    match = re.search(r'window\.__NUXT__\s*=\s*(\{.+?\});\s*</script>', html, re.DOTALL)
    if not match:
        return []
    try:
        nuxt_data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return []

    raw_products = nuxt_data.get("state", {}).get("search", {}).get("products", [])
    products = []
    for rank, item in enumerate(raw_products, start=1):
        hash_id = item.get("hash")
        if not hash_id:
            continue
        price_cents = item.get("price")
        products.append(Product(
            external_id=hash_id,                    # hash é o mais estável
            title=item.get("title", hash_id),
            url=f"https://marketplace.braip.com/{item.get('slug', hash_id)}",
            platform_id=BRAIP_PLATFORM_ID,
            niche_id=niche_id,
            rank=rank,
            price=price_cents / 100.0 if price_cents else None,
            rating=item.get("star"),
            thumbnail_url=item.get("src"),
        ))
    return products
```

### Exemplo 2: Scanner de Fallback Puro (Eduzz, Monetizze, PerfectPay)

```python
# Source: Padrão hotmart.py + decisão de CONTEXT.md
import structlog
from mis.scanner import PlatformScanner, Product
from mis.platform_ids import EDUZZ_PLATFORM_ID

log = structlog.get_logger(__name__)

class EduzzScanner(PlatformScanner):
    """Eduzz scanner — marketplace requer autenticação. Retorna fallback."""

    async def scan_niche(
        self,
        niche_slug: str,
        platform_slug: str,
        niche_id: int = 0,
    ) -> list[Product]:
        log.warning(
            "eduzz_scanner.marketplace_unavailable",
            alert="marketplace_unavailable",
            niche=niche_slug,
            platform_slug=platform_slug,
            reason="Eduzz vitrine requires authentication — no public marketplace",
        )
        return []
```

### Exemplo 3: Migration _007_is_stale

```python
# Source: mis/migrations/_006_v2_platforms.py (padrão replicado)
import sqlite_utils

def run_migration_007(db_path: str) -> None:
    """Add is_stale column to products table.

    Idempotent: safe to run multiple times.
    """
    db = sqlite_utils.Database(db_path)
    if "products" in db.table_names():
        existing_cols = {col.name for col in db["products"].columns}
        if "is_stale" not in existing_cols:
            db["products"].add_column("is_stale", bool, not_null_default=False)
    db.conn.commit()
```

### Exemplo 4: test_is_stale (6º teste — padrão para todos 4 scanners)

```python
# Source: mis/tests/test_hotmart_scanner.py (padrão do test_upsert_no_duplicates adaptado)
@pytest.mark.asyncio
async def test_is_stale(tmp_path):
    """is_stale=True when scan returns []; is_stale=False when products arrive."""
    from mis.db import get_db, run_migrations
    from mis.product_repository import upsert_product, mark_stale
    from mis.scanner import Product

    db_path = str(tmp_path / "mis.db")
    run_migrations(db_path)  # inclui migration _007
    db = get_db(db_path)

    # Setup: inserir produto
    product = Product(
        external_id="test-hash-001",
        title="Produto Teste",
        url="https://marketplace.braip.com/produto-teste",
        platform_id=BRAIP_PLATFORM_ID,
        niche_id=1,
        rank=1,
        price=97.0,
    )
    upsert_product(db, product)  # is_stale deve ser False após upsert normal

    row = list(db.execute(
        "SELECT is_stale FROM products WHERE platform_id=? AND external_id=?",
        [BRAIP_PLATFORM_ID, "test-hash-001"],
    ))[0]
    assert row[0] == 0, "is_stale deve ser False/0 após upsert com produto"

    # Marcar como stale (simula scan retornando [])
    mark_stale(db, BRAIP_PLATFORM_ID, 1)
    row = list(db.execute(
        "SELECT is_stale FROM products WHERE platform_id=? AND external_id=?",
        [BRAIP_PLATFORM_ID, "test-hash-001"],
    ))[0]
    assert row[0] == 1, "is_stale deve ser True/1 após mark_stale()"

    # Upsert novamente — deve resetar is_stale para False
    upsert_product(db, product)
    row = list(db.execute(
        "SELECT is_stale FROM products WHERE platform_id=? AND external_id=?",
        [BRAIP_PLATFORM_ID, "test-hash-001"],
    ))[0]
    assert row[0] == 0, "is_stale deve ser resetado para False/0 após upsert"
```

### Exemplo 5: Dashboard filter — nenhuma mudança necessária

```python
# Source: mis/web/routes/ranking.py linhas 40-45
# O filtro de plataforma já funciona via:
# SELECT DISTINCT slug, name FROM platforms ORDER BY NAME
# + filtragem em dossier_repository.list_dossiers_by_rank(platform=platform)
# Basta que as platforms existam no DB (migration _006 já inseriu Eduzz=4,
# Monetizze=5, PerfectPay=6, Braip=7) e que existam produtos com esses platform_ids.
# Nenhuma mudança no código da rota /ranking é necessária.
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Eduzz em `eduzz.com/marketplace` | `orbita.eduzz.com` SPA (sem marketplace público) | ~2023-2024 | Scanner de fallback necessário |
| Monetizze com vitrine pública | Vitrine somente para afiliados autenticados | Desconhecido | Scanner de fallback necessário |
| Nuxt 2 `window.__NUXT__` (objeto) | Nuxt 3 pode usar `window.__NUXT_DATA__` (array) | Nuxt 3 estável 2023 | Braip pode migrar; regex deve checar ambos formatos |

**Deprecated/outdated:**
- `eduzz.com/marketplace`: retorna 404 em 2026-03-17 — não usar esta URL
- `eduzz.com/loja`: retorna 404 em 2026-03-17 — não usar esta URL

---

## Open Questions

1. **Slugs de categoria Braip além de `encapsulados`, `livros`, `cursos-online`**
   - What we know: URL `marketplace.braip.com/search?categorySlug=cursos-online` funciona
   - What's unclear: Lista completa de slugs válidos por nicho (marketing-digital, emagrecimento, financas-pessoais)
   - Recommendation: Researcher captura a lista de categorias da home `marketplace.braip.com` — o menu de categorias lista todos slugs disponíveis

2. **Braip Nuxt versão — `window.__NUXT__` vs `window.__NUXT_DATA__`**
   - What we know: Inspeção de 2026-03-17 retornou `window.__NUXT__` com objeto JSON e `state.search.products`
   - What's unclear: Se Braip migrou para Nuxt 3 recentemente (usa array `__NUXT_DATA__`)
   - Recommendation: Capturar fixture HTML real ao vivo e testar o regex antes de escrever o parser. Implementar fallback para ambos formatos.

3. **Braip paginação — quantas páginas buscar**
   - What we know: 12 produtos por página, `productMetaLastPage` disponível no NUXT state
   - What's unclear: Se vale a pena paginar além da primeira página para top-ranking
   - Recommendation: Implementar com 1 página (top 12) na Phase 14. Paginação pode ser adicionada como enhancement.

4. **Eduzz futuro — planos para marketplace público**
   - What we know: Atualmente SPA com vitrine somente autenticada
   - What's unclear: Se Eduzz planeja expor API pública ou marketplace sem login
   - Recommendation: Scanner de fallback registrado e funcional. Quando Eduzz liberar, apenas `scan_niche()` precisa ser reimplementado — a estrutura do scanner permanece.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest + pytest-asyncio |
| Config file | `mis/pytest.ini` ou `setup.cfg` (existente) |
| Quick run command | `python -m pytest mis/tests/test_braip_scanner.py -x -q` |
| Full suite command | `python -m pytest mis/tests/ -x -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SCAN-BR-01 | EduzzScanner.scan_niche() retorna [] + alert='marketplace_unavailable' | unit | `pytest mis/tests/test_eduzz_scanner.py -x` | ❌ Wave 0 |
| SCAN-BR-01 | EduzzScanner.scan_niche() sets is_stale=True em produtos existentes | unit | `pytest mis/tests/test_eduzz_scanner.py::test_is_stale -x` | ❌ Wave 0 |
| SCAN-BR-02 | MonetizzeScanner.scan_niche() retorna [] + alert='marketplace_unavailable' | unit | `pytest mis/tests/test_monetizze_scanner.py -x` | ❌ Wave 0 |
| SCAN-BR-02 | MonetizzeScanner is_stale behavior | unit | `pytest mis/tests/test_monetizze_scanner.py::test_is_stale -x` | ❌ Wave 0 |
| SCAN-BR-03 | PerfectPayScanner.scan_niche() retorna [] + alert | unit | `pytest mis/tests/test_perfectpay_scanner.py -x` | ❌ Wave 0 |
| SCAN-BR-03 | PerfectPayScanner is_stale behavior | unit | `pytest mis/tests/test_perfectpay_scanner.py::test_is_stale -x` | ❌ Wave 0 |
| SCAN-BR-04 | BraipScanner happy path: retorna produtos com external_id=hash, price=float | unit | `pytest mis/tests/test_braip_scanner.py::test_happy_path -x` | ❌ Wave 0 |
| SCAN-BR-04 | BraipScanner field types: rank int, price float, external_id str | unit | `pytest mis/tests/test_braip_scanner.py::test_field_types -x` | ❌ Wave 0 |
| SCAN-BR-04 | BraipScanner fallback selector quando NUXT ausente | unit | `pytest mis/tests/test_braip_scanner.py::test_fallback_selector -x` | ❌ Wave 0 |
| SCAN-BR-04 | BraipScanner schema_drift alert quando NUXT e fallback falham | unit | `pytest mis/tests/test_braip_scanner.py::test_drift_alert -x` | ❌ Wave 0 |
| SCAN-BR-04 | BraipScanner upsert idempotente (re-run não duplica) | unit | `pytest mis/tests/test_braip_scanner.py::test_upsert_no_duplicates -x` | ❌ Wave 0 |
| SCAN-BR-04 | BraipScanner is_stale behavior | unit | `pytest mis/tests/test_braip_scanner.py::test_is_stale -x` | ❌ Wave 0 |
| _007 migration | is_stale coluna adicionada, idempotente, default=False | unit | `pytest mis/tests/test_migration_007.py -x` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `python -m pytest mis/tests/test_{scanner_being_implemented}.py -x -q`
- **Per wave merge:** `python -m pytest mis/tests/ -x -q`
- **Phase gate:** Full suite green antes do `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `mis/tests/test_eduzz_scanner.py` — 6 testes SCAN-BR-01 (fallback-only)
- [ ] `mis/tests/test_monetizze_scanner.py` — 6 testes SCAN-BR-02 (fallback-only)
- [ ] `mis/tests/test_perfectpay_scanner.py` — 6 testes SCAN-BR-03 (fallback-only)
- [ ] `mis/tests/test_braip_scanner.py` — 6 testes SCAN-BR-04 (NUXT parsing)
- [ ] `mis/tests/test_migration_007.py` — 3-4 testes migration _007
- [ ] `mis/tests/fixtures/braip/catalog_cursos-online.html` — fixture HTML real capturada ao vivo
- [ ] `mis/tests/fixtures/eduzz/` — pasta vazia (scanner de fallback, sem fixture necessária)
- [ ] `mis/tests/fixtures/monetizze/` — pasta vazia
- [ ] `mis/tests/fixtures/perfectpay/` — pasta vazia
- [ ] `mis/scanners/eduzz.py`, `monetizze.py`, `perfectpay.py`, `braip.py` — implementações
- [ ] `mis/migrations/_007_is_stale.py` — migration
- [ ] Atualizar `mis/product_repository.py` — `upsert_product()` + nova função `mark_stale()`
- [ ] Atualizar `mis/db.py` — import + chamada `_run_007`
- [ ] Atualizar `mis/scanner.py` — SCANNER_MAP com 4 novos scanners

---

## Sources

### Primary (HIGH confidence)

- `mis/scanners/hotmart.py` — padrão de referência para scanner SSR, fallback selectors, logging
- `mis/scanners/kiwify.py` — padrão de referência para extractor functions por selector
- `mis/tests/test_hotmart_scanner.py` — estrutura canônica dos 5 testes + como escrever o 6º
- `mis/tests/test_kiwify_scanner.py` — confirmação do padrão de testes
- `mis/migrations/_006_v2_platforms.py` — padrão de migration (add_column + idempotency)
- `mis/db.py` — como registrar nova migration
- `mis/scanner.py` — SCANNER_MAP e run_all_scanners() — onde registrar novos scanners
- `mis/product_repository.py` — upsert_product() que precisa ser atualizado para is_stale
- `mis/platform_ids.py` — EDUZZ=4, MONETIZZE=5, PERFECTPAY=6, BRAIP=7 (confirmado)
- `mis/base_scraper.py` — DOMAIN_DELAYS, fetch(), fetch_spa() — entender rate limiting
- `mis/web/routes/ranking.py` — confirma que filtro de plataforma não precisa de mudança
- `mis/tests/conftest.py` — fixture `db_path` reutilizável em todos testes
- WebFetch `marketplace.braip.com` (2026-03-17) — confirma: SSR Nuxt.js, `window.__NUXT__`, `hash` como external_id, `?categorySlug=` como URL pattern
- WebFetch `orbita.eduzz.com/marketplace` (2026-03-17) — confirma: SPA React, sem marketplace público
- WebFetch `app.monetizze.com.br/r/vitrine` (2026-03-17) — confirma: 403 sem autenticação

### Secondary (MEDIUM confidence)

- WebFetch `perfectpay.com.br` — confirma: plataforma de checkout, não marketplace público
- WebSearch Braip — confirma URL `marketplace.braip.com` e slugs de categoria

### Tertiary (LOW confidence)

- WebSearch Eduzz — referências a "Órbita" como plataforma atual; sem URL de marketplace público identificada
- WebSearch Monetizze — confirma vitrine de afiliados mas sem URL pública verificada diretamente

---

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — sem novas dependências, padrão completamente estabelecido no código v1.0
- Architecture patterns: HIGH para BraipScanner (confirmado por WebFetch) e fallback scanners (padrão do CONTEXT.md); MEDIUM para slugs de categoria (precisam de inspeção live)
- Marketplace URLs: HIGH para Braip (verificado), HIGH para Eduzz/Monetizze/PerfectPay (sem marketplace público confirmado por múltiplas fontes)
- Test patterns: HIGH — replicação direta de test_hotmart e test_kiwify com 6º teste adicionado
- Migration _007: HIGH — replicação direta de _006 pattern com uma coluna simples

**Research date:** 2026-03-17
**Valid until:** 2026-04-17 (stable pattern) — ressalva: Braip pode migrar Nuxt version; verificar window.__NUXT__ vs window.__NUXT_DATA__ ao capturar fixture ao vivo
