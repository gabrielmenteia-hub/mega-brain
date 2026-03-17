# Market Intelligence System (MIS)

## What This Is

Sistema de inteligência de mercado integrado ao MEGABRAIN que varre automaticamente produtos e infoprodutos campeões em 15+ plataformas globais e BR (Hotmart, ClickBank, Kiwify, Eduzz, Monetizze, PerfectPay, Braip, Product Hunt, Udemy, JVZoo, Gumroad, AppSumo), executa espionagem completa de cada produto via LLM (copy, anúncios Meta, reviews), e gera relatórios horários das dores e desejos do mercado via 6 fontes. Ranking cross-platform unificado por percentile normalization exibido em dashboard FastAPI/HTMX e integrado ao MEGABRAIN via mis_agent.py.

**Shipped v2.0** — 2026-03-17 | 19 fases | 41 planos | 48/48 requisitos (v1.0+v2.0) | 15+ plataformas

## Core Value

Entregar ao usuário, sem esforço manual, o mapa completo do que está vendendo e por que está vendendo — para que ele possa modelar e lançar seus próprios produtos com máxima vantagem competitiva.

## Requirements

### Validated (v1.0)

- ✓ FOUND-01: Schema SQLite com tabelas products, platforms, niches, pains, dossiers — v1.0
- ✓ FOUND-02: BaseScraper com rate limiting, retry, rotação de proxies e headers anti-bot — v1.0
- ✓ FOUND-03: Configuração de 3–5 nichos alvo em config.yaml — v1.0
- ✓ FOUND-04: Health monitor detecta scrapers quebrados via canary checks — v1.0
- ✓ SCAN-01: Hotmart top products ranked by niche — v1.0
- ✓ SCAN-02: Kiwify top products ranked by niche — v1.0
- ✓ SCAN-03: ClickBank gravity score ranking — v1.0
- ✓ SCAN-04: Ranking atualizado em ciclo diário via APScheduler — v1.0
- ✓ SCAN-05: Filtro por plataforma e nicho no dashboard — v1.0
- ✓ SPY-01 a SPY-05: Pipeline completo de espionagem com data completeness gate — v1.0
- ✓ DOS-01 a DOS-05: Dossiê IA com fatores de sucesso, dores, template, opportunity score, confidence score — v1.0
- ✓ RADAR-01 a RADAR-06: 6 fontes de radar + síntese horária idempotente — v1.0
- ✓ DASH-01 a DASH-04: Dashboard ranking, dossiê, feed, alertas — v1.0
- ✓ INT-01 a INT-02: MEGABRAIN integration via mis_agent.py + skill — v1.0

### Validated (v2.0)

- ✓ INFRA-01: Migration _006 cria rows para todas as plataformas com INSERT OR IGNORE — v2.0
- ✓ INFRA-02: platform_ids.py centraliza todos os IDs como constantes nomeadas — v2.0
- ✓ INFRA-03: Campo rank_type adicionado à tabela platforms para semântica do rank — v2.0
- ✓ SCAN-BR-01: EduzzScanner varre marketplace por nicho e persiste ranking — v2.0
- ✓ SCAN-BR-02: MonetizzeScanner varre marketplace por nicho e persiste ranking — v2.0
- ✓ SCAN-BR-03: PerfectPayScanner fallback-only com alert='marketplace_unavailable' — v2.0
- ✓ SCAN-BR-04: BraipScanner com window.__NUXT__ IIFE parser (Nuxt 2 SSR) — v2.0
- ✓ SCAN-INTL-01: ProductHuntScanner GraphQL cursor pagination com credencial guard — v2.0
- ✓ SCAN-INTL-02: UdemyScanner REST Basic Auth com fallback api_discontinued — v2.0
- ✓ SCAN-INTL-03: JVZooScanner SSR com detecção Incapsula dupla — v2.0
- ✓ SCAN-INTL-04: GumroadScanner Playwright scroll loop por nicho — v2.0
- ✓ SCAN-INTL-05: AppSumoScanner SSR-first com PLAYWRIGHT_SEMAPHORE(3) — v2.0
- ✓ DASH-V2-01: /ranking/unified com percentile normalization cross-platform — v2.0
- ✓ DASH-V2-02: Filtro por nicho obrigatório + toggle multi-platform — v2.0
- ✓ DASH-V2-03: Badges de plataforma, unified score, rank bruto por plataforma — v2.0
- ✓ DEBT-01: nyquist_compliant: false corrigido em todos os 12 VALIDATION.md — v2.0
- ✓ DEBT-02: Docstring radar/__init__.py:141 corrigida "5 jobs" → "6 jobs" — v2.0

### Future (v3.0+)

- ADV-01: Exportação de dossiê em PDF
- ADV-02: Comparação lado a lado de 2+ produtos concorrentes
- ADV-03: Histórico de evolução de produto (tracking de mudanças na copy/oferta)
- ADV-04: Notificações via WhatsApp/Telegram além do dashboard
- SCAN-V3: Kajabi, Teachable, Skool, Stan Store (plataformas de alta fricção / paywall)

### Out of Scope

- Automação de criação do produto final — o sistema modela e inspira, a criação é do usuário
- Integração com plataformas de pagamento — fora do escopo
- Monitoramento de redes sociais fechadas — bloqueado por TOS
- SEO intelligence completo — território do SEMrush/Ahrefs
- Monitoramento sub-minuto — horário é suficiente
- Interface mobile nativa — web responsiva suficiente

## Context

**v2.0 estado atual (2026-03-17):**
- Stack: Python 3.14, FastAPI + Jinja2 + HTMX, APScheduler 3.x AsyncIOScheduler, SQLite + sqlite-utils, httpx + Playwright stealth, claude-sonnet-4-6
- 15+ plataformas: Hotmart, ClickBank, Kiwify, Eduzz, Monetizze, PerfectPay, Braip, Product Hunt, Udemy, JVZoo, Gumroad, AppSumo
- Fallback Scanner Pattern: plataformas inacessíveis retornam [] + alert='marketplace_unavailable' (documentado em scanner.py)
- PLAYWRIGHT_SEMAPHORE(3) global em base_scraper.py previne OOM em scans paralelos
- Dashboard: python -m mis dashboard → http://localhost:8000 | /ranking/unified cross-platform
- MEGABRAIN: skill /mis-briefing + python -m mis export

**Tech debt conhecido:**
- test_cli_spy_help falha pré-existente (PYTHONPATH em subprocess) — não é bug de produção
- Kajabi, Teachable, Skool, Stan Store ainda não implementados (paywall / alta fricção extrema)
- JVZoo pode ser bloqueado por Incapsula em produção — scanner retorna fallback graciosamente

## Constraints

- Hotmart/Kiwify sem API pública robusta — scraping ou APIs não-oficiais
- Rate limiting: Google, Reddit, YouTube respeitados
- Ciclo horário para radar — pipeline leve
- Python principal, integrado ao MEGABRAIN
- Scraping de páginas públicas apenas; dados pessoais nunca coletados
- META_ACCESS_TOKEN necessário para RADAR-04 (degrada graciosamente sem token)
- PRODUCT_HUNT_API_TOKEN necessário para ProductHuntScanner (degrada sem token)
- PLAYWRIGHT_SEMAPHORE(3) como limite hard para concorrência de browsers

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Dashboard web separado do MEGABRAIN CLI | UX para consumo rápido de dados visuais | ✓ Correto |
| Scraping vs APIs oficiais plataformas BR | APIs inexistentes | ✓ Correto |
| Ciclo horário para radar de dores | Frequência suficiente sem sobrecarregar APIs | ✓ Correto |
| SQLite como DB | Sem infra, portável, suficiente MVP single-user | ✓ Correto para v1.0/v2.0 |
| LLM como parser universal para sales pages | Sem selectors por plataforma — qualquer URL | ✓ Robusto |
| ClickBank via GraphQL API | Gravity score sem auth, mais estável que HTML | ✓ Correto |
| INSERT OR IGNORE + url_hash para idempotência | UNIQUE index suficiente | ✓ Radar idempotente |
| APScheduler AsyncIOScheduler | Compatível com FastAPI lifespan async | ✓ Necessário |
| mis_agent.py como único ponto de integração | Fronteira limpa MIS/MEGABRAIN | ✓ Correto |
| MIS_PATH aponta para parent de mis/ | from mis.mis_agent import... requer package sob o path | ⚠️ Documentação ambígua no SKILL.md |
| Fallback Scanner Pattern (marketplace_unavailable) | Plataformas instáveis não devem crashar o pipeline | ✓ Robusto — estabelecido em v2.0 |
| PLAYWRIGHT_SEMAPHORE(3) global | Previne OOM em scans de múltiplos nichos simultâneos | ✓ Necessário para AppSumo/Gumroad |
| Percentile normalization para unified ranking | Escalas incompatíveis entre plataformas (posição vs gravity vs upvotes) | ✓ Solução correta |
| TDD RED/GREEN para scanners internacionais (Phase 15) | APIs externas exigem contratos testáveis | ✓ Encontrou bug real em cursor pagination |

---
*Last updated: 2026-03-17 after v2.0 Platform Expansion milestone*
