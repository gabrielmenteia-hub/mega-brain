# T-07 — compute-session-xp

**ID:** T-07
**Executor:** progress-tracker
**Workflow:** WF-04

## Propósito
Calcular XP total ganho na sessão com base nos scores e multiplicadores.

## Inputs
- `session_summary` — scores médios por dimensão da sessão completa
- `mode` — modo da sessão (livre | guiado | desafio)
- `character` — personagem usada
- `session_completed` — booleano (interesse final > 20 E turno >= 5)

## Steps
1. Calcular XP base = score_médio_geral × 10
2. Aplicar multiplicador de modo
3. Aplicar multiplicador de personagem
4. Aplicar multiplicador de conclusão
5. Calcular XP por skill (baseado em score individual de cada dimensão)
6. Retornar breakdown completo

## Output
Ver formato em `progress-tracker.md` (seção OUTPUT FORMAT)

## Condições de Bloqueio
- Nenhuma
