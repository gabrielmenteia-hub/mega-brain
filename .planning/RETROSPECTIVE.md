# Retrospective

## Milestone: v1.0 — MIS MVP

**Shipped:** 2026-03-16
**Phases:** 12 | **Plans:** 30 | **Timeline:** 2026-02-27 → 2026-03-16 (18 dias)

### What Was Built

- **Foundation**: Schema SQLite 5 tabelas, BaseScraper com proxy rotation + retry + stealth Playwright, APScheduler, health monitor com canary checks
- **Platform Scanners**: Hotmart (httpx SSR), ClickBank (GraphQL API sem auth, gravity score), Kiwify (HTML sintético)
- **Product Espionage + Dossiers**: SalesPageScraper LLM-as-parser, MetaAdsScraper, ReviewsScraper, completeness gate, pipeline copy_analyzer → dossier_generator (claude-sonnet-4-6), confidence + opportunity scores
- **Pain Radar**: 6 fontes (Trends, Reddit, Quora, YouTube, Meta Ads) + synthesizer LLM horário, idempotente via url_hash UNIQUE
- **Dashboard FastAPI/HTMX**: Ranking filtrável, dossiê individual com tabs, feed de dores, alertas badge polling
- **MEGABRAIN Integration**: mis_agent.py bridge, skill /mis-briefing, CLI export → knowledge/mis/
- **Bug fixes + production wiring** (fases 7–12): 6 fases de audit/fix para fechar gaps de integração identificados após fases principais

### What Worked

- **TDD estrito**: RED → GREEN por task — resultou em 167 testes robustos sem mock hell (testes usam SQLite real via tmp_path)
- **Wave-based execution**: Planos paralelos dentro de ondas reduziram tempo de execução das fases maiores
- **gsd-verifier pós-fase**: Cada fase terminou com VERIFICATION.md validado, tornando o audit final trivial (12/12 passed)
- **Decisões explícitas em STATE.md**: Context entre sessões preservado — retomada de trabalho sem regredir
- **LLM como parser universal**: SalesPageScraper funciona em qualquer URL sem selectors específicos por plataforma — robusto contra mudanças de estrutura
- **INSERT OR IGNORE + url_hash**: Idempotência simples e eficaz para o radar — sem upsert complexo

### What Was Inefficient

- **Fases de bugfix (7–12) representaram 6/12 fases totais**: Muitos gaps de integração foram descobertos só após as fases principais — poderiam ter sido detectados mais cedo com integration checks por fase
- **Nyquist compliance nunca formalizado**: todos os 12 VALIDATION.md ficaram com nyquist_compliant: false — o processo TDD foi seguido na prática mas a documentação não foi assinada
- **SUMMARY.md requirements-completed incompleto**: 7 requirements (SCAN-04, SCAN-05, DASH-02–04, INT-01, INT-02) sem SUMMARY frontmatter explícito — documentação foi rastreada via VERIFICATION.md mas não uniformemente
- **Roadmap vs realidade**: ROADMAP.md ficou dessincronizado por várias fases (fases marcadas como [ ] quando já estavam completas) — exigiu reconciliação manual ao final

### Patterns Established

- **Fases de gap closure decimal (X.Y)** provaram ser eficientes para bugs urgentes sem renumerar fases
- **mis_agent.py como único ponto de integração**: Padrão limpo — replicar para outros módulos que integram ao MEGABRAIN
- **graceful degradation sem token**: return [] + log.warning (não raise) — padrão para collectors com dependências externas opcionais
- **run_migrations() chaining**: Chamar migration sequencial em uma chamada, callers recebem schema completo
- **replace_existing=True no APScheduler**: Safe para chamar register_*_jobs() no startup sem duplicate job errors

### Key Lessons

1. **Fazer integration check por fase, não só no final**: Fases 7–12 existiram porque integrações foram verificadas apenas no audit do milestone. Próximo milestone: integration check ao final de cada fase crítica.
2. **ROADMAP.md merece atenção contínua**: Manter atualizado ao longo da execução evita trabalho de reconciliação no fechamento do milestone.
3. **AsyncIOScheduler requer async def wrappers**: DEFECT-3 (asyncio.run dentro de AsyncIOScheduler) é um padrão a evitar ativamente — adicionar como regra de linting ou checklist de fase.
4. **Kiwify sem URL pública**: Fixture HTML sintético é a única opção viável — documentar nas constraints do scanner.
5. **nyquist_compliant sign-off**: Adicionar como gate explícito ao final de cada fase, não apenas criar VALIDATION.md e deixar como false.

### Cost Observations

- Model mix: ~100% sonnet (executor + verifier + integration checker)
- Sessions: ~15 sessões ao longo de 18 dias
- Notable: Fases de bugfix (7–12) custaram ~50% do total de tokens apesar de representarem pequenas mudanças de código — o overhead de contexto de 12 fases completas é significativo

---

## Milestone: v2.0 — Platform Expansion

**Shipped:** 2026-03-17
**Phases:** 7 (13–19) | **Plans:** 11 | **Timeline:** 2026-02-27 → 2026-03-17 (18 dias)

### What Was Built

- **Infrastructure + Tech Debt (Phase 13)**: Migration _006/_007 para platforms + is_stale, platform_ids.py com constantes nomeadas, rank_type schema, nyquist sign-off v1.0
- **BR Scanners (Phase 14)**: EduzzScanner/MonetizzeScanner (SSR httpx), PerfectPayScanner/BraipScanner (fallback-only + window.__NUXT__ parser) — Fallback Scanner Pattern estabelecido
- **International API-Based (Phase 15)**: ProductHuntScanner (GraphQL cursor pagination, 2 páginas), UdemyScanner (Basic Auth REST, fallback api_discontinued) — TDD RED/GREEN cycle completo
- **International High-Friction (Phase 16)**: JVZooScanner (Incapsula detection dupla), GumroadScanner (Playwright scroll loop), AppSumoScanner (SSR-first + Playwright fallback) — PLAYWRIGHT_SEMAPHORE(3) global
- **Unified Cross-Platform Ranking (Phase 17)**: list_unified_ranking() com percentile normalization, /ranking/unified FastAPI route, HTMX templates com niche filter + multi-platform toggle + tab navigation
- **Nyquist Sign-off + Quality Cleanup (Phases 18–19)**: VALIDATION.md retroativos assinados, null slug guard, platform badges estilizados, REQUIREMENTS.md INFRA-03 corrigido

### What Worked

- **Lição do v1.0 aplicada — nyquist sign-off explícito**: Phase 18 dedicada a assinar VALIDATION.md retroativos — dívida técnica de documentação identificada e fechada antes do milestone complete
- **Fallback Scanner Pattern**: Decidir que plataformas instáveis retornam [] + alert='marketplace_unavailable' em vez de exception — zero crashes no pipeline por plataformas indisponíveis
- **TDD RED/GREEN para scanners internacionais**: Ciclo TDD completo na Phase 15 encontrou um bug real em cursor pagination do ProductHunt antes da integração — padrão comprovado
- **PLAYWRIGHT_SEMAPHORE(3)**: Solução limpa para OOM em scans paralelos — uma linha em base_scraper.py protege todos os scanners Playwright futuros automaticamente
- **Percentile normalization**: Escalas incompatíveis (posição vs gravity vs upvotes) resolvidas corretamente — unified score comparável entre plataformas
- **gsd-verifier pós-fase**: 7/7 fases terminaram com VERIFICATION.md — audit final foi trivial

### What Was Inefficient

- **Phase 16 subestimada**: Incapsula + Playwright OOM + SPA rendering eram 3 problemas independentes na mesma fase — poderia ter sido 3 fases menores com mais paralelismo
- **ROADMAP.md ainda ficou dessincronizado**: Phases 18 e 19 não tinham `roadmap_complete: true` no analyze — pequeno mas recorrente
- **Phases 18 e 19 foram necessárias por tech debt acumulado**: Se nyquist sign-off e code quality fossem gates em cada fase principal, não precisariam de fases dedicadas no fechamento

### Patterns Established

- **Fallback Scanner Pattern**: Plataformas inacessíveis → return [] + alert='marketplace_unavailable'. Documentado em scanner.py module docstring. Replicar para qualquer scanner novo de plataforma instável.
- **PLAYWRIGHT_SEMAPHORE global**: `asyncio.Semaphore(3)` em base_scraper.py como proteção global contra OOM — não no scanner individual
- **TDD RED cycle obrigatório para APIs externas**: Escrever fixtures + stubs antes de qualquer implementação — contratos testáveis antes do GREEN
- **Percentile normalization como padrão de unified ranking**: `score_percentile = rank / max_rank` por plataforma antes de qualquer comparação cross-platform

### Key Lessons

1. **Tech debt de documentação acumula**: Fases 18 e 19 existiram porque nyquist sign-off e quality cleanup foram deixados para o final. Próximo milestone: gate explícito de nyquist_compliant e quality checklist ao fechar cada fase.
2. **Fases de alta fricção merecem pesquisa antecipada**: JVZoo/Gumroad/AppSumo tinham características de bot detection / SPA desconhecidas antes da execução — vale um spike de 30 min antes de planejar.
3. **Scanner de fallback é feature, não gambiarra**: Documentar o padrão explicitamente (como foi feito em scanner.py) é mais valioso do que tentar fazer o scanner funcionar em plataformas estruturalmente inacessíveis.
4. **PLAYWRIGHT_SEMAPHORE pertence à infraestrutura, não ao scanner**: Decisões de limite de concorrência devem ser globais — colocar no BaseScraper garantiu proteção automática para AppSumo e Gumroad sem configuração adicional.

### Cost Observations

- Model mix: ~100% sonnet (executor + verifier)
- Sessions: ~5 sessões ao longo do milestone v2.0
- Notable: Fases menores (7 fases, 11 planos) vs v1.0 (12 fases, 30 planos) — mas escopo técnico similar. Lições do v1.0 reduziram o overhead de bugfix (apenas 2 fases de cleanup vs 6 no v1.0).

---

## Cross-Milestone Trends

| Metric | v1.0 | v2.0 |
|--------|------|------|
| Phases | 12 | 7 |
| Plans | 30 | 11 |
| Tests | 167 GREEN | +12 GREEN (Phase 15 TDD) |
| LOC | 11.393 | +~3.000 est. |
| Timeline | 18 dias | 18 dias |
| Gap closure phases | 6/12 (50%) | 2/7 (29%) |
| Requirements met | 31/31 (100%) | 17/17 (100%) |
| Integration flows | 4/4 (100%) | 4/4 (100%) |
| Platforms | 3 | 15+ |
