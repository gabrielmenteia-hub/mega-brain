# Checklist: Copy Quality

**Checklist ID:** copy-quality
**Version:** 1.0.0
**Purpose:** Validação final de qualidade antes de entrega de qualquer copy
**Gate:** QG-004 (Tier 3 → Delivery)
**Used by:** joseph-sugarman + copy-chief

---

## Como usar

- **MANDATORY:** Todos devem passar (100%) antes da entrega
- **QUALITY:** Mínimo 80% deve passar
- Status: ✅ PASS | ❌ FAIL | ⚠️ PARCIAL

---

## SEÇÃO 1: Calibração Estratégica

**MANDATORY**

- [ ] **1.1** Awareness level foi diagnosticado antes de escrever
- [ ] **1.2** Headline está calibrada para o nível de awareness correto
- [ ] **1.3** Ângulo principal é consistente do início ao CTA
- [ ] **1.4** ICP está implícita ou explicitamente definido na copy
- [ ] **1.5** CTA é único (apenas um por copy, exceto landing page com múltiplos pontos)

**QUALITY**

- [ ] **1.6** Copy atrai explicitamente quem é o ICP
- [ ] **1.7** Copy repele (implicitamente) quem não é o ICP
- [ ] **1.8** Urgência presente com razão lógica (se aplicável ao formato)
- [ ] **1.9** Oferta está estruturada com valor percebido > preço

---

## SEÇÃO 2: Estrutura e Flow

**MANDATORY**

- [ ] **2.1** Primeira frase é irresistível de não ler
- [ ] **2.2** Cada parágrafo tem no máximo 4 linhas
- [ ] **2.3** Nenhum bloco sem espaço em branco (exceto sales letter densa)
- [ ] **2.4** CTA descreve o que o prospect recebe, não o que ele deve fazer
- [ ] **2.5** Todos os componentes do formato estão presentes

**QUALITY**

- [ ] **2.6** Slippery slide test: cada parágrafo puxa para o próximo
- [ ] **2.7** P.S. presente em emails e sales letters
- [ ] **2.8** Transições suaves entre seções
- [ ] **2.9** Copy pode ser lida em voz alta sem tropeçar

---

## SEÇÃO 3: Credibilidade e Prova

**MANDATORY**

- [ ] **3.1** Nenhuma afirmação genérica sem especificidade ou prova
- [ ] **3.2** Mínimo 1 prova concreta (depoimento com resultado, dado, caso)
- [ ] **3.3** Nenhum superlativo sem suporte ("melhor", "líder", "único") sem prova
- [ ] **3.4** Claims de alto risco têm prova equivalente (Believability Gradient)

**QUALITY**

- [ ] **3.5** Depoimentos têm nome + cargo + resultado específico
- [ ] **3.6** Reason-why presente para benefícios principais
- [ ] **3.7** Preemptive claim identificado e incluído (se aplicável)
- [ ] **3.8** Guarantee é específica (prazo + condições claras)

---

## SEÇÃO 4: Triggers Psicológicos

**MANDATORY**

- [ ] **4.1** Curiosidade ativa (lacuna aberta e não fechada antes do CTA)
- [ ] **4.2** Pelo menos 3 dos 15 power triggers ativos e bem implementados
- [ ] **4.3** Nenhum trigger ativo gerando fricção de credibilidade

**QUALITY**

- [ ] **4.4** Trigger de esperança ou desejo de ganho presente
- [ ] **4.5** Urgência real com razão lógica ativa
- [ ] **4.6** Involvement device presente (pergunta retórica, cenário, yes-ladder)
- [ ] **4.7** Especificidade numérica presente em mínimo 2 pontos da copy

---

## SEÇÃO 5: Objeções

**MANDATORY**

- [ ] **5.1** Top 3 objeções (do market brief) foram endereçadas
- [ ] **5.2** Objeção de preço endereçada (se copy tem preço)
- [ ] **5.3** Objeção de credibilidade endereçada

**QUALITY**

- [ ] **5.4** Todas as 5 objeções mapeadas foram endereçadas
- [ ] **5.5** Objeção "já tentei antes" endereçada (se mercado Stage 3+)
- [ ] **5.6** FAQ presente em landing pages e sales letters

---

## SEÇÃO 6: Linguagem

**MANDATORY**

- [ ] **6.1** Zero jargão corporativo ("soluções inovadoras", "excelência", "ecossistema")
- [ ] **6.2** Zero voz passiva predominante
- [ ] **6.3** Copy está na linguagem DO PROSPECT (não do vendedor)
- [ ] **6.4** Nenhum erro de ortografia ou gramática

**QUALITY**

- [ ] **6.5** Frases curtas predominam (máx 20 palavras na maioria)
- [ ] **6.6** Verbos ativos e fortes (transforma, elimina, garante vs. pode ajudar)
- [ ] **6.7** Especificidade: números em vez de adjetivos vagos
- [ ] **6.8** Tom consistente do início ao fim

---

## SEÇÃO 7: Análise Estratégica (Entrega)

**MANDATORY**

- [ ] **7.1** copy-final.md gerado em output/copy/{project-slug}/
- [ ] **7.2** copy-analysis.md gerado com diagnóstico estratégico
- [ ] **7.3** Trigger audit completo em copy-analysis.md
- [ ] **7.4** Top 3 problemas e fixes documentados em copy-analysis.md

**QUALITY**

- [ ] **7.5** Pelo menos 2 recomendações de A/B teste em copy-analysis.md
- [ ] **7.6** Score por dimensão (0-10) documentado
- [ ] **7.7** Seções reescritas incluídas se solicitado

---

## Scoring

```
MANDATORY: {N}/{total} passing
QUALITY: {N}/{total} passing

PASS: mandatory = 100% AND quality >= 80%
FAIL: qualquer mandatory falha OU quality < 80%
```

---

## On Fail

| Seção | Falha | Agente Responsável |
|-------|-------|-------------------|
| Calibração (1) | Awareness errado | eugene-schwartz |
| Estrutura (2) | Flow quebrado | joseph-sugarman |
| Credibilidade (3) | Claim sem prova | gary-bencivenga + claude-hopkins |
| Triggers (4) | Triggers ausentes | joseph-sugarman |
| Objeções (5) | Objeção sem resposta | dan-kennedy + gary-bencivenga |
| Linguagem (6) | Jargão ou passivo | gary-halbert |
| Entrega (7) | Análise incompleta | copy-chief |

---

## Quick Reference: Anti-Patterns Críticos

Qualquer um destes → reescrever antes de entregar:

- `"Somos líderes em..."` sem dado que prove
- `"Qualidade superior"` sem especificidade
- `"Clique aqui para saber mais"` como CTA
- `"Nosso produto vai te ajudar"` no início (fale do prospect primeiro)
- Parágrafo de mais de 6 linhas sem espaço em branco
- Urgência sem razão lógica ("Última chance!" sem contexto)
- Depoimento vago ("Ótimo produto! — João")
- Headline genérica para mercado Stage 3+ (foque no mecanismo, não no resultado)
