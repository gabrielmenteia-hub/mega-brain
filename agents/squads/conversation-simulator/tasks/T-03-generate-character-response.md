# T-03 — generate-character-response

**ID:** T-03
**Executor:** character-engine
**Workflow:** WF-01 (paralelo com T-04)

## Propósito
Gerar resposta da personagem feminina mantendo coerência de persona e ajustando nível de interesse.

## Inputs
- `history` — histórico da conversa
- `persona` — persona ativa (casual_fun | intellectual | high_value | girl_next_door)
- `interest_level` — nível de interesse atual (0-100)
- `turn_count` — número do turno atual
- `last_test_turn` — último turno em que foi aplicado teste
- `coach_score` — score médio do turno anterior (para calcular delta de interesse)

## Steps
1. Carregar persona matrix da personagem ativa
2. Determinar se aplicar shit test (baseado em threshold e frequência)
3. Calcular tom da resposta baseado no interesse atual
4. Gerar resposta com LLM usando system prompt da persona
5. Calcular novo nível de interesse (± delta baseado em coach_score anterior)
6. Retornar resposta + estado atualizado

## Output
```json
{
  "character_response": "texto da resposta",
  "interest_level": 40,
  "interest_delta": +5,
  "applied_test": true,
  "test_type": "shit_test_qualificacao"
}
```

## Condições de Bloqueio
- Nenhuma (sempre retorna, mesmo com interesse = 0 — retorna mensagem de encerramento)
