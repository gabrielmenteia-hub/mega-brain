# Garfield Time 🐱

> **Squad de Modelagem e Engenharia Reversa de Info Produtos Milionários**

Especializado em dissecar produtos campeões, desmontar ofertas e copy de alta conversão, modelar funis milionários e criar produtos próprios baseados nos padrões que realmente funcionam.

---

## Quick Start

```bash
# Ativar o orquestrador
@garfield-chief

# Comandos principais
*benchmark {produto}   # Analisar produto campeão
*reverse               # Engenharia reversa completa
*model                 # Modelar funil
*create                # Criar produto modelado
*help                  # Ver todos os comandos
```

---

## Agentes

| Agente | Tier | DNA | Especialidade |
|--------|------|-----|---------------|
| `garfield-chief` | Orch | — | Orquestração, triagem, síntese |
| `product-diagnostician` | 0 | — | Diagnóstico e classificação de produtos |
| `offer-architect` | 1 | Alex Hormozi | Value Equation, Grand Slam Offer |
| `launch-strategist` | 1 | Jeff Walker | Product Launch Formula, funis de lançamento |
| `ask-methodologist` | 2 | Ryan Levesque | Ask Method, survey funnels, segmentação |
| `market-seducer` | 2 | Frank Kern | Core Influence, story selling, narrativa |
| `copy-decoder` | 3 | Halbert/Carlton/Ogilvy | Engenharia reversa de copy e headlines |
| `br-market-strategist` | 3 | Ícaro / Naro | Posicionamento e autoridade no mercado BR |

---

## Tasks

| Task | ID | Executor | Propósito |
|------|----|----------|-----------|
| `benchmark-product.md` | GT-TP-001 | diagnostician + offer | Análise completa de produto campeão |
| `reverse-offer.md` | GT-TP-002 | offer + copy + seducer | Engenharia reversa de oferta e copy |
| `reverse-copy.md` | GT-TP-005 | copy-decoder | Engenharia reversa de copy específico |
| `model-funnel.md` | GT-TP-003 | strategist + ask | Modelagem de funil |
| `create-product.md` | GT-TP-004 | todos | Criar produto modelado completo |

---

## Casos de Uso

### 1. Analisar concorrente
```
@garfield-chief
*benchmark "Método X — curso de emagrecimento R$997"
```

### 2. Engenharia reversa completa
```
@garfield-chief
*reverse [URL ou descrição da página de vendas]
```

### 3. Criar produto do zero modelado
```
@garfield-chief
*create
# O chief guia você por todas as fases
```

### 4. Especialistas diretos
```
@garfield-time:offer-architect     # Análise de oferta com Hormozi DNA
@garfield-time:copy-decoder        # Análise de copy
@garfield-time:launch-strategist   # Estratégia de lançamento
@garfield-time:br-market-strategist # Adaptação para mercado BR
```

---

## Arquitetura

```
ORCHESTRATOR: garfield-chief
    │
    ▼
TIER 0: product-diagnostician (triagem)
    │
    ├── TIER 1: offer-architect (Hormozi DNA)
    ├── TIER 1: launch-strategist (Jeff Walker DNA)
    │
    ├── TIER 2: ask-methodologist (Levesque DNA)
    ├── TIER 2: market-seducer (Frank Kern DNA)
    │
    ├── TIER 3: copy-decoder
    └── TIER 3: br-market-strategist
```

---

## Quality Gates

| Gate | Transição | Tipo |
|------|-----------|------|
| QG-GT-001 | Input → Tier 0 | Routing |
| QG-GT-002 | Tier 0 → Tier 1 | Blocking |
| QG-GT-003 | Após análise Tier 1 | Blocking |
| QG-GT-004 | Antes de criação | Blocking |
| QG-GT-005 | Saída final | Blocking |

---

_Versão: 1.0.0 | Squad Type: EXPERT | Criado: 2026-03-19_
