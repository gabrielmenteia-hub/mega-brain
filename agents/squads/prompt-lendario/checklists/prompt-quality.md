# Quality Gate — Prompt Lendário (PL-QP-001)

> Checklist obrigatório antes de entregar qualquer prompt.
> Score mínimo para entrega: 6/8 dimensões ✅

---

## Checklist Universal (Todas as Modalidades)

### L — LENTE (Persona)
- [ ] Persona específica definida (não "especialista em X")
- [ ] Inclui referência de expertise (anos, escola, especialidade)
- [ ] Persona é relevante para a tarefa específica

### E — EXCITANTE (Contexto)
- [ ] Contexto situacional presente
- [ ] Explica por que a tarefa importa agora
- [ ] Stakes ou urgência identificados

### N — NÚCLEO (Tarefa)
- [ ] Instrução usa verbo de ação específico
- [ ] Objeto e escopo claramente definidos
- [ ] Sem ambiguidade — apenas uma interpretação possível

### D — DADOS (Input)
- [ ] Briefing suficiente para executar sem perguntas
- [ ] Dados de audiência presentes (quando relevante)
- [ ] Informações que a IA não pode adivinhar estão incluídas

### Â — ÂNCORAS (Constraints)
- [ ] Mínimo 3 constraints definidos
- [ ] Tom ou palavras proibidas especificadas
- [ ] Formato ou estrutura inadequados excluídos

### R — RESULTADO (Formato)
- [ ] Formato de output especificado (lista, parágrafo, JSON...)
- [ ] Extensão ou número de itens definidos
- [ ] Estilo visual (markdown, plain text, etc.) especificado

### I — ITERAÇÃO
- [ ] Usuário sabe como pedir variações
- [ ] Pelo menos 1 dica de iteração fornecida

### O — OBJETIVO (Sucesso)
- [ ] Critério de sucesso explícito
- [ ] Usuário sabe quando o prompt "funcionou"

---

## Checklist Específico por Modalidade

### Chat/Texto ✅ adicionais
- [ ] Prompt copiável sem edição adicional
- [ ] Não contém marcadores de template ([NOME], {variável})

### System Prompt ✅ adicionais
- [ ] Blocos ALWAYS e NEVER presentes
- [ ] Comandos mapeados se o agente suportar
- [ ] Greeting de abertura definido

### Imagem ✅ adicionais
- [ ] Aspect ratio especificado
- [ ] Parâmetros da plataforma incluídos (--ar, --style, etc.)
- [ ] Pelo menos 2 variações entregues

### Vídeo ✅ adicionais
- [ ] Câmera e movimento definidos
- [ ] Duração especificada
- [ ] Plataforma alvo considerada na gramática

---

## Score Final

```
Dimensões presentes: [X]/8

8/8 → ⚡ LENDÁRIO — Entregar
7/8 → ✅ SÓLIDO — Entregar com nota
6/8 → ⚠️ ACEITÁVEL — Entregar mencionando dimensão fraca
5/8 → ❌ INSUFICIENTE — Revisar antes de entregar
<5  → 🚫 RECUSAR — Coletar mais briefing e reconstruir
```
