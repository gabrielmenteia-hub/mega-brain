# Phase 2: Platform Scanners - Context

**Gathered:** 2026-03-14
**Status:** Ready for planning

<domain>
## Phase Boundary

O sistema descobre e rankeia automaticamente produtos campeões em Hotmart, ClickBank e Kiwify, com dados frescos disponíveis diariamente via jobs APScheduler independentes por plataforma. Espionagem profunda de produtos, análise de copy e geração de dossiê pertencem à Phase 3.

</domain>

<decisions>
## Implementation Decisions

### Cobertura de Plataformas

- Plataformas incluídas na Phase 2: **Hotmart** (BR, SPA), **ClickBank** (gringa, API oficial) e **Kiwify** (BR, SSR)
- Kiwify incluída por ser mais simples (SSR, sem anti-bot significativo) — pode ser implementada primeiro para validar o PlatformScanner pattern
- ClickBank: usar **API oficial** com gravity score — mais estável que scraping HTML
- ClickBank mercado: researcher decide qual (US vs BR) tem mais dados por nicho
- Hotmart: **scraping público apenas** — sem autenticação, sem expor credenciais de conta
- Jobs separados por plataforma no APScheduler — falha de uma não afeta as demais

### Dados Coletados por Produto

- Campos obrigatórios: `external_id`, `title`, `url`, `platform_id`, `niche_id`, `rank`
- Campos adicionais (todos nullable): `price` (float), `commission_pct` (float), `rating` (float), `thumbnail_url` (str — URL remota apenas, não baixar)
- Kiwify: coletar nome + URL, preço, categoria, nº de vendas/estudantes (se disponível)
- Thumbnail: salvar só a URL remota — não fazer download local
- Nova migration `_002_product_enrichment.py` para adicionar colunas à tabela `products` existente

### Deduplication e Upsert

- `external_id` por plataforma: slug da URL para Hotmart (ex: `/produto-nome-123`), ID da API para ClickBank, researcher define para Kiwify
- Estratégia: **upsert por external_id** — atualiza campos dinâmicos (rank, score, price, updated_at), não duplica registros
- Preservar dados antigos quando drift detectado — nunca sobrescrever com resultado vazio

### Volume de Coleta

- Objetivo: **top 10 a 50 produtos por nicho por plataforma** (não "mínimo de 10" — é o alvo real)
- `max_products_per_niche: 50` configurável no config.yaml

### Abordagem Hotmart

- Estratégia: **Playwright + interceptar requisições XHR/GraphQL** — dados estruturados do backend, mais estável que parsear DOM
- Anti-bot: researcher testa ao vivo e reporta se precisa de configuração extra de stealth/proxy
- Horário do job diário: Claude decide o default (configurável via cron no config.yaml)

### Abordagem Kiwify

- Estrutura: SSR — **httpx suficiente**, sem necessidade de Playwright
- Marketplace público navegável por categoria — categorias similares ao Hotmart
- Sem anti-bot significativo
- Comissão de afiliado: researcher verifica se é exposta publicamente

### Arquitetura dos Scrapers

- Hierarquia: `PlatformScanner(BaseScraper)` como classe base intermediária, com método abstrato `scan_niche(niche_slug: str) -> list[Product]`
- `mis/scanner.py`: contém tanto a classe `PlatformScanner` quanto a função `run_all_scanners(config)`
- `mis/scanners/`: subpackage com `hotmart.py`, `clickbank.py`, `kiwify.py`, `__init__.py`
- `Product`: dataclass com todos os campos possíveis, os opcionais como `Optional[]`
- Persistência fora do scraper: `ProductRepository` ou função `upsert_product()` em arquivo separado
- `run_all_scanners()`: **asyncio.gather()** paralelo com `return_exceptions=True` — falha de uma plataforma não cancela as outras

### Config.yaml Extensão

- Cada nicho recebe bloco `platforms` com slugs de categoria por plataforma:
  ```yaml
  niches:
    - slug: emagrecimento
      name: Emagrecimento
      platforms:
        hotmart: saude-e-fitness
        clickbank: health
        kiwify: saude
  ```
- Nicho sem bloco `platforms`: skip + warning no structlog (backward compatible)
- Validação expandida: typos de plataforma (ex: `hotmrt`) lançam `ValueError`; pelo menos uma plataforma mapeada por nicho
- Novos settings no bloco `settings`:
  - `max_products_per_niche: 50`
  - `scan_schedule: "0 3 * * *"` (cron)
  - `parallel_scanners: true`

### Schema Drift Detection

- Fallback selectors/endpoints **hardcoded no scraper** em lista ordenada
- Sequência: tenta primary selector → tenta fallbacks → só então emite alerta
- Quando todos os fallbacks falham: alerta via structlog com `alert='schema_drift'`
- Payload do alerta inclui: platform + nicho afetado, selector/endpoint que falhou, timestamp do último run bem-sucedido, URL tentada
- Integrar ao **health_monitor** como canary check de plataforma — o canary verifica no DB se `updated_at` do produto mais recente é > 25h (sem request ao vivo)
- Dados antigos preservados quando 0 produtos retornados — job não sobrescreve com vazio
- Sem desabilitar job: sempre alerta e tenta novamente no próximo ciclo

### Testes

- Estratégia: **fixtures HTML/JSON gravadas ao vivo** (uma vez) → commitadas no repo → testes sempre usam os fixtures
- Localização: `mis/tests/fixtures/` organizado por plataforma (`hotmart/`, `clickbank/`, `kiwify/`)
- Mock httpx via **respx**; Playwright: mock do `fetch_spa()` retornando HTML da fixture
- Testes completos: scraper + upsert no DB (usando DB real em `tmp_path`)
- **5 testes mínimos por scraper:**
  1. Happy path: retorna lista de produtos com todos os campos obrigatórios
  2. Campos tipados: price é float, rank é int, external_id não-None
  3. Fallback selector usado quando primary falha
  4. Alerta de drift (`alert='schema_drift'`) emitido quando todos os selectors falham
  5. Upsert DB: inserir + re-run atualiza rank sem duplicar

### Claude's Discretion

- Horário default do job diário (dentro da janela de madrugada)
- Implementação interna do ProductRepository (classe vs funções)
- Formato do external_id para Kiwify e ClickBank (researcher confirma o campo estável)
- Algoritmo de detecção de 0 produtos (threshold, timeout handling)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets

- `BaseScraper`: classe base com `fetch()` (httpx+tenacity) e `fetch_spa()` (Playwright+stealth) — `PlatformScanner` subclasses diretamente
- `DOMAIN_DELAYS`: `hotmart.com: 2.0`, `kiwify.com.br: 2.0`, `clickbank.com: 2.0` — já configurados, adicionar conforme necessário
- `get_scheduler()`: singleton APScheduler — jobs de cada plataforma registrados aqui
- `run_canary_check()` + `register_canary_job()`: padrão de canary existente — estender para canary de plataforma (DB-based, não live request)
- `load_config()`: validação de nichos — estender para validar bloco `platforms` e novos settings
- `get_db()` + `run_migrations()`: pattern de acesso ao DB — reutilizar em ProductRepository
- `conftest.py`: fixture `tmp_path` com DB real — reutilizar nos testes de scraper
- `ScraperError`: exceção base — scrapers de plataforma lançam essa exceção

### Established Patterns

- Structlog JSON com `alert=` machine-readable field — replicar em schema drift com `alert='schema_drift'`
- `@retry` via tenacity como inner function dentro de `fetch()` — manter padrão
- `replace_existing=True` no APScheduler — reutilizar nos jobs de plataforma
- Testes com dados reais (DB real em tmp_path, sem mocks de DB) — manter abordagem

### Integration Points

- `mis/scheduler.py`: adicionar `register_scanner_jobs(config)` que registra 1 job APScheduler por plataforma
- `mis/health_monitor.py`: estender para suportar canary checks de plataforma (consulta DB)
- `mis/config.py` + `mis/config.yaml`: adicionar bloco `platforms` por nicho e novos settings
- `mis/migrations/`: nova migration `_002_product_enrichment.py` para novos campos de products
- `mis/db.py`: ponto de entrada para ProductRepository

</code_context>

<specifics>
## Specific Ideas

- Kiwify pode ser implementada primeiro (mais simples/rápida) para validar o PlatformScanner interface antes de Hotmart
- `run_all_scanners()` com `asyncio.gather(return_exceptions=True)` — falha de uma plataforma retorna no resultado mas não cancela as outras
- Canary check de plataforma: `SELECT MAX(updated_at) FROM products WHERE platform_id = ?` — se > 25h atrás, dispara alerta

</specifics>

<deferred>
## Deferred Ideas

- Kiwify estava inicialmente fora do escopo da Phase 2 (REQUIREMENTS.md como SCAN-V2-01) — usuário decidiu incluir. O REQUIREMENTS.md deve ser atualizado para mover SCAN-02/Kiwify para Phase 2.
- JVZoo, Eduzz, Udemy, Product Hunt, AppSumo — REQUIREMENTS.md v2, fora de Phase 2
- Histórico de evolução de ranking (tabela de snapshots) — REQUIREMENTS.md ADV-03, fora de Phase 2
- Proxy residencial e configuração avançada de stealth para Cloudflare — Pre-Phase 3 blocker conforme STATE.md

</deferred>

---

*Phase: 02-platform-scanners*
*Context gathered: 2026-03-14*
