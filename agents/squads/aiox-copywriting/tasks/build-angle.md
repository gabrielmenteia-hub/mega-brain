# Task: Build Angle & Strategy

**Task ID:** build-angle
**Version:** 1.0.0
**Purpose:** Definir ângulo, drivers emocionais, estrutura de oferta e framework de prova
**Agent:** dan-kennedy (lead) + alex-hormozi + claude-hopkins
**Command:** `*angle {produto}`
**Execution Type:** Agent
**Output:** `output/copy/{project-slug}/copy-strategy.md`

---

## Task Anatomy

```yaml
task_name: build-angle
status: active
responsible_executor: dan-kennedy (angle) + alex-hormozi (offer) + claude-hopkins (proof)
execution_type: agent
input:
  required:
    - market_brief: "output/copy/{project-slug}/market-brief.md"
  optional:
    - formato: "Qual copy vai ser produzida"
    - prioridade: "angle | offer | proof — qual aspecto priorizar"
output:
  copy_strategy:
    file: "output/copy/{project-slug}/copy-strategy.md"
    sections:
      - "Ângulo principal selecionado e justificado"
      - "Top 3 ângulos candidatos"
      - "Drivers emocionais mapeados (medo/desejo/identidade)"
      - "ICP refinado para o ângulo"
      - "Estrutura de oferta (se aplicável)"
      - "Framework de prova"
      - "Urgência e deadline"
action_items:
  - "STEP 1 (@dan-kennedy): Mapear top 3 ângulos magnéticos"
  - "STEP 2 (@dan-kennedy): Identificar driver emocional dominante"
  - "STEP 3 (@dan-kennedy): Estruturar urgência real"
  - "STEP 4 (@alex-hormozi): Avaliar e fortalecer oferta (se copy inclui oferta)"
  - "STEP 5 (@claude-hopkins): Auditar claims com reason-why e preemptivos"
  - "STEP 6 (integrado): Selecionar ângulo e consolidar copy-strategy.md"
acceptance_criteria:
  - "Top 3 ângulos identificados com driver emocional e copy de abertura para cada"
  - "Ângulo principal selecionado com justificativa"
  - "Drivers emocionais mapeados"
  - "Oferta avaliada e/ou estruturada (se aplicável)"
  - "Framework de prova definido"
  - "copy-strategy.md gerado"
```

---

## Strategy Protocol

### STEP 1: Angle Mapping (Kennedy)

Para cada ângulo candidato, documentar:
```
ÂNGULO: {nome}
Driver emocional: medo / desejo / identidade / urgência
ICP refinado: {quem especificamente se conecta mais com esse ângulo}
Copy de abertura: {primeiras 3 linhas}
Melhor para awareness level: Stage {N}
Ponto forte: {por que funciona}
Ponto fraco: {quando não funciona}
```

**Tipos de ângulo:**
- **Medo de perda:** "O que você está perdendo ao não agir"
- **Desejo de ganho:** "O que você ganha ao agir"
- **Identidade:** "Quem você se torna ao usar"
- **Contraintuitivo:** "O que você acredita está errado"
- **Mecanismo único:** "Por que este método é diferente"
- **Transformação:** "Antes/depois de pessoas como você"
- **Urgência de mercado:** "O mercado está mudando — você precisa mudar também"

### STEP 2: Emotional Driver Map (Kennedy)

```yaml
driver_dominante: [medo | desejo | identidade]
justificativa: "{por que esse driver é o correto para esse mercado}"

medo_mapping:
  tipo: [loss | fomo | regret | embarrassment]
  o_que_perdem: "{específico}"
  custo_de_inacao: "R${X} por {período} ou {consequência específica}"

desejo_mapping:
  tipo: [dinheiro | tempo | status | liberdade | segurança]
  o_que_ganham: "{específico e visual}"
  cenario_ideal: "{descreva o estado desejado}"

identidade_mapping:
  quem_querem_ser: "{identidade aspirada}"
  quem_nao_querem_ser: "{identidade que estão fugindo}"
```

### STEP 3: Offer Evaluation (Hormozi)

Value Equation assessment:
```
Dream Outcome: {específico} — Força: Fraco/Médio/Forte
Perceived Likelihood: {como está suportada} — Força: Fraco/Médio/Forte
Time Delay: {quando veem primeiro resultado} — Força: Fraco/Médio/Forte
Effort & Sacrifice: {quanto é exigido} — Força: Fraco/Médio/Forte

PONTOS FRACOS: {o que precisa fortalecer}
RECOMENDAÇÕES: {o que adicionar à oferta}
```

### STEP 4: Proof Framework (Hopkins)

```
Claims de alto risco identificados:
1. {claim} — Prova disponível: {prova} — Força: {1-4}
2. {claim} — Prova disponível: {prova} — Força: {1-4}

Claims preemptivos disponíveis:
1. {o que fazem que concorrentes não dizem}
2. {idem}

Reason-why para benefícios principais:
"{benefício} porque {razão}. Isso significa {implicação concreta}."
```

### STEP 5: Strategy Consolidation

Output final em copy-strategy.md:

```markdown
# Copy Strategy — {produto} — {data}

## Ângulo Principal
{ângulo escolhido}
Justificativa: {por que esse ângulo para esse awareness level e ICP}
Driver dominante: {medo | desejo | identidade}

## Top 3 Ângulos Candidatos
### Ângulo 1 — {nome} [SELECIONADO]
...
### Ângulo 2 — {nome}
...
### Ângulo 3 — {nome}
...

## ICP para esse Ângulo
{descrição específica — quem vai se conectar mais com esse ângulo}

## Drivers Emocionais
Primário: {driver + o que especificamente}
Secundário: {driver + o que especificamente}

## Oferta (se aplicável)
Dream Outcome: {específico}
Perceived Likelihood: {como suportamos}
Quick Win: {primeiro resultado em Xh/dias}
Effort: {como minimizamos}
Garantia: {tipo e condições}

## Framework de Prova
Claims principais: {lista}
Prova disponível: {o que temos}
Preemptive claims: {oportunidade}

## Urgência
Tipo: {deadline | scarcity | custo de inação}
Razão lógica: {o que justifica}
Copy de urgência: {texto}

## Estrutura Recomendada para {formato}
{esboço da estrutura com ângulo aplicado}
```

---

## Quality Gate: QG-002

```yaml
mandatory:
  - "Ângulo principal selecionado com justificativa"
  - "Driver emocional dominante identificado"
  - "Oferta avaliada (mesmo se não for fortalecer agora)"
  - "Framework de prova definido"
  - "copy-strategy.md gerado"

quality:
  - "Top 3 ângulos com copy de abertura para cada"
  - "Custo de inação calculado"
  - "Preemptive claims identificados"
  - "Quick win definido"

pass_criteria:
  mandatory: "100%"
  quality: "75%+"
```

---

## Handoff

```yaml
on_complete:
  pass_to: copy-chief
  deliver: "output/copy/{project-slug}/copy-strategy.md"
  context: "Estratégia completa. Ângulo: {ângulo}. Driver: {driver}. Pronto para Tier 2."
  next_gate: "QG-002 passed"
```
