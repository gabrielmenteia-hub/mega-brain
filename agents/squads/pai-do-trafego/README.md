# Pai do Tráfego Squad

> **Direct Response Creative para Infoprodutos Brasileiros**
> Versão: 1.0.0 | Tipo: Hybrid (Expert + Pipeline) | Modo: Incremental

## O que é

Squad especializado em produzir **pacotes completos de criativos validados** — copy, hook, briefing visual e critique — prontos para veicular em Meta Ads e TikTok Ads, com loop de otimização por métricas reais.

Combina princípios de Direct Response (Brunson, Halbert, Schwartz) com execução nativa por plataforma (Meta e TikTok), dentro de um pipeline com checkpoints que garantem que nenhum criativo sai sem validação.

## Ativação

```
@pdt-chief
```

## Agentes (9)

| Agente | Tier | Função |
|---|---|---|
| `pdt-chief` | Orchestrator | Routing, quality gates, handoffs |
| `market-auditor` | 0 | Avatar, awareness level, ângulos, benchmark |
| `dr-master` | 1 | USP, mecanismo único, oferta core, estrutura DR |
| `offer-architect` | 2 | Framing de oferta, matriz de ângulos, creative brief |
| `hook-writer` | 3 | Hooks para vídeo UGC e DTC |
| `static-creative` | 3 | Criativos estáticos Meta Ads (imagem e carrossel) |
| `tiktok-creative` | 3 | Roteiros 15-30s e copy TikTok Ads |
| `lp-funnel` | 3 | Páginas de captura e pré-lançamento |
| `creative-critic` | Tool | Review e checklist pré-publicação |
| `metrics-optimizer` | Tool | Iteração por CTR, Hook Rate, CPL, ROAS |

## Casos de Uso

1. **Hooks para vídeo** (UGC e direto à câmera): `*audit → *dr → *offer → *hook → *critique`
2. **Criativos estáticos Meta** (imagem única e carrossel): `*audit → *dr → *offer → *static → *critique`
3. **TikTok Ads** (roteiro 15-30s): `*audit → *dr → *offer → *tiktok → *critique`
4. **Página de captura**: `*audit → *dr → *lp → *critique`
5. **Iteração com métricas**: `*optimize` (com dados reais de campanha)

## Pipeline Completo

```
*full — executa o pipeline do zero:
  ┌─────────────────────────────────────────────────────┐
  │  market-auditor → dr-master → offer-architect       │
  │       → [especialista Tier 3] → creative-critic     │
  └─────────────────────────────────────────────────────┘
```

## Quality Gates

| Gate | Descrição | Tipo |
|---|---|---|
| PDT-QG-001 | Audit completo antes de qualquer criativo | Bloqueante |
| PDT-QG-002 | Ângulo aprovado antes do Tier 3 | Bloqueante |
| PDT-QG-003 | Creative review antes da entrega | Bloqueante |
| PDT-QG-004 | Checklist de publicação | Bloqueante |
| PDT-QG-005 | Loop de iteração com métricas | Condicional |

## Practitioners de Referência

Russell Brunson · Alex Hormozi · Eugene Schwartz · Gary Halbert · Gary Bencivenga · Sabri Suby · Tom Breeze · Savannah Sanchez · Cody Plofker · Ryan Deiss · Perry Belcher · Dan Kennedy · John Caples · David Ogilvy

## Comandos Rápidos

```
*audit     — Auditar mercado e avatar
*dr        — Definir USP e mecanismo único
*offer     — Framing de oferta e creative brief
*hook      — Hooks para vídeo
*static    — Criativos estáticos Meta
*tiktok    — Roteiros TikTok
*lp        — Página de captura
*critique  — Review pré-publicação
*optimize  — Iterar com métricas
*full      — Pipeline completo
*help      — Listar todos os comandos
```
