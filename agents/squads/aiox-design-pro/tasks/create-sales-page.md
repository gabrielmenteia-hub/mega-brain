# Task: Create Sales Page

**Task ID:** create-sales-page
**Execution Type:** Agent
**Purpose:** Criar sales page completa e especializada para venda de infoproduto especifico
**Executor:** Agent (infoproduct-specialist + conversion-copywriter)
**Model:** Opus

---

## Inputs

| Parametro | Tipo | Obrigatorio | Descricao |
|-----------|------|-------------|-----------|
| `tipo_produto` | enum | Sim | curso, ebook, mentoria, membership, vsl |
| `produto` | string | Sim | Nome, descricao, o que entrega |
| `ticket` | string | Sim | Preco e modalidade (unico, mensal, parcelado) |
| `modulos_bonus` | list | Para cursos | Lista de modulos e bonus com valores |
| `historia_criador` | string | Recomendado | Historia de onde vinha para onde chegou |
| `depoimentos` | list | Recomendado | Depoimentos com nome, foto e resultado |
| `urgencia` | string | Nao | Escassez ou prazo real se existir |

---

## Preconditions

- [ ] Tipo de infoproduto definido
- [ ] Ticket definido
- [ ] Pelo menos descricao basica do produto

---

## Steps

### STEP 1: Selecao do Modelo de Sales Page

```yaml
selecao_modelo:
  IF ticket <= 97:
    modelo: "short-form"
    caracteristicas:
      - "Pagina media (400-700px scroll)"
      - "Copy direto, sem historia longa"
      - "CTA imediato"
      - "Garantia de 7-15 dias"

  IF ticket 97-997 AND tipo == "curso":
    modelo: "long-form"
    caracteristicas:
      - "Pagina longa com VSL opcional"
      - "Historia do criador"
      - "Modulos detalhados com resultado"
      - "Pilha de valor com bonus"
      - "10+ depoimentos"
      - "Garantia de 30 dias"

  IF ticket > 997 OR tipo == "mentoria":
    modelo: "premium-qualificacao"
    caracteristicas:
      - "Foco em autoridade e resultado"
      - "Cases documentados"
      - "CTA de aplicacao, nao compra direta"
      - "Pagina media (qualidade > quantidade)"

  IF tipo == "vsl":
    modelo: "vsl-page"
    caracteristicas:
      - "Video em destaque acima da dobra"
      - "Minimalismo ao redor do player"
      - "CTA aparece apos percentual do video"
      - "Fallback textual para quem nao assiste"
```

---

### STEP 2: Estrutura Especifica da Sales Page

**Modelo Long-Form (Curso Online):**

```
HERO / VSL
└── Headline orientada a resultado
└── Subheadline com social proof numerico
└── Video (se VSL) ou imagem hero
└── CTA primario

PROVA SOCIAL RAPIDA
└── Numero de alunos / clientes
└── Rating / estrelas se disponivel
└── Logos de midia / parceiros

PROBLEMA / AGITACAO
└── Descricao empatica da dor
└── Consequencias de nao resolver
└── Transicao para a solucao

HISTORIA DO CRIADOR
└── Onde estava (situacao relatable)
└── O que descobriu
└── O que aconteceu
└── Por que decidiu ensinar

APRESENTACAO DO PRODUTO
└── Nome + o que e
└── Para quem e (e para quem nao e)
└── O que voce vai conseguir

MODULOS (para cursos)
└── Lista de modulos com resultado especifico
└── Numero de aulas / horas de conteudo
└── Formato (video, PDF, audio)
└── Bonus com valor separado

DEPOIMENTOS (8-12)
└── Foto + nome + cidade
└── Resultado especifico em destaque
└── Citacao autentica

PILHA DE VALOR
└── O que esta incluido + valor unitario
└── Total calculado (valor real)
└── Preco de oferta com comparacao

GARANTIA
└── Prazo e tipo
└── Como solicitar (simples e claro)
└── Visual de confianca

CTA FINAL
└── Botao principal com verbo de acao
└── Microcopy de reducao de risco
└── Urgencia real se existir

FAQ
└── 6-8 perguntas reais do comprador
└── Respostas diretas e honestas
```

---

### STEP 3: Copy da Sales Page

**Executor:** Agent (conversion-copywriter)

```yaml
copy_elements:
  headline:
    formula: "[Resultado especifico] para [Publico] em [Tempo] sem [Objecao]"
    alternativas: 5

  historia_criador:
    estrutura:
      - "Onde eu estava: [situacao de dor relatable]"
      - "O que eu tentei: [alternativas que nao funcionaram]"
      - "O que eu descobri: [insight/mecanismo unico]"
      - "O que aconteceu: [resultado especifico]"
      - "Por que compartilho: [missao genuina]"
    tom: "vulneravel e autentico, nao heroico"

  pilha_de_valor:
    template: |
      Quando voce entra hoje, voce recebe:
      ✓ [Item 1] — Valor: R$[XX]
      ✓ [Item 2] — Valor: R$[XX]
      ✓ [Bonus 1] — Valor: R$[XX]
      Total: R$[SOMA]
      Hoje por apenas: R$[PRECO REAL]

  garantia:
    elementos:
      - "Prazo claro: [X dias]"
      - "Como solicitar: [instrucao simples]"
      - "Tom de confianca, nao de ansiedade"
```

---

### STEP 4: Elementos de Urgencia (se aplicavel)

```yaml
urgencia_valida:
  tipos:
    lancamento:
      - "Carrinho abre em [data] e fecha em [data+X]"
      - "Contador regressivo real"
      - "Preco sobe apos encerramento"

    vagas_limitadas:
      - "Mentoria: apenas [N] vagas por turma"
      - "Numero real e justificado"

    bonus_com_prazo:
      - "Bonus X disponivel apenas para as primeiras [N] inscricoes"
      - "Ou bonus disponivel ate [data especifica]"

  urgencia_invalida:
    - "Contador que reinicia — NAO USAR"
    - "Vagas limitadas sem numero — NAO USAR"
    - "Oferta 'so hoje' que e permanente — NAO USAR"
```

---

## Outputs

| Output | Formato | Descricao |
|--------|---------|-----------|
| Modelo Selecionado | YAML | Tipo de sales page e justificativa |
| Estrutura Completa | MD | Todas as secoes com elementos |
| Copy Completo | MD | Copy escrito secao por secao |
| Pilha de Valor | MD | Tabela de valor calculada |
| Checklist Final | MD | Todos os itens validados |

---

## Acceptance Criteria

- [ ] Modelo de sales page correto para o ticket e tipo
- [ ] Todas as secoes essenciais presentes
- [ ] Headline com resultado especifico
- [ ] Historia do criador (se long-form)
- [ ] Pilha de valor calculada (se curso/produto com bonus)
- [ ] Depoimentos estruturados (foto + nome + resultado)
- [ ] Garantia clara e proeminente
- [ ] CTA em pelo menos 3 pontos da pagina
- [ ] FAQ respondendo top 5 objecoes
- [ ] Urgencia genuina ou ausente (nunca falsa)

---

## Validation

```yaml
checklist_final:
  estrutura:
    - "Hero comunica proposta em 5 segundos"
    - "Prova social acima do preco"
    - "Garantia visivel e clara"

  copy:
    - "Headline orienta para resultado, nao tema"
    - "Copy em linguagem do comprador"
    - "Objecoes principais respondidas"

  conversao:
    - "CTA em multiplos pontos"
    - "Urgencia genuina ou ausente"
    - "Sem claims sem prova"
```

---

_Task Version: 1.0_
_Lines: 300+_
