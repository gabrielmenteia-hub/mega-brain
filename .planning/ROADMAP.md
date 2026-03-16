# Roadmap: Market Intelligence System (MIS)

## Overview

O MIS é construído em dependência estrita: cada fase desbloqueia a próxima. A fundação de dados e scraping deve existir antes de qualquer scanner funcionar. Scanners devem produzir dados confiáveis antes de espionagem e dossiês poderem ser gerados. O pipeline de inteligência deve ser validado antes de o dashboard ser construído. A integração ao MEGABRAIN é a última camada — um wrapper sobre um sistema funcionando.

## Phases

- [x] **Phase 1: Foundation** - Infraestrutura de dados, scraping e agendamento que tudo depende ✓ 2026-03-14
- [ ] **Phase 2: Platform Scanners** - Varredura e ranking de produtos campeões em Hotmart, ClickBank e Kiwify
- [ ] **Phase 2.5: Platform Expansion** - Scanners automáticos para 15+ plataformas internacionais e nichos (Gumroad, Kajabi, Teachable, JVZoo, Digistore24, Stan Store, Skool, etc.)
- [ ] **Phase 3: Product Espionage + Dossiers** - Espionagem profunda de produtos e geração de dossiês com IA
- [x] **Phase 4: Pain Radar** - Radar horário de dores e desejos do mercado via fontes sociais e de tendências (completed 2026-03-15)
- [ ] **Phase 5: Dashboard** - Interface web para visualizar rankings, dossiês e relatórios de dores
- [x] **Phase 6: MEGABRAIN Integration** - MIS como módulo de primeira classe dentro do MEGABRAIN (completed 2026-03-15)

## Phase Details

### Phase 1: Foundation
**Goal**: A infraestrutura que torna possível coletar, armazenar e processar dados de mercado de forma confiável existe e está operacional
**Depends on**: Nothing (first phase)
**Requirements**: FOUND-01, FOUND-02, FOUND-03, FOUND-04
**Success Criteria** (what must be TRUE):
  1. `mis.db` existe com todas as tabelas (products, platforms, niches, pains, dossiers) e migrations rodam sem erro
  2. `BaseScraper` coleta uma URL de teste com rate limiting ativo, retry automático em falha e rotação de headers — sem erros silenciosos
  3. Arquivo de configuração aceita 3-5 nichos alvo e esses nichos são referenciados consistentemente por todos os módulos
  4. Health monitor detecta quando um scraper retorna dados vazios em produto canário conhecido e emite alerta legível
**Plans**: 4 plans

Plans:
- [x] 01-01-PLAN.md — Schema SQLite (5 tabelas), migrations sqlite-utils, ScraperError, infraestrutura de testes (Wave 0 + Wave 1)
- [x] 01-02-PLAN.md — BaseScraper: fetch() httpx + retry tenacity, fetch_spa() Playwright + stealth, rate limiting por dominio
- [x] 01-03-PLAN.md — config.yaml + load_config() com validacao 3-5 nichos, APScheduler skeleton
- [x] 01-04-PLAN.md — Health monitor run_canary_check(), alertas structlog, canary job registrado no scheduler

### Phase 2: Platform Scanners
**Goal**: O sistema descobre e rankeia automaticamente produtos campeões nas principais plataformas, com dados frescos disponíveis diariamente
**Depends on**: Phase 1
**Requirements**: SCAN-01, SCAN-02, SCAN-03, SCAN-04
**Success Criteria** (what must be TRUE):
  1. Sistema varre Hotmart e retorna pelo menos 10 produtos ranqueados por nicho configurado, com dados persistidos em `products`
  2. Sistema varre ClickBank e retorna produtos com gravity score por nicho configurado, com dados persistidos
  3. Sistema varre Kiwify e retorna produtos ranqueados por nicho configurado, com dados persistidos
  4. Ranking é atualizado automaticamente uma vez ao dia via APScheduler sem intervenção manual
  5. Scraper de cada plataforma tem fallback selectors e alerta quando estrutura HTML muda (schema drift detection)
**Plans**: 3 plans

Plans:
- [ ] 02-01-PLAN.md — Kiwify scraper (httpx SSR) + base architecture (PlatformScanner, Product dataclass, ProductRepository, migration _002)
- [ ] 02-02-PLAN.md — ClickBank scraper (httpx marketplace SSR scraping, gravity score ou rank posicional)
- [ ] 02-03-PLAN.md — Hotmart scraper (Playwright XHR intercept, stealth) + APScheduler jobs + canary DB-based

### Phase 2.5: Platform Expansion
**Goal**: O sistema descobre e rankeia produtos campeões nas principais plataformas internacionais e de nicho, expandindo a cobertura além de Hotmart/ClickBank/Kiwify
**Depends on**: Phase 2
**Requirements**: SCAN-V2-01, SCAN-V2-02, SCAN-V2-03, SCAN-V2-04 (+ plataformas adicionais a definir em requirements)
**Success Criteria** (what must be TRUE):
  1. Scanners implementados para: Gumroad, Payhip, Podia, Sellfy, Lemon Squeezy, SendOwl, Etsy
  2. Scanners implementados para: Kajabi, Teachable, Skool, Mighty Networks, LearnWorlds, Stan Store
  3. Scanners implementados para: JVZoo, Digistore24
  4. Todos os novos scanners seguem o padrão PlatformScanner com upsert, fallback selectors e canary checks
  5. Ranking atualizado diariamente para todas as plataformas
**Plans**: TBD

Plans:
- [ ] 02.5-01: Scanners de plataformas de criadores (Gumroad, Payhip, Podia, Sellfy, Lemon Squeezy, SendOwl)
- [ ] 02.5-02: Scanners de plataformas de cursos BR/intl (Kajabi, Teachable, Skool, Mighty Networks, LearnWorlds, Stan Store)
- [ ] 02.5-03: Scanners de marketplaces de afiliados (JVZoo, Digistore24) + Etsy digital products

### Phase 3: Product Espionage + Dossiers
**Goal**: Para qualquer produto campeão identificado, o sistema extrai inteligência competitiva completa e gera um dossiê com análise de IA explicando por que o produto vende
**Depends on**: Phase 2
**Requirements**: SPY-01, SPY-02, SPY-03, SPY-04, SPY-05, DOS-01, DOS-02, DOS-03, DOS-04, DOS-05
**Success Criteria** (what must be TRUE):
  1. Sistema extrai copy completa da página de vendas de produto selecionado (headlines, argumentos, estrutura narrativa, CTA) e armazena estruturado
  2. Sistema coleta anúncios ativos do produto via Meta Ad Library e estrutura da oferta (preço, bônus, garantias) de forma persistida
  3. Sistema coleta reviews, classifica por valência (positivo/negativo) e não passa os dados para IA enquanto completude mínima não é atingida
  4. IA gera dossiê completo com: fatores de sucesso, dores endereçadas, template de modelagem e score de oportunidade por nicho
  5. Todo dossiê exibe confidence score indicando qualidade dos dados usados na análise
**Plans**: 5 plans

Plans:
- [ ] 03-01-PLAN.md — Migration _003 + SalesPageScraper platform-agnostic (copy + oferta em uma chamada LLM)
- [ ] 03-02-PLAN.md — MetaAdsScraper (API oficial) + ReviewsScraper (plataformas nativas + Google fallback)
- [ ] 03-03-PLAN.md — SpyData dataclass + data completeness gate + confidence score
- [ ] 03-04-PLAN.md — Pipeline LLM: copy_analyzer + dossier_generator com tracking de tokens
- [ ] 03-05-PLAN.md — spy_orchestrator end-to-end + CLI + hook APScheduler pós-scanner

### Phase 4: Pain Radar
**Goal**: O sistema monitora automaticamente, a cada hora, as fontes onde o mercado expõe suas dores e desejos, e consolida em relatório por nicho
**Depends on**: Phase 3
**Requirements**: RADAR-01, RADAR-02, RADAR-03, RADAR-04, RADAR-05, RADAR-06
**Success Criteria** (what must be TRUE):
  1. Google Trends é consultado a cada hora por nicho com normalização por anchor term — resultado armazenado como índice relativo (não volume absoluto)
  2. Sistema coleta posts e perguntas de Reddit e Quora relacionados aos nichos e persiste sem duplicatas
  3. Sistema analisa títulos e comentários de vídeos YouTube por nicho respeitando quota diária de 10.000 unidades
  4. Pipeline do radar é idempotente — re-execução após falha não gera registros duplicados
  5. Relatório horário consolidado com as principais dores/desejos por nicho é gerado e armazenado a cada ciclo
**Plans**: 5 plans

Plans:
- [ ] 04-01-PLAN.md — Migration _004 (pain_signals, pain_reports, youtube_quota_log) + config.yaml radar fields + Wave 0 test scaffolds
- [ ] 04-02-PLAN.md — TrendsCollector (pytrends-modern) + RedditCollector (PRAW executor) + QuoraCollector (fetch_spa)
- [ ] 04-03-PLAN.md — YouTubeCollector (google-api-python-client) + quota guard persistido em banco
- [ ] 04-04-PLAN.md — Synthesizer LLM (claude-sonnet-4-6) + pain_reports idempotente + prompt pt-BR
- [ ] 04-05-PLAN.md — register_radar_jobs() no scheduler + CLI 'radar --niche' + cleanup job 30 dias

### Phase 5: Dashboard
**Goal**: Usuário pode consumir visualmente toda a inteligência gerada — rankings, dossiês e radar de dores — em interface web sem tocar em código
**Depends on**: Phase 4
**Requirements**: DASH-01, DASH-02, DASH-03, DASH-04, SCAN-05
**Success Criteria** (what must be TRUE):
  1. Dashboard exibe ranking de produtos campeões filtrável por plataforma e nicho com dados atualizados do último ciclo
  2. Página individual de dossiê exibe todos os dados de espionagem e análise IA de forma legível para um produto selecionado
  3. Feed de dores do mercado mostra relatório horário mais recente por nicho com timestamp de última atualização
  4. Sistema envia alerta (notificação no dashboard) quando novo produto campeão entra no radar
**Plans**: 5 plans

Plans:
- [ ] 05-01-PLAN.md — Test scaffolds Wave 0: 9 arquivos em tests/web/ com contratos failing (21+ testes RED)
- [ ] 05-02-PLAN.md — Camada de dados: migration _005 (alerts) + 3 repositórios (alert, dossier, pain) + db.py atualizado
- [ ] 05-03-PLAN.md — Web layer: FastAPI app factory + Ranking page + subcomando dashboard CLI (DASH-01, SCAN-05)
- [ ] 05-04-PLAN.md — Dossiê individual com tabs HTMX + Feed de dores por nicho (DASH-02, DASH-03)
- [ ] 05-05-PLAN.md — Sistema de alertas: página + badge polling + trigger top-20 nos 3 scanners (DASH-04)

### Phase 6: MEGABRAIN Integration
**Goal**: MIS é acessível como módulo dentro do MEGABRAIN via comando de agente, com ponto de integração único e limpo
**Depends on**: Phase 5
**Requirements**: INT-01, INT-02
**Success Criteria** (what must be TRUE):
  1. `mis/` existe como módulo independente com `mis_agent.py` como único arquivo que cruza a fronteira MIS/MEGABRAIN
  2. Usuário pode invocar `/mis-briefing` dentro do MEGABRAIN e receber resumo dos últimos produtos campeões e dores detectadas
  3. Dados do MIS (dossiês e relatórios) podem ser exportados em formato compatível com o pipeline de conhecimento do MEGABRAIN
**Plans**: 2 plans

Plans:
- [ ] 06-01-PLAN.md — Bridge mis_agent.py com get_briefing_data() e export_to_megabrain() + testes (INT-01)
- [ ] 06-02-PLAN.md — CLI export subcommand + skill /mis-briefing JARVIS-style + CLAUDE.md MIS Integration (INT-02)

### Phase 7: MIS Integration Bug Fixes
**Goal**: Os 3 bugs críticos de integração identificados no audit v1.0 são corrigidos — export_to_megabrain exporta dossiês reais, health score calcula corretamente, e o pipeline automático scan→spy→dossiê funciona de ponta a ponta
**Depends on**: Phase 6
**Requirements**: INT-01, INT-02
**Gap Closure**: Closes gaps from v1.0 milestone audit
**Success Criteria** (what must be TRUE):
  1. `export_to_megabrain()` exporta dossiês com `status='done'` (não 'complete') e retorna contagem > 0 quando dossiês existem
  2. `get_briefing_data()` calcula health score corretamente — `last_cycle` e `dossiers_today` retornam valores reais (coluna `generated_at` usada ao invés de `created_at`)
  3. `_scan_and_spy_job()` salva produtos no banco via `save_batch_with_alerts()` antes de tentar espionar — pipeline automático scan→spy→dossiê executa end-to-end
**Plans**: 1 plan

Plans:
- [ ] 07-01-PLAN.md — Fix export status filter, fix created_at→generated_at, fix _scan_and_spy_job save + testes

### Phase 8: Foundation Verification
**Goal**: Phase 1 é retroativamente verificada — FOUND-02 (proxy rotation) e FOUND-04 (health monitor) são confirmados ou implementados, e VERIFICATION.md da Phase 1 é criado documentando o estado real
**Depends on**: Phase 7
**Requirements**: FOUND-01, FOUND-02, FOUND-03, FOUND-04
**Gap Closure**: Closes gaps from v1.0 milestone audit
**Success Criteria** (what must be TRUE):
  1. `BaseScraper` implementa proxy rotation (lista de proxies configurável) além de rate limiting e retry já existentes — ou confirma que proxy rotation está presente e documentada
  2. `run_canary_check()` em `health_monitor.py` cobre verificações de Phase 1 (schema integrity, scraper liveness) e não apenas plataformas (Phase 2)
  3. VERIFICATION.md da Phase 1 existe com status passed ou gaps_found refletindo estado real do código
**Plans**: 1 plan

Plans:
- [ ] 08-01-PLAN.md — Proxy rotation (proxy_list + _select_proxy) no BaseScraper, schema integrity canary no health_monitor, re-verificacao VERIFICATION.md Phase 1

### Phase 9: Production Wiring & Proxy Fix
**Goal**: Os 2 gaps críticos identificados no audit v1.0 são corrigidos — scheduler é iniciado automaticamente quando o servidor sobe, e proxy_list é corretamente propagado por toda a cadeia PlatformScanner → BaseScraper
**Depends on**: Phase 8
**Requirements**: SCAN-04, FOUND-02
**Gap Closure**: Closes gaps from v1.0 milestone audit (SCAN-04 unsatisfied, FOUND-02 partial, INT-GAP-01, INT-GAP-02)
**Success Criteria** (what must be TRUE):
  1. `python -m mis dashboard` inicia o servidor E registra todos os APScheduler jobs — scans diários e radar horário disparam automaticamente sem CLI manual
  2. Configurar `proxy_list` não-vazio em `config.yaml` não levanta `TypeError` — `PlatformScanner` e seus 3 subclasses aceitam e propagam `proxy_list` para `BaseScraper`
  3. Flow "Automated Scan → Persist → Dashboard" funciona end-to-end quando servidor sobe
  4. Testes RED → GREEN para ambos os paths (lifespan hook e proxy forwarding)

Plans:
- [ ] 09-01-PLAN.md — Lifespan hook FastAPI + proxy_list forwarding em PlatformScanner + testes

### Phase 10: Critical Runtime Fixes
**Goal**: Os 2 defects críticos identificados no audit de integração v1.0 são corrigidos — niche_id é corretamente resolvido via DB antes de cada scan, e os radar jobs são convertidos para async nativo compatível com AsyncIOScheduler
**Depends on**: Phase 9
**Requirements**: SCAN-01, SCAN-02, SCAN-03, DASH-01, RADAR-01, RADAR-02, RADAR-03, RADAR-05, RADAR-06
**Gap Closure**: Closes DEFECT-1 (niche_id=0) and DEFECT-3 (asyncio.run in AsyncIOScheduler) from v1.0 audit
**Success Criteria** (what must be TRUE):
  1. `run_all_scanners()` resolve `niche_id` via `SELECT id FROM niches WHERE slug=?` — produtos salvos com niche_id correto e visíveis no dashboard ranking
  2. Todos os 5 radar job wrappers convertidos de `sync + asyncio.run()` para `async def` — jobs disparam sem RuntimeError no AsyncIOScheduler
  3. Testes RED → GREEN cobrindo ambos os fixes; suite completa continua green

Plans:
- [x] 10-01-PLAN.md — Fix niche_id resolution in run_all_scanners() (DEFECT-1) + Fix radar async wrappers (DEFECT-3) + tests

### Phase 11: Health Monitor Wiring & Tech Debt
**Goal**: Os gaps de observabilidade identificados no audit v1.0 são fechados — run_schema_integrity_check() e run_platform_canary() entram no caminho de execução de produção, bugs latentes são corrigidos e código morto é removido
**Depends on**: Phase 10
**Requirements**: FOUND-02, FOUND-04
**Gap Closure**: Closes partial gaps from v1.0 milestone audit
**Success Criteria** (what must be TRUE):
  1. `run_schema_integrity_check(db_path)` é chamado automaticamente no startup do servidor (lifespan) — alerta quando tabelas estão faltando
  2. `run_platform_canary()` é registrado no APScheduler — dados obsoletos de plataforma são detectados automaticamente
  3. `fetch_spa()` usa `_select_proxy()` para selecionar proxy da lista — proxy_list funciona tanto para httpx quanto para Playwright
  4. `_compute_health()` em mis_agent.py não usa `asyncio.run()` — seguro para chamada em contexto async
  5. `register_scanner_jobs()` e funções `run_*_scan` são removidos ou documentados como código morto; `datetime.utcnow()` substituído por `datetime.now(timezone.utc)` nos 3 arquivos afetados
  6. Suite completa de testes continua green

Plans:
- [ ] 11-01-PLAN.md — Wire schema integrity + platform canary into production; fix fetch_spa proxy; fix asyncio.run in _compute_health; clean dead code + datetime deprecation

### Phase 12: Meta Ads Pain Radar (RADAR-04)
**Goal**: O sistema coleta comentários de anúncios patrocinados no Meta por nicho — fechando o único requisito v1 que foi explicitamente excluído do escopo das fases anteriores
**Depends on**: Phase 11
**Requirements**: RADAR-04
**Gap Closure**: Closes RADAR-04 from v1.0 milestone audit
**Success Criteria** (what must be TRUE):
  1. `MetaAdsRadarCollector.collect_ad_comments(niche_slug)` retorna lista de comentários de anúncios patrocinados filtrados por nicho — persiste em `pain_signals` com `source='meta_ads'`
  2. Coletor funciona com `META_ACCESS_TOKEN` configurado e degrada graciosamente sem token (retorna `[]` sem propagar exceção)
  3. Comentários coletados são incluídos na janela de síntese do `synthesizer.py` — aparecem no `pain_reports` horário
  4. Job `radar_meta_ads` registrado no APScheduler via `register_radar_jobs()` — coleta automática a cada hora
  5. Testes RED → GREEN cobrindo happy path, graceful degradation sem token, e idempotência via `url_hash` UNIQUE

Plans:
- [ ] 12-01-PLAN.md — MetaAdsRadarCollector + APScheduler job + synthesizer integration + tests

## Progress

**Execution Order:**
Phases execute in strict dependency order: 1 → 2 → 2.5 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 4/4 | Complete | 2026-03-14 |
| 2. Platform Scanners | 3/3 | Complete | 2026-03-14 |
| 2.5. Platform Expansion | 0/3 | Not started | - |
| 3. Product Espionage + Dossiers | 5/5 | Complete | 2026-03-14 |
| 4. Pain Radar | 5/5 | Complete | 2026-03-15 |
| 5. Dashboard | 5/5 | Complete | 2026-03-15 |
| 6. MEGABRAIN Integration | 2/2 | Complete | 2026-03-15 |
| 7. MIS Integration Bug Fixes | 1/1 | Complete | 2026-03-15 |
| 8. Foundation Verification | 1/1 | Complete | 2026-03-16 |
| 9. Production Wiring & Proxy Fix | 1/1 | Complete | 2026-03-16 |
| 10. Critical Runtime Fixes | 1/1 | Complete | 2026-03-16 |
| 11. Health Monitor Wiring & Tech Debt | 1/1 | Complete   | 2026-03-16 |
| 12. Meta Ads Pain Radar (RADAR-04) | 0/1 | Not started | - |
