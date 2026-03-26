# Task: Analyze Brief

**Task ID:** analyze-brief
**Execution Type:** Agent
**Purpose:** Analisar produto e publico para gerar brief completo de conversao
**Executor:** Agent (conversion-diagnostician)
**Model:** Opus

---

## Inputs

| Parametro | Tipo | Obrigatorio | Descricao |
|-----------|------|-------------|-----------|
| `produto` | string | Sim | Descricao do produto |
| `publico_inicial` | string | Nao | Percepcao inicial do publico |
| `objecoes_conhecidas` | list | Nao | Objecoes que o criador ja conhece |
| `provas_disponiveis` | list | Nao | Depoimentos, resultados, dados disponíveis |

---

## Steps

### STEP 1: Perguntas de Diagnostico (7 Dimensoes)

Coletar informacoes nas 7 dimensoes criticas:

```yaml
dimensoes:
  1_produto:
    perguntas:
      - "O que e o produto exatamente? (nome, formato, duracao)"
      - "Quais sao os entregaveis especificos?"
      - "Qual e o diferencial vs alternativas no mercado?"

  2_promessa:
    perguntas:
      - "Qual e a transformacao que o comprador vai vivenciar?"
      - "Em quanto tempo ele consegue o resultado principal?"
      - "Qual e o resultado mais especifico que voce pode prometer?"

  3_publico:
    perguntas:
      - "Descreva 3 clientes ideais reais (sem nome)"
      - "Qual e a ocupacao/situacao de vida do comprador ideal?"
      - "Ele e iniciante ou tem algum nivel de experiencia?"

  4_dores:
    perguntas:
      - "Qual e a maior frustracao do comprador antes do produto?"
      - "Quais consequencias ele sofre por nao ter esse conhecimento/habilidade?"
      - "O que ele ja tentou que nao funcionou?"

  5_objecoes:
    perguntas:
      - "Por que alguem do publico ideal NAO compraria?"
      - "Qual e o maior medo relacionado a essa compra?"
      - "Qual e a crenca limitante mais comum no publico?"

  6_prova:
    perguntas:
      - "Quais resultados de clientes voce pode documentar?"
      - "Voce tem depoimentos com foto e nome?"
      - "Voce tem dados numericos (X alunos, Y% de resultado)?"

  7_contexto:
    perguntas:
      - "Qual e o preco e como ele e comparado as alternativas?"
      - "E lancamento ou evergreen?"
      - "Existe urgencia ou escassez real?"
```

---

### STEP 2: Gerar Persona Card

```yaml
persona_card:
  nome_ficticio: "Maria, 34 anos"  # demografico representativo
  perfil_demografico:
    idade: "faixa etaria"
    genero: "genero predominante"
    localizacao: "regiao ou contexto"
    ocupacao: "cargo ou situacao"

  situacao_atual: |
    [Estado de dor antes do produto — especifico, empatico]

  situacao_desejada: |
    [Estado de transformacao desejada — especifico, inspirador]

  principais_barreiras:
    - "Barreira 1"
    - "Barreira 2"
    - "Barreira 3"

  objecoes_compra:
    - objecao: "Objecao 1"
      nivel_de_risco: "alto | medio | baixo"
    - objecao: "Objecao 2"
      nivel_de_risco: "alto | medio | baixo"
    - objecao: "Objecao 3"
      nivel_de_risco: "alto | medio | baixo"

  linguagem_organica:
    expressoes_usam:
      - "Como eles descrevem o problema"
      - "Como eles descrevem o resultado desejado"
    expressoes_evitar:
      - "Jargoes tecnicos que eles nao usam"
```

---

### STEP 3: Gerar Brief de Conversao

```yaml
brief_conversao:
  produto:
    nome: string
    formato: string
    entregaveis: list
    diferencial: string

  promessa_principal:
    formato: "De [estado atual] para [estado desejado] em [tempo] sem [objecao principal]"
    especifica: bool  # deve ser especifica o suficiente para ser crivel

  publico_ideal:
    inclui: list  # quem e o comprador certo
    exclui: list  # quem NAO se beneficiaria

  principais_objecoes:
    - objecao: string
      resposta_prevista: string

  inventario_de_provas:
    disponiveis:
      - tipo: "depoimento | dado | certificado | midia"
        descricao: string
    ausentes:
      - tipo: string
        estrategia: string  # como compensar a falta

  contexto_de_compra:
    preco: string
    modelo_venda: "lancamento | evergreen | assinatura"
    urgencia_real: string | null
    alternativas_mercado: list
```

---

### STEP 4: Recomendacoes Estrategicas

```yaml
recomendacoes:
  estrategia_de_pagina:
    tipo_recomendado: "short-form | long-form | vsl | premium"
    justificativa: string

  elementos_criticos:
    - elemento: string
      prioridade: "alta | media | baixa"
      razao: string

  gaps_de_prova:
    - gap: string
      impacto: string
      solucao: string

  proximos_passos:
    - "Acionar ux-architect com este brief para estrutura de pagina"
    - "Acionar conversion-copywriter com persona e objecoes"
    - "Coletar provas ausentes identificadas"
```

---

## Outputs

| Output | Formato | Descricao |
|--------|---------|-----------|
| Persona Card | YAML | Perfil completo do comprador |
| Brief de Conversao | YAML | Produto, promessa, publico, objecoes |
| Inventario de Provas | MD | O que tem e o que falta |
| Recomendacoes | MD | Estrategia de pagina e proximos passos |

---

## Acceptance Criteria

- [ ] Persona com estado atual e desejado especificos
- [ ] Promessa principal em formato "De X para Y"
- [ ] Minimo 3 objecoes identificadas com nivel de risco
- [ ] Inventario de provas (disponiveis e ausentes)
- [ ] Recomendacao de tipo de pagina justificada
- [ ] Linguagem organica do comprador documentada

---

_Task Version: 1.0_
_Lines: 300+_
