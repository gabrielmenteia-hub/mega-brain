# T-02 — receive-user-message

**ID:** T-02
**Executor:** session-manager
**Workflow:** WF-01, WF-02

## Propósito
Salvar mensagem do usuário no histórico da sessão e atualizar estado.

## Inputs
- `session_id` — ID da sessão ativa
- `text` — texto da mensagem do usuário

## Steps
1. Verificar se sessão existe e está com status `active`
2. Incrementar `turn_count`
3. Salvar mensagem na tabela `messages` com timestamp
4. Atualizar histórico em memória para o turno atual
5. Retornar histórico atualizado para os próximos agentes

## Output
```json
{
  "turn": 5,
  "message_saved": true,
  "history": [...],
  "session_status": "active"
}
```

## Condições de Bloqueio
- Sessão não encontrada ou status ≠ `active` → erro
