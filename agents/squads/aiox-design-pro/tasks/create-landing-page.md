# Task: Create Landing Page

**Task ID:** create-landing-page
**Execution Type:** Hybrid
**Purpose:** Criar landing page completa para infoproduto, do brief ao wireframe textual com copy e diretivas visuais
**Executor:** Agent (com revisao humana nos checkpoints)
**Model:** Opus

---

## Inputs

| Parametro | Tipo | Obrigatorio | Descricao |
|-----------|------|-------------|-----------|
| `produto` | string | Sim | Nome e descricao do produto |
| `publico` | string | Sim | Perfil do comprador ideal |
| `preco` | string | Sim | Preco e modelo de venda |
| `objetivo` | string | Sim | Meta de conversao (venda, lead, inscricao) |
| `provas` | list | Recomendado | Depoimentos, resultados, certificacoes disponíveis |
| `tipo_produto` | enum | Sim | curso, ebook, mentoria, membership, workshop |
| `tom` | enum | Nao | premium, acessivel, urgente, educativo |

---

## Preconditions

- [ ] Brief de produto preenchido com pelo menos: produto, publico, preco, objetivo
- [ ] Tipo de infoproduto definido
- [ ] Provas sociais mapeadas (mesmo que indisponiveis ainda)

---

## Steps

### STEP 1: Diagnostico de Conversao

**Executor:** Agent (conversion-diagnostician)

```yaml
acoes:
  - Identificar o estado atual do comprador (antes do produto)
  - Identificar o estado desejado (apos o produto)
  - Mapear top 3 objecoes
  - Definir promessa principal em formato "De X para Y em Z"
  - Identificar linguagem organica do comprador

output:
  persona_card:
    estado_atual: string
    estado_desejado: string
    top_objecoes: list[3]
    promessa_principal: string
    linguagem_chave: list[5]
```

**Checkpoint DP-QG-001:** Brief Completo — persona, promessa e objecoes definidos.

---

### STEP 2: Arquitetura de Informacao

**Executor:** Agent (ux-architect)

```yaml
acoes:
  - Selecionar secoes necessarias baseado no tipo de produto e nivel de consciencia
  - Ordenar secoes pela jornada emocional
  - Definir elementos de cada secao
  - Posicionar CTAs estrategicos

output:
  wireframe_textual:
    secoes:
      - nome: string
        posicao: int
        elementos: list
        cta_aqui: bool
        justificativa: string
```

**Secoes padrao por tipo:**

| Tipo | Secoes Essenciais |
|------|-------------------|
| Curso online | Hero, Prova rapida, Problema, Historia, Modulos, Prova social, Oferta, Garantia, CTA, FAQ |
| Ebook | Hero, Bullets de beneficio, Amostra de conteudo, Depoimentos, CTA |
| Mentoria | Hero, Autoridade, Cases, Metodologia, Aplicacao, Qualificacao |
| Workshop | Hero, O que vai aprender, Para quem e, Sobre o facilitador, Cronograma, CTA |

**Checkpoint DP-QG-002:** Estrutura Aprovada — secoes ordenadas com justificativa emocional.

---

### STEP 3: Copy da Landing Page

**Executor:** Agent (conversion-copywriter)

```yaml
acoes:
  - Escrever headline principal (5+ opcoes, selecionar melhor)
  - Escrever copy de cada secao seguindo a estrutura aprovada
  - Criar bullets de beneficio em formato de alta conversao
  - Escrever CTAs (primario + secundarios)
  - Redigir FAQ respondendo as top objecoes

output:
  copy_completo:
    headline_principal: string
    headline_alternativas: list[4]
    copy_por_secao:
      - secao: string
        copy: string
    cta_principal: string
    cta_alternativas: list[2]
    faq: list[5-8 perguntas com respostas]
```

---

### STEP 4: Diretivas Visuais

**Executor:** Agent (visual-designer)

```yaml
acoes:
  - Definir paleta de cores estrategica (6 cores com HEX e uso)
  - Definir sistema tipografico (heading + body + CTA)
  - Especificar hierarquia visual por secao
  - Definir tratamento de imagens e mockups

output:
  design_system:
    paleta:
      primaria: {hex: string, uso: string}
      secundaria: {hex: string, uso: string}
      cta: {hex: string, uso: string}
      background: {hex: string, uso: string}
      alternado: {hex: string, uso: string}
      texto: {hex: string, uso: string}
    tipografia:
      heading: {font: string, tamanho_desktop: string, tamanho_mobile: string, peso: string}
      body: {font: string, tamanho: string, line_height: string}
      cta: {font: string, tamanho: string, peso: string}
    imagens:
      hero: string  # descricao do tipo de imagem ideal
      depoimentos: string
      produto: string
```

---

### STEP 5: Especializacao por Tipo de Infoproduto

**Executor:** Agent (infoproduct-specialist)

```yaml
acoes:
  - Validar se todos os elementos especificos do tipo de produto estao presentes
  - Adicionar elementos ausentes (VSL, pilha de valor, etc.)
  - Definir urgencia/escassez se aplicavel
  - Especificar modelo de checkout

output:
  especializacoes:
    elementos_adicionados: list
    pilha_de_valor: list[{item: string, valor_unit: string}]
    urgencia_escassez: string | null
    modelo_checkout: string
```

**Checkpoint DP-QG-003:** Checklist de Conversao — todos os elementos criticos presentes.

---

### STEP 6: Validacao Mobile

**Executor:** Agent (mobile-optimizer)

```yaml
acoes:
  - Revisar estrutura para problemas de mobile
  - Definir breakpoints e adaptacoes
  - Especificar requisitos de performance (LCP target)
  - Identificar elementos que precisam de adaptacao mobile

output:
  mobile_spec:
    breakpoints: {mobile: string, tablet: string, desktop: string}
    adaptacoes_por_secao: list
    lcp_target: string
    alertas: list
```

---

## Outputs

| Output | Formato | Descricao |
|--------|---------|-----------|
| Persona Card | YAML | Perfil completo do comprador |
| Wireframe Textual | MD | Estrutura de secoes com elementos |
| Copy Completo | MD | Headline, copy por secao, CTAs, FAQ |
| Design System | YAML | Paleta, tipografia, hierarquia visual |
| Mobile Spec | MD | Adaptacoes e requisitos mobile |
| Checklist de Entrega | MD | Todos os itens validados |

---

## Acceptance Criteria

- [ ] Persona card com estado atual, desejado, objecoes e linguagem
- [ ] Wireframe com todas as secoes ordenadas pela jornada emocional
- [ ] Headline principal + 4 alternativas
- [ ] Copy completo para cada secao
- [ ] CTAs em formato de alta conversao com microcopy
- [ ] FAQ respondendo top 5 objecoes
- [ ] Design system com paleta completa (6 usos) e tipografia
- [ ] Elementos especificos do tipo de infoproduto presentes
- [ ] Especificacoes mobile definidas
- [ ] Checklist de conversao passando

---

## Validation

Antes da entrega final, validar:

1. **Teste dos 5 segundos:** Alguem do publico-alvo consegue entender a proposta em 5 segundos?
2. **Teste de objecoes:** As top 3 objecoes estao respondidas na pagina?
3. **Teste mobile:** A estrutura funciona em coluna unica no mobile?
4. **Teste de copy:** O copy usa linguagem do comprador ou do vendedor?
5. **Teste de CTA:** O CTA continua a conversa ou encerra bruscamente?

---

_Task Version: 1.0_
_Lines: 500+_
