# Requirements: Market Intelligence System (MIS)

**Defined:** 2026-03-16
**Milestone:** v2.0 Platform Expansion
**Core Value:** Entregar ao usuário, sem esforço manual, o mapa completo do que está vendendo e por que está vendendo — para que ele possa modelar e lançar seus próprios produtos com máxima vantagem competitiva.

## v2.0 Requirements

### INFRA — Pré-condições (bloqueantes)

- [ ] **INFRA-01**: Migration `_006_v2_platforms.py` cria rows para todas as 12 plataformas com `INSERT OR IGNORE` (elimina FK constraint violation em produção)
- [ ] **INFRA-02**: `mis/platform_ids.py` centraliza todos os IDs de plataforma como constantes nomeadas (elimina risco de collision entre scanners)
- [ ] **INFRA-03**: Campo `rank_type` adicionado à tabela `products` para identificar a semântica do rank por plataforma (posição, gravity, EPC, upvotes, enrollment, etc.)

### SCAN-BR — Scanners Brasil

- [ ] **SCAN-BR-01**: `EduzzScanner` varre marketplace Eduzz por nicho e persiste top produtos por posição
- [ ] **SCAN-BR-02**: `MonetizzeScanner` varre marketplace Monetizze por nicho e persiste top produtos
- [ ] **SCAN-BR-03**: `PerfectPayScanner` varre marketplace PerfectPay por nicho (após verificação de URL live)
- [ ] **SCAN-BR-04**: `BraipScanner` varre marketplace Braip por nicho (após verificação de URL live)

### SCAN-INTL — Scanners Internacionais

- [ ] **SCAN-INTL-01**: `ProductHuntScanner` busca trending products via GraphQL API usando `PH_ACCESS_TOKEN`
- [ ] **SCAN-INTL-02**: `UdemyScanner` busca top cursos por nicho via REST `/api-2.0/courses/`
- [ ] **SCAN-INTL-03**: `JVZooScanner` varre marketplace JVZoo por nicho (com contorno Incapsula ou fallback SSR)
- [ ] **SCAN-INTL-04**: `GumroadScanner` varre `gumroad.com/discover` por nicho ordenado por popular
- [ ] **SCAN-INTL-05**: `AppSumoScanner` varre `appsumo.com/products` por nicho (SSR-first, Playwright fallback)

### DASH-V2 — Dashboard Cross-Platform

- [ ] **DASH-V2-01**: View `/ranking/unified` exibe top produtos por nicho consolidados de todas as plataformas usando normalização por percentil
- [ ] **DASH-V2-02**: View unificada filtra por nicho (obrigatório) e suporta toggle "multi-platform only" (produtos em 2+ plataformas)
- [ ] **DASH-V2-03**: View unificada exibe badges de plataforma, unified score e rank bruto por plataforma

### DEBT — Tech Debt v1.0

- [ ] **DEBT-01**: `nyquist_compliant: false` corrigido ou removido em todos os 12 `VALIDATION.md`
- [ ] **DEBT-02**: Docstring `radar/__init__.py:141` atualizada de "5 jobs" → "6 jobs"

## Out of Scope (v2.0)

| Feature | Razão |
|---------|-------|
| Kajabi scanner | Sem marketplace público — white-label hosting, cada criador no próprio subdomínio |
| Teachable scanner | Sem marketplace público — mesmo padrão do Kajabi |
| Stan Store scanner | Link-in-bio tool sem ranking centralizado |
| Skool scanner | SPA sem dados de vendas — contagem de membros não é proxy confiável |
| ADV-01: PDF export | Deferido para v3.0 |
| ADV-02: Comparação lado a lado | Deferido para v3.0 |
| ADV-03: Histórico de evolução | Deferido para v3.0 |
| ADV-04: Notificações WhatsApp/Telegram | Deferido para v3.0 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| INFRA-01 | Phase 13 | Pending |
| INFRA-02 | Phase 13 | Pending |
| INFRA-03 | Phase 13 | Pending |
| DEBT-01 | Phase 13 | Pending |
| DEBT-02 | Phase 13 | Pending |
| SCAN-BR-01 | Phase 14 | Pending |
| SCAN-BR-02 | Phase 14 | Pending |
| SCAN-BR-03 | Phase 14 | Pending |
| SCAN-BR-04 | Phase 14 | Pending |
| SCAN-INTL-01 | Phase 15 | Pending |
| SCAN-INTL-02 | Phase 15 | Pending |
| SCAN-INTL-03 | Phase 16 | Pending |
| SCAN-INTL-04 | Phase 16 | Pending |
| SCAN-INTL-05 | Phase 16 | Pending |
| DASH-V2-01 | Phase 17 | Pending |
| DASH-V2-02 | Phase 17 | Pending |
| DASH-V2-03 | Phase 17 | Pending |

**Coverage:**
- v2.0 requirements: 17 total
- Mapped to phases: 17
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-16*
*Last updated: 2026-03-16 — traceability updated after ROADMAP.md v2.0 creation*
