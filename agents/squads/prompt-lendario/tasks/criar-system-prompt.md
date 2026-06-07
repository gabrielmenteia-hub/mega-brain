# Task: Criar System Prompt

```yaml
task_name: "Criar System Prompt para Agente/Persona"
status: pending
responsible_executor: prompt-chief
execution_type: Hybrid
estimated_time: "15-30min"
input:
  - objetivo do agente (o que ele deve fazer)
  - tom e personalidade desejados
  - plataforma (Claude, GPT via API, outro)
  - comandos que o agente deve suportar (opcional)
output:
  - system prompt completo estruturado
  - lista de comandos com ações mapeadas
  - guia de teste (como validar o agente)
acceptance_criteria:
  - Identidade e missão claras
  - Regras ALWAYS/NEVER explícitas
  - Comandos mapeados (se aplicável)
  - Tom e limites definidos
  - Testável imediatamente após copiar
quality_gate: PL-QP-001
```

---

## Anatomia de um System Prompt de Elite

```
1. IDENTIDADE    → Quem é o agente
2. MISSÃO        → Para que ele existe
3. SEMPRE        → Comportamentos obrigatórios
4. NUNCA         → Comportamentos proibidos
5. COMANDOS      → Mapeamento de ações
6. TOM           → Como se comunica
7. LIMITES       → O que está fora do escopo
8. GREETING      → Como se apresenta ao usuário
```

---

## Workflow de Execução

### FASE 1 — Briefing

Perguntar se não fornecido:

```
Para criar seu system prompt, preciso de:

1. FUNÇÃO: O que o agente faz? (responde dúvidas, cria copy, analisa dados...)
2. PERSONALIDADE: Tom (formal/direto/empático) + referência de estilo
3. USUÁRIO-ALVO: Quem vai usar o agente?
4. COMANDOS: O agente deve responder a comandos específicos? (*/comando)
5. LIMITES: O que o agente NUNCA deve fazer?
6. PLATAFORMA: Claude via Claude.ai, API, GPT, outro?
```

---

### FASE 2 — Construção

**BLOCO 1: Identidade**
```
You are [Nome] — [título/role específico].
[1-2 frases sobre expertise e perspectiva única]
```

**BLOCO 2: Missão**
```
YOUR MISSION:
[Declaração clara do propósito — o que o agente existe para fazer]
[Métrica de sucesso implícita]
```

**BLOCO 3: Sempre (ALWAYS)**
```
ALWAYS:
- [Comportamento obrigatório 1]
- [Comportamento obrigatório 2]
- [Comportamento obrigatório 3]
[Mínimo 4 itens]
```

**BLOCO 4: Nunca (NEVER)**
```
NEVER:
- [Comportamento proibido 1]
- [Comportamento proibido 2]
- [Comportamento proibido 3]
[Mínimo 4 itens]
```

**BLOCO 5: Comandos (se aplicável)**
```
COMMANDS:
When user says *[comando] → [ação específica]
When user says *[comando] → [ação específica]
When user says *help → list all available commands
```

**BLOCO 6: Tom**
```
VOICE & TONE:
- [Adjetivo de estilo 1]
- [Adjetivo de estilo 2]
- Sentence length: [curtas/médias/variadas]
- Vocabulary level: [técnico/acessível/misto]
```

**BLOCO 7: Limites**
```
OUT OF SCOPE:
- [O que está fora do escopo 1]
- [O que está fora do escopo 2]
When user asks about out-of-scope topics: [como redirecionar]
```

**BLOCO 8: Greeting**
```
OPENING:
When activated, introduce yourself as:
"[Saudação de abertura — identidade + proposta de valor + convite]"
```

---

### FASE 3 — Output Final

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[SYSTEM PROMPT — pronto para colar]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Após o system prompt:

**Como testar:**
1. Cole o system prompt no campo de instruções do sistema
2. Inicie conversa com: "Olá" ou "Hello"
3. Verifique se o greeting está correto
4. Teste o primeiro comando com `*[comando]`

**Para ajustar:**
- Tom mais formal: adicionar "Use formal language at all times" em ALWAYS
- Tom mais casual: adicionar "Write as if texting a smart friend"
- Mais restrições: expandir bloco NEVER
