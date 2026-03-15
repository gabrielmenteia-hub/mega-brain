# Phase 4: Pain Radar - Research

**Researched:** 2026-03-15
**Domain:** Data collection pipelines — Google Trends, Reddit (PRAW), Quora scraping, YouTube Data API v3, LLM synthesis, APScheduler, SQLite deduplication
**Confidence:** HIGH (decisions locked, código existente inspecionado, APIs verificadas)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Google Trends**
- Library: pytrends — apesar da manutenção incerta, é a abordagem mais simples e sem credenciais. Se quebrar, o canary check alertará; researcher confirma status antes de implementar.
- Anchor term: configurado por nicho no `config.yaml` (ex: `emagrecimento → anchor: academia`). Constante entre todos os ciclos do mesmo nicho para permitir comparação histórica.
- Keywords buscadas: reutilizar o campo `keywords` já existente por nicho no config.yaml — sem duplicar configuração.
- Janela temporal: `now 7-d` — últimos 7 dias com granularidade horária.
- Dados salvos por ciclo: somente o índice normalizado no pico do período (um número por keyword por ciclo).
- Rate limiting: delay de 5–10s entre keywords do mesmo nicho + tenacity retry com backoff exponencial. Se bloqueado: `alert='trends_ratelimited'` no structlog e pular o ciclo.
- Ciclo: horário.

**Reddit**
- Acesso: PRAW com credenciais OAuth — `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT` no `.env`.
- Subreddits por nicho: lista configurada por nicho no config.yaml.
- Dados coletados: título + URL + score (upvotes) + data de criação — sem texto completo.
- Volume: top 25 posts por nicho por ciclo.
- Filtro temporal: posts das últimas 24h (hot/new).

**Quora**
- Acesso: scraping via `httpx` + BeautifulSoup — `BaseScraper.fetch()` com stealth headers. Sem credenciais. Pesquisador confirma se SSR é suficiente ou precisa de `fetch_spa()`.
- Dados coletados: título da pergunta + URL + data.
- Volume: top 25 perguntas por nicho por ciclo.
- Keywords usadas: mesmo campo `keywords` do config.yaml.

**YouTube**
- Estratégia: `search.list(q=keyword, maxResults=10)` = 100u/chamada; `commentThreads.list` nos top 5 vídeos = 5u. Total ~105u por keyword.
- Dados: título + URL + view_count + like_count + top comentários dos 5 vídeos mais relevantes.
- Ciclo: a cada 4–6h (não horário).
- Idioma: configurado por nicho via `relevance_language` no config.yaml.
- Quota guard: ao atingir 9.000u: `alert='youtube_quota_exhausted'` + desabilitar job YouTube para ciclos restantes do dia. Reativa à meia-noite.
- Credenciais: `YOUTUBE_DATA_API_KEY` no `.env`.

**Síntese e Relatório**
- LLM: `claude-sonnet-4-6`, pt-BR, mesmo padrão do pipeline de dossiers (Phase 3).
- Conteúdo: top 5 dores + fonte de evidência + nível de interesse (Alto/Médio/Baixo).
- Armazenamento: tabela `pain_reports(id, niche_id, cycle_at, report_json, created_at)`.
- Timing: job `radar_synthesizer` roda 30min após coletores (coletores no :00, synthesizer no :30).

**Idempotência e Deduplicação**
- Deduplicação: hash do URL como chave única (`unique constraint` em `pain_signals.url_hash`). Upsert preserva o mais recente.
- Idempotência do relatório: unique constraint em `(niche_id, cycle_hour)` na tabela `pain_reports`. Re-execução substitui via upsert.

**Scheduler e Jobs**
- `radar_trends`: CronTrigger a cada 1h
- `radar_reddit_quora`: CronTrigger a cada 1h
- `radar_youtube`: CronTrigger a cada 4h
- `radar_synthesizer`: CronTrigger a cada 1h, offset de 30min
- `replace_existing=True` padrão.

**CLI Manual**
- `python -m mis radar --niche <slug>` — roda ciclo completo para um nicho específico.

**Retenção**
- Sinais brutos retidos 30 dias; cleanup job diário.
- Relatórios retidos indefinidamente.

**RADAR-04 (Meta)**
- Adiado para v2.

### Claude's Discretion
- Schema detalhado da tabela `pain_signals` (campos, índices)
- Prompt exato do LLM synthesizer
- Threshold exato do quota guard (configurável em config.yaml como `youtube_quota_daily_limit: 9000`)
- Algoritmo de cleanup de dados brutos (batch size, frequência)
- Campos exatos do bloco `radar` no config.yaml (researcher define com base na estrutura existente)

### Deferred Ideas (OUT OF SCOPE)
- RADAR-04 — Comentários de anúncios Meta por nicho (v2)
- Solicitar quota expandida YouTube API (ação operacional separada)
- Rising queries / related queries do Google Trends (v2)
- Subreddits auto-descobertos por keyword (v2)
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| RADAR-01 | Sistema monitora Google Trends por nicho a cada hora, com normalização por anchor term estável | pytrends arquivado — usar `pytrends-modern` ou `trendspyg`; padrão `interest_over_time()` com `timeframe='now 7-d'`; índice normalizado (0–100) por anchor |
| RADAR-02 | Sistema coleta perguntas e posts de Reddit e Quora relacionados aos nichos configurados | PRAW OAuth ativo e mantido (60 req/min); Quora requer `fetch_spa()` — não SSR puro; padrão de upsert por URL hash |
| RADAR-03 | Sistema analisa títulos e comentários de vídeos no YouTube por nicho (com quota management) | `google-api-python-client`; `search.list`=100u; `commentThreads.list`=1u; quota diária 10.000u resets à meia-noite PT |
| RADAR-04 | Sistema coleta comentários de anúncios patrocinados no Meta por nicho | ADIADO para v2 — sem API oficial, anti-bot agressivo |
| RADAR-05 | Pipeline do radar é idempotente (re-execução não gera duplicatas) | `url_hash` UNIQUE em `pain_signals`; `(niche_id, cycle_hour)` UNIQUE em `pain_reports`; upsert pattern |
| RADAR-06 | Relatório horário consolidado é gerado com as principais dores/desejos detectados por nicho | LLM `claude-sonnet-4-6`, mesmo padrão de `dossier_generator.py`; tabela `pain_reports`; `radar_synthesizer` job no :30 |
</phase_requirements>

---

## Summary

A Phase 4 implementa um pipeline de monitoramento de sinais de mercado com quatro coletores independentes (Google Trends, Reddit, Quora, YouTube) e um synthesizer LLM que consolida os dados em relatórios horários por nicho. O sistema é construído sobre os padrões já estabelecidos nas phases 1–3: APScheduler singleton, BaseScraper com retry/semaphore, structlog com `alert=` field, migrações idempotentes, e LLM via Anthropic SDK.

O principal descoberto crítico de research é que **pytrends foi arquivado em abril de 2025** — a decisão de "verificar status" no CONTEXT.md é corroborada. A recomendação é usar `pytrends-modern` (PyPI: `pytrends-modern`) ou `trendspyg` como substituto drop-in, ambos ativamente mantidos e com mesma interface de `interest_over_time()`. Igualmente crítico: **Quora é uma SPA JavaScript**, não SSR — `BaseScraper.fetch()` retornará HTML vazio; será necessário `fetch_spa()` (Playwright), o que implica maior latência e risco de bloqueio anti-bot.

A arquitetura de jobs segue exatamente o padrão dos scanners de plataforma: cada fonte é um job isolado com `replace_existing=True`, registrados via `register_radar_jobs(config)` no `scheduler.py`. A migração `_004_pain_radar.py` cria duas tabelas novas: `pain_signals` (sinais brutos com deduplicação por URL hash) e `pain_reports` (relatórios LLM com idempotência por ciclo).

**Primary recommendation:** Usar `pytrends-modern` no lugar do `pytrends` arquivado; implementar Quora via `fetch_spa()` desde o início com fallback gracioso; controlar quota YouTube com contador persistido no banco (não em memória) para sobreviver a restarts.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pytrends-modern | 0.2.5+ | Google Trends pseudo-API | Fork ativo do pytrends arquivado; mesma API `interest_over_time()` |
| praw | >=7.0 | Reddit OAuth API wrapper | Único wrapper oficial; rate limiting automático; mantido ativamente |
| google-api-python-client | >=2.0 | YouTube Data API v3 | Wrapper oficial Google; build('youtube','v3') pattern |
| httpx[http2] | >=0.28.1 | HTTP async client para Quora | Já no projeto; reusa BaseScraper |
| beautifulsoup4 | >=4.12.0 | Parse HTML da Quora | Já no projeto |
| anthropic | >=0.79.0 | LLM synthesis (dossier pattern) | Já no projeto; AsyncAnthropic com tenacity |
| apscheduler | >=3.11.2 | Job scheduler | Já no projeto; AsyncIOScheduler singleton |
| structlog | >=25.5.0 | JSON logging com `alert=` field | Já no projeto |
| sqlite-utils | >=3.39 | ORM leve SQLite | Já no projeto; upsert/create pattern |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| trendspyg | latest | Alternativa ao pytrends-modern | Se pytrends-modern falhar; mesma interface |
| tenacity | >=9.1.4 | Retry com backoff exponencial | Já no projeto; replicar em todos os coletores |
| python-dotenv | >=1.2.1 | Carregar .env | Já no projeto |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pytrends-modern | SerpAPI Google Trends | SerpAPI é pago; pytrends-modern é gratuito mas sem SLA |
| PRAW | Reddit JSON endpoints diretos | PRAW tem rate limiting automático e tratamento OAuth; sem PRAW requer reimplementar |
| google-api-python-client | youtube-data-api (PyPI) | Wrapper não oficial; menos confiável |

**Installation (novos pacotes apenas):**
```bash
pip install pytrends-modern praw google-api-python-client
```

---

## Architecture Patterns

### Recommended Project Structure
```
mis/
├── radar/                   # novo — coletores do Pain Radar
│   ├── __init__.py
│   ├── trends_collector.py  # RADAR-01: Google Trends
│   ├── reddit_collector.py  # RADAR-02: Reddit via PRAW
│   ├── quora_collector.py   # RADAR-02: Quora via fetch_spa()
│   ├── youtube_collector.py # RADAR-03: YouTube Data API v3
│   └── synthesizer.py       # RADAR-06: LLM synthesis
├── migrations/
│   └── _004_pain_radar.py   # tabelas pain_signals + pain_reports
├── scheduler.py             # adicionar register_radar_jobs()
├── __main__.py              # adicionar subcomando 'radar'
└── config.yaml              # adicionar bloco radar por nicho
```

### Pattern 1: Collector com Graceful Degradation
**What:** Cada coletor é uma função async independente que retorna lista de sinais ou lista vazia em falha. Nunca propaga exceção para o scheduler.
**When to use:** Todos os quatro coletores (trends, reddit, quora, youtube).

```python
# Padrão estabelecido em health_monitor.py (run_canary_check() nunca propaga)
async def collect_reddit_signals(niche: dict, config: dict) -> list[dict]:
    try:
        import praw
        reddit = praw.Reddit(
            client_id=os.environ["REDDIT_CLIENT_ID"],
            client_secret=os.environ["REDDIT_CLIENT_SECRET"],
            user_agent=os.environ["REDDIT_USER_AGENT"],
        )
        subreddits = niche.get("subreddits", [])
        signals = []
        for sub_name in subreddits:
            sub = reddit.subreddit(sub_name)
            for post in sub.new(limit=25):
                signals.append({
                    "url": f"https://reddit.com{post.permalink}",
                    "title": post.title,
                    "score": post.score,
                    "collected_at": datetime.utcnow().isoformat(),
                    "source": "reddit",
                    "niche_slug": niche["slug"],
                })
        return signals
    except Exception as e:
        log.error("radar.reddit.failed", niche=niche["slug"], error=str(e),
                  alert="radar_collector_failed")
        return []
```

### Pattern 2: Upsert por URL Hash (RADAR-05)
**What:** Deduplicação de sinais brutos usando hash SHA-256 do URL como chave única.
**When to use:** Ao persistir qualquer sinal no `pain_signals`.

```python
import hashlib

def _url_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()

def upsert_signal(db, signal: dict) -> None:
    url_hash = _url_hash(signal["url"])
    # sqlite-utils upsert com hash como identificador único
    db["pain_signals"].upsert(
        {**signal, "url_hash": url_hash},
        hash_id="url_hash",  # ou pk="url_hash" com alter=True
    )
```

### Pattern 3: Quota Guard YouTube (RADAR-03)
**What:** Contador de quota persistido no banco (não em memória) para sobreviver a restarts do processo.
**When to use:** Job `radar_youtube` antes de cada chamada à API.

```python
def get_quota_used_today(db, reset_hour_utc: int = 7) -> int:
    """Retorna quota usada hoje (reset à meia-noite PT = 07:00 UTC)."""
    today_reset = datetime.utcnow().replace(
        hour=reset_hour_utc, minute=0, second=0, microsecond=0
    )
    rows = list(db["youtube_quota_log"].rows_where(
        "logged_at > ?", [today_reset.isoformat()]
    ))
    return sum(r["units"] for r in rows)
```

### Pattern 4: radar_synthesizer (RADAR-06)
**What:** Job separado que agrega sinais do ciclo atual e chama LLM. Idempotente via upsert em `(niche_id, cycle_hour)`.
**When to use:** CronTrigger no :30 de cada hora.

```python
# Padrão baseado em dossier_generator.py
async def synthesize_niche_pains(niche_id: int, cycle_at: str, db_path: str) -> dict:
    signals = fetch_cycle_signals(db_path, niche_id, cycle_at)
    prompt = build_synthesis_prompt(signals)
    response = await call_llm(prompt, model="claude-sonnet-4-6")
    report = parse_report(response)
    # upsert idempotente
    db["pain_reports"].upsert(
        {"niche_id": niche_id, "cycle_at": cycle_at, "report_json": json.dumps(report)},
        hash_id=None,
        # unique constraint (niche_id, cycle_hour) garante idempotência
    )
    return report
```

### Pattern 5: register_radar_jobs (scheduler.py)
**What:** Função que registra os 4 jobs do radar no APScheduler singleton.
**When to use:** Chamada no startup junto com `register_scan_and_spy_job`.

```python
def register_radar_jobs(config: dict) -> None:
    from apscheduler.triggers.cron import CronTrigger
    scheduler = get_scheduler()

    # radar_trends: a cada 1h no :00
    scheduler.add_job(_radar_trends_job, CronTrigger(minute=0),
                      args=[config], id="radar_trends", replace_existing=True)

    # radar_reddit_quora: a cada 1h no :00
    scheduler.add_job(_radar_reddit_quora_job, CronTrigger(minute=0),
                      args=[config], id="radar_reddit_quora", replace_existing=True)

    # radar_youtube: a cada 4h no :00
    scheduler.add_job(_radar_youtube_job, CronTrigger(hour="*/4", minute=0),
                      args=[config], id="radar_youtube", replace_existing=True)

    # radar_synthesizer: a cada 1h no :30
    scheduler.add_job(_radar_synthesizer_job, CronTrigger(minute=30),
                      args=[config], id="radar_synthesizer", replace_existing=True)
```

### Anti-Patterns to Avoid
- **Propagar exceção no job do scheduler:** Qualquer exceção não capturada derruba o job. Todos os coletores devem `try/except` e retornar `[]` em falha, emitindo `alert=` no structlog.
- **Quota YouTube em variável de módulo:** Processo pode restartar; contador deve ser persistido em tabela SQLite `youtube_quota_log`.
- **Usar pytrends original (arquivado):** O pacote `pytrends` foi arquivado em abril de 2025 e não recebe mais manutenção. Usar `pytrends-modern` (PyPI).
- **Assumir Quora como SSR:** Quora é SPA JavaScript; `BaseScraper.fetch()` retorna HTML shell sem conteúdo. Usar `fetch_spa()` (Playwright).
- **Série temporal completa do Trends:** Decisão locked: salvar apenas o índice normalizado no pico — não a série completa. Economiza espaço e simplifica comparação histórica.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Reddit API access | Cliente HTTP manual com auth OAuth | PRAW | Rate limiting automático, paginação, tratamento de erros de API |
| YouTube API calls | Requests diretos para `youtube.googleapis.com` | `google-api-python-client` | Tratamento de paginação, refresh de credenciais, tipo-safe |
| Google Trends data | Scraping direto de trends.google.com | `pytrends-modern` | Google usa tokens CSRF internos, rotação de cookies — difícil de manter |
| Deduplicação de URLs | Comparar strings de URL completas | SHA-256 hash + UNIQUE constraint SQLite | URLs podem ter query params em ordem diferente mas serem equivalentes; hash normaliza |
| Retry com backoff | Loop manual com `time.sleep` | tenacity `@retry` com `wait_exponential` | Já estabelecido no projeto; consistência de comportamento |

**Key insight:** Todos os problemas de deduplicação, rate limiting e retry já têm soluções estabelecidas no projeto. O risco principal está em Quora (SPA) e pytrends (arquivado) — não inventar soluções, usar os substitutos identificados.

---

## Common Pitfalls

### Pitfall 1: pytrends arquivado quebra silenciosamente
**What goes wrong:** `import pytrends` pode ainda funcionar se instalado, mas a biblioteca não recebe patches de segurança e pode quebrar a qualquer mudança de endpoint do Google sem atualização.
**Why it happens:** GeneralMills/pytrends foi arquivado em abril de 2025 — read-only, sem PRs aceitos.
**How to avoid:** Instalar `pytrends-modern` explicitamente no `requirements.txt`. Adicionar canary check para o job `radar_trends` (padrão já existente em `health_monitor.py`).
**Warning signs:** `TrendReq` raises `ResponseError` ou retorna sempre `None`; canary check falha.

### Pitfall 2: Quora não é SSR
**What goes wrong:** `BaseScraper.fetch()` retorna HTML shell do React app sem perguntas — BeautifulSoup não encontra nada.
**Why it happens:** Quora é SPA JavaScript; todo conteúdo é carregado via chamadas API após o JS ser executado.
**How to avoid:** Usar `fetch_spa()` (Playwright) desde o início. Adicionar fallback: se `len(parsed_questions) == 0`, emitir `alert='quora_empty_response'` e retornar `[]`.
**Warning signs:** `soup.find_all('div', class_='question')` retorna lista vazia; HTML retornado é < 5KB.

### Pitfall 3: Quota YouTube estourada antes do horário previsto
**What goes wrong:** Com 3 nichos × 3 keywords × 105u = ~945u por ciclo de 4h. Em 10 ciclos = 9.450u — acima do threshold de 9.000u. Se ciclos atrasarem e se acumularem, pode esgotar cedo.
**Why it happens:** Estimativa assume exatamente 10 ciclos por dia; na prática, restarts de processo podem causar execuções extras.
**How to avoid:** Persistir `youtube_quota_log` no banco (não em memória). Quota guard verifica o log desde o último reset (meia-noite PT = 07:00 UTC).
**Warning signs:** `alert='youtube_quota_exhausted'` aparece antes das 20h UTC; relatórios sem dados YouTube.

### Pitfall 4: Relatório do synthesizer gerado mesmo sem sinais
**What goes wrong:** `radar_synthesizer` roda no :30 mas todos os coletores falharam às :00 — LLM gera relatório com "sem dados" ou alucina dores.
**Why it happens:** Job do synthesizer não sabe que os coletores falharam.
**How to avoid:** Synthesizer verifica `COUNT(*)` de sinais do ciclo atual antes de chamar LLM. Se `count == 0`, emitir `alert='radar_synthesizer_no_signals'` e pular geração (não criar registro vazio em `pain_reports`).
**Warning signs:** `pain_reports` com `report_json` contendo `"pains": []`; LLM cost_usd sendo cobrado sem sinais.

### Pitfall 5: PRAW síncrono bloqueando event loop
**What goes wrong:** PRAW é uma biblioteca síncrona. Chamadas dentro de job `async def _radar_reddit_quora_job()` bloqueiam o event loop do APScheduler.
**Why it happens:** PRAW não tem API async nativa.
**How to avoid:** Usar `asyncio.get_event_loop().run_in_executor(None, _sync_reddit_collect, niche, config)` para executar PRAW em thread pool. Padrão análogo ao httpx síncrono em contexto async.
**Warning signs:** Outros jobs (trends, synthesizer) ficam aguardando enquanto Reddit coleta.

---

## Code Examples

Verified patterns from official sources:

### pytrends-modern: interest_over_time com anchor
```python
# Source: https://github.com/yiromo/pytrends-modern
from pytrends.request import TrendReq  # pytrends-modern mantém mesma API

async def collect_trends_signal(keyword: str, anchor: str, niche_slug: str) -> dict | None:
    try:
        pytrends = TrendReq(hl='pt-BR', tz=360)
        kw_list = [keyword, anchor]  # anchor sempre presente para normalização
        pytrends.build_payload(kw_list, timeframe='now 7-d')
        df = pytrends.interest_over_time()
        if df.empty:
            return None
        # índice normalizado no pico do período (relativo ao anchor)
        peak_idx = int(df[keyword].max())
        return {
            "keyword": keyword,
            "anchor": anchor,
            "peak_index": peak_idx,
            "niche_slug": niche_slug,
            "collected_at": datetime.utcnow().isoformat(),
            "source": "google_trends",
        }
    except Exception as e:
        log.error("radar.trends.failed", keyword=keyword, error=str(e),
                  alert="trends_ratelimited")
        return None
```

### PRAW: coleta Reddit síncrona (wrappear em executor)
```python
# Source: https://github.com/praw-dev/praw (mantido, OAuth pattern)
import praw, asyncio

def _sync_collect_reddit(niche: dict) -> list[dict]:
    reddit = praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        user_agent=os.environ["REDDIT_USER_AGENT"],
    )
    results = []
    for sub_name in niche.get("subreddits", []):
        for post in reddit.subreddit(sub_name).new(limit=25):
            age_h = (datetime.utcnow() - datetime.utcfromtimestamp(post.created_utc)).seconds / 3600
            if age_h <= 24:
                results.append({
                    "url": f"https://reddit.com{post.permalink}",
                    "title": post.title,
                    "score": post.score,
                    "source": "reddit",
                    "niche_slug": niche["slug"],
                    "collected_at": datetime.utcnow().isoformat(),
                })
    return results

async def collect_reddit_signals(niche: dict) -> list[dict]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _sync_collect_reddit, niche)
```

### YouTube Data API v3: search + commentThreads
```python
# Source: https://developers.google.com/youtube/v3/docs/search/list
from googleapiclient.discovery import build

def _sync_collect_youtube(keyword: str, lang: str, api_key: str) -> list[dict]:
    youtube = build("youtube", "v3", developerKey=api_key)

    # search.list = 100 units
    search_resp = youtube.search().list(
        q=keyword,
        part="snippet",
        maxResults=10,
        relevanceLanguage=lang,
        type="video",
    ).execute()

    videos = search_resp.get("items", [])[:5]
    signals = []

    for video in videos:
        vid_id = video["id"]["videoId"]
        title = video["snippet"]["title"]

        # commentThreads.list = 1 unit per call
        try:
            comments_resp = youtube.commentThreads().list(
                videoId=vid_id,
                part="snippet",
                maxResults=10,
                order="relevance",
            ).execute()
            top_comments = [
                c["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                for c in comments_resp.get("items", [])
            ]
        except Exception:
            top_comments = []

        signals.append({
            "url": f"https://youtube.com/watch?v={vid_id}",
            "title": title,
            "top_comments": top_comments,
            "source": "youtube",
            "collected_at": datetime.utcnow().isoformat(),
        })

    return signals  # ~105 units consumed
```

### Migration _004: pain_signals + pain_reports
```python
# Padrão de _003_spy_dossiers.py com IF NOT EXISTS
import sqlite_utils

def run_migration_004(db_path: str) -> None:
    db = sqlite_utils.Database(db_path)

    if "pain_signals" not in db.table_names():
        db["pain_signals"].create({
            "id": int,
            "url_hash": str,       # SHA-256 do URL — chave única
            "url": str,
            "title": str,
            "source": str,         # 'reddit'|'quora'|'youtube'|'google_trends'
            "niche_slug": str,
            "score": int,          # upvotes (Reddit) ou view_count (YouTube) ou peak_index (Trends)
            "extra_json": str,     # campos adicionais por fonte (JSON)
            "collected_at": str,
        }, pk="id")
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_pain_signals_url_hash ON pain_signals(url_hash)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_pain_signals_niche_collected ON pain_signals(niche_slug, collected_at)")

    if "pain_reports" not in db.table_names():
        db["pain_reports"].create({
            "id": int,
            "niche_id": int,
            "cycle_at": str,       # ISO-8601 truncado ao minuto do ciclo
            "report_json": str,
            "created_at": str,
        }, pk="id", foreign_keys=[("niche_id", "niches", "id")])
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_pain_reports_niche_cycle ON pain_reports(niche_id, cycle_at)")

    if "youtube_quota_log" not in db.table_names():
        db["youtube_quota_log"].create({
            "id": int,
            "units": int,
            "operation": str,
            "logged_at": str,
        }, pk="id")
        db.execute("CREATE INDEX IF NOT EXISTS idx_youtube_quota_log_at ON youtube_quota_log(logged_at)")
```

### config.yaml: bloco radar por nicho
```yaml
# Campos novos por nicho (adicionados ao config.yaml existente)
niches:
  - name: "Emagrecimento"
    slug: "emagrecimento"
    keywords:
      - "emagrecer rapido"
      - "dieta low carb"
    radar:
      anchor_term: "academia"
      subreddits:
        - "Dieta"
        - "loseit"
      relevance_language: "pt"

settings:
  # ... campos existentes ...
  youtube_quota_daily_limit: 9000
  radar_synthesizer_offset_min: 30
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| pytrends (GeneralMills) | pytrends-modern ou trendspyg | Abril 2025 (arquivado) | Mesma API; substituição drop-in; sem breaking changes conhecidos |
| YouTube `search.list` retorna views | Requer `videos().list(part='statistics')` para view_count | Sempre foi assim | search.list retorna apenas snippet; estatísticas precisam de chamada separada (+1u por vídeo) |
| `commentThreads.list` = 100u | `commentThreads.list` = 1u | Confirmado 2025 | Decision do CONTEXT.md estava correta |

**Nota sobre YouTube view_count:** O CONTEXT.md menciona coletar `view_count` e `like_count`. A chamada `search.list` retorna apenas `snippet` — para estatísticas é necessário `videos().list(part='statistics', id=vid_id)` = 1u adicional por vídeo. Para 5 vídeos: +5u. Total por keyword: ~110u (não 105u). Ainda dentro do orçamento com 3 nichos × 3 keywords × 110u = ~990u por ciclo de 4h.

**Deprecated/outdated:**
- `pytrends==4.9.2` (GeneralMills): arquivado, não instalar
- `interest_over_time(is_partial=True)`: filtra linha parcial — usar por padrão para evitar índice 0 espúrio no último ponto da série

---

## Open Questions

1. **Quora: `fetch_spa()` será suficiente ou Quora usa anti-bot agressivo?**
   - What we know: Quora é JavaScript SPA; Playwright com stealth já está no projeto (playwright-stealth 2.0+)
   - What's unclear: Quora pode detectar automação mesmo com stealth e retornar CAPTCHA ou 403
   - Recommendation: Implementar com `fetch_spa()` e graceful degradation (`return []` em falha). Se bloqueio for consistente, adicionar `alert='quora_blocked'` e documentar como known limitation. Não bloquear o MVP em Quora.

2. **niches table: existe foreign key para pain_reports?**
   - What we know: `pain_reports` referencia `niche_id` via FK. A migration `_001_initial.py` precisa ter uma tabela `niches` ou usar o `slug` como texto.
   - What's unclear: Se a tabela `niches` existe no schema atual (migration _001) ou se nichos são apenas config.yaml.
   - Recommendation: Verificar `_001_initial.py` antes de implementar `_004`. Se não houver tabela `niches`, usar `niche_slug TEXT` em vez de `niche_id INT` em `pain_reports` para evitar FK sem tabela pai.

3. **PRAW async: asyncpraw como alternativa?**
   - What we know: `asyncpraw` é fork async do PRAW; mesma API com `await`.
   - What's unclear: Status de manutenção do asyncpraw em 2026.
   - Recommendation: CONTEXT.md decidiu PRAW padrão (síncrono). Wrappear em `run_in_executor` é padrão seguro. Se performance for problema depois, migrar para asyncpraw em v2.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (pytest.ini já existe em `mis/`) |
| Config file | `mis/pytest.ini` |
| Quick run command | `cd mis && python -m pytest tests/test_radar_*.py -x -q` |
| Full suite command | `cd mis && python -m pytest tests/ -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| RADAR-01 | `collect_trends_signal()` retorna peak_index normalizado | unit | `pytest tests/test_trends_collector.py -x` | ❌ Wave 0 |
| RADAR-01 | Trends ratelimited: retorna None + alert structlog | unit | `pytest tests/test_trends_collector.py::test_ratelimited -x` | ❌ Wave 0 |
| RADAR-02 | `collect_reddit_signals()` retorna lista de posts com campos corretos | unit | `pytest tests/test_reddit_collector.py -x` | ❌ Wave 0 |
| RADAR-02 | `collect_quora_signals()` retorna lista de perguntas ou [] em falha | unit | `pytest tests/test_quora_collector.py -x` | ❌ Wave 0 |
| RADAR-03 | `collect_youtube_signals()` retorna sinais + quota registrada no banco | unit | `pytest tests/test_youtube_collector.py -x` | ❌ Wave 0 |
| RADAR-03 | Quota guard: job desabilitado ao atingir 9.000u | unit | `pytest tests/test_youtube_collector.py::test_quota_guard -x` | ❌ Wave 0 |
| RADAR-05 | Upsert idempotente: re-inserir mesmo URL não gera duplicata | unit | `pytest tests/test_migration_004.py::test_upsert_idempotent -x` | ❌ Wave 0 |
| RADAR-05 | Relatório: re-executar ciclo substitui via upsert (não duplica) | unit | `pytest tests/test_synthesizer.py::test_report_idempotent -x` | ❌ Wave 0 |
| RADAR-06 | `synthesize_niche_pains()` gera relatório com top 5 dores | unit | `pytest tests/test_synthesizer.py -x` | ❌ Wave 0 |
| RADAR-06 | Synthesizer não chama LLM se count de sinais == 0 | unit | `pytest tests/test_synthesizer.py::test_no_signals_skip -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `cd mis && python -m pytest tests/test_radar_*.py tests/test_migration_004.py tests/test_synthesizer.py -x -q`
- **Per wave merge:** `cd mis && python -m pytest tests/ -q`
- **Phase gate:** Full suite green antes de `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `mis/tests/test_trends_collector.py` — cobre RADAR-01
- [ ] `mis/tests/test_reddit_collector.py` — cobre RADAR-02 (Reddit)
- [ ] `mis/tests/test_quora_collector.py` — cobre RADAR-02 (Quora)
- [ ] `mis/tests/test_youtube_collector.py` — cobre RADAR-03
- [ ] `mis/tests/test_migration_004.py` — cobre RADAR-05 (schema + upsert)
- [ ] `mis/tests/test_synthesizer.py` — cobre RADAR-06
- [ ] `mis/tests/test_radar_jobs.py` — cobre register_radar_jobs() no scheduler
- [ ] `mis/tests/fixtures/reddit_response.json` — fixture PRAW mock
- [ ] `mis/tests/fixtures/youtube_search_response.json` — fixture YouTube API mock
- [ ] Framework install: `pip install pytrends-modern praw google-api-python-client` — se não detectado

---

## Sources

### Primary (HIGH confidence)
- Código fonte `mis/` inspecionado diretamente — padrões de BaseScraper, scheduler, migrations, dossier_generator
- [YouTube Data API v3 Quota Calculator](https://developers.google.com/youtube/v3/determine_quota_cost) — `search.list`=100u, `commentThreads.list`=1u confirmados
- [PRAW GitHub](https://github.com/praw-dev/praw) — mantido ativamente, OAuth 60 req/min
- [pytrends GitHub Issues](https://github.com/GeneralMills/pytrends/issues) — status arquivado confirmado

### Secondary (MEDIUM confidence)
- [pytrends-modern GitHub](https://github.com/yiromo/pytrends-modern) — fork ativo pós-arquivamento; mesma API
- [pytrends-modern PyPI](https://libraries.io/pypi/pytrends-modern) — 0.2.5+ disponível
- [ScraperAPI: How to Scrape Quora](https://www.scraperapi.com/web-scraping/quora/) — confirma necessidade de Selenium/Playwright (SPA, não SSR)
- [Google Developers YouTube v3 Quickstart Python](https://developers.google.com/youtube/v3/quickstart/python) — `build('youtube', 'v3', developerKey=API_KEY)` pattern

### Tertiary (LOW confidence)
- Reddit API rate limits variações (100 QPM vs 60/min) — fontes comunitárias divergem; PRAW lida automaticamente

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — pytrends-modern/PRAW/google-api-python-client verificados; código existente inspecionado
- Architecture: HIGH — padrões de scheduler, migrations e collectors replicam diretamente phases 1–3
- Pitfalls: HIGH para Quora SPA e pytrends archivado (verificados via WebSearch); MEDIUM para PRAW blocking (comportamento observado)

**Research date:** 2026-03-15
**Valid until:** 2026-04-15 (pytrends-modern muda com frequência; verificar se API quebrou antes de implementar)
