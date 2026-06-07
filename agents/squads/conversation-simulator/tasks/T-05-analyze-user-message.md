# T-05 — analyze-user-message

**ID:** T-05
**Executor:** coach-analyzer
**Workflow:** WF-01 (executa após T-03 e T-04 completarem)

## Propósito
Analisar a mensagem do usuário em 5 dimensões com scores e diagnósticos específicos.

## Inputs
- `user_message` — texto da mensagem do usuário
- `history` — histórico completo da sessão
- `concepts` — output do T-04 (top-3 conceitos relevantes)
- `character_state` — estado atual da personagem (interesse, persona, teste aplicado)

## Steps
1. Avaliar mensagem em cada uma das 5 dimensões (0-10)
2. Gerar diagnóstico específico por dimensão
3. Identificar red flags e green flags presentes
4. Determinar `priority_issue` (dimensão com pior score e maior impacto)
5. Mapear conceitos aplicados da lista recebida de T-04
6. Calcular score médio geral
7. Retornar análise estruturada para T-06

## Output
Ver formato em `coach-analyzer.md` (seção OUTPUT FORMAT)

## Condições de Bloqueio
- Depende de T-03 (personagem respondeu?) e T-04 (conceitos recuperados?)
- Se T-03 não completou → aguardar
- Se T-04 não completou → aguardar
