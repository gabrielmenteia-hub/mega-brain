# Task: Auditar e Melhorar Prompt

```yaml
task_name: "Auditar e Melhorar Prompt Existente"
status: pending
responsible_executor: prompt-chief
execution_type: Agent
estimated_time: "10-15min"
input:
  - prompt existente (colado pelo usuário)
  - problema observado (opcional: o que está saindo errado)
  - IA alvo (se diferente do que está no prompt)
output:
  - diagnóstico por dimensão LENDÁRIO
  - score de qualidade (X/8)
  - versão melhorada do prompt
  - explicação das mudanças feitas
acceptance_criteria:
  - Diagnóstico identifica dimensão(ões) problemáticas
  - Score calculado corretamente
  - Versão melhorada endereça todos os problemas
  - Explicação clara das mudanças
quality_gate: PL-QP-001
```

---

## Workflow de Execução

### FASE 1 — Receber o Prompt

Se o usuário não colou o prompt, solicitar:

```
Cole o prompt que precisa de auditoria.
Se souber o problema ("o output está genérico", "a IA ignora partes"), mencione.
```

---

### FASE 2 — Diagnóstico por Dimensão

Avaliar o prompt em cada dimensão do Método LENDÁRIO:

```
DIAGNÓSTICO LENDÁRIO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

L — LENTE (Persona)
  Status: [✅ Presente / ⚠️ Genérica / ❌ Ausente]
  Observação: [o que está bom / o que está faltando]

E — EXCITANTE (Contexto)
  Status: [✅ / ⚠️ / ❌]
  Observação:

N — NÚCLEO (Tarefa)
  Status: [✅ / ⚠️ / ❌]
  Observação:

D — DADOS (Input)
  Status: [✅ / ⚠️ / ❌]
  Observação:

Â — ÂNCORAS (Constraints)
  Status: [✅ / ⚠️ / ❌]
  Observação:

R — RESULTADO (Formato)
  Status: [✅ / ⚠️ / ❌]
  Observação:

I — ITERAÇÃO
  Status: [✅ / ⚠️ / ❌]
  Observação:

O — OBJETIVO (Sucesso)
  Status: [✅ / ⚠️ / ❌]
  Observação:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SCORE: [X]/8 — [Lendário / Sólido / Revisão necessária / Reconstruir]

PROBLEMAS PRINCIPAIS:
1. [Dimensão mais crítica para corrigir]
2. [Segunda dimensão problemática]
3. [Terceira se houver]
```

---

### FASE 3 — Diagnóstico de Sintomas (se usuário reportou problema)

Tabela de diagnóstico rápido:

| Sintoma reportado | Dimensão problemática | Diagnóstico provável |
|---|---|---|
| "Output genérico" | L ou E | Persona fraca ou sem contexto |
| "IA ignora partes do prompt" | N ou D | Instrução enterrada no texto ou dados excessivos |
| "Output muito variado entre tentativas" | N ou Â | Núcleo ambíguo ou constraints ausentes |
| "Formato errado" | R | Formato de output não especificado |
| "IA faz coisas que não pedi" | Â | Constraints insuficientes |
| "Output muito curto/longo" | R | Extensão não especificada |
| "Tom errado" | L ou Â | Persona inadequada + tom não restringido |

---

### FASE 4 — Versão Melhorada

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROMPT MELHORADO:

[prompt completo com todas as dimensões corrigidas]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**O que mudou:**
- **L:** [o que foi melhorado na persona]
- **Â:** [constraints adicionados]
- **R:** [formato especificado]
- [outras dimensões corrigidas]

**Novo score:** [X]/8 ✅

---

## Critérios de Score

| Score | Classificação | Ação |
|---|---|---|
| 8/8 | Lendário ⚡ | Nenhuma — pronto para uso |
| 6-7/8 | Sólido ✅ | Ajuste leve nas dimensões fracas |
| 4-5/8 | Mediano ⚠️ | Revisão substancial necessária |
| 1-3/8 | Fraco ❌ | Reconstrução recomendada |
| 0/8 | Inválido 🚫 | Começar do zero com briefing completo |
