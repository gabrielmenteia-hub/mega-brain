# Requirements: Market Intelligence System (MIS)

**Defined:** 2026-03-17
**Milestone:** v3.0 — Market Intelligence 2.0
**Core Value:** Entregar ao usuário o mapa completo do que está vendendo e por que está vendendo — sem esforço manual — para que ele possa modelar e lançar produtos com máxima vantagem competitiva.

## v3.0 Requirements

### Nichos e Subnichos

- [x] **NICHE-01**: Sistema define 4 nichos fixos (Relacionamento, Saúde, Finanças, Renda Extra) com ~40 subnichos pré-configurados e mapeados por plataforma
- [x] **NICHE-02**: Cada subnicho tem slug de busca específico por plataforma (ex: "weight-loss" no ClickBank, "emagrecimento" no Hotmart)

### Pesquisa Manual

- [ ] **SEARCH-01**: Usuário seleciona nicho → subnicho → clica "Pesquisar" para iniciar scan sob demanda
- [ ] **SEARCH-02**: Resultado exibe produtos agrupados por plataforma e país de origem (BR / US / Global)
- [ ] **SEARCH-03**: Zero automação — nenhum scan roda sem ação explícita do usuário

### Espionagem

- [ ] **SPY-V3-01**: Ao pesquisar, espionagem automática roda nos top produtos de cada plataforma do resultado
- [ ] **SPY-V3-02**: Usuário pode clicar em qualquer produto para abrir dossiê completo
- [ ] **SPY-V3-03**: Dossiê inclui: anúncios Meta Ads ativos, página de venda completa, upsell/downsell mapeados, copy e gatilhos identificados, estrutura de oferta (preço, bônus, garantia)

### Dashboard

- [ ] **DASH-V3-01**: Tela principal com seletor de nicho/subnicho e botão "Pesquisar"
- [ ] **DASH-V3-02**: Grid de resultados separado por plataforma/país com thumbnail, título, rank, comissão/preço
- [ ] **DASH-V3-03**: Página de dossiê por produto com todas as estratégias de marketing estruturadas

### Favoritos e Tracking

- [ ] **TRACK-01**: Usuário pode favoritar produtos para acompanhamento contínuo
- [ ] **TRACK-02**: Sistema registra histórico de posição por produto favoritado (subiu/caiu no ranking ao longo do tempo)

### Alertas

- [ ] **ALERT-V3-01**: Alerta visual no dashboard quando novo produto entra no top de um subnicho que o usuário pesquisou anteriormente

### Exportação

- [ ] **EXPORT-01**: Exportar dossiê completo de um produto em PDF com todas as estratégias de marketing

## Fora do Escopo (v3.0)

| Feature | Motivo |
|---------|--------|
| Scan automático agendado | Substituído por pesquisa manual sob demanda |
| Pain Radar automático | Fora do foco v3.0 — pode retornar em v3.1 |
| Comparação lado a lado | Complexidade alta — v3.1+ |
| Notificações WhatsApp/Telegram | Infraestrutura externa — v3.1+ |
| Kajabi, Teachable, Skool, Stan Store | Sem marketplace público — paywall extremo |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| NICHE-01 | Phase 20 | Complete |
| NICHE-02 | Phase 20 | Complete |
| SEARCH-01 | Phase 21 | Pending |
| SEARCH-02 | Phase 21 | Pending |
| SEARCH-03 | Phase 21 | Pending |
| SPY-V3-01 | Phase 22 | Pending |
| SPY-V3-02 | Phase 22 | Pending |
| SPY-V3-03 | Phase 22 | Pending |
| DASH-V3-01 | Phase 23 | Pending |
| DASH-V3-02 | Phase 23 | Pending |
| DASH-V3-03 | Phase 23 | Pending |
| TRACK-01 | Phase 24 | Pending |
| TRACK-02 | Phase 24 | Pending |
| ALERT-V3-01 | Phase 25 | Pending |
| EXPORT-01 | Phase 26 | Pending |

**Coverage:**
- v3.0 requirements: 15 total
- Mapped to phases: 15
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-17*
