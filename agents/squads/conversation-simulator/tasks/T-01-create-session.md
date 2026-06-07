# T-01 — create-session

**ID:** T-01
**Executor:** session-manager
**Workflow:** WF-03

## Propósito
Criar nova sessão de simulação com estado inicial configurado.

## Inputs
- `user_id` — ID do usuário
- `scenario` — cenário escolhido (ex: testes_e_objecoes)
- `character` — persona escolhida (casual_fun | intellectual | high_value | girl_next_door)
- `mode` — modo de treino (livre | guiado | desafio)
- `user_plan` — plano do usuário (free | pro | master)

## Steps
1. Verificar rate limit (plano FREE: máx 3 sessões/24h)
2. Se bloqueado → retornar `{ blocked: true }` → simulation-chief redireciona para paywall
3. Se liberado → gerar `session_id` (UUID)
4. Inicializar estado da sessão com interesse inicial da persona
5. Persistir no PostgreSQL (tabela `training_sessions`)
6. Retornar `session_id` + estado inicial

## Output
```json
{
  "session_id": "uuid",
  "status": "active",
  "character_state": { "persona": "Isabela", "interest_level": 20 },
  "blocked": false
}
```

## Condições de Bloqueio
- Plano FREE + 3 sessões nas últimas 24h → paywall
- `scenario` ou `character` inválido → erro de validação
