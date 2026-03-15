# Phase 3: Product Espionage + Dossiers - Research

**Researched:** 2026-03-14
**Domain:** Web scraping (platform-agnostic), Meta Ads Library API, Anthropic LLM pipeline, SQLite migrations
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Gatilho de Espionagem**
- Automatico: todo produto novo detectado pelo scanner e enfileirado para espionagem
- Criterio de selecao: top 10 por nicho por plataforma (hardcoded, nao configura top-N)
- Timing: disparado por evento — apos `run_all_scanners()` completar (nao por horario fixo)
- Frequencia automatica: nunca re-espionar produto com dossier existente (MVP)
- Manual: `python -m mis spy --url <URL>` aceita URL direta de qualquer plataforma; `--product-id` para produtos ja no banco
- Prioridade na fila: produtos manuais tem prioridade maxima; automaticos ordenados por rank (posicao 1 primeiro); hardcoded no codigo (nao configuravel)
- Re-espionar manual: sim, sempre — `--url` ou `--product-id` forcam nova espionagem mesmo com dossier existente
- Produto que sai do top-10: dossier preservado no banco, produto nao re-espionado automaticamente
- Concorrencia: `asyncio.Semaphore` com `max_concurrent_spy` configuravel em config.yaml
- Falha: `structlog alert='spy_failed'`, produto marcado como `status=failed`, pipeline continua com proximo produto
- Dados raw: nao persistidos — apenas dados estruturados no banco

**Data Completeness Gate (SPY-05)**
- Fontes obrigatorias: copy da pagina de vendas, estrutura da oferta, reviews (minimo 10), anuncios Meta Ad Library
- Copy e bloqueante: sem copy, dossier nao e gerado — produto fica em `status=failed`
- Oferta + copy: extraidas juntas pelo mesmo `SalesPageScraper` (mesma pagina, mesmo fetch)
- Reviews minimo: 10 reviews de qualquer fonte (plataforma ou Google) — configuravel via `min_reviews` em config.yaml
- Meta Ads: obrigatorio por padrao; apos 3 tentativas falhas → gera dossier sem ads com confidence score reduzido
- Sem META_ACCESS_TOKEN: pula ads, reduz confidence score, sem bloqueio do pipeline
- Timeout: apos 3 tentativas falhas (em ciclos diferentes), gera dossier parcial com confidence baixo + flag `incomplete: true`
- Gate log: structlog com campos individuais: `{copy_ok, offer_ok, reviews_count, ads_ok, gate_passed}` — machine-readable
- Dossier parcial: gerado com o disponivel + flag `incomplete: true` + confidence score proporcional

**Pipeline de Analise IA**
- Modelo: Claude (Anthropic API) — `claude-sonnet-4-6`; credenciais via `ANTHROPIC_API_KEY` no `.env`
- Arquitetura: pipeline especializado em 2 etapas: `copy_analyzer` → `dossier_generator`
- copy_analyzer recebe: copy da pagina + estrutura da oferta + anuncios Meta + reviews
- copy_analyzer identifica: framework de copy (AIDA, PAS, Story-based, etc.), gatilhos emocionais, estrutura narrativa, elementos de prova social
- copy_analyzer e bloqueante: falha do copy_analyzer para o pipeline — status=failed, retry na proxima execucao
- dossier_generator recebe: output do copy_analyzer + dados brutos completos (reviews, oferta, ads)
- Retry LLM: tenacity 3x com backoff exponencial — mesmo padrao do BaseScraper
- Idioma: sempre pt-BR, independente do idioma do produto espionado
- Score de oportunidade (DOS-04): LLM estima com base nos dados coletados (nao algoritmo deterministico)
- Analise: generica do produto espionado — sem contexto do nicho/produto do usuario (MVP)
- Template de modelagem (DOS-03): estrutural — framework reutilizavel (secoes, argumentos-chave, estrutura de oferta sugerida). Nao draft de copy pronta
- Few-shot: zero-shot com instrucoes claras no system prompt (sem exemplos no MVP)
- Tracking de custo: tabela `llm_calls(id, dossier_id, model, stage, input_tokens, output_tokens, cost_usd, created_at)`

**SalesPageScraper (Platform-Agnostic)**
- Parser universal: HTML da pagina → texto limpo (markdownify/html2text) → LLM extrai copy + oferta em um unico prompt
- LLM extrai em uma chamada: headlines, sub-headlines, argumentos, CTAs, estrutura narrativa, preco, bonus, garantias, upsells/downsells
- SPAs: `fetch_spa()` do BaseScraper (Playwright + stealth) para paginas JavaScript-rendered
- Sem seletores por plataforma: sistema e genuinamente platform-agnostic

**Reviews: Fontes de Coleta**
- Plataformas com reviews nativos (Hotmart, ClickBank, Kiwify): pagina do produto na plataforma
- Plataformas sem reviews nativos (Gumroad, Kajabi, Teachable, etc.): Google Search `"{nome produto} review"`
- Threshold: 10 reviews de qualquer fonte (plataforma OU externas) para atingir completude minima
- Campo source na tabela reviews: `'hotmart' | 'clickbank' | 'kiwify' | 'google' | 'sales_page'`

**Meta Ad Library**
- Acesso: API oficial do Meta (`graph.facebook.com/ads_archive`) — nao scraping
- Token: `META_ACCESS_TOKEN` no `.env`
- Sem token: espionagem prossegue sem ads, confidence score reduzido, warning no log

**Confidence Score (DOS-05)**
- Escala: 0–100%
- Inputs: copy presente (peso maior), quantidade de reviews (escala 0–10+), Meta ads presentes, oferta estruturada presente
- Exibicao: campo `confidence_score` (int 0–100) na tabela dossiers

**Formato do Dossier**
- Banco: JSON estruturado em coluna `dossier_json TEXT` na tabela `dossiers`
- Secoes obrigatorias: `why_it_sells`, `pains_addressed`, `modeling_template`, `opportunity_score`, `copy_analysis`, `confidence_score`, `incomplete`

**Estrutura de Modulos**
```
mis/
├── spies/
│   ├── __init__.py
│   ├── sales_page.py      # SalesPageScraper (platform-agnostic)
│   ├── meta_ads.py        # MetaAdsScraper (API oficial)
│   └── reviews.py         # ReviewsScraper (plataforma + Google fallback)
├── intelligence/
│   ├── __init__.py
│   ├── copy_analyzer.py   # Etapa 1 do pipeline LLM
│   └── dossier_generator.py # Etapa 2 do pipeline LLM
├── prompts/
│   ├── sales_page_extractor.md
│   ├── copy_analyzer.md
│   └── dossier_generator.md
└── spy_orchestrator.py    # run_spy(product_id), run_spy_url(url)
```

**Schema do Banco (Migration _003)**
- Uma migration: `_003_spy_dossiers.py` cria todas as tabelas de Phase 3
- Tabela dossiers: `id, product_id FK, status [pending|running|done|failed], dossier_json TEXT, confidence_score INT, incomplete BOOL, created_at, updated_at`
- Tabela reviews: `id, product_id FK, text TEXT, valence TEXT [positive|negative], rating FLOAT, source TEXT, created_at` + INDEX em `(product_id, valence)`
- Tabela llm_calls: `id, dossier_id FK, model TEXT, stage TEXT, input_tokens INT, output_tokens INT, cost_usd REAL, created_at`
- Anuncios: coluna `ads_json TEXT` em dossiers (nao tabela separada — MVP)

**Testes**
- LLM calls: mock da API Anthropic com fixture JSON gravada ao vivo uma vez → commitada no repo
- Minimo por componente: 5 testes (happy path, campos tipados, degraded mode/gate, alerta de falha, integracao DB)
- Data completeness gate: unit tests com objetos `SpyData` mock com diferentes combinacoes de campos ausentes/presentes

**CLI Manual**
- Invocacao: `python -m mis spy --url <URL>` ou `python -m mis spy --product-id <ID>`
- Progresso: structlog em tempo real
- Output: JSON formatado no terminal + confirmacao de save com product_id

**Interface Externa**
- Ponto de entrada publico: `spy_orchestrator.run_spy(product_id)` e `spy_orchestrator.run_spy_url(url)`
- Phase 6 conecta MEGABRAIN chamando essas funcoes — sem acoplamento na Phase 3

### Claude's Discretion

- Campos internos do JSON do dossier (estrutura detalhada dentro de cada secao)
- Pesos exatos de cada fonte no calculo do confidence score
- Biblioteca especifica: markdownify vs html2text
- Implementacao interna da fila de espionagem (lista simples vs asyncio.Queue)
- Parametros exatos da chamada a API Meta (researcher confirma — ver secao Standard Stack)

### Deferred Ideas (OUT OF SCOPE)

- Phase 2.5 — Expansao de Plataformas (scanners adicionais para Gumroad, Kajabi, Teachable, etc.)
- Integracao MEGABRAIN (Phase 6): mis_agent.py, JARVIS slash commands
- Re-espionar quando copy muda: detector de drift de copy (hash da pagina de vendas)
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| SPY-01 | Sistema extrai copy completa da pagina de vendas (headlines, sub-headlines, argumentos, CTA, estrutura narrativa) | SalesPageScraper: BaseScraper.fetch() + html2text + LLM extrai campos em uma chamada. Padrao platform-agnostic verificado. |
| SPY-02 | Sistema coleta anuncios ativos do produto via Meta Ad Library (criativos e copy) | Meta Graph API v25.0 `ads_archive` endpoint. Token via META_ACCESS_TOKEN. Parametros: search_terms, ad_reached_countries, ad_active_status. |
| SPY-03 | Sistema extrai estrutura da oferta (preco, bonus, garantias, upsells, downsells) | Mesma chamada LLM do SPY-01 (mesma pagina, mesmo fetch) — sem custo extra de HTTP. |
| SPY-04 | Sistema coleta e classifica reviews separando positivos (4-5 estrelas) e negativos (1-3 estrelas) | ReviewsScraper: plataforma nativa para Hotmart/ClickBank/Kiwify; Google Search fallback para demais. Valence field na tabela. |
| SPY-05 | Dados de espionagem so sao processados pelo LLM quando completude minima e atingida (data completeness gate) | SpyData dataclass com campos booleanos + reviewscount. Gate logado via structlog com campos machine-readable. |
| DOS-01 | IA gera analise explicando por que o produto esta vendendo (fatores de sucesso) | dossier_generator: secao `why_it_sells` gerada por LLM em pt-BR. Input: output do copy_analyzer + dados brutos. |
| DOS-02 | IA mapeia as dores enderecadas pelo produto com base na copy e reviews | dossier_generator: secao `pains_addressed` com fonte evidenciando (copy/review/ad). |
| DOS-03 | IA gera template de modelagem com estrutura pronta para criar produto proprio | dossier_generator: secao `modeling_template` — framework estrutural reutilizavel (nao draft de copy). |
| DOS-04 | IA atribui score de oportunidade por nicho | dossier_generator: secao `opportunity_score` — LLM estima 0-100 + justificativa. Nao algoritmo deterministico. |
| DOS-05 | Dossier exibe confidence score indicando qualidade/completude dos dados | Campo `confidence_score` INT 0-100 calculado antes de chamar LLM. Pesos: copy (maior) + reviews_count + ads_ok + offer_ok. |
</phase_requirements>

---

## Summary

Phase 3 constroi o pipeline completo de inteligencia competitiva do MIS: desde a coleta de dados brutos (pagina de vendas, anuncios Meta, reviews) ate a geracao de dossies com analise de IA. O sistema e genuinamente platform-agnostic — o LLM substitui seletores HTML especificos por plataforma, usando markdownify/html2text para limpeza e depois inferencia de campos.

A Phase 3 reutiliza intensamente os componentes existentes: `BaseScraper.fetch()` e `fetch_spa()` para todos os scrapers, `tenacity` para retry do pipeline LLM, `get_db()` + padrao de migration para `_003_spy_dossiers.py`, `structlog` JSON para todos os alertas, e `conftest.py` com `tmp_path` DB real para testes. O Anthropic SDK Python (v0.84.0) e usado de forma sincrona ou assincrona com `AsyncAnthropic` para o pipeline de 2 etapas.

O maior risco tecnico e a Meta Ads Library API: requer um User Access Token ou System User Token com permissao `ads_library`, e os parametros exatos para busca por nome/termo de produto precisam de validacao live. O segundo risco e o custo de tokens LLM — a tabela `llm_calls` foi corretamente projetada para tracking, mas o planner deve estimar custo medio por dossier.

**Recomendacao principal:** Implementar o SalesPageScraper + migration _003 primeiro (03-01), pois sao bloqueantes para todos os outros planos. O data completeness gate (03-03) deve ser implementado antes do pipeline LLM (03-04) para garantir que a IA so recebe dados de qualidade.

---

## Standard Stack

### Core
| Biblioteca | Versao | Proposito | Por que usar |
|-----------|--------|-----------|--------------|
| `anthropic` (SDK Python) | 0.84.0 | Cliente Anthropic API para pipeline LLM | SDK oficial; suporta sync e async; usado no projeto (ANTHROPIC_API_KEY no .env) |
| `html2text` | latest | Converte HTML → Markdown limpo para input do LLM | Zero dependencias, battle-tested, simples de usar — adequado para SalesPageScraper platform-agnostic |
| `markdownify` | latest | Alternativa ao html2text com mais controle via subclassing | Usa BeautifulSoup4 (ja no requirements.txt); mais flexivel para customizacao |
| `httpx[http2]` | >=0.28.1 | HTTP async para Meta Ads API e Google Search | Ja instalado; BaseScraper usa; suporte HTTP/2 |
| `tenacity` | >=9.1.4 | Retry com backoff exponencial para chamadas LLM | Ja instalado; padrao estabelecido no BaseScraper |
| `structlog` | >=25.5.0 | JSON logging com campos machine-readable | Ja instalado; padrao obrigatorio do projeto |
| `sqlite-utils` | >=3.39 | ORM leve para SQLite | Ja instalado; padrao de migration estabelecido |
| `beautifulsoup4` | >=4.12.0 | Parsing HTML para ReviewsScraper | Ja instalado; usado nos scanners existentes |

### Recomendacao: markdownify vs html2text

**Use `markdownify`** (Claude's Discretion):
- BeautifulSoup4 ja esta no requirements.txt — sem nova dependencia de transporte
- Permite subclassing para remover scripts, styles, navs antes do LLM (reduz tokens)
- Mais controle sobre a saida Markdown
- Padrao: `markdownify.markdownify(html, strip=['script', 'style', 'nav', 'footer', 'header'])`

**Alternativa `html2text`** se markdownify produzir output ruidoso em paginas especificas.

### Instalacao Nova (adicionar ao mis/requirements.txt)
```bash
pip install anthropic markdownify
```

### Nao precisa instalar (ja disponivel)
```
httpx[http2], playwright, playwright-stealth, tenacity, structlog,
fake-useragent, sqlite-utils, apscheduler, PyYAML, python-dotenv,
beautifulsoup4, lxml, respx (tests)
```

---

## Architecture Patterns

### Estrutura de Modulos (Confirmada pelo CONTEXT.md)
```
mis/
├── spies/
│   ├── __init__.py
│   ├── sales_page.py        # SalesPageScraper — fetch + html2text/markdownify + LLM
│   ├── meta_ads.py          # MetaAdsScraper — API oficial Meta (httpx, nao Playwright)
│   └── reviews.py           # ReviewsScraper — plataforma nativa + Google fallback
├── intelligence/
│   ├── __init__.py
│   ├── copy_analyzer.py     # Etapa 1: analisa copy, identifica framework
│   └── dossier_generator.py # Etapa 2: gera JSON estruturado do dossie
├── prompts/
│   ├── sales_page_extractor.md   # System prompt: extrai copy + oferta
│   ├── copy_analyzer.md          # System prompt: analisa framework de copy
│   └── dossier_generator.md      # System prompt: gera dossie em pt-BR
├── migrations/
│   └── _003_spy_dossiers.py      # Cria dossiers, reviews, llm_calls
└── spy_orchestrator.py      # run_spy(product_id), run_spy_url(url) — ponto de entrada
```

### Pattern 1: SalesPageScraper (Platform-Agnostic)

**O que faz:** Recebe URL arbitraria, faz fetch (com fallback para SPA), converte HTML para texto limpo, chama LLM em uma unica chamada para extrair copy + oferta estruturada.

**Quando usar:** Qualquer URL de pagina de vendas — Hotmart, Gumroad, Kajabi, custom pages.

```python
# Padrao verificado — combina BaseScraper existente com markdownify + Anthropic SDK
import markdownify
from anthropic import AsyncAnthropic

class SalesPageScraper(BaseScraper):
    async def extract(self, url: str) -> dict:
        try:
            html = await self.fetch(url)
        except ScraperError:
            html = await self.fetch_spa(url)  # fallback para SPA

        clean_text = markdownify.markdownify(
            html,
            strip=['script', 'style', 'nav', 'footer', 'header', 'aside']
        )

        client = AsyncAnthropic()
        response = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SALES_PAGE_EXTRACTOR_PROMPT,
            messages=[{"role": "user", "content": clean_text}],
        )
        return json.loads(response.content[0].text)
```

### Pattern 2: Meta Ads Library API Call

**O que faz:** Busca anuncios ativos de um produto por nome/termo via API oficial do Meta.

**Endpoint:** `GET https://graph.facebook.com/v25.0/ads_archive`

**Parametros confirmados (fonte: Meta Developer Docs):**
```python
params = {
    "access_token": os.getenv("META_ACCESS_TOKEN"),
    "search_terms": product_title,           # nome do produto (max 100 chars)
    "ad_reached_countries": ["BR"],           # OBRIGATORIO — ISO country code
    "ad_active_status": "ACTIVE",
    "ad_type": "ALL",
    "fields": "page_name,ad_snapshot_url,ad_creative_bodies,ad_creative_link_titles,ad_delivery_start_time,spend,impressions",
    "limit": 25,
}
# Source: developers.facebook.com/docs/graph-api/reference/ads_archive/
```

**Sem token (degraded mode):**
```python
if not os.getenv("META_ACCESS_TOKEN"):
    log.warning("meta_ads.skipped", reason="no_token")
    return []  # ads_ok = False → confidence_score reduzido
```

**IMPORTANTE:** `ad_reached_countries` e obrigatorio. Sem ele a API retorna erro 400.

### Pattern 3: Pipeline LLM com Retry (tenacity — mesmo padrao do BaseScraper)

**O que faz:** Chama Anthropic API com retry 3x e backoff exponencial. Exatamente o padrao do BaseScraper para evitar inconsistencia.

```python
# Source: padrao estabelecido em mis/base_scraper.py
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from anthropic import APIError, APIConnectionError, RateLimitError

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type((APIConnectionError, RateLimitError)),
    reraise=True,
)
async def _call_llm(client: AsyncAnthropic, **kwargs) -> str:
    response = await client.messages.create(**kwargs)
    return response.content[0].text
```

### Pattern 4: Data Completeness Gate

**O que faz:** Avalia SpyData coletado, calcula confidence_score, decide se pipeline LLM pode rodar.

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class SpyData:
    copy_text: Optional[str]
    offer_data: Optional[dict]
    reviews: list[dict]           # lista de reviews coletados
    ads: list[dict]               # lista de anuncios Meta (pode ser [])
    copy_ok: bool = False
    offer_ok: bool = False
    ads_ok: bool = False

def check_completeness(data: SpyData, min_reviews: int = 10) -> tuple[bool, int]:
    """Retorna (gate_passed, confidence_score 0-100)."""
    copy_ok = bool(data.copy_text and len(data.copy_text) > 100)
    offer_ok = bool(data.offer_data)
    reviews_count = len(data.reviews)
    ads_ok = bool(data.ads)

    log.info(
        "completeness_gate",
        copy_ok=copy_ok,
        offer_ok=offer_ok,
        reviews_count=reviews_count,
        ads_ok=ads_ok,
        gate_passed=copy_ok and reviews_count >= min_reviews,
    )

    if not copy_ok:
        return False, 0   # copy e bloqueante

    # Confidence score: copy tem peso maior
    score = 0
    if copy_ok:      score += 50
    if offer_ok:     score += 15
    if ads_ok:       score += 20
    # reviews: escala 0 a 15 baseada em 0-10+ reviews
    score += min(15, int((reviews_count / min_reviews) * 15))

    gate_passed = copy_ok and reviews_count >= min_reviews
    return gate_passed, score
```

### Pattern 5: Migration _003 (mesmo padrao de _001 e _002)

```python
# Source: padrao estabelecido em mis/migrations/_001_initial.py e _002_product_enrichment.py
import sqlite_utils

def run_migration_003(db_path: str) -> None:
    db = sqlite_utils.Database(db_path)

    if "dossiers" not in db.table_names():
        # ATENCAO: _001 ja criou uma tabela 'dossiers' com schema diferente
        # _003 deve dropar e recriar OU alterar a tabela existente
        # Recomendacao: usar add_column() para colunas novas + rename/alter para status
        pass  # ver pitfall abaixo
```

**ATENCAO (Pitfall critico):** A migration `_001_initial.py` JA cria uma tabela `dossiers` com schema diferente (`analysis TEXT, opportunity_score FLOAT, confidence_score FLOAT, generated_at`). A migration `_003` precisa:
1. Verificar se as novas colunas existem com `{col.name for col in db["dossiers"].columns}`
2. Adicionar colunas faltantes via `add_column()` (idempotente)
3. Adicionar as tabelas `reviews` e `llm_calls` se nao existirem

### Anti-Patterns a Evitar

- **Seletores por plataforma:** Nao criar `if 'hotmart' in url: use_selector(...)`. O LLM e o parser — qualquer logica de plataforma especifica vai contra a arquitetura decidida.
- **Persistir dados raw:** Nao salvar o HTML original ou o texto limpo no banco. Apenas dados estruturados.
- **Chamar LLM sem gate:** Nunca chamar `copy_analyzer` antes de `check_completeness()` retornar `gate_passed=True`.
- **Re-criar tabela dossiers:** `_001_initial.py` ja criou — usar `add_column()` na migration `_003`, nao `DROP TABLE`.
- **asyncio.Semaphore por produto:** O semaforo deve ser global por dominio (padrao BaseScraper), nao por produto individual.

---

## Don't Hand-Roll

| Problema | Nao construir | Usar | Por que |
|----------|--------------|------|---------|
| Retry com backoff exponencial | loop manual try/except com sleep | `tenacity @retry` (ja instalado) | edge cases de jitter, reraise, logging ja resolvidos |
| HTML → texto limpo para LLM | regex strip de tags | `markdownify` (ou `html2text`) | preserva estrutura semantica, remove noise de CSS/JS |
| Deteccao de SPA vs SSR | heuristica de tamanho do HTML | `BaseScraper.fetch()` → fallback `fetch_spa()` | stealth + Playwright ja configurados |
| Rate limiting da Meta API | sleep manual | `asyncio.Semaphore` via `BaseScraper._get_semaphore()` | padrao estabelecido, evita duplicar logica |
| Persistencia + migrations | SQL raw | `sqlite-utils` + padrao de migration existente | WAL mode, FK, upsert ja abstraidos |
| Calculo de custo de tokens | divisao manual | `response.usage.input_tokens + output_tokens` do SDK Anthropic | SDK retorna o dado diretamente em `Message.usage` |

---

## Common Pitfalls

### Pitfall 1: Tabela `dossiers` ja existe com schema antigo

**O que ocorre:** `_001_initial.py` cria `dossiers` com: `id, product_id, analysis, opportunity_score, confidence_score, generated_at`. A migration `_003` precisa do schema novo com `status, dossier_json, incomplete, updated_at`.

**Por que ocorre:** Design incremental — _001 criou o schema minimo, _003 expande.

**Como evitar:** Em `_003_spy_dossiers.py`, checar colunas existentes antes de `add_column()`. Nao usar `db["dossiers"].create()` que falharia com "table already exists". Usar `add_column()` para cada nova coluna que nao existe. Para renomear `analysis` → `dossier_json`: considerar criar nova coluna e migrar, ou documentar que `analysis` e `dossier_json` coexistem temporariamente.

**Sinais de alerta:** `sqlite3.OperationalError: table dossiers already exists`

### Pitfall 2: `ad_reached_countries` obrigatorio na Meta API

**O que ocorre:** A API de Meta Ad Library exige `ad_reached_countries` como parametro obrigatorio. Sem ele, retorna HTTP 400.

**Por que ocorre:** Requisito de conformidade da Meta para o Ad Library (transparencia de anuncios politicos/sociais).

**Como evitar:** Sempre incluir `"ad_reached_countries": ["BR"]` (ou configuravel via config). Testar com fixture JSON gravada — mock da resposta HTTP.

**Sinais de alerta:** `400 Bad Request` na chamada a `ads_archive`

### Pitfall 3: SPA fallback inflando tokens

**O que ocorre:** `fetch_spa()` via Playwright retorna HTML completo renderizado incluindo React/Vue hydration state, que pode ser 5-10x maior que o conteudo util. Isso infla custo de tokens do LLM.

**Por que ocorre:** Playwright captura o DOM completo pos-render.

**Como evitar:** Aplicar `markdownify` com `strip=['script', 'style', 'noscript', 'meta', 'head', '__next_data__']` e truncar o texto limpo para um maximo razoavel (ex: 50.000 chars) antes de enviar ao LLM.

**Sinais de alerta:** `input_tokens > 100.000` na tabela `llm_calls`

### Pitfall 4: Google Search para reviews bloqueando por rate limit

**O que ocorre:** Google detecta scraping de resultados de busca e retorna CAPTCHA ou 429 apos poucos requests.

**Por que ocorre:** Google nao tem API publica para busca de reviews de produtos.

**Como evitar:** Para o MVP, fazer fetch simples do resultado de busca `"{nome produto}" review site:google.com/shopping` via `BaseScraper.fetch()` com headers realistas e delay generoso. Aceitar que pode falhar graciosamente — Google reviews nao e fonte obrigatoria bloqueante (o gate so requer 10 reviews de qualquer fonte). Alternativa: buscar a pagina de reviews da plataforma nativa primeiro.

**Sinais de alerta:** `ScraperError` frequente no `ReviewsScraper` para produtos de plataformas sem reviews nativos

### Pitfall 5: `asyncio.PriorityQueue` e comparacao de tuplas

**O que ocorre:** `asyncio.PriorityQueue` compara tuplas `(priority, item)`. Se dois items tiverem mesma prioridade, Python tenta comparar o segundo elemento — se for um objeto sem `__lt__`, levanta `TypeError`.

**Por que ocorre:** Python compara tuplas elemento-a-elemento.

**Como evitar:** Usar `(priority, counter, item)` onde `counter` e um inteiro monotonicamente crescente (desempate FIFO). Padrao: `(0, next(counter), product_id)` para manuais, `(rank, next(counter), product_id)` para automaticos.

**Sinais de alerta:** `TypeError: '<' not supported between instances of 'int' and 'Product'`

### Pitfall 6: Confundir `copy_analyzer` output com JSON

**O que ocorre:** LLM pode retornar texto livre em vez de JSON estruturado se o prompt nao for estrito o suficiente.

**Por que ocorre:** Modelos LLM nao garantem JSON por default sem instrucoes explicitas ou structured outputs.

**Como evitar:** No system prompt de `copy_analyzer.md`, instruir explicitamente: "Responda APENAS com JSON valido, sem texto adicional, sem markdown fencing". Fazer `json.loads()` no retorno e propagar `json.JSONDecodeError` como falha do pipeline (status=failed + retry).

**Sinais de alerta:** `json.JSONDecodeError` no `copy_analyzer.py`

---

## Code Examples

Verificados a partir de fontes oficiais:

### Anthropic SDK — Async com system prompt (pt-BR)
```python
# Source: platform.claude.com/docs/en/api/messages-examples (verificado 2026-03-14)
import os
from anthropic import AsyncAnthropic

async def call_llm(system_prompt: str, user_content: str) -> str:
    client = AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    return response.content[0].text
```

### Tracking de tokens e custo
```python
# response.usage retornado automaticamente pelo SDK Anthropic
response = await client.messages.create(...)
cost_usd = (response.usage.input_tokens * 0.000003 +
            response.usage.output_tokens * 0.000015)  # preco claude-sonnet-4-6
db["llm_calls"].insert({
    "dossier_id": dossier_id,
    "model": "claude-sonnet-4-6",
    "stage": stage,  # "copy_analyzer" ou "dossier_generator"
    "input_tokens": response.usage.input_tokens,
    "output_tokens": response.usage.output_tokens,
    "cost_usd": round(cost_usd, 6),
    "created_at": datetime.utcnow().isoformat(),
})
```

### Meta Ads API com httpx (sem token = graceful skip)
```python
# Source: developers.facebook.com/docs/graph-api/reference/ads_archive/
import httpx, os, structlog

log = structlog.get_logger()

async def fetch_meta_ads(product_title: str) -> list[dict]:
    token = os.getenv("META_ACCESS_TOKEN", "").strip()
    if not token:
        log.warning("meta_ads.skipped", reason="no_META_ACCESS_TOKEN")
        return []

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://graph.facebook.com/v25.0/ads_archive",
            params={
                "access_token": token,
                "search_terms": product_title[:100],
                "ad_reached_countries": "BR",        # OBRIGATORIO
                "ad_active_status": "ACTIVE",
                "ad_type": "ALL",
                "fields": "page_name,ad_snapshot_url,ad_creative_bodies,ad_delivery_start_time",
                "limit": 25,
            },
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp.json().get("data", [])
```

### markdownify para limpeza de HTML antes do LLM
```python
# Source: github.com/matthewwithanm/python-markdownify
import markdownify

def html_to_clean_text(html: str, max_chars: int = 50_000) -> str:
    """Converte HTML para Markdown limpo, removendo ruido para input do LLM."""
    clean = markdownify.markdownify(
        html,
        strip=["script", "style", "noscript", "meta", "head", "aside", "footer", "nav"],
        heading_style=markdownify.ATX,
    )
    # Truncar para evitar contexto excessivo de tokens
    return clean[:max_chars] if len(clean) > max_chars else clean
```

### asyncio.PriorityQueue com desempate por contador
```python
# Source: docs.python.org/3/library/asyncio-queue.html
import asyncio
from itertools import count

_counter = count()

async def enqueue_spy(queue: asyncio.PriorityQueue, product_id: int, is_manual: bool, rank: int = 999):
    priority = 0 if is_manual else rank
    await queue.put((priority, next(_counter), product_id))
```

### structlog alert para falha de espionagem (padrao do projeto)
```python
# Source: padrao estabelecido em mis/health_monitor.py
import structlog
log = structlog.get_logger()

log.error("spy.failed", alert="spy_failed", product_id=product_id, stage="sales_page", error=str(exc))
# Campos machine-readable: alert= e o campo chave para parsing externo
```

---

## State of the Art

| Abordagem Antiga | Abordagem Atual | Quando Mudou | Impacto |
|-----------------|-----------------|--------------|---------|
| Seletores CSS por plataforma | LLM como parser universal (platform-agnostic) | Design desta phase | Elimina manutencao de seletores; funciona em qualquer plataforma |
| Scraping Meta Ad Library | API oficial `ads_archive` | Meta 2018+ | Mais confiavel, ToS-compliant, menor risco de bloqueio |
| `html.parser` do stdlib para extracao de copy | markdownify → LLM em uma chamada | 2023+ | Elimina logica de parsing especifica de dominio |
| Anthropic SDK sync | `AsyncAnthropic` (async/await nativo) | SDK v0.20+ | Compativel com event loop asyncio do APScheduler |

**Deprecated / Desatualizado:**
- `BeautifulSoup` com seletores CSS especificos por plataforma: substituido por markdownify + LLM
- Prefill de resposta do LLM (assistant message parcial): DEPRECATED no claude-sonnet-4-6 — usar structured outputs ou instrucoes no system prompt

---

## Open Questions

1. **Schema conflict: tabela `dossiers` em _001 vs _003**
   - O que sabemos: `_001_initial.py` cria `dossiers` com `analysis TEXT, opportunity_score FLOAT, confidence_score FLOAT`. O CONTEXT.md especifica schema diferente para _003.
   - O que esta incerto: dados existentes em `dossiers` precisam ser migrados ou descartados?
   - Recomendacao: Tratar _003 como migration aditiva — adicionar colunas `status`, `dossier_json`, `incomplete`, `updated_at` via `add_column()`. Manter `analysis` como legado. Documentar que `dossier_json` e o campo canonico daqui para frente.

2. **Token de Meta Ads Library: tipo exato necessario**
   - O que sabemos: API requer `access_token`. Meta oferece User Access Token e System User Token.
   - O que esta incerto: User Access Token expira em 60 dias; System User Token e permanente mas requer Business Manager. Qual tipo o usuario vai gerar?
   - Recomendacao: Documentar no `.env.example` que `META_ACCESS_TOKEN` deve ser System User Token (permanente) para evitar expiracao automatica.

3. **Google Search para reviews: confiabilidade**
   - O que sabemos: Google bloqueia scraping agressivo. Nao ha API publica gratuita para busca de reviews.
   - O que esta incerto: Taxa de sucesso do fallback do Google para produtos de plataformas sem reviews nativos.
   - Recomendacao: Implementar fetch simples com retry; aceitar falha graciosamente. O gate requer 10 reviews de QUALQUER fonte — se a plataforma nativa tiver 10+, Google nunca e chamado.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.4.2 + pytest-asyncio 0.24 |
| Config file | `mis/pytest.ini` ou `pyproject.toml` (verificar se existe) |
| Quick run command | `pytest mis/tests/test_spy_*.py mis/tests/test_intelligence_*.py -x -q` |
| Full suite command | `pytest mis/tests/ -x -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SPY-01 | SalesPageScraper extrai copy de HTML fixture | unit | `pytest mis/tests/test_sales_page_spy.py -x` | ❌ Wave 0 |
| SPY-02 | MetaAdsScraper retorna lista de ads com token mock | unit | `pytest mis/tests/test_meta_ads_spy.py -x` | ❌ Wave 0 |
| SPY-02 | MetaAdsScraper retorna [] graciosamente sem token | unit | `pytest mis/tests/test_meta_ads_spy.py::test_no_token -x` | ❌ Wave 0 |
| SPY-03 | SalesPageScraper extrai preco, bonus, garantias da mesma pagina | unit | `pytest mis/tests/test_sales_page_spy.py::test_offer_extraction -x` | ❌ Wave 0 |
| SPY-04 | ReviewsScraper classifica reviews por valence corretamente | unit | `pytest mis/tests/test_reviews_spy.py -x` | ❌ Wave 0 |
| SPY-05 | Gate passa quando copy presente + 10 reviews | unit | `pytest mis/tests/test_completeness_gate.py::test_gate_passes -x` | ❌ Wave 0 |
| SPY-05 | Gate bloqueia quando copy ausente | unit | `pytest mis/tests/test_completeness_gate.py::test_copy_missing -x` | ❌ Wave 0 |
| SPY-05 | Gate bloqueia com < 10 reviews | unit | `pytest mis/tests/test_completeness_gate.py::test_reviews_below_threshold -x` | ❌ Wave 0 |
| DOS-01 | copy_analyzer retorna why_it_sells nao vazio | unit | `pytest mis/tests/test_copy_analyzer.py::test_happy_path -x` | ❌ Wave 0 |
| DOS-02 | dossier_generator retorna pains_addressed com fonte | unit | `pytest mis/tests/test_dossier_generator.py::test_pains_addressed -x` | ❌ Wave 0 |
| DOS-03 | dossier_generator retorna modeling_template estrutural | unit | `pytest mis/tests/test_dossier_generator.py::test_modeling_template -x` | ❌ Wave 0 |
| DOS-04 | dossier_generator retorna opportunity_score 0-100 + justificativa | unit | `pytest mis/tests/test_dossier_generator.py::test_opportunity_score -x` | ❌ Wave 0 |
| DOS-05 | confidence_score calculado corretamente para dados completos | unit | `pytest mis/tests/test_completeness_gate.py::test_confidence_full -x` | ❌ Wave 0 |
| DOS-05 | confidence_score reduzido sem ads | unit | `pytest mis/tests/test_completeness_gate.py::test_confidence_no_ads -x` | ❌ Wave 0 |

### Sampling Rate
- **Por task commit:** `pytest mis/tests/ -x -q --timeout=30`
- **Por wave merge:** `pytest mis/tests/ -x -q`
- **Phase gate:** Full suite green antes de `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `mis/tests/test_sales_page_spy.py` — cobre SPY-01, SPY-03
- [ ] `mis/tests/test_meta_ads_spy.py` — cobre SPY-02
- [ ] `mis/tests/test_reviews_spy.py` — cobre SPY-04
- [ ] `mis/tests/test_completeness_gate.py` — cobre SPY-05, DOS-05
- [ ] `mis/tests/test_copy_analyzer.py` — cobre DOS-01 (com fixture JSON gravada ao vivo)
- [ ] `mis/tests/test_dossier_generator.py` — cobre DOS-02, DOS-03, DOS-04
- [ ] `mis/tests/fixtures/sales_page/` — HTML fixtures de paginas de vendas reais
- [ ] `mis/tests/fixtures/meta_ads/` — JSON fixture da resposta da Meta API
- [ ] `mis/tests/fixtures/llm_responses/` — JSON fixtures das respostas do LLM (gravadas ao vivo)
- [ ] `mis/migrations/_003_spy_dossiers.py` — migration que cria reviews, llm_calls e adiciona colunas em dossiers
- [ ] Instalar: `pip install anthropic markdownify` + adicionar ao `mis/requirements.txt`

---

## Sources

### Primary (HIGH confidence)
- `mis/base_scraper.py` — padrao de retry, Semaphore, fetch/fetch_spa verificado diretamente
- `mis/migrations/_001_initial.py` — schema da tabela dossiers existente (pitfall critico identificado)
- `mis/requirements.txt` — dependencias atuais confirmadas
- `mis/scanner.py` — padrao de run_all_scanners() e integracao para hook pos-scan
- `platform.claude.com/docs/en/api/messages-examples` — API Anthropic, model ID confirmado como `claude-sonnet-4-6` (verificado 2026-03-14)
- `developers.facebook.com/docs/graph-api/reference/ads_archive/` — parametros obrigatorios da Meta API (verificado 2026-03-14)
- `github.com/anthropics/anthropic-sdk-python` — versao 0.84.0, Python 3.9+ confirmado (verificado 2026-03-14)

### Secondary (MEDIUM confidence)
- `github.com/matthewwithanm/python-markdownify` — opcoes de strip e heading_style verificadas via WebSearch + confirmadas multiplas fontes
- `docs.python.org/3/library/asyncio-queue.html` — PriorityQueue pattern com counter para desempate

### Tertiary (LOW confidence)
- Preco de tokens do `claude-sonnet-4-6` para calculo de cost_usd (estimativa no code example — verificar preco atual em anthropic.com/pricing)
- Taxa de sucesso do Google Search fallback para reviews (nao testado — depende de rate limiting da Google no ambiente de producao)

---

## Metadata

**Confidence breakdown:**
- Standard Stack: HIGH — dependencias verificadas contra requirements.txt existente + SDK oficial confirmado
- Architecture: HIGH — modulo structure extraido diretamente do CONTEXT.md + padroes existentes confirmados no codigo
- Meta API Parameters: MEDIUM — endpoint e parametros obrigatorios confirmados na documentacao oficial; parametros de fields sao configuracao, nao requisito critico
- Pitfalls: HIGH para schema conflict (evidencia direta em _001_initial.py); MEDIUM para demais (baseado em padroes conhecidos)

**Research date:** 2026-03-14
**Valid until:** 2026-04-14 (30 dias — stack relativamente estavel; Meta API versao pode mudar)
