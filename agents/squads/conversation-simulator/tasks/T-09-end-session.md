# T-09 — end-session

**ID:** T-09
**Executor:** session-manager
**Workflow:** WF-04 (executa após T-08)

## Propósito
Finalizar a sessão, salvar summary e arquivar estado.

## Inputs
- `session_id` — ID da sessão
- `progress_result` — output do T-08
- `session_data` — dados completos da sessão (mensagens, scores, duração)

## Steps
1. Calcular scores médios de toda a sessão
2. Montar summary da sessão
3. Atualizar status da sessão para `ended`
4. Persistir summary no PostgreSQL
5. Arquivar mensagens
6. Retornar summary final para exibição ao usuário

## Output
```json
{
  "session_ended": true,
  "summary": {
    "duration_minutes": 12,
    "total_turns": 8,
    "final_interest": 45,
    "scores_average": { ... },
    "concepts_encountered": [...],
    "session_outcome": "neutral",
    "xp_gained": 72,
    "level_up": false,
    "milestones": ["calibracao chegou ao nível 3"]
  }
}
```

## Condições de Bloqueio
- Depende de T-08 completar
