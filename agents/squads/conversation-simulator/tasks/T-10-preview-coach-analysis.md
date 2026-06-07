# T-10 — preview-coach-analysis

**ID:** T-10
**Executor:** coach-analyzer + feedback-writer
**Workflow:** WF-02 (Modo Guiado)

## Propósito
Analisar mensagem ANTES de ser enviada e sugerir melhorias — exclusivo para planos PRO e MASTER.

## Inputs
- `draft_message` — texto rascunhado pelo usuário (não enviado ainda)
- `history` — histórico da sessão até o momento
- `character_state` — estado atual da personagem
- `user_level` — nível do usuário
- `user_plan` — plano do usuário

## Steps
1. Verificar se `user_plan` = pro ou master → se free → retornar blocked
2. Executar T-04 (retrieve-relevant-concepts) com o rascunho como query
3. Executar T-05 (analyze-user-message) com o rascunho
4. Executar T-06 (write-coach-feedback) em modo preview (tom mais sugestivo)
5. Retornar análise prévia + sugestões de melhoria

## Output
```json
{
  "blocked": false,
  "preview_feedback": "Antes de enviar: seu frame está fraco aqui...",
  "score_preview": 5.8,
  "priority_issue": "frame",
  "suggestions": [
    "sugestão 1",
    "sugestão 2"
  ],
  "send_anyway": true
}
```

## Condições de Bloqueio
- `user_plan` = free → `{ blocked: true, upgrade_url: "/upgrade" }`
