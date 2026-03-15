# Phase 4: Pain Radar - Context

**Gathered:** 2026-03-14
**Status:** Ready for planning

<domain>
## Phase Boundary

O sistema monitora automaticamente, a cada hora, as fontes onde o mercado expõe suas dores e desejos (Google Trends, Reddit, Quora, YouTube), coleta sinais por nicho configurado, e consolida em relatório horário por nicho via LLM. Análise de comentários de anúncios Meta (RADAR-04) está adiada para v2. Dashboard web para exibir os relatórios pertence à Phase 5.

</domain>

<decisions>
## Implementation Decisions

### Google Trends

- **Library**: pytrends — apesar da manutenção incerta, é a abordagem mais simples e sem credenciais. Se quebrar, o canary check alertará; researcher confirma status antes de implementar.
- **Anchor term**: configurado por nicho no `config.yaml` (ex: `emagrecimento → anchor: academia`). Constante entre todos os ciclos do mesmo nicho para permitir comparação histórica.
- **Keywords buscadas**: reutilizar o campo `keywords` já existente por nicho no config.yaml — sem duplicar configuração.
- **Janela temporal**: `now 7-d` — últimos 7 dias com granularidade horária. Captura tendências recentes com contexto suficiente para detectar picos.
- **Dados salvos por ciclo**: somente o índice normalizado no pico do período (um número por keyword por ciclo) — sem série temporal completa.
- **Rate limiting**: delay de 5–10s entre keywords do mesmo nicho + tenacity retry com backoff exponencial (padrão do BaseScraper). Se bloqueado: `alert='trends_ratelimited'` no structlog e pular o ciclo.
- **Ciclo**: horário (mesmo ritmo do radar principal).

### Reddit

- **Acesso**: PRAW com credenciais OAuth — API oficial, sem risco de ban, rate limit claro (60 req/min). Credenciais: `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT` no `.env`.
- **Subreddits por nicho**: lista configurada por nicho no config.yaml (ex: `emagrecimento → [r/Dieta, r/Emagrecimento, r/loseit]`). Usuário controla onde buscar.
- **Dados coletados**: título + URL + score (upvotes) + data de criação — sem texto completo do post.
- **Volume**: top 25 posts por nicho por ciclo.
- **Filtro temporal**: posts das últimas 24h (hot/new).

### Quora

- **Acesso**: scraping via `httpx` + BeautifulSoup — `BaseScraper.fetch()` com stealth headers. Sem credenciais. Pesquisador confirma se SSR é suficiente ou precisa de `fetch_spa()`.
- **Dados coletados**: título da pergunta + URL + data — mesmo formato do Reddit para consistência.
- **Volume**: top 25 perguntas por nicho por ciclo.
- **Keywords usadas**: mesmo campo `keywords` do config.yaml.

### YouTube

- **Estratégia de coleta**: `search.list(q=keyword, maxResults=10)` = 100 unidades/chamada. Depois `commentThreads.list` nos top 5 vídeos = 5u. Total ~105u por keyword.
- **Dados coletados**: título + URL + view_count + like_count + top comentários dos 5 vídeos mais relevantes.
- **Ciclo**: a cada 4–6h (não horário) — evita estourar a quota diária gratuita de 10.000u.
- **Idioma**: configurado por nicho via `relevance_language` no config.yaml (ex: emagrecimento → `pt`, marketing-digital → `pt`, nichos gringa → `en`).
- **Quota guard**: monitorar uso acumulado diário. Ao atingir 9.000u: `alert='youtube_quota_exhausted'` no structlog + desabilitar job YouTube para os ciclos restantes do dia. Reativa automaticamente à meia-noite (reset diário do Google).
- **Credenciais**: `YOUTUBE_DATA_API_KEY` no `.env`.

### Síntese e Relatório de Dores

- **Síntese**: LLM `claude-sonnet-4-6` sintetiza todos os sinais brutos do ciclo em dores acionáveis. Idioma: sempre pt-BR. Mesmo padrão do pipeline de dossiers (Phase 3).
- **Conteúdo do relatório por nicho**: top 5 dores + fonte de evidência (ex: "Reddit: 23 posts, YouTube: alto view_count") + nível de interesse (Alto/Médio/Baixo).
- **Armazenamento**: tabela `pain_reports(id, niche_id, cycle_at, report_json, created_at)` no SQLite. Compatível com DASH-03 da Phase 5.
- **Timing do synthesizer**: job separado `radar_synthesizer` que roda 30min após o ciclo de coleta (ex: coletores no :00, synthesizer no :30). Independente de quais fontes falharam.

### Idempotência e Deduplicação

- **Deduplicação de sinais brutos**: hash do URL como chave única (unique constraint em `pain_signals.url_hash`). Upsert preserva o mais recente. Posts do Reddit/Quora/YouTube que reaparecem em ciclos diferentes não geram duplicatas.
- **Idempotência do relatório**: unique constraint em `(niche_id, cycle_hour)` na tabela `pain_reports`. Re-execução do ciclo substitui o relatório existente via upsert.

### Scheduler e Jobs

- **Jobs separados por fonte** (mesma estratégia dos scanners de plataforma):
  - `radar_trends`: CronTrigger a cada 1h
  - `radar_reddit_quora`: CronTrigger a cada 1h
  - `radar_youtube`: CronTrigger a cada 4h
  - `radar_synthesizer`: CronTrigger a cada 1h, offset de 30min
- Falha de uma fonte não afeta as demais. `replace_existing=True` padrão.

### CLI Manual

- **Comando**: `python -m mis radar --niche <slug>` — roda o ciclo completo de radar para um nicho específico.
- Mesmo padrão do `python -m mis spy --url`. Output: structlog em tempo real + confirmação de relatório gerado.

### Retenção de Dados Brutos

- Sinais brutos (tabela `pain_signals`) retidos por 30 dias.
- Job de cleanup diário deleta registros com `collected_at < now() - 30 dias`.
- Relatórios (`pain_reports`) retidos indefinidamente — são o output final do sistema.

### RADAR-04 (Comentários de Anúncios Meta)

- **Adiado para v2** — coleta de comentários de anúncios patrocinados não tem API oficial no Meta, requer Playwright com anti-bot agressivo. Reddit + YouTube cobrem o sinal de dores para MVP.
- MetaAdsScraper da Phase 3 (coleta anúncios por produto) permanece sem alteração.

### Claude's Discretion

- Schema detalhado da tabela `pain_signals` (campos, índices)
- Prompt exato do LLM synthesizer
- Threshold exato do quota guard (configurável em config.yaml como `youtube_quota_daily_limit: 9000`)
- Algoritmo de cleanup de dados brutos (batch size, frequência)
- Campos exatos do bloco `radar` no config.yaml (researcher define com base na estrutura existente)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets

- `BaseScraper.fetch()` + `fetch_spa()`: Quora usa `fetch()` (SSR), scrapers de Reddit/YouTube usam bibliotecas dedicadas (PRAW, google-api-python-client) mas podem subclassificar BaseScraper para retry e logging
- `asyncio.Semaphore` + tenacity `@retry`: replicar exatamente nos coletores de Trends/Quora
- `get_scheduler()` singleton: adicionar os 4 novos jobs de radar (`radar_trends`, `radar_reddit_quora`, `radar_youtube`, `radar_synthesizer`)
- `structlog` JSON com `alert=` field: replicar para `alert='trends_ratelimited'`, `alert='youtube_quota_exhausted'`, `alert='radar_collector_failed'`
- `get_db()` + `run_migrations()`: padrão para migration `_004_pain_radar.py`
- `conftest.py` com `tmp_path` DB real: reutilizar nos testes dos coletores e synthesizer
- `ScraperError`: coletores de radar lançam a mesma exceção base
- `replace_existing=True` no APScheduler: padrão para os novos jobs

### Established Patterns

- Fixtures HTML/JSON gravadas ao vivo → commitadas → testes usam fixtures (replicar para Reddit, Quora, YouTube responses)
- 5 testes mínimos por componente: happy path, campos tipados, degraded mode (falha de fonte), alerta estruturado, integração DB
- Migrations idempotentes com `IF NOT EXISTS` e `add_column` checks
- `config.yaml` como fonte de truth — novos campos: `anchor_term`, `subreddits`, `relevance_language` por nicho; `radar_schedule`, `youtube_quota_daily_limit` em settings

### Integration Points

- `mis/scheduler.py`: adicionar `register_radar_jobs(config)` que registra os 4 jobs de radar
- `mis/migrations/`: nova migration `_004_pain_radar.py` para tabelas `pain_signals` e `pain_reports`
- `mis/config.yaml`: adicionar bloco `radar` por nicho e novos settings de quota/schedule
- `.env`: novas variáveis `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT`, `YOUTUBE_DATA_API_KEY`
- `mis/__main__.py`: adicionar subcomando `radar` ao CLI

</code_context>

<specifics>
## Specific Ideas

- Jobs do radar separados por fonte replicam exatamente o padrão dos scanners de plataforma — falha de uma fonte (ex: Quora scraping quebrado) não interrompe Reddit nem YouTube
- O `radar_synthesizer` rodando 30min depois garante que mesmo ciclos com falhas parciais geram um relatório com o que foi coletado
- Quota guard do YouTube como quota_used acumulado no banco (ou em memória no job) — não depende de chamada à API do Google para verificar saldo

</specifics>

<deferred>
## Deferred Ideas

- **RADAR-04 — Comentários de anúncios Meta por nicho**: sem API oficial, anti-bot agressivo do Meta. Adiar para v2 — Reddit + YouTube cobrem o sinal de dores para MVP.
- **Solicitar quota expandida YouTube API**: conforme STATE.md blocker, aprovação leva 1-2 semanas. Implementar com ciclo de 4h e quota guard — solicitar expansão como ação operacional separada.
- **Rising queries do Google Trends**: capturar "related queries" / "breakout queries" além do índice normalizado. Mais rico para detectar dores emergentes — v2.
- **Subreddits auto-descobertos**: auto-descoberta de subreddits por keyword via Reddit search API. Mais flexível que lista manual — v2 após validar com lista configurada.

</deferred>

---

*Phase: 04-pain-radar*
*Context gathered: 2026-03-14*
