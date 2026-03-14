# Roadmap: Market Intelligence System (MIS)

## Overview

O MIS é construído em dependência estrita: cada fase desbloqueia a próxima. A fundação de dados e scraping deve existir antes de qualquer scanner funcionar. Scanners devem produzir dados confiáveis antes de espionagem e dossiês poderem ser gerados. O pipeline de inteligência deve ser validado antes de o dashboard ser construído. A integração ao MEGABRAIN é a última camada — um wrapper sobre um sistema funcionando.

## Phases

- [x] **Phase 1: Foundation** - Infraestrutura de dados, scraping e agendamento que tudo depende ✓ 2026-03-14
- [ ] **Phase 2: Platform Scanners** - Varredura e ranking de produtos campeões em Hotmart, ClickBank e Kiwify
- [ ] **Phase 3: Product Espionage + Dossiers** - Espionagem profunda de produtos e geração de dossiês com IA
- [ ] **Phase 4: Pain Radar** - Radar horário de dores e desejos do mercado via fontes sociais e de tendências
- [ ] **Phase 5: Dashboard** - Interface web para visualizar rankings, dossiês e relatórios de dores
- [ ] **Phase 6: MEGABRAIN Integration** - MIS como módulo de primeira classe dentro do MEGABRAIN

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
**Plans**: TBD

Plans:
- [ ] 03-01: Scraper de copy e estrutura de oferta (sales page)
- [ ] 03-02: Coletor de anúncios Meta Ad Library e reviews
- [ ] 03-03: Data completeness gate e queue de processamento
- [ ] 03-04: Pipeline de análise IA (copy_analyzer, dossier_generator)
- [ ] 03-05: Score de oportunidade e confidence score

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
**Plans**: TBD

Plans:
- [ ] 04-01: Scraper Google Trends com normalização por anchor term
- [ ] 04-02: Coletores Reddit (PRAW) e Quora
- [ ] 04-03: Coletor YouTube com quota management
- [ ] 04-04: Idempotência, checkpoint store e job singleton
- [ ] 04-05: Pain synthesizer e gerador de relatório horário

### Phase 5: Dashboard
**Goal**: Usuário pode consumir visualmente toda a inteligência gerada — rankings, dossiês e radar de dores — em interface web sem tocar em código
**Depends on**: Phase 4
**Requirements**: DASH-01, DASH-02, DASH-03, DASH-04, SCAN-05
**Success Criteria** (what must be TRUE):
  1. Dashboard exibe ranking de produtos campeões filtrável por plataforma e nicho com dados atualizados do último ciclo
  2. Página individual de dossiê exibe todos os dados de espionagem e análise IA de forma legível para um produto selecionado
  3. Feed de dores do mercado mostra relatório horário mais recente por nicho com timestamp de última atualização
  4. Sistema envia alerta (notificação no dashboard) quando novo produto campeão entra no radar
**Plans**: TBD

Plans:
- [ ] 05-01: FastAPI server e estrutura de rotas
- [ ] 05-02: Página de ranking com filtros (Jinja2 + HTMX)
- [ ] 05-03: Página de dossiê individual
- [ ] 05-04: Feed de dores e sistema de alertas

### Phase 6: MEGABRAIN Integration
**Goal**: MIS é acessível como módulo dentro do MEGABRAIN via comando de agente, com ponto de integração único e limpo
**Depends on**: Phase 5
**Requirements**: INT-01, INT-02
**Success Criteria** (what must be TRUE):
  1. `mis/` existe como módulo independente com `mis_agent.py` como único arquivo que cruza a fronteira MIS/MEGABRAIN
  2. Usuário pode invocar `/mis-briefing` dentro do MEGABRAIN e receber resumo dos últimos produtos campeões e dores detectadas
  3. Dados do MIS (dossiês e relatórios) podem ser exportados em formato compatível com o pipeline de conhecimento do MEGABRAIN
**Plans**: TBD

Plans:
- [ ] 06-01: Estrutura de módulo `mis/` e bridge `mis_agent.py`
- [ ] 06-02: Comando `/mis-briefing` e exportação para MEGABRAIN pipeline

## Progress

**Execution Order:**
Phases execute in strict dependency order: 1 → 2 → 3 → 4 → 5 → 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 4/4 | Complete | 2026-03-14 |
| 2. Platform Scanners | 0/3 | Not started | - |
| 3. Product Espionage + Dossiers | 0/5 | Not started | - |
| 4. Pain Radar | 0/5 | Not started | - |
| 5. Dashboard | 0/4 | Not started | - |
| 6. MEGABRAIN Integration | 0/2 | Not started | - |
