# Phase 15: International API-Based - Context

**Gathered:** 2026-03-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Implementar dois scanners com APIs oficiais: `ProductHuntScanner` (GraphQL v2) e `UdemyScanner` (REST API v2.0). Ambos registrados no SCANNER_MAP, com degradação graciosa quando credenciais ausentes. Config.yaml atualizado com slugs para todos os nichos existentes.

Scanners de outras plataformas internacionais (JVZoo, Gumroad, AppSumo) são fases separadas.

</domain>

<decisions>
## Implementation Decisions

### Product Hunt — rank semantics
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

### Product Hunt — escopo de produtos
- Trending geral sem filtro por categoria — `scan_niche()` ignora `niche_slug` e retorna os mesmos 40 produtos para qualquer nicho
- Duplicatas entre nichos resolvidas automaticamente por `INSERT OR IGNORE` via UNIQUE index `(external_id, platform_id)` já existente

### Udemy — scanner
- Endpoint: `GET /api-2.0/courses/` com params `?search=<keyword>&ordering=most-reviewed&category=<cat>&page_size=20`
- Ordering: `most-reviewed` — reflete popularidade real (matrículas)
- Top 20 cursos por nicho (page_size=20), 1 requisição por nicho
- Autenticação: Basic Auth com base64 de `UDEMY_CLIENT_ID:UDEMY_CLIENT_SECRET`
- `external_id` = ID numérico do curso (campo `'id'`, ex: `1234567`) — mais estável que slug
- `rank_type` = `'enrollment'` — semântica correta para ordenação por reviews/matrículas
- `price` = `price_detail.amount` em USD — armazenar (dado rico da API)
- `rating` = `avg_rating` (escala 0-5) — armazenar (único scanner com rating real)
- `thumbnail_url` = `image_480x270` — armazenar

### Config.yaml — slugs por nicho
- Adicionar entradas `product_hunt` e `udemy` a todos os nichos existentes
- Product Hunt: `product_hunt: trending` (mesmo valor para todos — scanner ignora, retorna geral)
- Udemy mapeamentos (categorias oficiais da API):
  - Marketing Digital → `udemy: "Marketing"`
  - Emagrecimento → `udemy: "Health & Fitness"`
  - Finanças Pessoais → `udemy: "Finance & Accounting"`

### Credenciais ausentes
- Ambos os scanners: quando env vars ausentes → `return []` + `log.warning(alert='missing_credentials')`
- Mesmo padrão dos scanners fallback (Eduzz/Monetizze/PerfectPay) — pipeline detecta e chama `mark_stale()`
- `PRODUCT_HUNT_API_TOKEN` — conforme citado nos success criteria do ROADMAP
- `UDEMY_CLIENT_ID` + `UDEMY_CLIENT_SECRET`
- Adicionar ambos ao `bin/templates/env.example` com comentários explicativos (onde obter o token)

### Testes
- Fixtures JSON salvas de respostas reais da API (mesmo padrão do BraipScanner com HTML fixture ao vivo)
- `mis/tests/fixtures/product_hunt/trending_today.json` — resposta GraphQL real
- `mis/tests/fixtures/udemy/courses_marketing.json` — resposta REST real por nicho
- Testes cobrem: retorno normal, credenciais ausentes (`missing_credentials`), resposta vazia da API

### Rate limiting
- Adicionar entradas em `DOMAIN_DELAYS` no `base_scraper.py`:
  - `"api.producthunt.com": 1.0` — API oficial com rate limit documentado
  - `"www.udemy.com": 0.5` — REST API com autenticação

### Claude's Discretion
- Estrutura exata da query GraphQL do Product Hunt (campos específicos a solicitar)
- Formato exato dos fixtures JSON (estrutura das fixtures de teste)
- Valores precisos dos IDs numéricos de categoria Udemy (confirmar via pesquisa)
- Wiring de `rank_type` no `product_repository.upsert_product()` — se via campo extra no `Product` dataclass ou outro mecanismo já existente da INFRA-03

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `mis/scanner.py` — `PlatformScanner` ABC com `scan_niche(niche_slug, platform_slug, niche_id) -> list[Product]` — interface obrigatória
- `mis/scanner.py:Product` dataclass — campos: external_id, title, url, platform_id, niche_id, rank, price, commission_pct, rating, thumbnail_url
- `mis/scanner.py:SCANNER_MAP` — dicionário `{platform_id: ScannerClass}` — registrar ambos
- `mis/scanners/clickbank.py` — padrão GraphQL com POST + Bearer token + query string (modelo para ProductHunt)
- `mis/scanners/braip.py` — padrão SSR parsing com fixture real; modelo para abordagem de fixtures de teste
- `mis/scanners/eduzz.py` — padrão fallback `missing_credentials` (log.warning + return [])
- `mis/platform_ids.py` — centraliza IDs de plataforma como constantes nomeadas (INFRA-02)
- `mis/product_repository.py` — `mark_stale()` + `upsert_product()` com INSERT OR IGNORE via UNIQUE index
- `mis/base_scraper.py` — `DOMAIN_DELAYS` dict para rate limiting por domínio

### Established Patterns
- Degradação graciosa: `log.warning(alert='...')` + `return []` quando indisponível
- `rank_type` adicionado na INFRA-03 — informar valor no scanner (mecanismo exato a confirmar via pesquisa)
- Config.yaml com slugs explícitos por plataforma+nicho (estabelecido na Phase 14 com Braip)
- Fixtures de teste: arquivo real capturado ao vivo em `mis/tests/fixtures/<platform>/`
- TDD: testes escritos antes da implementação

### Integration Points
- `mis/scanner.py:SCANNER_MAP` — adicionar `PRODUCT_HUNT_PLATFORM_ID` e `UDEMY_PLATFORM_ID`
- `mis/platform_ids.py` — constantes já devem existir (Phase 13 - INFRA-02 criou todos os platform IDs)
- `mis/config.yaml` — entradas `product_hunt:` e `udemy:` em cada nicho
- `bin/templates/env.example` — documentar `PRODUCT_HUNT_API_TOKEN`, `UDEMY_CLIENT_ID`, `UDEMY_CLIENT_SECRET`

</code_context>

<specifics>
## Specific Ideas

- ProductHuntScanner segue o mesmo padrão GraphQL que o ClickBankScanner — reutilizar estrutura de request
- Udemy rating (avg_rating) é campo único que nenhum outro scanner popula — aproveitar para enriquecer análise
- 2 requisições no Product Hunt (cursor pagination) para cobrir top 40 do dia

</specifics>

<deferred>
## Deferred Ideas

- Nenhuma ideia de escopo extra surgiu — discussão ficou dentro dos limites da Phase 15

</deferred>

---

*Phase: 15-international-api-based*
*Context gathered: 2026-03-17*
