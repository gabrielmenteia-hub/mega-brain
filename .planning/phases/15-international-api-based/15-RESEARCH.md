# Phase 15: International API-Based - Research

**Researched:** 2026-03-17
**Domain:** Product Hunt GraphQL API v2 + Udemy Affiliate API v2.0 (deprecated)
**Confidence:** MEDIUM — Product Hunt HIGH, Udemy CRITICAL BLOCKER (see below)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Product Hunt scanner:**
- `rank` = posição no trending (1, 2, 3...) — não votesCount bruto
- `rank_type` = `'position'`
- Período: `today` (trending do dia)
- Paginação: 2 requisições GraphQL com cursor (first: 20 + afterCursor) → top 40 produtos
- `external_id` = slug do produto (ex: `'jarvis-ai-assistant'`) — estável e legível
- `price` = preço inicial se disponível na API; `None` se ausente/nulo
- `thumbnail_url` = `thumbnail.imageUrl` da API — armazenar
- `url` = URL da página no Product Hunt (`producthunt.com/posts/...`), não o site externo
- Autenticação: `Bearer PRODUCT_HUNT_API_TOKEN` no header `Authorization`
- Endpoint: `https://api.producthunt.com/v2/api/graphql`
- Trending geral sem filtro por categoria — `scan_niche()` ignora `niche_slug` e retorna os mesmos 40 produtos para qualquer nicho
- Duplicatas entre nichos resolvidas por `INSERT OR IGNORE` via UNIQUE index `(external_id, platform_id)` já existente

**Udemy scanner:**
- Endpoint: `GET /api-2.0/courses/` com params `?search=<keyword>&ordering=most-reviewed&category=<cat>&page_size=20`
- Ordering: `most-reviewed`
- Top 20 cursos por nicho (page_size=20), 1 requisição por nicho
- Autenticação: Basic Auth com base64 de `UDEMY_CLIENT_ID:UDEMY_CLIENT_SECRET`
- `external_id` = ID numérico do curso (campo `'id'`)
- `rank_type` = `'enrollment'`
- `price` = `price_detail.amount` em USD
- `rating` = `avg_rating` (escala 0-5)
- `thumbnail_url` = `image_480x270`

**Config.yaml slugs:**
- Adicionar `product_hunt: trending` e `udemy: <category>` a todos os nichos
- Udemy: Marketing Digital → `"Marketing"`, Emagrecimento → `"Health & Fitness"`, Finanças → `"Finance & Accounting"`

**Credenciais ausentes:**
- `PRODUCT_HUNT_API_TOKEN` ausente → `return []` + `log.warning(alert='missing_credentials')`
- `UDEMY_CLIENT_ID` / `UDEMY_CLIENT_SECRET` ausentes → `return []` + `log.warning(alert='missing_credentials')`

**Rate limiting (DOMAIN_DELAYS):**
- `"api.producthunt.com": 1.0`
- `"www.udemy.com": 0.5`

**Testes:**
- Fixtures JSON: `mis/tests/fixtures/product_hunt/trending_today.json` e `mis/tests/fixtures/udemy/courses_marketing.json`
- Cobertura: retorno normal, credenciais ausentes (`missing_credentials`), resposta vazia da API

### Claude's Discretion
- Estrutura exata da query GraphQL do Product Hunt (campos específicos a solicitar)
- Formato exato dos fixtures JSON
- Valores precisos dos IDs numéricos de categoria Udemy (confirmar via pesquisa)
- Wiring de `rank_type` no `product_repository.upsert_product()` — se via campo extra no `Product` dataclass ou outro mecanismo já existente da INFRA-03

### Deferred Ideas (OUT OF SCOPE)
- Nenhuma ideia de escopo extra surgiu
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SCAN-INTL-01 | `ProductHuntScanner` busca trending products via GraphQL API usando `PH_ACCESS_TOKEN` | GraphQL v2 API confirmado ativo; schema verificado; thumbnail.url (não imageUrl); Bearer token auth |
| SCAN-INTL-02 | `UdemyScanner` busca top cursos por nicho via REST `/api-2.0/courses/` | BLOQUEADOR CRÍTICO: Udemy Affiliate API descontinuada em 01/01/2025; decisão de abordagem necessária |
</phase_requirements>

---

## Summary

Phase 15 implementa dois scanners internacionais com APIs oficiais. O ProductHuntScanner é straightforward: a API GraphQL v2 está ativa, documentada, e segue exatamente o padrão do ClickBankScanner existente (POST + Bearer token). A query GraphQL para posts com `featured: true` e `postedAfter`/`postedBefore` para o dia de hoje retorna dados paginados com cursor.

**BLOQUEADOR CRÍTICO para UdemyScanner:** A Udemy Affiliate API v2.0 foi oficialmente descontinuada em 01/01/2025. O endpoint `/api-2.0/courses/` que estava documentado nas decisões já não está disponível. Múltiplas fontes confirmam isso: Pydemy (wrapper oficial Python), Content Egg Pro, e a própria documentação Udemy. O planner precisa decidir entre: (a) implementar UdemyScanner como fallback-only com `alert='api_discontinued'`, similar ao EduzzScanner, e documentar a descontinuação claramente; ou (b) pesquisar se credenciais antigas ainda funcionam (o endpoint pode ainda responder para tokens legados).

**Recomendação:** Implementar UdemyScanner como scanner condicional — tenta o endpoint `/api-2.0/courses/` e, se receber 401/403/404, faz fallback gracioso com `alert='api_discontinued'`. Isso preserva a arquitetura sem criar débito técnico. A decisão final cabe ao usuário, mas o planner deve expor esse risco no PLAN.md.

**Primary recommendation:** ProductHunt - use posts query com `featured: true, postedAfter: <hoje 00:00>, first: 20` e cursor pagination. Udemy - implementar com tentativa real + fallback gracioso dado risco de descontinuação.

---

## Standard Stack

### Core (já presente no projeto)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| httpx | existente | HTTP async client para API calls | Já é base do BaseScraper; suporte http2 |
| structlog | existente | Structured logging com alert= fields | Padrão MIS para log.warning(alert=...) |
| base64 | stdlib | Encode `CLIENT_ID:SECRET` para Basic Auth | Stdlib Python, sem dependência extra |

### Sem novas dependências necessárias
Ambos os scanners usam apenas httpx (já instalado) via `self._base._client` para POST/GET com headers customizados — exatamente como ClickBankScanner já faz.

## Architecture Patterns

### Recommended Project Structure (novos arquivos)
```
mis/
├── scanners/
│   ├── product_hunt.py        # ProductHuntScanner — GraphQL v2
│   └── udemy.py               # UdemyScanner — REST API v2 (com fallback gracioso)
├── tests/
│   ├── test_product_hunt_scanner.py
│   ├── test_udemy_scanner.py
│   └── fixtures/
│       ├── product_hunt/
│       │   └── trending_today.json    # Fixture capturada ao vivo
│       └── udemy/
│           └── courses_marketing.json # Fixture capturada ao vivo
```

### Pattern 1: ProductHuntScanner — GraphQL com Bearer Token + Cursor Pagination
**What:** POST para `https://api.producthunt.com/v2/api/graphql` com Authorization Bearer token, usando posts query com `featured: true` e range de data para hoje, cursor pagination para top 40.
**When to use:** Scanner de trending products do Product Hunt.

**GraphQL Query verificada contra schema oficial:**
```python
# Source: github.com/producthunt/producthunt-api/blob/master/schema.graphql
TRENDING_TODAY_QUERY = """
query TrendingToday($after: String) {
  posts(
    featured: true
    postedAfter: "{today_00_00}"
    postedBefore: "{today_23_59}"
    order: VOTES
    first: 20
    after: $after
  ) {
    edges {
      node {
        id
        name
        tagline
        slug
        url
        votesCount
        thumbnail {
          url
        }
        website
        pricingType
      }
    }
    pageInfo {
      endCursor
      hasNextPage
    }
  }
}
"""
```

**NOTA CRÍTICA sobre thumbnail:** O schema oficial confirma que `thumbnail` é do tipo `Media` com campo `url: String!` (não `imageUrl`). A decisão em CONTEXT.md referencia `thumbnail.imageUrl` mas o schema real é `thumbnail.url`. O planner deve resolver isso — usar `thumbnail.url` conforme o schema oficial.

**Auth pattern (mesmo que ClickBankScanner):**
```python
# Source: padrão existente em mis/scanners/clickbank.py
async def _post_graphql(self, query: str, variables: dict) -> str:
    client: httpx.AsyncClient = self._base._client
    headers = {
        "Authorization": f"Bearer {os.environ.get('PRODUCT_HUNT_API_TOKEN', '')}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = json.dumps({"query": query, "variables": variables})
    response = await client.post(PRODUCT_HUNT_GRAPHQL_URL, content=payload, headers=headers)
    response.raise_for_status()
    return response.text
```

**Credencial ausente:**
```python
# Source: padrão existente em mis/scanners/eduzz.py
token = os.environ.get("PRODUCT_HUNT_API_TOKEN")
if not token:
    log.warning(
        "product_hunt_scanner.missing_credentials",
        alert="missing_credentials",
        reason="PRODUCT_HUNT_API_TOKEN not set",
    )
    return []
```

**rank semantics:** `rank` = posição na lista ordenada (1=primeiro), não `votesCount`. `votesCount` pode ser armazenado como... não há campo no `Product` dataclass para isso. O planner deve verificar se `rank = votesCount` (decisão CONTEXT.md inicial) ou `rank = position` (decisão final em CONTEXT.md). **Decisão final: rank = posição (1, 2, 3...).**

### Pattern 2: UdemyScanner — REST Basic Auth (com risco de API descontinuada)
**What:** GET para `https://www.udemy.com/api-2.0/courses/` com Basic Auth `base64(CLIENT_ID:SECRET)`, filtrando por categoria e ordenando por `most-reviewed`.

**SITUAÇÃO ATUAL DA API:** A Udemy Affiliate API foi descontinuada em 01/01/2025. O endpoint pode não responder. O planner deve incluir fallback gracioso.

**Implementação sugerida (condicional):**
```python
# Basic Auth encoding
import base64, os

client_id = os.environ.get("UDEMY_CLIENT_ID")
client_secret = os.environ.get("UDEMY_CLIENT_SECRET")

if not client_id or not client_secret:
    log.warning(
        "udemy_scanner.missing_credentials",
        alert="missing_credentials",
        reason="UDEMY_CLIENT_ID or UDEMY_CLIENT_SECRET not set",
    )
    return []

credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
headers = {
    "Authorization": f"Basic {credentials}",
    "Accept": "application/json",
}
```

**Request pattern:**
```python
# Source: Udemy Affiliate API v2.0 docs (arquivado — API descontinuada 01/01/2025)
url = "https://www.udemy.com/api-2.0/courses/"
params = {
    "search": niche_keyword,   # ex: "marketing digital"
    "ordering": "most-reviewed",
    "category": category_slug,  # ex: "Marketing"
    "page_size": 20,
    "fields[course]": "id,title,url,price_detail,avg_rating,image_480x270",
}
```

**Response fields (baseado em documentação arquivada):**
```json
{
  "results": [
    {
      "id": 1234567,
      "title": "Complete Digital Marketing Course",
      "url": "/course/digital-marketing/",
      "price_detail": {"amount": 19.99, "currency": "USD"},
      "avg_rating": 4.6,
      "image_480x270": "https://img-c.udemycdn.com/course/480x270/..."
    }
  ]
}
```

**Produto construído:**
- `external_id` = `str(course["id"])` — ID numérico como string
- `url` = `"https://www.udemy.com" + course["url"]` (API retorna path relativo)
- `rank` = posição na lista (1-indexed)
- `price` = `course["price_detail"]["amount"]` se presente, else `None`
- `rating` = `course["avg_rating"]` se presente, else `None`
- `thumbnail_url` = `course["image_480x270"]` se presente, else `None`

### Pattern 3: Fallback gracioso para API descontinuada (Udemy)
**O planner deve incluir:**
```python
# Em caso de HTTP 401/403/404 ou ConnectionError
except (httpx.HTTPStatusError, Exception) as exc:
    log.warning(
        "udemy_scanner.api_unavailable",
        alert="api_discontinued",
        error=str(exc),
        reason="Udemy Affiliate API deprecated 2025-01-01",
    )
    return []
```

### Pattern 4: Registro no SCANNER_MAP (scanner.py)
**O planner deve adicionar** ao bloco de imports e SCANNER_MAP em `run_all_scanners()`:
```python
from .scanners.product_hunt import ProductHuntScanner
from .scanners.udemy import UdemyScanner

SCANNER_MAP = {
    ...existing...,
    "product_hunt": ProductHuntScanner,
    "udemy": UdemyScanner,
}
```

### Anti-Patterns to Avoid
- **Usar `thumbnail.imageUrl`:** O schema real usa `thumbnail.url`. `imageUrl` não existe no Media type.
- **Assumir que a Udemy API ainda funciona:** API oficialmente descontinuada em 01/01/2025 — sempre tratar 401/403/404 como fallback gracioso.
- **Usar `votesCount` como rank:** A decisão final em CONTEXT.md é rank = posição (1, 2, 3...), não votesCount bruto.
- **`price` no Product Hunt como campo obrigatório:** A API do PH não retorna preço de forma confiável — `price` sempre `None` para ProductHuntScanner (campo `pricingType` existe mas não é valor monetário).
- **URL relativa da Udemy:** A API retorna `/course/slug/` — prefixar com `https://www.udemy.com`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| HTTP retry/rate limiting | Custom retry loop | `BaseScraper.fetch()` + `DOMAIN_DELAYS` | Já implementado com tenacity; basta adicionar domínio ao dict |
| POST com headers customizados | Novo client httpx | `self._base._client.post()` | Padrão estabelecido pelo ClickBankScanner |
| Basic Auth encoding | Lib externa | `base64.b64encode()` stdlib | Uma linha, zero deps |
| Cursor pagination | Lógica custom | Loop `while hasNextPage` com `after=endCursor` | 2 iterações fixas conforme decisão (top 40) |
| Deduplicação cross-niche | UNIQUE check manual | `INSERT OR IGNORE` via `upsert_product()` | UNIQUE index `(external_id, platform_id)` já criado pela migration |

**Key insight:** Todos os patterns de infraestrutura (retry, rate limiting, logging, upsert, mark_stale) já existem — novos scanners são apenas adaptadores de API dentro do envelope do PlatformScanner ABC.

---

## Common Pitfalls

### Pitfall 1: `thumbnail.imageUrl` não existe no schema
**What goes wrong:** `KeyError` ou `None` ao tentar `node["thumbnail"]["imageUrl"]`
**Why it happens:** CONTEXT.md referencia `thumbnail.imageUrl` mas o schema GraphQL real (verificado em producthunt/producthunt-api) define `Media.url` não `imageUrl`
**How to avoid:** Usar `thumbnail["url"]` — campo `url` recebe parâmetros opcionais `height` e `width`
**Warning signs:** Response JSON com `thumbnail: {"type": "image", "url": "..."}` sem campo `imageUrl`

### Pitfall 2: Udemy API descontinuada em 01/01/2025
**What goes wrong:** Requests para `/api-2.0/courses/` retornam 401 ou 404 — scanner sempre retorna `[]`
**Why it happens:** Udemy encerrou o programa de Affiliate API — confirmado por múltiplas fontes
**How to avoid:** Implementar com try/except que captura HTTP errors e retorna `[]` com `alert='api_discontinued'`
**Warning signs:** Resposta 401 imediata mesmo com credenciais válidas

### Pitfall 3: Date range para "hoje" em UTC
**What goes wrong:** `postedAfter` em fuso horário errado perde posts do início do dia
**Why it happens:** Product Hunt opera em UTC — posts às 00:01 PST são do dia anterior em UTC
**How to avoid:** Usar `datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)` como `postedAfter`
**Warning signs:** Lista de trending retornando menos produtos do que esperado no período da manhã

### Pitfall 4: Product Hunt posts com `thumbnail: null`
**What goes wrong:** `NoneType` ao acessar `node["thumbnail"]["url"]`
**Why it happens:** `thumbnail` é `Media` (nullable) — o schema permite `null`
**How to avoid:** `thumbnail_url = node.get("thumbnail", {}) or {}; thumbnail_url = thumbnail_url.get("url") or None`
**Warning signs:** `TypeError` durante parse de nodes individuais

### Pitfall 5: Cursor pagination com `hasNextPage` falso na segunda page
**What goes wrong:** Segunda requisição retorna 0 resultados se há menos de 40 posts trending hoje
**Why it happens:** Em dias com poucos lançamentos, `hasNextPage` pode ser False após primeira page
**How to avoid:** Checar `hasNextPage` antes de fazer segunda requisição; não assumir sempre 2 pages
**Warning signs:** `pageInfo.hasNextPage = false` na resposta da primeira requisição

### Pitfall 6: UdemyScanner com `url` relativa
**What goes wrong:** `url` armazenada como `/course/nome-do-curso/` sem domínio base
**Why it happens:** API Udemy retorna paths relativos no campo `url`
**How to avoid:** Sempre prefixar: `url = "https://www.udemy.com" + course.get("url", "")`
**Warning signs:** URLs começando com `/course/` no DB

### Pitfall 7: `price_detail` pode ser `None` na Udemy
**What goes wrong:** `AttributeError` ou `TypeError` ao fazer `price_detail["amount"]`
**Why it happens:** Cursos gratuitos ou com preço variável podem ter `price_detail: null`
**How to avoid:** `price = (course.get("price_detail") or {}).get("amount") or None`
**Warning signs:** Cursos com preço `None` quando API retornou `price_detail: null`

---

## Code Examples

### Product Hunt — query completa com paginação
```python
# Source: schema verificado em github.com/producthunt/producthunt-api/blob/master/schema.graphql
import json
from datetime import datetime, timezone

def _build_posts_query() -> tuple[str, dict]:
    """Build GraphQL query for today's trending posts."""
    today = datetime.now(timezone.utc)
    posted_after = today.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    posted_before = today.replace(hour=23, minute=59, second=59, microsecond=0).isoformat()

    query = """
    query TrendingToday($after: String) {
      posts(
        featured: true
        postedAfter: "%s"
        postedBefore: "%s"
        order: VOTES
        first: 20
        after: $after
      ) {
        edges {
          node {
            id
            name
            tagline
            slug
            url
            votesCount
            thumbnail {
              url
            }
          }
        }
        pageInfo {
          endCursor
          hasNextPage
        }
      }
    }
    """ % (posted_after, posted_before)

    return query, {}
```

### Product Hunt — parse de node para Product
```python
def _parse_post(node: dict, rank: int, niche_id: int) -> Product | None:
    """Parse GraphQL post node into Product dataclass."""
    from mis.platform_ids import PRODUCT_HUNT_PLATFORM_ID

    slug = node.get("slug")
    if not slug:
        return None

    name = node.get("name") or slug
    url = node.get("url") or f"https://www.producthunt.com/posts/{slug}"

    # thumbnail.url (not imageUrl — verified against official schema)
    thumbnail_data = node.get("thumbnail") or {}
    thumbnail_url = thumbnail_data.get("url") or None

    return Product(
        external_id=slug,                        # slug é estável e legível
        title=name,
        url=url,
        platform_id=PRODUCT_HUNT_PLATFORM_ID,
        niche_id=niche_id,
        rank=rank,                               # posição ordinal (1=top), não votesCount
        price=None,                              # PH não retorna preço monetário
        thumbnail_url=thumbnail_url,
    )
```

### Udemy — Basic Auth + GET request
```python
# Source: Udemy Affiliate API v2.0 docs (arquivado) + base64 stdlib
import base64

def _build_udemy_headers(client_id: str, client_secret: str) -> dict:
    """Build Authorization header for Udemy Basic Auth."""
    credentials = base64.b64encode(
        f"{client_id}:{client_secret}".encode()
    ).decode()
    return {
        "Authorization": f"Basic {credentials}",
        "Accept": "application/json",
    }

# Request params
params = {
    "search": keyword,           # ex: "marketing digital"
    "ordering": "most-reviewed",
    "category": category_slug,   # ex: "Marketing"
    "page_size": 20,
    "fields[course]": "id,title,url,price_detail,avg_rating,image_480x270",
}
```

### SCANNER_MAP update em scanner.py
```python
# Adicionar no bloco de imports de run_all_scanners()
from .scanners.product_hunt import ProductHuntScanner
from .scanners.udemy import UdemyScanner

SCANNER_MAP = {
    "kiwify": KiwifyScanner,
    "hotmart": HotmartScanner,
    "clickbank": ClickBankScanner,
    "eduzz": EduzzScanner,
    "monetizze": MonetizzeScanner,
    "perfectpay": PerfectPayScanner,
    "braip": BraipScanner,
    "product_hunt": ProductHuntScanner,   # NOVO
    "udemy": UdemyScanner,               # NOVO
}
```

### config.yaml update
```yaml
# Adicionar em cada nicho:
niches:
  - name: "Marketing Digital"
    slug: "marketing-digital"
    platforms:
      ...existing...
      product_hunt: trending     # Scanner ignora slug, retorna trending geral
      udemy: "Marketing"         # Categoria oficial Udemy Affiliate API

  - name: "Emagrecimento"
    slug: "emagrecimento"
    platforms:
      ...existing...
      product_hunt: trending
      udemy: "Health & Fitness"

  - name: "Financas Pessoais"
    slug: "financas-pessoais"
    platforms:
      ...existing...
      product_hunt: trending
      udemy: "Finance & Accounting"
```

### Fixture JSON — estrutura esperada

**product_hunt/trending_today.json:**
```json
{
  "data": {
    "posts": {
      "edges": [
        {
          "node": {
            "id": "123456",
            "name": "Jarvis AI Assistant",
            "tagline": "Your personal AI assistant",
            "slug": "jarvis-ai-assistant",
            "url": "https://www.producthunt.com/posts/jarvis-ai-assistant",
            "votesCount": 450,
            "thumbnail": {
              "url": "https://ph-files.imgix.net/..."
            }
          }
        }
      ],
      "pageInfo": {
        "endCursor": "eyJpZCI6MTIzNDU2fQ==",
        "hasNextPage": true
      }
    }
  }
}
```

**udemy/courses_marketing.json:**
```json
{
  "count": 100,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1234567,
      "title": "Complete Digital Marketing Course",
      "url": "/course/complete-digital-marketing-course/",
      "price_detail": {"amount": 19.99, "currency": "USD", "price_string": "$19.99"},
      "avg_rating": 4.6,
      "image_480x270": "https://img-c.udemycdn.com/course/480x270/1234567_abc1.jpg"
    }
  ]
}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Udemy Affiliate API `/api-2.0/courses/` | API descontinuada — sem substituto direto | 01/01/2025 | UdemyScanner deve ser implementado com fallback gracioso |
| Product Hunt V1 REST API | V2 GraphQL obrigatório | 2022 (V1 deprecated), 2023 (shutdown) | Usar apenas GraphQL em `https://api.producthunt.com/v2/api/graphql` |
| `thumbnail.imageUrl` (nomenclatura incorreta) | `thumbnail.url` (campo real no schema Media) | Schema sempre foi assim | Parse de thumbnails usa `.get("url")` não `.get("imageUrl")` |

**Deprecated/outdated:**
- Udemy Affiliate API v2.0: descomissionada em 01/01/2025 — credenciais existentes podem não funcionar
- Product Hunt V1 REST API: encerrada em 2023 — usar apenas GraphQL v2

---

## Open Questions

1. **`thumbnail.url` vs `thumbnail.imageUrl` (CONTEXT.md vs schema real)**
   - O que sabemos: Schema oficial do Product Hunt define `Media.url`, não `Media.imageUrl`
   - O que não está claro: Se `imageUrl` é um alias ou campo alternativo não documentado
   - Recomendação: Usar `thumbnail.url` conforme schema verificado; capturar fixture ao vivo para confirmar estrutura real

2. **Udemy API: tentativa real ou fallback-only?**
   - O que sabemos: API descontinuada em 01/01/2025; múltiplas libs Python confirmam morte
   - O que não está claro: Se credenciais legadas (emitidas antes de 2025) ainda autenticam
   - Recomendação: Implementar UdemyScanner com tentativa real ao endpoint + fallback gracioso em qualquer HTTP error; isso preserva a arquitetura e funciona se o usuário tiver credenciais válidas — caso contrário degrada graciosamente

3. **`pricingType` do Product Hunt como proxy de preço?**
   - O que sabemos: O schema tem campo `pricingType: String` (valores como `free`, `paid`, `freemium`)
   - O que não está claro: Não há valor monetário real disponível na API pública
   - Recomendação: `price = None` para todos os produtos do Product Hunt; `pricingType` não é solicitado na query

4. **Product Hunt: posts com `featured: true` vs `featured: false`**
   - O que sabemos: `featured: true` filtra apenas produtos curados pelo PH editorial team
   - O que não está claro: Produtos sem review editorial podem estar no trending mas `featured: false`
   - Recomendação: Usar `featured: true` conforme padrão mais comum em exemplos de community; capturar fixture ao vivo antes de decidir

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest + pytest-asyncio |
| Config file | `mis/pytest.ini` (asyncio_mode = auto) |
| Quick run command | `cd mis && python -m pytest tests/test_product_hunt_scanner.py tests/test_udemy_scanner.py -x` |
| Full suite command | `cd mis && python -m pytest tests/ -x` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SCAN-INTL-01 | ProductHuntScanner retorna products com campos obrigatórios | unit (respx mock) | `pytest tests/test_product_hunt_scanner.py::test_happy_path -x` | ❌ Wave 0 |
| SCAN-INTL-01 | ProductHuntScanner degrada com PRODUCT_HUNT_API_TOKEN ausente | unit | `pytest tests/test_product_hunt_scanner.py::test_missing_credentials -x` | ❌ Wave 0 |
| SCAN-INTL-01 | ProductHuntScanner retorna [] com resposta vazia da API | unit (respx mock) | `pytest tests/test_product_hunt_scanner.py::test_empty_results -x` | ❌ Wave 0 |
| SCAN-INTL-02 | UdemyScanner retorna products com campos obrigatórios | unit (respx mock) | `pytest tests/test_udemy_scanner.py::test_happy_path -x` | ❌ Wave 0 |
| SCAN-INTL-02 | UdemyScanner degrada com UDEMY_CLIENT_ID/SECRET ausentes | unit | `pytest tests/test_udemy_scanner.py::test_missing_credentials -x` | ❌ Wave 0 |
| SCAN-INTL-02 | UdemyScanner retorna [] com resposta vazia da API | unit (respx mock) | `pytest tests/test_udemy_scanner.py::test_empty_results -x` | ❌ Wave 0 |
| SCAN-INTL-01+02 | Upsert sem duplicatas (mesmo external_id, rank atualizado) | unit (sqlite tmp) | `pytest tests/test_product_hunt_scanner.py::test_upsert_no_duplicates -x` | ❌ Wave 0 |
| SCAN-INTL-01+02 | is_stale reset após upsert | unit (sqlite tmp) | `pytest tests/test_product_hunt_scanner.py::test_is_stale -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `cd mis && python -m pytest tests/test_product_hunt_scanner.py tests/test_udemy_scanner.py -x`
- **Per wave merge:** `cd mis && python -m pytest tests/ -x`
- **Phase gate:** Full suite green antes do `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `mis/tests/test_product_hunt_scanner.py` — cobre SCAN-INTL-01 (6 tests: happy_path, field_types, missing_credentials, empty_results, upsert_no_duplicates, is_stale)
- [ ] `mis/tests/test_udemy_scanner.py` — cobre SCAN-INTL-02 (6 tests: mesmo padrão)
- [ ] `mis/tests/fixtures/product_hunt/trending_today.json` — fixture JSON real capturada ao vivo
- [ ] `mis/tests/fixtures/udemy/courses_marketing.json` — fixture JSON real capturada ao vivo
- [ ] `mis/scanners/product_hunt.py` — implementação ProductHuntScanner
- [ ] `mis/scanners/udemy.py` — implementação UdemyScanner

---

## Sources

### Primary (HIGH confidence)
- `github.com/producthunt/producthunt-api/blob/master/schema.graphql` — Schema GraphQL v2 verificado: Post type fields, posts query arguments, Media type (thumbnail.url não imageUrl)
- `api.producthunt.com/v2/docs` — Endpoint, autenticação Bearer token, developer token não expira
- `mis/scanners/clickbank.py` (projeto local) — Padrão GraphQL POST + Bearer token + _post_graphql helper
- `mis/scanners/eduzz.py` (projeto local) — Padrão fallback gracioso com alert='marketplace_unavailable'
- `mis/base_scraper.py` (projeto local) — DOMAIN_DELAYS dict, _base._client pattern para POST

### Secondary (MEDIUM confidence)
- `bijenpatel.com/blog/how-to-query-product-hunt-graphql-python/` — Confirma votesCount e posts query para hoje
- GitHub `pydemy` README — Confirma descontinuação Udemy Affiliate API em 01/01/2025
- `ce-docs.keywordrush.com/modules/affiliate/udemy` — Confirma descontinuação; sugere alternativas

### Tertiary (LOW confidence — marcar para validação)
- Udemy Affiliate API docs (arquivado) — Estrutura de response `price_detail.amount`, `avg_rating`, `image_480x270` — baseada em documentação arquivada e libs Python legacy; PRECISA ser verificada ao capturar fixture ao vivo
- Udemy category slugs `"Marketing"`, `"Health & Fitness"`, `"Finance & Accounting"` — valores baseados em research anterior; confirmar via request real ou documentação arquivada

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — sem novas dependências; patterns idênticos ao ClickBankScanner existente
- Architecture Product Hunt: HIGH — schema GraphQL verificado contra repositório oficial; padrão ClickBank já validado
- Architecture Udemy: LOW — API descontinuada; estrutura de response baseada em fontes arquivadas
- Pitfalls: HIGH — thumbnail.url vs imageUrl verificado no schema real; descontinuação Udemy confirmada por 3+ fontes
- Test patterns: HIGH — idênticos ao BraipScanner e ClickBankScanner já funcionando

**Research date:** 2026-03-17
**Valid until:** Product Hunt — 30 dias (API estável). Udemy — verificar IMEDIATAMENTE ao capturar fixture (API possivelmente morta).
