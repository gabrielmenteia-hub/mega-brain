# Phase 12: Meta Ads Pain Radar - Research

**Researched:** 2026-03-16
**Domain:** Meta Ad Library API — coletor de radar, APScheduler, TDD com respx
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- Sinal de dor = `ad_creative_bodies`: texto do criativo do anúncio. Comentários reais de usuários não são acessíveis via API oficial — não implementar.
- 1 signal por anúncio: `ad_creative_bodies` concatenados com `\n\n`. Um `url_hash` por `ad_snapshot_url`.
- Content = texto completo do criativo. Sem truncamento.
- Anúncios sem `ad_creative_bodies` (campo ausente ou lista vazia): pular silenciosamente com log `debug`. Sem signal salvo.
- Idempotência: `url_hash` baseado em `ad_snapshot_url`. INSERT OR IGNORE — mesmo padrão Phase 4.
- Search terms: campo `keywords[]` do config.yaml por nicho. 1 chamada API por keyword.
- Execução: sequencial com `asyncio.sleep(1-2s)` entre keywords do mesmo nicho.
- Paginação: apenas primeira página (limit=25). Sem cursor/paginação.
- Status: `ad_active_status=ACTIVE` apenas.
- País: campo `ad_countries` por nicho no config.yaml (lista, ex: `[BR]`). Default: `[BR]` quando ausente. Backward compatible.
- Metadata salva: `{"page_name": ..., "ad_delivery_start_time": ...}` no campo `extra_json` de pain_signals.
- Quantidade: limit=25 por keyword.
- Arquivo: `mis/radar/meta_ads_collector.py` — novo arquivo, responsabilidade única.
- Interface pública: `async def collect_ad_comments(niche: dict, db_path: str) -> list[dict]`. Sem classe.
- HTTP: `httpx.AsyncClient` diretamente, sem BaseScraper.
- Graceful degradation sem token: retornar `[]` + log `warning("meta_ads.skipped", reason="no_META_ACCESS_TOKEN")`.
- Job `radar_meta_ads` com `CronTrigger(minute=0)`.
- Total de jobs após Phase 12: 6 (era 5).
- `radar_cleanup` existente já cobre `source='meta_ads'`. Nenhum novo job de cleanup.
- Synthesizer: zero mudanças. Query de pain_signals não tem filtro de `source`.
- Mocking: fixture JSON em `tests/fixtures/meta_ads/ads_archive_radar_response.json` + `respx`.
- Cenários TDD: happy path 3 anúncios → 3 signals; sem token → []; idempotência; anúncio sem creative body → COUNT=0.
- Atualizar `test_lifespan.py`: `assert len(jobs) == 6` (era 5). Verificar `radar_meta_ads` nos job IDs.

### Claude's Discretion

- Schema exato do arquivo de fixture (quais campos além de page_name, ad_snapshot_url, ad_creative_bodies, ad_delivery_start_time)
- Delay exato entre keywords (1s ou 2s — dentro do range 1-2s decidido)
- Nome do logger structlog interno (`meta_ads_radar.fetched`, `meta_ads_radar.inserted`, etc.)
- Tratamento de HTTPStatusError da API Meta (propagar como ScraperError ou retornar [] após log)

### Deferred Ideas (OUT OF SCOPE)

- Comentários reais de usuários em anúncios — sem API oficial, requer Playwright anti-bot. Escopo separado futuro.
- Paginação além de 25 resultados por keyword — limit=25 é suficiente para MVP.
- Suporte a `ad_type` específico (ex: apenas VIDEO ou apenas IMAGE) — `ALL` é suficiente.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| RADAR-04 | Sistema coleta comentários de anúncios patrocinados no Meta por nicho | Meta Ad Library API (`ads_archive` endpoint) com `search_terms=keyword`, `ad_active_status=ACTIVE`, `fields=ad_creative_bodies` — texto do criativo como proxy de "comentário"/sinal de dor |
</phase_requirements>

---

## Summary

Esta fase implementa o único requisito v1 ainda pendente: RADAR-04. O trabalho é puramente aditivo — um novo arquivo `mis/radar/meta_ads_collector.py`, uma linha de import no `mis/radar/__init__.py`, e um novo job no `_job_specs`. Zero migrações, zero mudanças no synthesizer.

O coletor segue exatamente o padrão estabelecido pelos outros coletores de radar: função top-level async, iteração sequencial sobre keywords do config.yaml, `INSERT OR IGNORE` via `url_hash` UNIQUE em `pain_signals`, graceful degradation sem token. O código-modelo (`mis/spies/meta_ads.py`) já usa o mesmo endpoint Meta Ad Library API e já resolve o token check + request params — apenas adaptar para busca por keyword em vez de produto.

A API Meta Ad Library exige `ad_reached_countries` obrigatório (sem ele retorna 400) — o `mis/spies/meta_ads.py` já demonstra o padrão correto. O campo `source='meta_ads'` já está previsto no schema `pain_signals` (migration _004 define `source` como string livre), sem necessidade de nova migração.

**Primary recommendation:** Copiar a estrutura de `trends_collector.py` (loop por keywords, sleep entre chamadas, INSERT OR IGNORE) e a lógica de request de `mis/spies/meta_ads.py` (token check, params, httpx.AsyncClient). A fase é de baixo risco — padrões todos estabelecidos, zero territory novo.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| httpx | instalado | HTTP async para Meta API | Já usado em meta_ads.py spy; REST oficial não precisa stealth |
| sqlite-utils | instalado | INSERT OR IGNORE em pain_signals | Padrão de todos os coletores de radar |
| structlog | instalado | Logging estruturado | Padrão do projeto inteiro |
| apscheduler | instalado | Job scheduling horário | Singleton `get_scheduler()` compartilhado |
| respx | instalado (test) | Mock de httpx.AsyncClient | Padrão de test_meta_ads_spy.py |
| pytest-asyncio | instalado (test) | Testes async | Padrão de todos os testes de radar |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| asyncio | stdlib | sleep entre keywords, event loop | Delay 1-2s entre keywords para evitar rate limit |
| hashlib | stdlib | SHA-256 para url_hash | Mesmo padrão de trends_collector.py e reddit_collector.py |
| json | stdlib | Serializar extra_json (metadata) | Campo `extra_json` em pain_signals é JSON string |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| httpx.AsyncClient direto | BaseScraper | BaseScraper tem stealth/proxy para scraping; API REST oficial não precisa |
| Função top-level | Classe MetaAdsRadarCollector | Classe adiciona boilerplate sem benefício; padrão do projeto é função top-level |

**Installation:** Nenhuma nova dependência — todas já instaladas.

## Architecture Patterns

### Recommended Project Structure
```
mis/radar/
├── __init__.py                  # register_radar_jobs() — adicionar _run_all_meta_ads + job
├── trends_collector.py          # Modelo a seguir para padrão de loop/sleep/INSERT
├── reddit_collector.py          # Modelo a seguir para padrão de persist
├── quora_collector.py
├── youtube_collector.py
├── synthesizer.py
└── meta_ads_collector.py        # NOVO — Phase 12

mis/tests/
├── test_meta_ads_spy.py         # Modelo de teste com respx + monkeypatch
├── test_radar_jobs.py           # Modelo de teste de job registration
├── test_lifespan.py             # ATUALIZAR — len(jobs) == 6
└── fixtures/meta_ads/
    ├── ads_archive_response.json           # Existente (spy)
    └── ads_archive_radar_response.json     # NOVO — Phase 12 (busca por keyword)
```

### Pattern 1: Coletor de Radar (Padrão Estabelecido)

**What:** Função async top-level que itera sobre keywords do niche, faz 1 chamada API por keyword, persiste via INSERT OR IGNORE, retorna lista de dicts inseridos.

**When to use:** Sempre que um novo coletor de radar for adicionado.

**Example:**
```python
# Baseado em mis/radar/trends_collector.py (padrão estabelecido)
import asyncio
import hashlib
import json
import os
import random
from datetime import datetime, timezone

import httpx
import sqlite_utils
import structlog

log = structlog.get_logger()
META_API_URL = "https://graph.facebook.com/v25.0/ads_archive"


def _url_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()


async def collect_ad_comments(niche: dict, db_path: str) -> list[dict]:
    token = os.getenv("META_ACCESS_TOKEN", "").strip()
    if not token:
        log.warning("meta_ads.skipped", reason="no_META_ACCESS_TOKEN")
        return []

    niche_slug = niche["slug"]
    ad_countries = niche.get("ad_countries", ["BR"])
    db = sqlite_utils.Database(db_path)
    collected = []

    for keyword in niche.get("keywords", []):
        params = {
            "access_token": token,
            "search_terms": keyword,
            "ad_reached_countries": ",".join(ad_countries),
            "ad_active_status": "ACTIVE",
            "ad_type": "ALL",
            "fields": "page_name,ad_snapshot_url,ad_creative_bodies,ad_delivery_start_time",
            "limit": 25,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(META_API_URL, params=params)
                resp.raise_for_status()
                ads = resp.json().get("data", [])
        except httpx.HTTPStatusError as e:
            log.error("meta_ads_radar.fetch_error", keyword=keyword, error=str(e))
            await asyncio.sleep(random.uniform(1, 2))
            continue

        for ad in ads:
            bodies = ad.get("ad_creative_bodies") or []
            if not bodies:
                log.debug("meta_ads_radar.skipped_no_body", keyword=keyword)
                continue

            content = "\n\n".join(bodies)
            url = ad["ad_snapshot_url"]
            signal = {
                "url_hash": _url_hash(url),
                "url": url,
                "title": content[:200],  # título curto para display
                "source": "meta_ads",
                "niche_slug": niche_slug,
                "score": 0,
                "extra_json": json.dumps({
                    "page_name": ad.get("page_name"),
                    "ad_delivery_start_time": ad.get("ad_delivery_start_time"),
                }),
                "collected_at": datetime.now(timezone.utc).isoformat(),
            }

            try:
                db["pain_signals"].insert(signal, ignore=True)
                collected.append(signal)
            except Exception as exc:
                log.warning("meta_ads_radar.persist_failed", error=str(exc))

        log.info("meta_ads_radar.fetched", keyword=keyword, niche=niche_slug, count=len(ads))
        await asyncio.sleep(random.uniform(1, 2))

    log.info("meta_ads_radar.done", niche=niche_slug, count=len(collected))
    return collected
```

### Pattern 2: Registro de Job no APScheduler

**What:** Adicionar função helper `_run_all_meta_ads` e entrada no `_job_specs` list no `mis/radar/__init__.py`.

**When to use:** Todo novo coletor de radar precisa de um job correspondente.

**Example:**
```python
# Em mis/radar/__init__.py — adicionar após _run_all_youtube

from .meta_ads_collector import collect_ad_comments  # novo import

async def _run_all_meta_ads(config: dict, db_path: str) -> None:
    """Run Meta Ads collection for all niches. Errors per niche are logged, not raised."""
    niches = config.get("niches", [])
    for niche in niches:
        try:
            signals = await collect_ad_comments(niche, db_path)
            log.info("radar.meta_ads.done", niche=niche.get("slug"), count=len(signals))
        except Exception as e:
            log.error("radar.meta_ads.error", niche=niche.get("slug"), error=str(e))
```

```python
# Em register_radar_jobs() — adicionar ao _job_specs

async def _meta_ads_job():
    await _run_all_meta_ads(config, db_path)

_job_specs = [
    ("radar_trends", _trends_job, CronTrigger(minute=0)),
    ("radar_reddit_quora", _reddit_quora_job, CronTrigger(minute=0)),
    ("radar_youtube", _youtube_job, CronTrigger(hour="*/4", minute=0)),
    ("radar_synthesizer", _synthesizer_job, CronTrigger(minute=30)),
    ("radar_cleanup", _cleanup_job, CronTrigger(hour=3, minute=0)),
    ("radar_meta_ads", _meta_ads_job, CronTrigger(minute=0)),  # NOVO
]

# Atualizar também o log final:
log.info("scheduler.radar_jobs_registered", job_count=6)  # era 5
```

### Pattern 3: Fixture JSON para Testes

**What:** Arquivo JSON simulando resposta da Meta Ad Library API com busca por keyword (não por produto).

**When to use:** Interceptar `httpx.AsyncClient.get` com `respx`.

**Example:**
```json
{
  "data": [
    {
      "page_name": "Método Emagrecer Agora",
      "ad_snapshot_url": "https://www.facebook.com/ads/archive/render_ad/?id=radar001",
      "ad_creative_bodies": [
        "Você sofre com o excesso de peso há anos? Descubra o método que eliminou 12kg em 30 dias...",
        "Versão B: Chega de frustração com dietas que não funcionam. Acesse o método."
      ],
      "ad_delivery_start_time": "2026-02-10"
    },
    {
      "page_name": "Curso Low Carb Definitivo",
      "ad_snapshot_url": "https://www.facebook.com/ads/archive/render_ad/?id=radar002",
      "ad_creative_bodies": [
        "A dieta low carb que sua médica não quer que você conheça. Resultados em 7 dias."
      ],
      "ad_delivery_start_time": "2026-01-20"
    },
    {
      "page_name": "Shake Detox Premium",
      "ad_snapshot_url": "https://www.facebook.com/ads/archive/render_ad/?id=radar003",
      "ad_creative_bodies": [
        "Detox poderoso. Perca até 5kg na primeira semana."
      ],
      "ad_delivery_start_time": "2026-03-01"
    }
  ],
  "paging": {
    "cursors": {
      "before": "radar_before_cursor",
      "after": "radar_after_cursor"
    }
  }
}
```

### Pattern 4: Testes com respx + monkeypatch (Padrão test_meta_ads_spy.py)

**What:** Interceptar chamadas HTTP do `httpx.AsyncClient` via `respx.mock` context manager. Monkeypatch de `META_ACCESS_TOKEN`.

**Example:**
```python
# Baseado em mis/tests/test_meta_ads_spy.py

import json
import sqlite3
from pathlib import Path
import httpx
import pytest
import respx

from mis.radar.meta_ads_collector import collect_ad_comments, META_API_URL

_FIXTURE = Path(__file__).parent / "fixtures" / "meta_ads" / "ads_archive_radar_response.json"


@pytest.fixture
def radar_fixture() -> dict:
    return json.loads(_FIXTURE.read_text(encoding="utf-8"))


@pytest.mark.asyncio
async def test_happy_path_inserts_3_signals(monkeypatch, tmp_path, radar_fixture):
    """3 anúncios na fixture com ad_creative_bodies → 3 pain_signals inseridos."""
    monkeypatch.setenv("META_ACCESS_TOKEN", "fake_token")
    db_path = str(tmp_path / "mis.db")
    # Criar tabela pain_signals
    from mis.db import run_migrations
    run_migrations(db_path)

    niche = {"slug": "emagrecimento", "keywords": ["emagrecer rapido"]}

    with respx.mock:
        respx.get(META_API_URL).mock(
            return_value=httpx.Response(200, json=radar_fixture)
        )
        signals = await collect_ad_comments(niche, db_path)

    assert len(signals) == 3
    conn = sqlite3.connect(db_path)
    count = conn.execute(
        "SELECT COUNT(*) FROM pain_signals WHERE source='meta_ads'"
    ).fetchone()[0]
    conn.close()
    assert count == 3


@pytest.mark.asyncio
async def test_no_token_returns_empty(monkeypatch, tmp_path):
    """Sem META_ACCESS_TOKEN → retorna [], nenhuma exceção."""
    monkeypatch.delenv("META_ACCESS_TOKEN", raising=False)
    db_path = str(tmp_path / "mis.db")
    from mis.db import run_migrations
    run_migrations(db_path)

    niche = {"slug": "emagrecimento", "keywords": ["emagrecer"]}
    signals = await collect_ad_comments(niche, db_path)
    assert signals == []


@pytest.mark.asyncio
async def test_idempotency_url_hash(monkeypatch, tmp_path, radar_fixture):
    """Segunda execução com mesma fixture não aumenta o COUNT em pain_signals."""
    monkeypatch.setenv("META_ACCESS_TOKEN", "fake_token")
    db_path = str(tmp_path / "mis.db")
    from mis.db import run_migrations
    run_migrations(db_path)

    niche = {"slug": "emagrecimento", "keywords": ["emagrecer"]}

    with respx.mock:
        respx.get(META_API_URL).mock(
            return_value=httpx.Response(200, json=radar_fixture)
        )
        await collect_ad_comments(niche, db_path)

    with respx.mock:
        respx.get(META_API_URL).mock(
            return_value=httpx.Response(200, json=radar_fixture)
        )
        await collect_ad_comments(niche, db_path)

    conn = sqlite3.connect(db_path)
    count = conn.execute(
        "SELECT COUNT(*) FROM pain_signals WHERE source='meta_ads'"
    ).fetchone()[0]
    conn.close()
    assert count == 3  # não duplicou


@pytest.mark.asyncio
async def test_ad_without_creative_body_skipped(monkeypatch, tmp_path):
    """Anúncio com ad_creative_bodies=[] não gera signal."""
    monkeypatch.setenv("META_ACCESS_TOKEN", "fake_token")
    db_path = str(tmp_path / "mis.db")
    from mis.db import run_migrations
    run_migrations(db_path)

    fixture_no_body = {
        "data": [{
            "page_name": "Page X",
            "ad_snapshot_url": "https://www.facebook.com/ads/archive/render_ad/?id=empty001",
            "ad_creative_bodies": [],
            "ad_delivery_start_time": "2026-01-01"
        }]
    }
    niche = {"slug": "emagrecimento", "keywords": ["emagrecer"]}

    with respx.mock:
        respx.get(META_API_URL).mock(
            return_value=httpx.Response(200, json=fixture_no_body)
        )
        signals = await collect_ad_comments(niche, db_path)

    assert signals == []
    conn = sqlite3.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM pain_signals").fetchone()[0]
    conn.close()
    assert count == 0
```

### Anti-Patterns to Avoid

- **Classe desnecessária:** Todos os coletores de radar são funções top-level. Não criar classe `MetaAdsRadarCollector`.
- **Importar `collect_ad_comments` no top-level errado:** O import deve ser adicionado no `from .meta_ads_collector import collect_ad_comments` junto com os outros imports no topo de `__init__.py`.
- **ad_reached_countries como string "BR" direta:** O campo `ad_countries` no config.yaml é uma lista `[BR]`. Converter com `",".join(ad_countries)` — mas a API aceita uma string separada por vírgula ou pode ser passada múltiplas vezes. O spy existente usa `"BR"` hardcoded. Para radar com default, `",".join(["BR"])` produz `"BR"` — compatível.
- **Propagar exceção HTTPStatusError:** Padrão dos outros coletores de radar é log + `continue` por keyword — não propagar. O spy propaga (`ScraperError`) porque é uma operação diferente (produto específico que pode falhar toda a coleta).
- **Sleep real nos testes:** Usar `monkeypatch` ou `respx` que completa imediatamente — o sleep é no código de produção, não nos testes. Se o sleep travar os testes, usar `monkeypatch` em `asyncio.sleep`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Idempotência de pain_signals | Verificar `url_hash` antes de inserir | `sqlite_utils insert(..., ignore=True)` | UNIQUE index em `url_hash` + INSERT OR IGNORE já implementado em Phase 4 |
| HTTP retry/timeout | Loop de retry manual | `httpx.AsyncClient(timeout=30.0)` + padrão de continue por erro | API Meta é estável; retry elaborado é overkill para MVP |
| Rate limiting Meta API | Token bucket personalizado | `asyncio.sleep(random.uniform(1, 2))` entre keywords | Simples e eficaz — padrão já aprovado do TrendsCollector |
| Deduplicação por conteúdo | Hash do texto do criativo | `url_hash` baseado em `ad_snapshot_url` | `ad_snapshot_url` é stable ID único por anúncio — mesma decisão de Phase 3 (MetaAdsScraper) |

**Key insight:** Todos os problemas desta fase foram resolvidos em fases anteriores. O coletor é uma composição de padrões existentes.

## Common Pitfalls

### Pitfall 1: ad_reached_countries — campo obrigatório
**What goes wrong:** API Meta retorna HTTP 400 se `ad_reached_countries` não for passado.
**Why it happens:** Requisito de compliance da API Meta Ad Library — obrigatório por design.
**How to avoid:** Sempre incluir no params. Default `[BR]` garante que nunca fica vazio.
**Warning signs:** HTTP 400 com mensagem sobre `ad_reached_countries`.

### Pitfall 2: `ad_creative_bodies` pode ser null/ausente (não apenas lista vazia)
**What goes wrong:** `ad.get("ad_creative_bodies")` pode retornar `None`, não apenas `[]`. `len(None)` lança TypeError.
**Why it happens:** API Meta não garante todos os campos em todos os anúncios.
**How to avoid:** `bodies = ad.get("ad_creative_bodies") or []` — o `or []` cobre tanto `None` quanto ausência.
**Warning signs:** TypeError em produção ao iterar bodies.

### Pitfall 3: URL do ad_snapshot_url como url_hash — não o conteúdo
**What goes wrong:** Usar hash do `content` (texto do criativo) como `url_hash` causaria duplicatas quando A/B variations mudam.
**Why it happens:** O campo UNIQUE em `pain_signals` é `url_hash` — se basear no conteúdo, variações do mesmo anúncio geram conflitos de hash diferentes.
**How to avoid:** `url_hash = hashlib.sha256(ad_snapshot_url.encode()).hexdigest()` — o `ad_snapshot_url` é o identificador estável do anúncio.
**Warning signs:** Signals duplicados ou INSERT OR IGNORE ignorando anúncios novos com creative body diferente.

### Pitfall 4: asyncio.sleep nos testes (suite lenta)
**What goes wrong:** Suite de testes fica 20-30s mais lenta se o sleep real executar para cada keyword.
**Why it happens:** `asyncio.sleep(random.uniform(1, 2))` em produção é real.
**How to avoid:** Usar `monkeypatch` em `asyncio.sleep` nos testes do coletor. Padrão já estabelecido em `test_radar_async_jobs.py`.
**Warning signs:** Testes de meta_ads_collector demorando > 5s cada.

### Pitfall 5: test_lifespan.py — assert len(jobs) que testa o scheduler mockado
**What goes wrong:** `test_lifespan_scheduler_has_jobs` pode não verificar o número de jobs (usa mocks que ignoram add_job). O teste relevante é `test_radar_jobs.py` que usa scheduler real.
**Why it happens:** `test_lifespan.py` mocka `register_radar_jobs` inteiro — não registra jobs reais.
**How to avoid:** O assert `len(jobs) == 6` deve ser adicionado em `test_radar_jobs.py` (onde usa `isolated_scheduler` real) e também verificar `radar_meta_ads` no job_ids set.

## Code Examples

Verified patterns from official sources (código do projeto):

### Schema de pain_signals (migration _004)
```python
# Source: mis/migrations/_004_pain_radar.py
# Campos relevantes para meta_ads:
{
    "id": int,            # PK autoincrement
    "url_hash": str,      # UNIQUE — SHA-256 de ad_snapshot_url
    "url": str,           # ad_snapshot_url
    "title": str,         # primeiros N chars do content (para display)
    "source": str,        # 'meta_ads'
    "niche_slug": str,    # niche["slug"]
    "score": int,         # 0 (sem score para anúncios)
    "extra_json": str,    # JSON: {"page_name": ..., "ad_delivery_start_time": ...}
    "collected_at": str,  # ISO-8601 UTC
}
# NOTA: não há coluna "content" separada — o texto completo vai em "title"
# (que é TEXT sem limite em SQLite). A decisão de usar "title" como container
# do texto completo é consistente com os outros coletores (ex: YouTube usa title
# para o título do vídeo, Reddit usa title para o título do post).
```

**ATENÇÃO — campo "content":** O schema de `pain_signals` não tem uma coluna `content` separada. Apenas `title`. O synthesizer lê `title` para extrair dores. O texto completo do criativo vai em `title`. Confirmar com `mis/radar/synthesizer.py` se necessário.

### INSERT OR IGNORE com sqlite-utils
```python
# Source: mis/radar/trends_collector.py e reddit_collector.py
db = sqlite_utils.Database(db_path)
db["pain_signals"].insert(signal_dict, ignore=True)
# ignore=True → INSERT OR IGNORE — se url_hash já existir, silenciosamente ignora
```

### Token check pattern (graceful degradation)
```python
# Source: mis/spies/meta_ads.py
token = os.getenv("META_ACCESS_TOKEN", "").strip()
if not token:
    log.warning("meta_ads.skipped", reason="no_META_ACCESS_TOKEN")
    return []
```

### Remove-before-add para APScheduler
```python
# Source: mis/radar/__init__.py (Phase 4 — DEFECT fix)
existing = scheduler.get_job(job_id)
if existing is not None:
    scheduler.remove_job(job_id)
scheduler.add_job(func, trigger, id=job_id, replace_existing=True)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| RADAR-04 adiado (comentários reais sem API) | `ad_creative_bodies` via API oficial | Phase 12 | Implementável sem Playwright anti-bot |
| Meta API v21 (Phase 3 inicial) | `v25.0` em `META_API_URL` | Phase 3 | `META_API_URL = "https://graph.facebook.com/v25.0/ads_archive"` |
| replace_existing no APScheduler | remove-before-add | Phase 4 | `replace_existing` só funciona com scheduler running em APScheduler 3.x |

## Open Questions

1. **Campo "title" vs "content" em pain_signals**
   - What we know: Schema tem "title" (str), sem coluna "content" separada.
   - What's unclear: Synthesizer lê qual campo para extrair dores? Se lê "title", textos longos de criativos (> 500 chars) podem ser truncados para display mas precisam estar completos para o LLM.
   - Recommendation: Verificar `mis/radar/synthesizer.py` para confirmar qual campo é lido. Se o synthesizer usa "title", colocar o texto completo em "title" sem truncamento. Se há outro campo, adaptar.

2. **Tratamento de HTTPStatusError (discretion area)**
   - What we know: O spy (`meta_ads.py`) propaga como `ScraperError`. Os coletores de radar (trends, reddit) fazem `log + continue`.
   - What's unclear: Qual padrão adotar para o coletor de radar.
   - Recommendation: `log.error + continue` (padrão radar) — erro em 1 keyword não deve abortar todo o niche.

3. **ad_reached_countries como string vs lista na API**
   - What we know: API aceita string "BR" (verificado em `mis/spies/meta_ads.py`). Config novo usa lista `[BR]`.
   - What's unclear: API aceita "BR,US" (string com vírgula) para múltiplos países?
   - Recommendation: Para v1 com default `[BR]`, `",".join(["BR"])` = `"BR"` — funciona. Multi-país é v2.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest + pytest-asyncio |
| Config file | `mis/pytest.ini` ou `pyproject.toml` (verificar) |
| Quick run command | `cd mis && pytest tests/test_meta_ads_radar.py -x -q` |
| Full suite command | `cd mis && pytest -x -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| RADAR-04 | `collect_ad_comments` retorna 3 signals com token | unit | `pytest tests/test_meta_ads_radar.py::test_happy_path_inserts_3_signals -x` | ❌ Wave 0 |
| RADAR-04 | Graceful degradation sem token | unit | `pytest tests/test_meta_ads_radar.py::test_no_token_returns_empty -x` | ❌ Wave 0 |
| RADAR-04 | Idempotência via url_hash | unit | `pytest tests/test_meta_ads_radar.py::test_idempotency_url_hash -x` | ❌ Wave 0 |
| RADAR-04 | Anúncio sem creative body pulado | unit | `pytest tests/test_meta_ads_radar.py::test_ad_without_creative_body_skipped -x` | ❌ Wave 0 |
| RADAR-04 | Job `radar_meta_ads` registrado no APScheduler | unit | `pytest tests/test_radar_jobs.py -x -k "meta_ads"` | ❌ Wave 0 (add to existing) |
| RADAR-04 | Total de 6 jobs após registro | unit | `pytest tests/test_radar_jobs.py -x -k "six_jobs"` | ❌ Wave 0 (add to existing) |
| RADAR-04 | `test_lifespan.py` assert len(jobs)==6 | unit | `pytest tests/test_lifespan.py -x` | ✅ (update assert) |

### Sampling Rate
- **Per task commit:** `cd mis && pytest tests/test_meta_ads_radar.py -x -q`
- **Per wave merge:** `cd mis && pytest -x -q`
- **Phase gate:** Full suite green antes de `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `mis/tests/test_meta_ads_radar.py` — cobre RADAR-04 (4 cenários TDD)
- [ ] `mis/tests/fixtures/meta_ads/ads_archive_radar_response.json` — fixture com 3 anúncios
- [ ] `mis/radar/meta_ads_collector.py` — módulo (importação falha com RED antes da implementação)
- [ ] Adicionar asserts de `radar_meta_ads` e `len(jobs)==6` em `mis/tests/test_radar_jobs.py`

*(test_lifespan.py existe mas precisa atualizar `len(jobs) == 5` para `== 6`)*

## Sources

### Primary (HIGH confidence)
- `mis/spies/meta_ads.py` — endpoint URL `v25.0/ads_archive`, params obrigatórios, token check pattern, campo `ad_creative_bodies`
- `mis/radar/__init__.py` — estrutura exata de `_job_specs`, remove-before-add pattern, `_run_all_*` helpers
- `mis/radar/trends_collector.py` — padrão de loop por keywords, sleep entre chamadas, INSERT OR IGNORE
- `mis/migrations/_004_pain_radar.py` — schema completo de `pain_signals` (colunas, constraints, índices)
- `mis/tests/test_meta_ads_spy.py` — padrão de teste com `respx` + `monkeypatch`
- `mis/tests/test_radar_jobs.py` — padrão de teste de job registration com `isolated_scheduler`
- `mis/tests/fixtures/meta_ads/ads_archive_response.json` — estrutura da fixture existente (modelo)

### Secondary (MEDIUM confidence)
- `.planning/phases/12-meta-ads-pain-radar/12-CONTEXT.md` — decisões de implementação discutidas e aprovadas pelo usuário

### Tertiary (LOW confidence)
- Nenhum.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — todas as bibliotecas já instaladas e em uso
- Architecture: HIGH — padrão completamente estabelecido por phases anteriores (cópia adaptada)
- Pitfalls: HIGH — derivados diretamente do código existente e das decisões documentadas no STATE.md
- Test patterns: HIGH — model existente em test_meta_ads_spy.py é idêntico ao necessário

**Research date:** 2026-03-16
**Valid until:** 2026-04-16 (API Meta Ad Library estável; padrões internos do projeto são fixos)
