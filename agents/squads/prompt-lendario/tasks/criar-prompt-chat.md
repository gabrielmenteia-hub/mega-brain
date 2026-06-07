# Task: Criar Prompt de Chat/Texto

```yaml
task_name: "Criar Prompt para IA de Chat/Texto"
status: pending
responsible_executor: prompt-chief
execution_type: Hybrid
estimated_time: "10-20min"
input:
  - briefing do usuário (objetivo, produto, público, tom)
  - IA alvo (Claude, GPT-4, Gemini, etc.)
  - contexto do projeto (se disponível)
output:
  - prompt completo pronto para uso
  - explicação de cada dimensão (opcional)
  - 2-3 variações ou dicas de iteração
acceptance_criteria:
  - Todas as 8 dimensões LENDÁRIO presentes
  - Persona específica (não genérica)
  - Mínimo 3 constraints definidos
  - Formato de output especificado
  - Prompt copiável sem edição
quality_gate: PL-QP-001
```

---

## Workflow de Execução

### FASE 1 — Briefing (se dados insuficientes)

Se o usuário não forneceu informações suficientes, perguntar:

```
Para criar seu prompt lendário, preciso de:

1. OBJETIVO: O que o prompt deve gerar? (headlines, email, análise, código...)
2. IA ALVO: Claude, GPT-4, Gemini, ou outra?
3. CONTEXTO: Produto, serviço ou projeto sobre o qual falar?
4. PÚBLICO: Para quem o output é direcionado?
5. TOM: Formal, direto, empático, técnico?
6. RESTRIÇÕES JÁ CONHECIDAS: Alguma palavra ou abordagem a evitar?
```

Não avançar para Fase 2 sem resposta das perguntas 1, 3 e 5 ao menos.

---

### FASE 2 — Construção LENDÁRIO

Construir o prompt preenchendo cada dimensão em ordem:

**L — LENTE**
- Definir persona com especialidade específica relevante à tarefa
- Incluir referência de experiência ou escola de pensamento
- Evitar personas genéricas ("especialista em marketing")

**E — EXCITANTE**
- Contextualizar a situação que torna a tarefa urgente
- Stakes: o que está em jogo se a IA fizer mal
- Uma ou duas frases focadas

**N — NÚCLEO**
- Formular instrução central com: verbo de ação + objeto + especificidade
- Exemplos de verbos fortes: Escreva, Analise, Liste, Crie, Avalie, Reescreva, Gere
- Evitar: "Me ajude a...", "Tente...", "Você poderia..."

**D — DADOS**
- Briefing completo do produto/projeto/contexto
- Dados de audiência (perfil, dores, desejos)
- Exemplos de referência quando disponíveis
- Informações específicas que a IA não pode adivinhar

**Â — ÂNCORAS**
- Tom a evitar (corporativo, hiperbólico, passivo...)
- Palavras ou frases proibidas (lista explícita)
- Estruturas inadequadas para o contexto
- Limitações de comprimento ou formato

**R — RESULTADO**
- Formato: lista, parágrafos, JSON, tabela, markdown...
- Extensão: número de itens OU número de palavras
- Divisões: seções, categorias, agrupamentos
- Estilo visual: com ou sem markdown, títulos, bullets

**I — ITERAÇÃO** (incluir quando relevante)
- "Para versão mais longa, diga: +extensão"
- "Para tom mais formal, diga: +formal"
- "Para mais exemplos, diga: +exemplos"

**O — OBJETIVO**
- Critério de sucesso explícito
- Como o usuário sabe que o output funcionou
- Teste de realidade (o output provocaria qual ação/reação?)

---

### FASE 3 — Output Final

Entregar o prompt no formato:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[PROMPT LENDÁRIO — pronto para copiar]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Após o prompt, adicionar:

**Score LENDÁRIO:** [X/8 dimensões] ✅
**Para iterar:** [dica de refinamento mais provável]
**Variação:** [uma versão alternativa ou ajuste sugerido]

---

## Erros Comuns a Evitar

| Erro | Dimensão | Correção |
|------|----------|----------|
| "Você é um especialista em X" | L | "Você é um X com 15 anos de experiência em Y, formado em Z..." |
| Sem contexto situacional | E | Adicionar por que esta tarefa importa agora |
| "Me ajude a fazer X" | N | "Escreva / Analise / Crie / Liste X com Y especificidade" |
| Briefing vago | D | Bullet points com dados específicos |
| Sem constraints | Â | Mínimo 3 restrições explícitas |
| "Responda bem" | R | "Responda em X formato com Y itens de Z extensão" |
| Sem critério de sucesso | O | "O output será bem-sucedido quando [condição mensurável]" |
