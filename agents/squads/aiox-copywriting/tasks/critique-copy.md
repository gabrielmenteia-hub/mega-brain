# Task: Critique Copy

**Task ID:** critique-copy
**Version:** 1.0.0
**Purpose:** Análise estratégica profunda de copy existente com diagnóstico, score e recomendações
**Agent:** joseph-sugarman (lead) + eugene-schwartz + dan-kennedy
**Command:** `*critique {copy}`
**Execution Type:** Agent
**Output:** `output/copy/{project-slug}/copy-analysis.md`

---

## Task Anatomy

```yaml
task_name: critique-copy
status: active
responsible_executor: joseph-sugarman (lead) + eugene-schwartz + dan-kennedy
execution_type: agent
input:
  required:
    - copy: "A copy a ser analisada (colada ou caminho do arquivo)"
  optional:
    - contexto: "Produto, formato, público-alvo, objetivo de conversão"
    - metricas: "Taxa de conversão atual, CTR, outros dados de performance"
output:
  copy_analysis:
    file: "output/copy/{project-slug}/copy-analysis.md"
    sections:
      - "Diagnóstico estratégico (awareness, ângulo, estrutura)"
      - "Score por dimensão"
      - "Trigger audit"
      - "Friction points"
      - "Top 3 problemas críticos"
      - "Recomendações de A/B teste"
      - "Copy reescrita (seções críticas)"
action_items:
  - "STEP 1 (@eugene-schwartz): Diagnóstico de awareness level da copy vs. mercado"
  - "STEP 2 (@dan-kennedy): Análise de ângulo e drivers emocionais"
  - "STEP 3 (@joseph-sugarman): Trigger audit (30 triggers) + flow/friction analysis"
  - "STEP 4 (integrado): Score por dimensão + top 3 problemas"
  - "STEP 5 (@gary-halbert): Reescrever seções críticas (opcional)"
  - "STEP 6: Consolidar copy-analysis.md"
acceptance_criteria:
  - "Awareness level diagnosticado para a copy existente"
  - "Score por dimensão (0-10 cada)"
  - "Top 3 problemas críticos identificados com impacto estimado"
  - "Trigger audit completo (quais estão ativos vs. ausentes)"
  - "Pelo menos 2 recomendações de A/B teste"
  - "copy-analysis.md gerado em output/copy/{project-slug}/"
```

---

## Critique Framework

### DIMENSÃO 1: Calibração de Awareness (Schwartz)
Score: 0-10

Perguntas:
- A headline está calibrada para o nível de awareness do mercado?
- Se Stage 3, a copy está vendendo mecanismo (não resultado genérico)?
- Se Stage 4-5, a copy está focando em oferta e prova (não mecanismo)?

**Diagnóstico de Mismatch:**
```
Copy está no Stage {N_copy}
Mercado está no Stage {N_mercado}
Mismatch: {N diferença}
Impacto: {explicação do por que isso prejudica conversão}
```

### DIMENSÃO 2: Clareza e Força do Ângulo (Kennedy)
Score: 0-10

Perguntas:
- Qual é o ângulo dominante? (medo / desejo / identidade / urgência)
- O ângulo está consistente ao longo de toda a copy?
- O ICP está claramente definido? (atrai os certos, repele os errados?)
- Existe urgência real com razão lógica?

### DIMENSÃO 3: Estrutura e Flow (Sugarman)
Score: 0-10

Checklist:
- [ ] Primeira frase é irresistível de abandonar?
- [ ] Cada parágrafo puxa para o próximo?
- [ ] Nenhum parágrafo tem mais de 4 linhas?
- [ ] Espaço em branco suficiente?
- [ ] Transições suaves entre seções?
- [ ] CTA único e específico?

### DIMENSÃO 4: Triggers Psicológicos (Sugarman)
Score: 0-10

Audit dos 15 principais triggers:
```
| Trigger | Status | Implementação |
|---------|--------|---------------|
| Curiosidade | ✓/✗/~ | {observação} |
| Urgência | ✓/✗/~ | {observação} |
| Medo | ✓/✗/~ | {observação} |
| Especificidade | ✓/✗/~ | {observação} |
| Prova social | ✓/✗/~ | {observação} |
| Exclusividade | ✓/✗/~ | {observação} |
| Escassez | ✓/✗/~ | {observação} |
| Involvement | ✓/✗/~ | {observação} |
| Esperança | ✓/✗/~ | {observação} |
| Familiaridade | ✓/✗/~ | {observação} |
| Estabelecimento de valor | ✓/✗/~ | {observação} |
| Garantia | ✓/✗/~ | {observação} |
| Culpa | ✓/✗/~ | {observação} |
| Greed | ✓/✗/~ | {observação} |
| Simplicidade | ✓/✗/~ | {observação} |

✓ = ativo e bem implementado
~ = presente mas subotimizado
✗ = ausente
```

### DIMENSÃO 5: Believability e Prova (Bencivenga + Hopkins)
Score: 0-10

Checklist:
- [ ] Claims de alto risco têm prova equivalente?
- [ ] Depoimentos são específicos (antes/depois/número)?
- [ ] Reason-why presente para benefícios principais?
- [ ] Nenhuma afirmação vaga sem suporte?
- [ ] Guarantee elimina o risco percebido?

### DIMENSÃO 6: Oferta (Hormozi)
Score: 0-10

Perguntas:
- Dream Outcome está articulado com especificidade?
- Perceived Likelihood está suportada por prova?
- Time Delay está minimizado (quick win presente)?
- Effort está minimizado?
- Seria "estúpido não aceitar"?

---

## Analysis Output Format

```markdown
# Análise Estratégica — {produto} — {data}

## Score Geral: {X}/10

| Dimensão | Score | Status |
|----------|-------|--------|
| Calibração de Awareness | {X}/10 | {Crítico/Atenção/OK} |
| Ângulo e ICP | {X}/10 | {Crítico/Atenção/OK} |
| Estrutura e Flow | {X}/10 | {Crítico/Atenção/OK} |
| Triggers Psicológicos | {X}/10 | {Crítico/Atenção/OK} |
| Believability e Prova | {X}/10 | {Crítico/Atenção/OK} |
| Oferta | {X}/10 | {Crítico/Atenção/OK} |

## Diagnóstico Principal

### Awareness Level
A copy está escrita para: Stage {N_copy}
O mercado está em: Stage {N_mercado}
{diagnóstico_de_mismatch_se_houver}

### Ângulo Dominante
{ângulo_identificado}
{avaliação_de_consistência}

## Top 3 Problemas Críticos

### PROBLEMA 1 — {nome} [IMPACTO: Alto/Médio/Baixo]
**Diagnóstico:** {texto}
**Por que prejudica:** {texto}
**Fix:** {texto}

### PROBLEMA 2 — {nome} [IMPACTO: Alto/Médio/Baixo]
**Diagnóstico:** {texto}
**Por que prejudica:** {texto}
**Fix:** {texto}

### PROBLEMA 3 — {nome} [IMPACTO: Alto/Médio/Baixo]
**Diagnóstico:** {texto}
**Por que prejudica:** {texto}
**Fix:** {texto}

## Trigger Audit

ATIVOS (✓): {lista}
SUBOTIMIZADOS (~): {lista com recomendação}
AUSENTES CRÍTICOS (✗): {lista com prioridade de implementação}

## Friction Points

| Tipo | Localização | Descrição | Fix |
|------|-------------|-----------|-----|
| {tipo} | {onde} | {descrição} | {fix} |

## Recomendações de A/B Teste

### TESTE 1 — [Alta Prioridade]
**Controle:** {headline/elemento atual}
**Variante:** {proposta}
**Hipótese:** {por que isso deve melhorar conversão}
**Métricas:** {o que medir}

### TESTE 2 — [Alta Prioridade]
...

### TESTE 3 — [Média Prioridade]
...

## Seções Reescritas

### Headline (versão original vs. recomendada)
**Original:** {texto}
**Recomendada:** {texto}
**Justificativa:** {texto}

### Hook/Abertura (se aplicável)
...

### CTA (se aplicável)
...

## Veredicto Final
{diagnóstico geral em 3-5 linhas — o que está bem, o que é crítico, por onde começar}
```

---

## Anti-Patterns

```yaml
never_do:
  - "Critique vaga ('a copy poderia ser melhor')"
  - "Score sem justificativa específica"
  - "Problema sem fix acionável"
  - "A/B test sem hipótese clara"
  - "Ignorar awareness level mismatch (é a causa raiz mais comum)"

always_do:
  - "Score por dimensão com justificativa"
  - "Top 3 problemas com impacto estimado"
  - "Pelo menos 2 seções reescritas para mostrar o que poderia ser"
  - "A/B tests com hipótese de por que vai melhorar"
  - "Diagnóstico de awareness (mesmo sem contexto explícito)"
```

---

## Handoff

```yaml
on_complete:
  pass_to: copy-chief
  deliver: "output/copy/{project-slug}/copy-analysis.md"
  context: "Análise completa. Score geral: {X}/10. Top problema: {problema_1}. Pronto para revisão com usuário."
```
