# T-08 — update-user-progress

**ID:** T-08
**Executor:** progress-tracker
**Workflow:** WF-04 (executa após T-07)

## Propósito
Persistir XP e skills atualizadas no banco de dados e detectar marcos de evolução.

## Inputs
- `user_id` — ID do usuário
- `xp_gained` — output do T-07
- `skills_xp` — XP por skill do T-07
- `current_user_state` — estado atual do usuário (nível, XP total, skills)

## Steps
1. Somar XP ganho ao XP total do usuário
2. Verificar se houve level-up (cruzou threshold do próximo nível)
3. Atualizar XP de cada skill individualmente
4. Verificar milestones de skill (skill subiu de nível?)
5. Persistir no PostgreSQL (tabelas `users` e `user_skills`)
6. Retornar estado atualizado + eventos detectados

## Output
```json
{
  "updated": true,
  "total_xp_new": 652,
  "level_new": 3,
  "level_up": false,
  "skill_milestones": ["calibracao chegou ao nível 3"],
  "new_skills_state": { ... }
}
```

## Condições de Bloqueio
- Depende de T-07 completar
