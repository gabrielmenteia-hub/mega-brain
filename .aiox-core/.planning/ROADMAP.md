# Roadmap: NEXUS

## Overview

NEXUS transforma o pipeline linear de criativos (scripts -> audio -> video) em um sistema autonomo com gate de qualidade. A jornada vai de modelos de dados tipados ate um CLI completo que orquestra pipeline.py, revisa com 4 agentes, regenera reprovados, e entrega pasta organizada com relatorios. Quatro fases, cada uma entregando uma capacidade verificavel.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3, 4): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Foundation** - Modelos Pydantic, configuracao via .env, e rubricas de revisao
- [ ] **Phase 2: Review Engine** - 4 agentes revisores em paralelo com output tipado e gate de custo
- [ ] **Phase 3: Regeneration Loop** - Ciclo de rejeicao-regeneracao com circuit breaker e feedback routing
- [ ] **Phase 4: Output & Integration** - Pasta organizada, relatorios, batch summary e CLI wrapper sobre pipeline.py

## Phase Details

### Phase 1: Foundation
**Goal**: O pipeline possui estrutura de dados tipada, configuracao externalizavel, e rubricas objetivas que calibram os agentes revisores
**Depends on**: Nothing (first phase)
**Requirements**: FND-01, FND-02, FND-03
**Success Criteria** (what must be TRUE):
  1. Modelos Pydantic (ReviewScore, CreativeBundle, NexusConfig) importaveis e validam dados invalidos com erros claros
  2. Toda configuracao (MAX_RETRIES, thresholds, model IDs) e carregada de .env -- alterar .env muda comportamento sem tocar codigo
  3. Cada dimensao de revisao (copy, tecnica, compliance, performance) possui rubrica com criterios objetivos e exemplos few-shot testados
**Plans:** 2 plans

Plans:
- [ ] 01-01-PLAN.md — Modelos Pydantic (AgentScore, CreativeBundle) + NexusConfig via .env + TDD suite
- [ ] 01-02-PLAN.md — 4 rubricas de revisao com criterios objetivos e few-shot calibration

### Phase 2: Review Engine
**Goal**: Um criativo submetido recebe veredictos tipados de 4 agentes especializados rodando em paralelo, com gate de custo que evita gerar audio/video desnecessario
**Depends on**: Phase 1
**Requirements**: REV-01, REV-02, REV-03, REV-04
**Success Criteria** (what must be TRUE):
  1. 4 agentes revisores (copy quality, Meta compliance, technical quality, performance score) rodam em paralelo e retornam em menos de 30s
  2. Cada agente retorna veredicto tipado via instructor: aprovado/reprovado + score numerico + feedback especifico e acionavel
  3. Script reprovado no copy gate NAO gera audio nem video -- gate de custo funciona
  4. Agente de qualidade tecnica analisa .mp4 via Claude vision e retorna score com feedback visual
**Plans**: TBD

Plans:
- [ ] 02-01: Agentes revisores com instructor + execucao paralela
- [ ] 02-02: Cost gate (script review antes de audio/video) e review multimodal do .mp4

### Phase 3: Regeneration Loop
**Goal**: Criativos reprovados sao regenerados automaticamente com feedback dos agentes, com limite de tentativas e quarentena para falhas persistentes
**Depends on**: Phase 2
**Requirements**: LOOP-01, LOOP-02, LOOP-03
**Success Criteria** (what must be TRUE):
  1. Script reprovado e reescrito usando feedback especifico dos agentes reprovadores injetado no prompt de regeneracao
  2. Apos MAX_RETRIES tentativas sem aprovacao, criativo vai para quarantine/ com relatorio completo de todas as tentativas
  3. Reprova no script regenera apenas o script -- audio e video so sao gerados apos aprovacao do copy gate
**Plans**: TBD

Plans:
- [ ] 03-01: Loop de regeneracao com feedback routing e circuit breaker

### Phase 4: Output & Integration
**Goal**: Criativos aprovados chegam organizados com relatorios auditaveis, e nexus.py funciona como drop-in wrapper do pipeline.py via CLI
**Depends on**: Phase 3
**Requirements**: OUT-01, OUT-02, OUT-03, INT-01, INT-02
**Success Criteria** (what must be TRUE):
  1. Criativos aprovados estao em approved/ com nomes claros, prontos para upload manual no Meta Ads
  2. Cada criativo tem relatorio JSON com scores por dimensao, feedback recebido e historico de tentativas
  3. Ao final do batch, resumo mostra total aprovados/reprovados/quarantined, custo estimado e tempo de execucao
  4. nexus.py aceita mesmos argumentos de pipeline.py (--image, --niche, --hooks) e orquestra o pipeline sem modificar o arquivo original
  5. Pipeline roda end-to-end sem intervencao manual: gera, revisa, regenera se necessario, organiza output
**Plans**: TBD

Plans:
- [ ] 04-01: Output organizado (approved/, quarantine/, relatorios JSON)
- [ ] 04-02: CLI wrapper nexus.py + integracao end-to-end com pipeline.py

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 0/2 | Not started | - |
| 2. Review Engine | 0/2 | Not started | - |
| 3. Regeneration Loop | 0/1 | Not started | - |
| 4. Output & Integration | 0/2 | Not started | - |
