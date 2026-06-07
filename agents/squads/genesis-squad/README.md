# Genesis Squad 🏭

Squad universal para criar squads de agentes completos para **qualquer nicho ou segmento**.

## O que faz

Recebe um nicho + objetivo e entrega um squad completo production-ready com agentes, tasks, workflows e config — pronto para uso imediato no MEGABRAIN.

## Pipeline de 5 Fases

```
INPUT: nicho + objetivo
    │
    ▼
[FASE 1] Domain Discovery     ← niche-analyst
    → Domain Brief
    │
    ▼
[FASE 2] Agent Architecture   ← agent-architect
    → Agent Architecture Document
    │
    ▼
[FASE 3] Workflow Design      ← workflow-designer
    → Workflow Specification
    │
    ▼
[FASE 4] Squad Assembly       ← squad-assembler
    → Todos os arquivos gerados
    │
    ▼
[FASE 5] Validation           ← quality-guardian
    → Quality Report (score 0-10)
    │
    ▼
OUTPUT: squads/{slug}/ completo
```

## Como usar

1. Ative o `genesis-chief`
2. Execute: `*build [nicho] [objetivo]`
3. Aprove o Domain Brief (Fase 1)
4. Aprove a Agent Architecture (Fase 2)
5. Aprove o Workflow Specification (Fase 3)
6. Aguarde a geração dos arquivos (Fase 4)
7. Receba o Quality Report (Fase 5)

## Agentes

| Agente | Tier | Papel |
|--------|------|-------|
| `genesis-chief` | 1 — Chief | Orquestrador, quality gates, entrega final |
| `niche-analyst` | 2 — Specialist | Mapeia domínio: atores, processos, lacunas |
| `agent-architect` | 2 — Specialist | Projeta agentes, hierarquia e DNA |
| `workflow-designer` | 2 — Specialist | Cria tasks, workflows e quality gates |
| `squad-assembler` | 2 — Specialist | Gera todos os arquivos físicos |
| `quality-guardian` | 2 — Specialist | Audita e pontua o squad final |

## Comandos

| Comando | Ação |
|---------|------|
| `*build [nicho] [objetivo]` | Inicia pipeline completo |
| `*phase [N]` | Executa fase específica |
| `*status` | Progresso atual do pipeline |
| `*output` | Exibe arquivos gerados |
| `*help` | Lista comandos |

## Outputs

| Artefato | Gerado em | Descrição |
|----------|-----------|-----------|
| `domain-brief.md` | Fase 1 | Atores, processos, lacunas do nicho |
| `agent-architecture.md` | Fase 2 | Estrutura de agentes com DNA |
| `workflow-spec.md` | Fase 3 | Tasks, workflows, quality gates |
| `squads/{slug}/` | Fase 4 | Squad completo em arquivos |
| `quality-report.md` | Fase 5 | Score AIOX + checklist P1/P2 |

## Exemplos de uso

```
*build fitness "criar conteúdo de vendas para personal trainers"
*build jurídico "automatizar triagem de casos para escritórios de advocacia"
*build e-commerce "gerenciar campanhas de ads e análise de métricas"
*build infoproduto "produzir e lançar cursos online do zero"
```

## Score mínimo de aprovação: 7.0 / 10.0
