# T-06 — write-coach-feedback

**ID:** T-06
**Executor:** feedback-writer
**Workflow:** WF-01 (executa após T-05)

## Propósito
Transformar análise estruturada em feedback narrativo do Coach, calibrado ao nível do usuário.

## Inputs
- `analysis` — output completo do T-05 (scores, diagnósticos, flags, concepts)
- `user_message` — mensagem original do usuário (para citar no feedback)
- `user_level` — nível atual (1-6) para calibrar linguagem
- `concepts` — conceitos completos do T-04 (para citar princípio e livro)

## Steps
1. Identificar `priority_issue` da análise
2. Selecionar conceito mais relevante para o problema principal
3. Gerar feedback no formato estruturado (ver feedback-writer.md)
4. Calibrar tom e profundidade baseado no `user_level`
5. Gerar 2-3 alternativas concretas para o problema principal
6. Retornar feedback formatado

## Output
```json
{
  "feedback_text": "Score geral: 6.0/10\n\nPROBLEMA PRINCIPAL...",
  "score_overall": 6.0,
  "priority_issue": "frame",
  "concept_cited": "frame_control_001",
  "alternatives": [
    "alternativa 1",
    "alternativa 2",
    "alternativa 3"
  ]
}
```

## Condições de Bloqueio
- Depende de T-05 completar com análise válida
