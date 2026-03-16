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

## Cross-Milestone Trends

| Metric | v1.0 |
|--------|------|
| Phases | 12 |
| Plans | 30 |
| Tests | 167 GREEN |
| LOC | 11.393 |
| Timeline | 18 dias |
| Gap closure phases | 6/12 (50%) |
| Requirements met | 31/31 (100%) |
| Integration flows | 4/4 (100%) |
