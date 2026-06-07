---
name: FURION-INFOPRODUTO
description: "Orquestra criação de infoprodutos via Furion em dois modos: Workflow completo (Do Zero Ao Primeiro Produto) ou Gerador standalone. JARVIS prepara todos os inputs com DNA do MEGABRAIN. Usuário só alimenta o Furion e traz outputs."
---

> **Auto-Trigger:** Quando usuário mencionar Furion, infoproduto, lançamento, oferta, gerador
> **Keywords:** "furion", "infoproduto", "lançamento", "oferta", "avatar", "vsl", "upsell", "página de vendas", "anúncio", "email", "instagram", "youtube", "gerador"
> **Prioridade:** ALTA

---

# FURION-INFOPRODUTO — Protocolo de Orquestração

## Conceito

JARVIS age como **estrategista e prompt engineer**. Furion age como **executor de geração**.
O usuário faz apenas a **ponte manual** entre os dois sistemas.

**Por que isso economiza créditos no Furion:**
- Furion não precisa "pensar" — recebe inputs já estruturados e ricos
- Sem iterações de refinamento (JARVIS já entrega preciso na primeira vez)
- MEGABRAIN injeta inteligência dos especialistas, eliminando output genérico

---

## Especialistas do MEGABRAIN Consultados

| Especialista | DNA Aplicado |
|---|---|
| **Eugene Schwartz** | Níveis de consciência, headline, mecanismo único |
| **Russell Brunson** | Funil, oferta, stack de valor, história de origem |
| **Dan Kennedy** | Avatar ultra-preciso, dor + desejo, direct response |
| **Donald Miller** | StoryBrand, o herói e o guia, clareza de mensagem |
| **Joseph Sugarman** | Slippery slope copy, objeções, curiosidade |
| **Robert Cialdini** | Prova social, escassez, autoridade |
| **Alan Nicolas** | Contexto Brasil, infoprodutos digitais, IA |
| **Tiago Brendon (MoneyClub)** | Prompts parametrizáveis, engenharia reversa, avatar 40+ dimensões |

---

## Pipeline Furion — Mapa Completo

```
[INPUT: Ideia de produto]
         │
         ▼
  ┌──────────────────────────────┐
  │  Avatar Destroyer            │  ← Furion gera AVATAR
  │  Desbravador De Mentes       │
  └──────────────┬───────────────┘
                 │ AVATAR
                 ▼
  ┌──────────────────────────────┐
  │  Gerador Devastador          │  ← Furion gera OFERTA
  │  de Ofertas                  │
  └──────────────┬───────────────┘
                 │ AVATAR + OFERTA
                 ▼
  ┌──────────────────────────────┐
  │  Proposta Única De Vendas    │  ← Furion gera USP
  │  Beast Mode                  │
  └──────────────┬───────────────┘
                 │ AVATAR + OFERTA + USP
                 ▼
  ┌──────────────────────────────┐
  │  Gerador De Info-Produto     │  ← Furion gera ESTRUTURA
  │  Automático                  │
  └──────────────┬───────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
  [OFERTA+AVATAR]   [OFERTA+USP]
   PV Obliteradora   Anúncios Dominadores
   Upsell+Order Bump VSL 60min
        │
        ▼ [UPSELL gerado]
   Página Upsell
   VSL Upsell 15min
```

---

## Execução — Passo a Passo

### FASE 0: Inicialização

Quando usuário chamar `/furion-infoproduto [ideia]`:

1. Ler DNAs relevantes de `knowledge/dna/persons/`
2. Consultar insights de `knowledge/dossiers/persons/` (especialistas de copy e funil)
3. Gerar o **PACOTE DE INPUTS** para o Furion

---

### FASE 1 — INPUT: Ideia de Produto

**Campo Furion:** `Digite aqui sua ideia de produto`

JARVIS gera um briefing compacto (máx. 150 palavras) contendo:
- Nicho + dor central (linguagem do avatar, não do produtor)
- Transformação prometida (antes → depois)
- Mecanismo único (o "porquê isso funciona")
- Nível de consciência do avatar (Schwartz: 1-5)
- 3 objeções principais

**Formato do output JARVIS:**
```
IDEIA: [nome provisório do produto]
NICHO: [segmento específico]
DOR: [dor visceral em palavras do avatar]
TRANSFORMAÇÃO: [estado atual] → [estado desejado]
MECANISMO: [o que torna único]
CONSCIÊNCIA: Nível [N] — [descrição]
OBJEÇÕES: 1) [objeção] 2) [objeção] 3) [objeção]
```

**Instrução para o usuário:** Cole no campo "Digite aqui sua ideia de produto" e clique Gerar. Quando o Avatar sair, cole aqui.

---

### FASE 2 — AVATAR gerado pelo Furion

Usuário traz o Avatar gerado. JARVIS:
1. Analisa o Avatar vs. DNA de Dan Kennedy (avatar ultra-preciso)
2. Enriquece com insights de Eugene Schwartz (linguagem emocional)
3. Gera o **Avatar Refinado** para usar nos próximos nós

**Formato para campos "Substitua pelo seu avatar":**
```
AVATAR: [nome fictício], [idade], [situação atual]
DESEJOS: [3 desejos principais]
MEDOS: [3 medos principais]
LINGUAGEM: [como fala, expressões que usa]
IDENTIDADE: [como se vê vs. como quer se ver]
```
(máx. 120 palavras — o Furion já tem o template, só precisa dos dados)

---

### FASE 3 — OFERTA gerada pelo Furion

Usuário traz a Oferta gerada. JARVIS:
1. Analisa vs. framework de Russell Brunson (stack de valor)
2. Verifica clareza vs. Donald Miller (StoryBrand)
3. Gera a **Oferta Refinada** para os próximos nós

**Formato para campos "Substitua pela sua oferta":**
```
OFERTA: [nome do produto]
PROMESSA: [resultado específico em X tempo]
STACK: [produto principal] + [bônus 1] + [bônus 2]
PREÇO: [âncora] → [preço real]
GARANTIA: [tipo e prazo]
```
(máx. 100 palavras)

---

### FASE 4 — USP gerada pelo Furion

Usuário traz a USP. JARVIS:
1. Valida vs. mecanismo único (Schwartz)
2. Testa clareza em 1 frase
3. Gera a **USP Compactada** para os nós de anúncios e VSL

**Formato para campos "Substitua pela sua USP":**
```
USP: [1 frase — o que é, para quem, resultado único]
DIFERENCIAL: [por que não é como os outros]
PROVA: [evidência ou mecanismo que sustenta]
```
(máx. 60 palavras)

---

### FASE 5 — UPSELL gerado pelo Furion

Usuário traz o Upsell. JARVIS:
1. Analisa complementaridade com a oferta principal
2. Verifica escassez/urgência (Cialdini)
3. Gera o **Upsell Compactado** para Página de Upsell e VSL 15min

**Formato para campos "Substitua pelo seu Upsell":**
```
UPSELL: [nome e descrição em 1 linha]
COMPLEMENTO: [por que faz sentido após o produto principal]
URGÊNCIA: [motivo legítimo para decidir agora]
PREÇO: [valor âncora] → [preço do upsell]
```
(máx. 80 palavras)

---

### FASE 6 — Coleta de Outputs Finais

Ao final do fluxo completo, o usuário traz todos os outputs gerados pelo Furion:
- Página de Vendas
- Upsell + Order Bump
- Sistema de Anúncios
- VSL 60min
- Página de Upsell
- VSL 15min

JARVIS então:
1. Salva cada output em `inbox/furion-outputs/[nome-produto]/`
2. Roda análise de qualidade vs. DNA dos especialistas
3. Gera **Relatório de Produto**: pontos fortes, gaps, sugestões de melhoria
4. Ingere no MEGABRAIN como novo conhecimento

---

---

---

## MODO 2: Geradores Standalone

Além do workflow completo, Furion tem geradores individuais por categoria.
JARVIS prepara o input para qualquer gerador sob demanda.

### Catálogo Completo de Geradores

#### PRODUTO
| Gerador | O que faz | Inputs JARVIS prepara |
|---|---|---|
| Avatar Destroyer – Desbravador De Mentes | Mapeia avatar completo desde medos primitivos | Ideia de produto |
| Gerador Devastador de Ofertas | Cria oferta com módulos tangíveis, bônus e stack | Avatar |
| Proposta Única De Vendas – Beast Mode | 6 componentes de psicologia de compra | Avatar + Oferta |
| Gerador De Info-Produto Automático | Estrutura módulos organizados de conteúdo | Avatar + Oferta + USP |
| Página De Upsell De Máxima Conversão | Página que destrói resistência a ofertas complementares | Upsell |
| Upsell + Order Bump Nuclear | Arsenal de 10 ofertas complementares | Avatar + Oferta |

#### COPYWRITING
| Gerador | O que faz | Inputs JARVIS prepara |
|---|---|---|
| Página De Vendas Obliteradora De Objeções | PV com PNL, gatilhos e frases pós-venda | Avatar + Oferta |
| (60-Min) Vídeo De Vendas Predador | VSL completa que "derrete o cartão de crédito" | Oferta + USP |
| (15-Min) Vídeo De Upsell Destroyer | VSL curta para momento pós-compra | Upsell |
| VSL Primeiro Upsell (5-7 min) | VSL curta de 1º upsell | Upsell |
| VSL Segundo Upsell (5-7 min) | VSL curta de 2º upsell | 2º Upsell |
| VSL Downsell (5-7 min) | VSL para quem recusou o upsell | Oferta alternativa |
| Copywriting Página de Obrigado | Texto completo da pág. de obrigado | Avatar + Oferta |
| Copywriting Página de Upsell | Texto completo da pág. de upsell | Upsell |
| Copywriting Página de Downsell | Texto completo da pág. de downsell | Oferta alternativa |

#### ESTRATÉGIA
| Gerador | O que faz | Inputs JARVIS prepara |
|---|---|---|
| Sistema De Anúncios Dominadores | 20+ variações de anúncio de alta conversão | Oferta + USP |

#### MÍDIA SOCIAL
| Gerador | O que faz | Inputs JARVIS prepara |
|---|---|---|
| LinkedIn com CTA | Posts de alta conversão para LinkedIn | Avatar + Oferta + Objetivo do post |
| LinkedIn Post sem CTA | Posts de valor/autoridade para LinkedIn | Avatar + Tema + Perspectiva do especialista |
| Tweets | Tweets virais | Avatar + Tema + Ângulo (polêmica, insight, provocação) |

#### YOUTUBE
| Gerador | O que faz | Inputs JARVIS prepara |
|---|---|---|
| Títulos Virais para YouTube | Títulos virais para vídeo | Avatar + Tema + Nível de consciência |
| Roteiro para YouTube | Roteiro viral completo | Avatar + Tema + CTA + Gancho de abertura |

#### E-MAILS
| Gerador | O que faz | Inputs JARVIS prepara |
|---|---|---|
| E-mail com CTA | E-mail de alta conversão com chamada para ação | Avatar + Oferta + Objetivo (venda/webinar/etc.) |
| E-mail longo sem CTA | E-mail longo e persuasivo (nurturing) | Avatar + Tema + História ou insight |
| E-mail curto sem CTA | E-mail curto e persuasivo (nurturing) | Avatar + Tema + Gancho |
| Headline de E-mails | Headlines de alta conversão (subject lines) | Avatar + Contexto + Nível de urgência |

#### INSTAGRAM (JARVIS gera direto — sem gerador no Furion)
| Formato | O que JARVIS entrega |
|---|---|
| Carrossel de valor | Roteiro completo (título + slides + CTA) baseado no DNA dos especialistas |
| Reels / Stories | Script com hook, desenvolvimento e CTA |
| Post de feed (copy) | Legenda completa com storytelling e hashtags |
| Bio otimizada | Bio de perfil focada em conversão |

---

#### MONEYCLUB PROMPTS (Prompt Templates Prontos — usar diretamente no ChatGPT/Claude)
> **Fonte:** Tiago Brendon / MoneyClub (TB014) — Prompts Exclusivos
> **Como usar:** JARVIS prepara o DATA, você cola o prompt + DATA no ChatGPT ou Claude e gera direto.
> **Templates:** `prompts/` nesta pasta

| Prompt | O que faz | Arquivo | Input necessário |
|---|---|---|---|
| **Prompt Parasita** | Engenharia reversa de qualquer material de vendas em 10 dimensões | `prompts/01-prompt-parasita.md` | Material de vendas (página/vídeo/script) |
| **Extração de Avatar (40+ dim.)** | Mapeia avatar em 90+ campos psicológicos — do consciente ao inconsciente | `prompts/02-extracao-avatar.md` | Nome/descrição do produto |
| **Oferta + Upsell + Order Bump** | Gera 10 nomes de oferta, preços, garantia, 3 bônus, testemunhos, módulos + 5 OB + 5 upsells | `prompts/03-oferta.md` | Avatar gerado |
| **USP + Mecanismo Único** | Cria USP com nova categoria, significado, segredo e mecanismo misterioso | `prompts/04-usp.md` | Avatar completo |
| **TSL / Advertorial (2.000+ palavras)** | Página de salto persuasiva em PT-BR para elite paulistana, 9 seções estruturadas | `prompts/05-tsl-advertorial.md` | Avatar + Oferta |
| **20 Headlines para Anúncios** | Gera 20 headlines viscerais para ad copy com 20+ templates de base | `prompts/06-headlines.md` | Avatar + Nicho + Objetivo + Dor |
| **6 Scripts de Vídeo 60s** | 6 ângulos diferentes: Anti-Sorte, Evolução, Humor, Antes/Depois, Whistleblower, Gap | `prompts/07-anuncios-video-60s.md` | Avatar + Oferta + USP |

**Mapeamento MoneyClub → Furion:**

| Prompt MoneyClub | Gerador Furion Equivalente |
|---|---|
| Extração de Avatar | Avatar Destroyer – Desbravador De Mentes |
| Oferta + Upsell | Gerador Devastador de Ofertas + Upsell Nuclear |
| USP + Mecanismo | Proposta Única De Vendas – Beast Mode |
| TSL / Advertorial | Página De Vendas Obliteradora De Objeções |
| Headlines | Sistema De Anúncios Dominadores |
| Scripts Vídeo 60s | (60-Min) Vídeo De Vendas Predador |
| Prompt Parasita | (análise pré-lançamento — sem equivalente no Furion) |

**Quando usar MoneyClub vs. Furion:**
- **MoneyClub prompts** → quando quiser controle total do output, usar fora do Furion, ou iterar manualmente
- **Furion generators** → quando quiser resultado rápido com UI guiada e templates pré-construídos
- **Combinado** → JARVIS prepara DATA com MoneyClub prompts → cola no Furion para output final

---

### Como Usar Gerador Standalone

```
/furion-infoproduto gerador [nome do gerador]
```

Exemplos:
```
/furion-infoproduto gerador anuncios
/furion-infoproduto gerador vsl-60min
/furion-infoproduto gerador email-cta
/furion-infoproduto gerador linkedin
/furion-infoproduto gerador youtube-roteiro
/furion-infoproduto gerador instagram-carrossel   ← JARVIS gera direto, sem Furion
```

JARVIS identifica o gerador, consulta o MEGABRAIN, e entrega o input pronto.
Se faltarem dados (ex: avatar ainda não definido), JARVIS pede antes de gerar.

---

## Estrutura de Pastas

```
inbox/
└── furion-outputs/
    └── [nome-produto]/
        ├── 01-avatar.md
        ├── 02-oferta.md
        ├── 03-usp.md
        ├── 04-infoproduto.md
        ├── 05-pagina-vendas.md
        ├── 06-upsell-bump.md
        ├── 07-anuncios.md
        ├── 08-vsl-60min.md
        ├── 09-pagina-upsell.md
        ├── 10-vsl-15min.md
        └── [outros outputs standalone]/
```

---

## Tom e Comportamento do JARVIS

- **Direto**: Entrega o input pronto, sem explicar demais
- **Sequencial**: No modo workflow, um passo de cada vez — não adianta sem o output do atual
- **Analítico**: Quando o usuário traz output do Furion, sempre avalia antes de passar adiante
- **Compacto**: Inputs para o Furion sempre dentro do limite de palavras especificado
- **Modular**: No modo standalone, pode pular fases já feitas se o usuário já tiver avatar/oferta/usp

---

## Comandos de Ativação

```
# Workflow completo (Do Zero Ao Primeiro Produto)
/furion-infoproduto [ideia do produto]

# Gerador específico
/furion-infoproduto gerador [tipo]

# Sem argumento — JARVIS pergunta modo e ideia interativamente
/furion-infoproduto
```

---

## Changelog

| Versão | Data | Mudanças |
|---|---|---|
| v1.3 | 2026-03-31 | **MoneyClub Prompts integrados** — 7 prompt templates de Tiago Brendon (TB014) adicionados ao catálogo; Tiago Brendon adicionado como especialista; pasta `prompts/` criada com templates prontos; mapeamento MoneyClub↔Furion documentado |
| v1.2 | 2026-03-29 | Catálogo 100% completo: Mídia Social, YouTube, E-mails + Instagram nativo JARVIS |
| v1.1 | 2026-03-29 | Adicionado catálogo completo de geradores + Modo Standalone |
| v1.0 | 2026-03-29 | Criação inicial baseada no workflow "Do Zero Ao Primeiro Produto" |
