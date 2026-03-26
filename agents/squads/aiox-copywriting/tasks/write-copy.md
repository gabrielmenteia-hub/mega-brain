# Task: Write Copy

**Task ID:** write-copy
**Version:** 1.0.0
**Purpose:** Produzir copy completa para o formato solicitado com base no market brief e copy strategy
**Agent:** gary-halbert (lead) + gary-bencivenga (revisão)
**Command:** `*write {formato}`
**Execution Type:** Agent
**Output:** `output/copy/{project-slug}/copy-draft.md`

---

## Task Anatomy

```yaml
task_name: write-copy
status: active
responsible_executor: gary-halbert (draft) → gary-bencivenga (proof layer)
execution_type: agent
input:
  required:
    - market_brief: "output/copy/{project-slug}/market-brief.md"
    - copy_strategy: "output/copy/{project-slug}/copy-strategy.md"
    - formato: "ad | landing-page | email | social | vsl | sales-letter"
  optional:
    - exemplos: "Copy de referência (swipe file)"
    - restricoes: "Tom, limite de caracteres, compliance"
output:
  copy_draft:
    file: "output/copy/{project-slug}/copy-draft.md"
    sections: "Todos os componentes do formato solicitado"
action_items:
  - "STEP 1 (@gary-halbert): Draft principal (todos os componentes do formato)"
  - "STEP 2 (@gary-halbert): So-what test em cada seção"
  - "STEP 3 (@gary-bencivenga): Proof layer — auditoria de believability"
  - "STEP 4 (@gary-bencivenga): Objection sweep — verificar se objeções do brief estão endereçadas"
  - "STEP 5: Consolidar copy-draft.md"
acceptance_criteria:
  - "Todos os componentes do formato presentes"
  - "Awareness level correto (headline calibrada para Stage diagnosticado)"
  - "Ângulo definido na estratégia está implementado"
  - "Oferta estruturada incorporada corretamente"
  - "Mínimo 1 prova/depoimento específico presente"
  - "CTA único e específico"
  - "Nenhuma afirmação sem prova ou reason-why associados"
  - "copy-draft.md gerado em output/copy/{project-slug}/"
```

---

## Format Structures

### AD (Meta/Google)

```markdown
# AD — {produto} — Variante {N}

## Hook (3 opções)
HOOK A: {texto}
HOOK B: {texto}
HOOK C: {texto}

## Body
{texto}

## CTA
{texto}

## Ângulo: {ângulo escolhido}
## Awareness Target: Stage {N}
## Driver: {medo/desejo/identidade}
```

**Regras:**
- Hook: 1-3 linhas. Para o scroll. Específico.
- Body: PAS ou Story. Máx 15-20 linhas para cold. Menos para warm.
- CTA: 1 ação. Específica. ("Acesse o treinamento gratuito" > "Clique aqui")
- Entregar 3 variantes de hook mínimo

### LANDING PAGE / SALES PAGE

```markdown
# LANDING PAGE — {produto}

## Hero Section
### Headline
{headline_principal}

### Subheadline
{subheadline}

### Hero CTA
{cta_hero}

## Pain/Problem Section
{texto}

## Agitation
{texto}

## Mechanism/Solution
### Mechanism Name: {nome do mecanismo}
{texto}

## Social Proof
### Depoimento 1
{texto_formatado}
— {nome, cargo, resultado}

### Depoimento 2
...

## Offer Stack
### O que você recebe:
- Item 1: {descrição + valor}
- Item 2: {descrição + valor}
- Bônus 1: {descrição + valor}
- Bônus 2: {descrição + valor}

### Total Value: R${X}
### Preço: R${Y}

## Guarantee
{texto_da_garantia}

## FAQ
**P: {objeção}**
R: {resposta}
(repetir para top 5 objeções)

## Close
{texto_de_fechamento}

### Final CTA
{cta_final}

## P.S.
{ps}
```

### EMAIL

```markdown
# EMAIL — {produto} — {objetivo}

## Assunto (5 variantes)
A: {texto}
B: {texto}
C: {texto}
D: {texto}
E: {texto}

## Preview Text (correspondente a cada assunto)
A: {texto}
...

## Body
{abertura_pessoal_ou_historia}

{desenvolvimento_pas_ou_story}

{transicao_para_oferta}

{cta_unico}

## P.S.
{ps_com_beneficio_ou_urgencia}

## Ângulo: {ângulo}
## Tipo: {nurture | vendas | reativação}
```

### SOCIAL MEDIA (Caption/Thread)

```markdown
# SOCIAL — {plataforma} — {produto}

## Hook (primeira linha — stop the scroll)
{texto — sem ponto no final para criar lacuna}

## Body
{texto — parágrafos de 1-2 linhas}
{espaço em branco entre cada ideia}

## CTA / Engajamento
{texto — pergunta ou instrução}

## Hashtags (se aplicável)
{hashtags}

## Variante Thread (se solicitado)
Post 1: {hook}
Post 2: {desenvolvimento}
...
Post N: {cta}
```

### VSL (Video Script)

```markdown
# VSL SCRIPT — {produto}

## Hook (0-30s)
{texto — lido em ~30 segundos}
**Visual cue:** {o que aparece na tela}

## Problem Identification (30s-2min)
{texto}

## Agitation (2min-4min)
{texto}

## Credibility / Story (4min-7min)
{texto — quem você é, por que pode ajudar}

## Solution / Mechanism (7min-10min)
{texto}

## Social Proof (10min-13min)
{depoimentos formatados para fala}

## Offer (13min-17min)
{apresentação da oferta com stack}

## Guarantee (17min-18min)
{texto}

## Close (18min-20min)
{texto}

## CTA Final
{texto — claro, específico, urgente}
```

### SALES LETTER (Long Form)

```markdown
# SALES LETTER — {produto}

## Headline
{headline}

## Subheadline
{subheadline}

---
Dear {nome/grupo específico},

## Abertura
{história pessoal ou fato chocante — 3-5 parágrafos}

## Problem Identification
{nomeie a dor — 3-5 parágrafos}

## Agitation
{aprofunde — 3-5 parágrafos}

## Solution Reveal
"Por isso eu criei {produto}..."
{apresentação — 2-3 parágrafos}

## Mechanism
"Funciona porque..."
{explicação do mecanismo — 3-5 parágrafos}

## Proof / Case Studies
{3+ casos com antes/depois específico}

## Bullets
- {bullet 1 — Bencivenga style}
- {bullet 2}
...

## Offer
{todos os componentes com valor individual}

## Guarantee
{garantia específica com prazo e condições}

## Urgency
{razão real para agir agora}

## CTA
{específico e simples}

Atenciosamente,
{nome}

## P.S.
{sintetiza promessa + urgência}

## P.P.S. (opcional)
{endereça a última objeção}
```

---

## Writing Protocol (Halbert)

### Draft Phase

1. **Personalize:** Escreva para UMA pessoa específica do ICP
2. **Open strong:** Primeira frase deve ser impossível de não ler
3. **PAS backbone:** Mesmo em formatos longos, PAS guia a estrutura
4. **Conversational:** Leia em voz alta. Parece um humano? Se não, reescreva.
5. **Short paragraphs:** Máx 4 linhas. Uma ideia por parágrafo.
6. **No jargon:** Se usar, traduza imediatamente.
7. **So-what test:** Após cada parágrafo, diga "e daí?". A resposta deve estar na próxima frase.

### Proof Layer (Bencivenga)

Após draft completo:
1. **Believability audit:** Identifique todos os claims de alto risco
2. **Proof match:** Para cada claim de alto risco, há prova equivalente?
3. **Objection sweep:** As 5 objeções do market brief foram endereçadas?
4. **Testimonial check:** Depoimentos são específicos (antes/depois/número)?
5. **Guarantee strength:** A garantia é agressiva o suficiente para eliminar risco?

---

## Anti-Patterns

```yaml
never_do:
  - "Começar com o produto antes do prospect"
  - "Parágrafos de mais de 5 linhas"
  - "Múltiplos CTAs no mesmo formato (exceto landing page)"
  - "Afirmação sem prova no mesmo parágrafo"
  - "Copy corporativa/passiva"
  - "Headline que ignora o awareness level"
  - "Bullets genéricos ('você vai aprender X')"

always_do:
  - "Escrever para uma pessoa específica"
  - "Testar cada frase com 'puxa para a próxima?'"
  - "Calibrar headline para awareness level correto"
  - "Incluir P.S. em emails e sales letters"
  - "Depoimentos com nome + resultado específico"
  - "CTA que descreve o QUE o prospect recebe"
```

---

## Handoff

```yaml
on_complete:
  pass_to: joseph-sugarman
  deliver: "output/copy/{project-slug}/copy-draft.md"
  context: "Draft completo ({formato}). Proof layer aplicado. Pronto para trigger audit e polimento final."
  next_gate: "QG-003 passed"
```
