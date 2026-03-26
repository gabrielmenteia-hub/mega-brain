# Task: Analyze Market

**Task ID:** analyze-market
**Version:** 1.0.0
**Purpose:** Mapear inteligência de mercado antes de qualquer copy: awareness level, ICP, desejo central, USP, objeções
**Agent:** eugene-schwartz + david-ogilvy
**Command:** `*awareness {produto/mercado}`
**Execution Type:** Agent
**Output:** `output/copy/{project-slug}/market-brief.md`

---

## Task Anatomy

```yaml
task_name: analyze-market
status: active
responsible_executor: eugene-schwartz (lead) + david-ogilvy (research)
execution_type: agent
input:
  required:
    - produto: "O que está sendo vendido"
    - formato: "Qual copy vai ser produzida"
  optional:
    - publico: "Descrição do público-alvo (se disponível)"
    - concorrentes: "Exemplos de copy de concorrentes"
    - dados_clientes: "Depoimentos, objeções reais, resultados"
    - restricoes: "Tom, compliance, palavras proibidas"
output:
  market_brief:
    file: "output/copy/{project-slug}/market-brief.md"
    sections:
      - "Awareness Level (1-5 Schwartz)"
      - "Sofisticação do Mercado (1-5)"
      - "ICP (Ideal Customer Profile)"
      - "Desejo Central / Mass Desire"
      - "Top 5 Objeções"
      - "USP / Unique Mechanism"
      - "Claims disponíveis e força de prova"
      - "Ângulos candidatos"
action_items:
  - "STEP 1 (@eugene-schwartz): Diagnosticar awareness level (1-5)"
  - "STEP 2 (@eugene-schwartz): Identificar desejo de massa e força dominante"
  - "STEP 3 (@eugene-schwartz): Avaliar sofisticação do mercado"
  - "STEP 4 (@david-ogilvy): Protocolo de pesquisa de produto"
  - "STEP 5 (@david-ogilvy): Identificar USP ou oportunidade de USP"
  - "STEP 6 (@david-ogilvy): Mapear claims disponíveis por força de prova"
  - "STEP 7 (integrado): Consolidar em market-brief.md"
acceptance_criteria:
  - "Awareness level diagnosticado com justificativa (não assumido)"
  - "ICP definido com demographics + psychographics"
  - "Desejo central articulado em linguagem do prospect (não do vendedor)"
  - "Mínimo 5 objeções mapeadas"
  - "USP identificado ou oportunidade clara apontada"
  - "Market brief gerado em output/copy/{project-slug}/market-brief.md"
```

---

## Execution Protocol

### STEP 1: Awareness Level Diagnosis (Schwartz)

**Referência:** `squads/copywriting/data/awareness-levels.yaml`

Perguntas de diagnóstico:
1. O prospect sabe que TEM O PROBLEMA/DESEJO? → Stage 1 se não
2. O prospect sabe que EXISTEM SOLUÇÕES? → Stage 2 se sim para 1, não para 2
3. O prospect sabe que PRODUTOS COMO O SEU existem? → Stage 3 se sim para 1+2
4. O prospect já conhece SEU PRODUTO ESPECÍFICO? → Stage 4 se sim
5. O prospect está pronto para comprar AGORA? → Stage 5

**Output:**
```
AWARENESS LEVEL: Stage {N} — {nome}
Justificativa: {por que esse nível}
Headline approach: {como calibrar headline para esse nível}
```

### STEP 2: Mass Desire Mapping (Schwartz)

Identificar:
- **Desejo de massa subjacente:** qual dos arquétipos (dinheiro, saúde, amor, status, liberdade, segurança)?
- **Força dominante:** o que a copy deve prometer primeiro?
- **Intensidade:** é desejo (quer ter) ou necessidade (precisa ter)?
- **Urgência:** é constante ou situacional?

### STEP 3: Market Sophistication (Schwartz)

Avaliar nível 1-5 baseado em:
- Quantas alternativas o prospect já conhece?
- Qual tipo de claim ainda funciona? (direto / maior / mecanismo / identidade / experiência)
- O que concorrentes estão prometendo?

### STEP 4: Product Research Protocol (Ogilvy)

Investigar:
1. **Fatos únicos:** O que é mais interessante/surpreendente sobre o produto?
2. **Resultados reais:** Que resultados específicos clientes já tiveram?
3. **Processo:** Qual etapa do processo/fabricação impressionaria o cliente?
4. **Claims disponíveis:** Liste todos os claims com nível de prova (1-4)
5. **Gap competitivo:** O que nenhum concorrente está dizendo?

### STEP 5: USP Identification (Ogilvy/Reeves)

Matriz:
```
Característica → Benefício → É Único? → É Importante para o ICP?
[listar todas as características]
Intersecção de ÚNICO + IMPORTANTE = USP
```

Se não há USP genuíno:
- Oportunidade de claim preemptivo (Hopkins)
- Oportunidade de posicionamento por nicho (Kennedy)
- Oportunidade de mecanismo nomeado (Schwartz Stage 3)

### STEP 6: Objection Mapping

Top 5 objeções prováveis baseadas em:
- Awareness level (ceticismo aumenta com sofisticação)
- Preço / ROI
- Tempo / Esforço
- Credibilidade ("por que você?")
- "Já tentei algo assim antes"
- "Não é pra mim" (fit)

### STEP 7: Consolidate Market Brief

```markdown
# Market Brief — {produto} — {data}

## Awareness Level
Stage {N}: {nome}
Justificativa: {texto}
Abordagem de headline: {texto}

## Sofisticação do Mercado
Nível {N}: {descrição}
Tipo de claim que funciona: {texto}

## ICP (Ideal Customer Profile)
### Demographics
- Cargo/situação: {texto}
- Faixa de resultado/renda: {texto}
- Contexto: {texto}

### Psychographics
- Maior frustração: {texto}
- Maior desejo: {texto}
- Crença limitante: {texto}
- Identidade aspirada: {texto}

### Behavioral
- Já tentou: {texto}
- Busca informação em: {texto}

## Desejo Central
{desejo_de_massa}: {força dominante}
Linguagem do prospect: "{como eles descrevem o problema/desejo}"

## USP / Mecanismo Único
{USP_identificado_ou_oportunidade}

## Claims Disponíveis
| Claim | Prova | Força (1-4) |
|-------|-------|-------------|
| {claim} | {prova} | {força} |

## Top 5 Objeções
1. {objeção} — Resposta recomendada: {texto}
2. {objeção} — Resposta recomendada: {texto}
3. {objeção} — Resposta recomendada: {texto}
4. {objeção} — Resposta recomendada: {texto}
5. {objeção} — Resposta recomendada: {texto}

## Ângulos Candidatos
1. {ângulo} — Driver: {medo/desejo/identidade}
2. {ângulo} — Driver: {medo/desejo/identidade}
3. {ângulo} — Driver: {medo/desejo/identidade}
```

---

## Quality Gate: QG-001

**BLOCKING.** Deve passar antes de avançar para Tier 1 (Estratégia).

```yaml
mandatory:
  - "Awareness level diagnosticado com justificativa"
  - "ICP definido com demographics + psychographics"
  - "Desejo central em linguagem do prospect"
  - "Mínimo 5 objeções mapeadas"
  - "USP ou oportunidade apontada"
  - "market-brief.md gerado"

quality:
  - "Awareness level justificado (não assumido)"
  - "ICP específico o suficiente para escrever copy para uma pessoa"
  - "Claims classificados por força de prova"
  - "Pelo menos 3 ângulos candidatos identificados"

pass_criteria:
  mandatory: "100%"
  quality: "75%+"

on_fail:
  - "Coletar informação faltante com usuário"
  - "Pesquisar concorrentes se necessário"
  - "Não avançar para Tier 1 sem QG-001"
```

---

## Anti-Patterns

```yaml
never_do:
  - "Assumir awareness level sem diagnóstico"
  - "Definir ICP como 'empreendedores' ou 'pessoas que querem X'"
  - "Pular mapeamento de objeções"
  - "Avançar sem market brief consolidado"
  - "Usar jargão do vendedor na linguagem do prospect"

always_do:
  - "Diagnosticar awareness com justificativa específica"
  - "Definir ICP com nome e situação específica imaginável"
  - "Mapear desejo na linguagem EXATA do prospect"
  - "Classificar claims por força de prova (não apenas listar)"
```

---

## Handoff

```yaml
on_complete:
  pass_to: copy-chief
  deliver: "output/copy/{project-slug}/market-brief.md"
  context: "Market intelligence completa. Stage {N}, ICP: {resumo}, USP: {resumo}. Pronto para Tier 1."
  next_gate: "QG-001 passed"
```
