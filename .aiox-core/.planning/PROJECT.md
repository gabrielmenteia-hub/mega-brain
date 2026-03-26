# NEXUS

## What This Is

NEXUS é uma evolução do pipeline de criativos para Meta Ads que adiciona uma camada de revisão autônoma por squad AIOX. O sistema gera scripts, áudio e vídeo automaticamente, submete cada criativo a agentes especializados para análise de qualidade, e entrega apenas criativos aprovados — organizados com relatório — prontos para upload.

## Core Value

Criativos aprovados sem intervenção humana: o pipeline gera, o squad revisa e rejeita com feedback, o loop regenera até aprovar, e o output chega organizado e auditável.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Pipeline existente (scripts → áudio → vídeo) integrado como base do NEXUS
- [ ] Squad AIOX revisa cada criativo com 4 critérios: qualidade do copy, qualidade técnica, conformidade Meta Ads, pontuação preditiva de performance
- [ ] Criativos reprovados disparam regeneração automática com feedback do agente
- [ ] Loop de revisão para quando o criativo é aprovado (todos os 4 critérios)
- [ ] Criativos aprovados salvos em pasta estruturada com relatório de revisão
- [ ] Pipeline roda end-to-end sem intervenção manual

### Out of Scope

- Upload automático no Meta Ads — será manual (v1 entrega pasta organizada)
- Interface web / dashboard — revisão é autônoma via agentes, sem UI
- Análise de performance retroativa (aprender com resultados do Meta) — v2

## Context

- Base de código existente: `pipeline.py` — fluxo linear funcional (Claude → ElevenLabs → Hedra)
- Integração com squad AIOX via `.aiox-core` — agentes especializados disponíveis
- Nicho primário: relacionamento após traição (avatar: mulher casada 30-45 anos), mas pipeline é agnóstico a nicho via `--niche`
- Output atual: `.mp4` em pasta `output/` sem qualquer gate de qualidade

## Constraints

- **Tech Stack**: Python (base existente) — manter compatibilidade com `pipeline.py`
- **APIs**: Anthropic, ElevenLabs, Hedra — todas via variáveis de ambiente no `.env`
- **Agentes**: AIOX squad — integração via `.aiox-core`
- **Sem UI**: revisão 100% autônoma por agentes, sem frontend

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Revisão por agentes autônomos (sem UI) | Velocidade e escala — sem bottleneck humano no loop | — Pending |
| Regeneração automática em caso de reprovação | Maximiza qualidade sem intervenção manual | — Pending |
| v1 entrega pasta local (não sobe no Meta) | Reduz escopo e dependências de API do Meta para v1 | — Pending |

---
*Last updated: 2026-03-26 after initialization*
