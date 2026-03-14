# Phase 3: Product Espionage + Dossiers - Context

**Gathered:** 2026-03-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Para qualquer produto campeão identificado pelos scanners (ou informado via URL manual), o sistema extrai inteligência competitiva completa (copy da página de vendas + estrutura da oferta, anúncios Meta Ad Library, reviews) e gera um dossiê com análise de IA explicando por que o produto vende. O sistema de espionagem é **platform-agnostic** — funciona com qualquer URL de página de vendas, independente da plataforma (Hotmart, Gumroad, Kajabi, Teachable, etc.).

Descoberta automática de novos produtos (scanners adicionais) e integração MEGABRAIN completa (JARVIS agent) pertencem a outras fases.

</domain>

<decisions>
## Implementation Decisions

### Gatilho de Espionagem

- **Automático**: todo produto novo detectado pelo scanner é enfileirado para espionagem
- **Critério de seleção**: top 10 por nicho por plataforma (hardcoded, não configura top-N)
- **Timing**: disparado por evento — após `run_all_scanners()` completar (não por horário fixo)
- **Frequência automática**: nunca re-espionar produto com dossier existente (MVP)
- **Manual**: `python -m mis spy --url <URL>` aceita URL direta de qualquer plataforma; `--product-id` para produtos já no banco
- **Prioridade na fila**: produtos manuais têm prioridade máxima; automáticos ordenados por rank (posição 1 primeiro); hardcoded no código (não configurável)
- **Re-espionar manual**: sim, sempre — `--url` ou `--product-id` forçam nova espionagem mesmo com dossier existente
- **Produto que sai do top-10**: dossier preservado no banco, produto não re-espionado automaticamente
- **Concorrência**: `asyncio.Semaphore` com `max_concurrent_spy` configurável em config.yaml
- **Falha**: `structlog alert='spy_failed'`, produto marcado como `status=failed`, pipeline continua com próximo produto
- **Dados raw**: não persistidos — apenas dados estruturados no banco

### Data Completeness Gate (SPY-05)

- **Fontes obrigatórias**: copy da página de vendas, estrutura da oferta, reviews (mínimo 10), anúncios Meta Ad Library
- **Copy é bloqueante**: sem copy, dossier não é gerado — produto fica em `status=failed`
- **Oferta + copy**: extraídas juntas pelo mesmo `SalesPageScraper` (mesma página, mesmo fetch)
- **Reviews mínimo**: 10 reviews de qualquer fonte (plataforma ou Google) — configurável via `min_reviews` em config.yaml
- **Meta Ads**: obrigatório por padrão; após 3 tentativas falhas → gera dossier sem ads com confidence score reduzido
- **Sem META_ACCESS_TOKEN**: pula ads, reduz confidence score, sem bloqueio do pipeline
- **Timeout**: após 3 tentativas falhas (em ciclos diferentes), gera dossier parcial com confidence baixo + flag `incomplete: true`
- **Gate log**: structlog com campos individuais: `{copy_ok, offer_ok, reviews_count, ads_ok, gate_passed}` — machine-readable
- **Dossier parcial**: gerado com o disponível + flag `incomplete: true` + confidence score proporcional

### Pipeline de Análise IA

- **Modelo**: Claude (Anthropic API) — `claude-sonnet-4-6`; credenciais via `ANTHROPIC_API_KEY` no `.env`
- **Arquitetura**: pipeline especializado em 2 etapas: `copy_analyzer` → `dossier_generator`
- **copy_analyzer recebe**: copy da página + estrutura da oferta + anúncios Meta + reviews
- **copy_analyzer identifica**: framework de copy (AIDA, PAS, Story-based, etc.), gatilhos emocionais, estrutura narrativa, elementos de prova social
- **copy_analyzer é bloqueante**: falha do copy_analyzer para o pipeline — status=failed, retry na próxima execução
- **dossier_generator recebe**: output do copy_analyzer + dados brutos completos (reviews, oferta, ads)
- **Retry LLM**: tenacity 3x com backoff exponencial — mesmo padrão do BaseScraper
- **Idioma**: sempre pt-BR, independente do idioma do produto espionado
- **Score de oportunidade (DOS-04)**: LLM estima com base nos dados coletados (não algoritmo determinístico)
- **Análise**: genérica do produto espionado — sem contexto do nicho/produto do usuário (MVP)
- **Template de modelagem (DOS-03)**: estrutural — framework reutilizável (seções, argumentos-chave, estrutura de oferta sugerida). Não draft de copy pronta
- **Few-shot**: zero-shot com instruções claras no system prompt (sem exemplos no MVP)
- **Tracking de custo**: tabela `llm_calls(id, dossier_id, model, stage, input_tokens, output_tokens, cost_usd, created_at)`

### SalesPageScraper (Platform-Agnostic)

- **Parser universal**: HTML da página → texto limpo (markdownify/html2text) → LLM extrai copy + oferta em um único prompt
- **LLM extrai em uma chamada**: headlines, sub-headlines, argumentos, CTAs, estrutura narrativa, preço, bônus, garantias, upsells/downsells
- **SPAs**: `fetch_spa()` do BaseScraper (Playwright + stealth) para páginas JavaScript-rendered
- **Sem seletores por plataforma**: sistema é genuinamente platform-agnostic

### Reviews: Fontes de Coleta

- **Plataformas com reviews nativos** (Hotmart, ClickBank, Kiwify): página do produto na plataforma
- **Plataformas sem reviews nativos** (Gumroad, Kajabi, Teachable, etc.): Google Search `"{nome produto} review"`
- **Threshold**: 10 reviews de qualquer fonte (plataforma OU externas) para atingir completude mínima
- **Campo source** na tabela reviews: `'hotmart' | 'clickbank' | 'kiwify' | 'google' | 'sales_page'`

### Meta Ad Library

- **Acesso**: API oficial do Meta (`graph.facebook.com/ads_archive`) — não scraping
- **Token**: `META_ACCESS_TOKEN` no `.env`
- **Parâmetros de busca** (por nome/termo do produto): researcher confirma campos exatos da API
- **Sem token**: espionagem prossegue sem ads, confidence score reduzido, warning no log

### Confidence Score (DOS-05)

- **Escala**: 0–100%
- **Inputs**: copy presente (peso maior), quantidade de reviews (escala 0–10+), Meta ads presentes, oferta estruturada presente
- **Exibição**: campo `confidence_score` (int 0–100) na tabela dossiers

### Formato do Dossier

- **Banco**: JSON estruturado em coluna `dossier_json TEXT` na tabela `dossiers`
- **Seções obrigatórias do JSON**:
  - `why_it_sells` — fatores de sucesso identificados (DOS-01)
  - `pains_addressed` — lista de dores com fonte evidenciando (copy/review/ad) (DOS-02)
  - `modeling_template` — framework estrutural reutilizável (DOS-03)
  - `opportunity_score` — score 0–100 + justificativa do LLM (DOS-04)
  - `copy_analysis` — framework identificado, gatilhos, estrutura narrativa (output do copy_analyzer)
  - `confidence_score` — 0–100
  - `incomplete` — bool flag

### Estrutura de Módulos

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
│   ├── sales_page_extractor.md  # Prompt: extrai copy + oferta do texto limpo
│   ├── copy_analyzer.md         # Prompt: analisa copy e identifica framework
│   └── dossier_generator.md     # Prompt: gera dossiê completo em pt-BR
└── spy_orchestrator.py    # run_spy(product_id), run_spy_url(url) — ponto de entrada público
```

### Schema do Banco (Migration _003)

- **Uma migration**: `_003_spy_dossiers.py` cria todas as tabelas de Phase 3
- **Tabela dossiers**: `id, product_id FK, status [pending|running|done|failed], dossier_json TEXT, confidence_score INT, incomplete BOOL, created_at, updated_at`
- **Tabela reviews**: `id, product_id FK, text TEXT, valence TEXT [positive|negative], rating FLOAT, source TEXT, created_at` + INDEX em `(product_id, valence)`
- **Tabela llm_calls**: `id, dossier_id FK, model TEXT, stage TEXT, input_tokens INT, output_tokens INT, cost_usd REAL, created_at`
- **Anúncios**: coluna `ads_json TEXT` em dossiers (não tabela separada — MVP)

### Testes

- **LLM calls**: mock da API Anthropic com fixture JSON gravada ao vivo uma vez → commitada no repo (mesmo padrão dos scrapers de plataforma)
- **Mínimo por componente**: 5 testes (happy path, campos tipados, degraded mode/gate, alerta de falha, integração DB)
- **Data completeness gate**: unit tests com objetos `SpyData` mock com diferentes combinações de campos ausentes/presentes

### CLI Manual

- **Invocação**: `python -m mis spy --url <URL>` ou `python -m mis spy --product-id <ID>`
- **Progresso**: structlog em tempo real (cada etapa logada: fetching, extracting, collecting, generating)
- **Output**: JSON formatado no terminal + confirmação de save com product_id

### Interface Externa

- **Ponto de entrada público**: `spy_orchestrator.run_spy(product_id)` e `spy_orchestrator.run_spy_url(url)`
- Phase 6 conecta MEGABRAIN chamando essas funções — sem acoplamento na Phase 3

### Claude's Discretion

- Campos internos do JSON do dossier (estrutura detalhada dentro de cada seção)
- Pesos exatos de cada fonte no cálculo do confidence score
- Biblioteca específica: markdownify vs html2text
- Implementação interna da fila de espionagem (lista simples vs asyncio.Queue)
- Parâmetros exatos da chamada à API Meta (researcher confirma)

</decisions>

<specifics>
## Specific Ideas

- `SalesPageScraper` deve ser genuinamente platform-agnostic — o LLM como parser universal elimina a necessidade de seletores por plataforma. Isso é fundamental dado o plano de expandir para 15+ plataformas na Phase 2.5
- spy_orchestrator.run_spy_url() é o mecanismo que permite espionar produtos de Gumroad, Kajabi, Teachable, Stan Store etc. antes dos scanners dessas plataformas existirem (Phase 2.5)
- Dossier com `incomplete: true` ainda tem valor para o usuário — melhor que não ter nenhum dossier

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets

- `BaseScraper.fetch()` + `fetch_spa()`: SalesPageScraper, MetaAdsScraper e ReviewsScraper subclassificam diretamente — sem reescrever HTTP/Playwright/stealth
- `asyncio.Semaphore` + `DOMAIN_DELAYS`: controle de concorrência e rate limiting já implementados no BaseScraper
- `tenacity @retry`: reutilizar exatamente no pipeline LLM — mesmo padrão de `stop_after_attempt(3)`, `wait_exponential`
- `get_scheduler()` singleton: spy job acionado após run_all_scanners() no mesmo APScheduler
- `get_db()` + `run_migrations()`: pattern de acesso ao DB para nova migration _003
- `ScraperError`: scrapers de espionagem lançam a mesma exceção base
- `structlog` JSON com `alert=` field: replicar para `alert='spy_failed'`, `alert='completeness_gate_failed'`
- `conftest.py` com `tmp_path` DB real: reutilizar nos testes dos spies e do pipeline

### Established Patterns

- Fixtures HTML/JSON gravadas ao vivo → commitadas → testes usam fixtures (reutilizar para spies e LLM responses)
- `replace_existing=True` no APScheduler — reutilizar no spy job
- `UPDATE-then-INSERT` upsert para dossiers (product_id como chave única)
- 5 testes mínimos por componente: happy path, campos tipados, degraded mode, alerta, integração DB

### Integration Points

- `mis/scanner.py:run_all_scanners()` → chamar `spy_orchestrator.run_spy_batch()` após completar
- `mis/scheduler.py` → spy job acionado por evento (não horário separado)
- `mis/migrations/` → nova migration `_003_spy_dossiers.py`
- `mis/config.yaml` → novos settings: `max_concurrent_spy`, `min_reviews`, `spy_top_n: 10`
- `.env` → nova variável `META_ACCESS_TOKEN`

</code_context>

<deferred>
## Deferred Ideas

- **Phase 2.5 — Expansão de Plataformas** (a inserir no roadmap entre Phase 2 e Phase 3):
  Scanners automáticos para: Gumroad, Payhip, Podia, Sellfy, Lemon Squeezy, SendOwl, Etsy, Kajabi, Teachable, Skool, Mighty Networks, LearnWorlds, Stan Store, JVZoo, Digistore24.
  Na Phase 3, produtos dessas plataformas podem ser espionados manualmente via `--url` até a Phase 2.5 estar implementada.

- **Integração MEGABRAIN** (Phase 6): mis_agent.py, JARVIS slash commands para invocar espionagem dentro do MEGABRAIN. Phase 3 apenas expõe `run_spy()` como ponto de entrada — a integração real é Phase 6.

- **Re-espionar quando copy muda**: detector de drift de copy (hash da página de vendas) para acionar re-espionagem automática quando produto atualiza oferta. Fora de MVP.

</deferred>

---

*Phase: 03-product-espionage-dossiers*
*Context gathered: 2026-03-14*
