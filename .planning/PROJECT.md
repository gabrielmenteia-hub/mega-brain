# Market Intelligence System (MIS)

## What This Is

Sistema de inteligência de mercado integrado ao MEGABRAIN que varre automaticamente produtos e infoprodutos campeões em Hotmart, ClickBank e Kiwify, executa espionagem completa de cada produto encontrado via LLM (copy, anúncios Meta, reviews), e gera relatórios horários das dores e desejos do mercado via 6 fontes (Google Trends, Reddit, Quora, YouTube, Meta Ads + síntese LLM). Resultados exibidos em dashboard FastAPI/HTMX e integrados ao MEGABRAIN via mis_agent.py.

**Shipped v1.0** — 2026-03-16 | 12 fases | 30 planos | 31/31 requisitos | 167 testes GREEN | 89 arquivos Python | 11.393 LOC

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

### Active (v2.0)

- [ ] SCAN-V2: Scanners para Eduzz, JVZoo, Udemy, Product Hunt, AppSumo, Gumroad, Kajabi, Teachable, Skool, Stan Store (15+ plataformas)
- [ ] ADV-01: Exportação de dossiê em PDF
- [ ] ADV-02: Comparação lado a lado de 2+ produtos concorrentes
- [ ] ADV-03: Histórico de evolução de produto (tracking de mudanças na copy/oferta)
- [ ] ADV-04: Notificações via WhatsApp/Telegram além do dashboard

### Out of Scope

- Automação de criação do produto final — o sistema modela e inspira, a criação é do usuário
- Integração com plataformas de pagamento — fora do escopo
- Monitoramento de redes sociais fechadas — bloqueado por TOS
- SEO intelligence completo — território do SEMrush/Ahrefs
- Monitoramento sub-minuto — horário é suficiente
- Interface mobile nativa — web responsiva suficiente

## Context

**v1.0 estado atual (2026-03-16):**
- Stack: Python 3.14, FastAPI + Jinja2 + HTMX, APScheduler 3.x AsyncIOScheduler, SQLite + sqlite-utils, httpx + Playwright stealth, claude-sonnet-4-6
- 89 arquivos Python, 11.393 LOC, 167 testes GREEN
- Plataformas: Hotmart (SSR httpx), ClickBank (GraphQL sem auth), Kiwify (HTML sintético)
- Radar: Google Trends, Reddit (PRAW), Quora, YouTube (quota guard), Meta Ads Library API
- Dashboard: python -m mis dashboard → http://localhost:8000
- MEGABRAIN: skill /mis-briefing auto-trigger + python -m mis export

**Tech debt v1.0:**
- test_cli_spy_help falha pré-existente (PYTHONPATH em subprocess) — não é bug de produção
- .claude/commands/mis-briefing.md ausente — /mis-briefing só via keyword auto-trigger
- nyquist_compliant: false em todos os 12 VALIDATION.md
- Docstring radar/__init__.py:141 desatualizada ("5 jobs" → 6)

## Constraints

- Hotmart/Kiwify sem API pública robusta — scraping ou APIs não-oficiais
- Rate limiting: Google, Reddit, YouTube respeitados
- Ciclo horário para radar — pipeline leve
- Python principal, integrado ao MEGABRAIN
- Scraping de páginas públicas apenas; dados pessoais nunca coletados
- META_ACCESS_TOKEN necessário para RADAR-04 (degrada graciosamente sem token)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Dashboard web separado do MEGABRAIN CLI | UX para consumo rápido de dados visuais | ✓ Correto |
| Scraping vs APIs oficiais plataformas BR | APIs inexistentes | ✓ Correto |
| Ciclo horário para radar de dores | Frequência suficiente sem sobrecarregar APIs | ✓ Correto |
| SQLite como DB | Sem infra, portável, suficiente MVP single-user | ✓ Correto para v1.0 |
| LLM como parser universal para sales pages | Sem selectors por plataforma — qualquer URL | ✓ Robusto |
| ClickBank via GraphQL API | Gravity score sem auth, mais estável que HTML | ✓ Correto |
| INSERT OR IGNORE + url_hash para idempotência | UNIQUE index suficiente | ✓ Radar idempotente |
| APScheduler AsyncIOScheduler | Compatível com FastAPI lifespan async | ✓ Necessário |
| mis_agent.py como único ponto de integração | Fronteira limpa MIS/MEGABRAIN | ✓ Correto |
| MIS_PATH aponta para parent de mis/ | from mis.mis_agent import... requer package sob o path | ⚠️ Documentação ambígua no SKILL.md |

---
*Last updated: 2026-03-16 after v1.0 milestone*
