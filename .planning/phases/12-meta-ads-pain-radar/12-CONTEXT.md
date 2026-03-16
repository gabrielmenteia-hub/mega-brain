# Phase 12: Meta Ads Pain Radar - Context

**Gathered:** 2026-03-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Adicionar um novo coletor de radar que busca criativos de anúncios patrocinados no Meta por nicho — fechando RADAR-04, último requisito pendente do v1. Zero código novo além do coletor: nenhuma migração de banco, nenhuma mudança no synthesizer, apenas fiação no register_radar_jobs() e um novo arquivo em mis/radar/.

</domain>

<decisions>
## Implementation Decisions

### O que são os "comentários" de anúncios

- **Sinal de dor = ad_creative_bodies**: texto do criativo do anúncio (copy que o anunciante escreveu). Anunciantes escrevem sobre dores reais do mercado para converter — é um sinal de dor tão valioso quanto posts do Reddit. Comentários reais de usuários em anúncios não são acessíveis via API oficial (sem API, anti-bot agressivo) — não implementar.
- **1 signal por anúncio**: `ad_creative_bodies` é uma lista de strings (variantes A/B). Concatenar com `\n\n` em um único string. Um `url_hash` por `ad_snapshot_url`.
- **Content = texto completo** do criativo concatenado. Sem truncamento. O synthesizer extrai dores do texto bruto (mesmo padrão de Reddit/YouTube).
- **Anúncios sem ad_creative_bodies** (campo ausente ou lista vazia): pular silenciosamente. Log `debug`. Sem signal salvo.
- **Idempotência**: `url_hash` baseado em `ad_snapshot_url`. INSERT OR IGNORE — anúncio recorrente em ciclos futuros é ignorado silenciosamente. Mesmo padrão Phase 4.

### Query por nicho

- **Search terms**: campo `keywords[]` do config.yaml por nicho — mesmo padrão de Trends, Reddit, Quora, YouTube. 1 chamada API por keyword.
- **Execução**: sequencial com `asyncio.sleep(1-2s)` entre keywords do mesmo nicho. Evita rate limit da API Meta. Padrão TrendsCollector.
- **Paginação**: apenas primeira página (limit=25). Os primeiros 25 anúncios por keyword são os mais relevantes pelo algoritmo da Meta. Sem cursor/paginação.

### Filtros de anúncios

- **Status**: `ad_active_status=ACTIVE` apenas. Dores atuais do mercado.
- **País**: campo `ad_countries` por nicho no config.yaml (lista, ex: `[BR]`). Default: `[BR]` quando ausente. Campo opcional — backward compatible com nichos existentes sem o campo.
- **Metadata salva**: `{"page_name": ..., "ad_delivery_start_time": ...}` no campo `metadata` de pain_signals.
- **Quantidade**: limit=25 por keyword.

### Estrutura do coletor

- **Arquivo**: `mis/radar/meta_ads_collector.py` — novo arquivo, responsabilidade única.
- **Interface pública**: função top-level `async def collect_ad_comments(niche: dict, db_path: str) -> list[dict]`. Sem classe. Mesmo padrão de `collect_niche_trends`, `collect_reddit_signals`, etc.
- **Retorno**: lista de dicts com os pain_signals inseridos (para testes e logging).
- **HTTP**: `httpx.AsyncClient` diretamente, sem BaseScraper. API REST oficial não precisa de stealth headers/proxies.
- **Graceful degradation sem token**: retornar `[]` + log `warning("meta_ads.skipped", reason="no_META_ACCESS_TOKEN")`. Exatamente o padrão do MetaAdsScraper de espionagem (Phase 3).

### Integração no register_radar_jobs()

- **Job**: `radar_meta_ads` com `CronTrigger(minute=0)` — junto com `radar_trends` e `radar_reddit_quora` no :00. Schedule hardcoded (sem campo configurável no config.yaml).
- **Total de jobs após Phase 12**: 6 (era 5 antes).
- **Cleanup**: `radar_cleanup` existente (30 dias, todos os pain_signals independente de source) já cobre `source='meta_ads'`. Nenhum novo job de cleanup.
- **Synthesizer**: zero mudanças. A query de pain_signals não tem filtro de `source` — `source='meta_ads'` aparece automaticamente na próxima janela de síntese.

### Testes TDD

- **Mocking**: fixture JSON em `tests/fixtures/meta_ads/ads_archive_radar_response.json` + `respx` para interceptar `httpx.AsyncClient.get`. Mesmo padrão do `test_meta_ads_spy.py` existente.
- **Cenários obrigatórios** (RED → GREEN):
  1. Happy path com token: 3 anúncios na fixture → assert 3 pain_signals inseridos com `source='meta_ads'`
  2. Graceful degradation sem token: `META_ACCESS_TOKEN` ausente → retorna `[]`, nenhum sinal inserido, sem exceção
  3. Idempotência via url_hash: rodar collect duas vezes com mesmo fixture → COUNT não muda na segunda execução
  4. Anúncio sem creative body: fixture com `ad_creative_bodies=[]` → sinal pulado, COUNT=0
- **Registro do job**: atualizar `test_lifespan.py` existente — `assert len(jobs) == 6` (era 5). Verificar que `radar_meta_ads` está na lista de job IDs.

### Claude's Discretion

- Schema exato do arquivo de fixture (quais campos além de page_name, ad_snapshot_url, ad_creative_bodies, ad_delivery_start_time)
- Delay exato entre keywords (1s ou 2s — dentro do range 1-2s decidido)
- Nome do logger structlog interno (`meta_ads_radar.fetched`, `meta_ads_radar.inserted`, etc.)
- Tratamento de HTTPStatusError da API Meta (propagar como ScraperError ou retornar [] após log)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets

- `mis/spies/meta_ads.py` (MetaAdsScraper): padrão de token check, `META_API_URL = "https://graph.facebook.com/v25.0/ads_archive"`, campos da API, graceful degradation. Copiar a lógica de fetch e adaptar para busca por keyword.
- `mis/radar/__init__.py` (register_radar_jobs + _run_all_* pattern): adicionar `_run_all_meta_ads(config, db_path)` e o 6º job no `_job_specs` list.
- `mis/radar/trends_collector.py`: padrão de delay sequencial entre keywords — replicar em meta_ads_collector.
- `tests/fixtures/meta_ads/ads_archive_response.json`: fixture existente para o spy. Criar variante `ads_archive_radar_response.json` com dados por keyword (não por produto).
- `mis/tests/test_meta_ads_spy.py`: padrão de teste com respx + monkeypatch para META_ACCESS_TOKEN — replicar nos novos testes.

### Established Patterns

- `INSERT OR IGNORE` via `url_hash` UNIQUE em `pain_signals` — idempotência (Phase 4).
- `source='meta_ads'` no campo `source` de pain_signals — já definido no schema, sem nova migração.
- Explicit remove-before-add no APScheduler (Phase 4): `scheduler.remove_job(job_id)` antes de `scheduler.add_job()`.
- `asyncio.to_thread` para funções síncronas (Phase 10/11) — não necessário aqui (coletor já é async).
- structlog com campos: `niche=`, `count=`, `alert=` — replicar.

### Integration Points

- `mis/radar/__init__.py` → adicionar import de `collect_ad_comments` e criar `_run_all_meta_ads()` + job no `_job_specs`.
- `mis/config.yaml` → adicionar campo opcional `ad_countries: [BR]` a cada nicho (ou não adicionar se usando default).
- `mis/tests/test_lifespan.py` → atualizar assert de `len(jobs) == 5` para `len(jobs) == 6`.
- Nenhuma migração nova necessária — `pain_signals` já tem coluna `source` (Phase 4).

</code_context>

<specifics>
## Specific Ideas

- O coletor replica exatamente o padrão dos outros coletores de radar: função top-level, retorna lista, INSERT OR IGNORE, structlog com count=. "Mais um coletor no pipeline" — não reinventa nada.
- A decisão de usar `ad_creative_bodies` como sinal de dor (em vez de tentar coletar comentários reais sem API) é a mesma razão pela qual RADAR-04 foi adiado em Phase 4 — agora implementando pela via oficial e viável.

</specifics>

<deferred>
## Deferred Ideas

- Comentários reais de usuários em anúncios — sem API oficial, requer Playwright anti-bot. Escopo separado futuro.
- Paginação além de 25 resultados por keyword — limit=25 é suficiente para MVP. v2 se necessário.
- Suporte a `ad_type` específico (ex: apenas VIDEO ou apenas IMAGE) — `ALL` é suficiente para sinal de dor.

</deferred>

---

*Phase: 12-meta-ads-pain-radar*
*Context gathered: 2026-03-16*
