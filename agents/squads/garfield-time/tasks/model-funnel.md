# Task: Modelagem de Funil de Alta Conversão

**Task ID:** GT-TP-003
**Task Name:** Modelar Funil Baseado em Padrões de Produtos Milionários
**Execution Type:** Agent
**Executor:** launch-strategist + ask-methodologist
**Squad:** garfield-time

---

## Inputs Obrigatórios

| Campo | Descrição |
|-------|-----------|
| `nicho` | Nicho do produto |
| `ticket` | Ticket alvo do produto |
| `avatar` | Descrição do avatar (ou resultado do ask-methodologist) |
| `benchmark` | Produto(s) de referência já analisados |

## Preconditions

- [ ] Avatar mapeado (ask-methodologist) ou descrição suficiente
- [ ] Pelo menos 1 benchmark analisado (GT-TP-001)

## Processo de Execução

### FASE 1 — Mapa de Segmentação (ask-methodologist)

1. Definir ou confirmar os 3-5 buckets do avatar
2. Mapear a dor predominante de cada bucket
3. Identificar a linguagem exata do avatar
4. Definir o tipo de entrada ideal (quiz, lead magnet, webinar)

### FASE 2 — Estrutura do Funil (launch-strategist)

1. Selecionar tipo de lançamento ideal (seed, internal, JV)
2. Definir a sequência de pre-launch content (PLC1, PLC2, PLC3)
3. Estruturar a janela de open cart (duração + sequência de emails)
4. Planejar o close cart (urgência + sequência final)
5. Definir sequência de onboarding pós-compra

### FASE 3 — Mapeamento de Funil Visual

1. Mapear a jornada completa do lead (entrada → compra → upsell)
2. Identificar pontos de abandono típicos e como mitigá-los
3. Definir métricas de conversão esperadas por etapa
4. Identificar upsells e order bumps na sequência

## Template de Output

```
FUNIL MODELADO: {Nicho} — Ticket {R$X}

ENTRADA
├── Canal: {Facebook Ads / YouTube / Orgânico}
├── Formato: {Quiz / Lead Magnet / Direto}
└── Conversão esperada: {X%}

PRE-LAUNCH (X semanas)
├── PLC1: {título} — Trigger: Autoridade
├── PLC2: {título} — Trigger: Comunidade
└── PLC3: {título} — Trigger: Antecipação

OPEN CART ({X} dias)
├── Dia 1: Email abertura + página de vendas
├── Dia 2-3: Case de sucesso + FAQ
├── Dia {X-1}: Urgência — 24h
└── Dia {X}: Close cart (3 emails)

PÓS-COMPRA
├── Welcome imediato
├── Onboarding dias 1-7
└── Pesquisa de satisfação dia 14

UPSELLS
├── OB: {descrição} — R${Y}
└── Upsell 1: {descrição} — R${Z}
```

## Acceptance Criteria

- [ ] 3-5 buckets de avatar definidos
- [ ] Tipo de lançamento selecionado com justificativa
- [ ] PLC completo (PLC1, PLC2, PLC3) estruturado
- [ ] Sequência de open cart com timing dia a dia
- [ ] Close cart estruturado (últimas 24h)
- [ ] Métricas de conversão por etapa definidas
- [ ] Upsells mapeados
