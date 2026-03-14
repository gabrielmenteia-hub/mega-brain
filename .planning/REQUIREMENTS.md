# Requirements: Market Intelligence System (MIS)

**Defined:** 2026-03-14
**Core Value:** Entregar o mapa completo do que está vendendo e por que está vendendo — sem esforço manual — para que o usuário possa modelar e lançar seus próprios produtos com máxima vantagem competitiva.

## v1 Requirements

### Foundation

- [x] **FOUND-01**: Sistema possui schema de banco de dados com tabelas para produtos, plataformas, nichos, dores e dossiês
- [ ] **FOUND-02**: BaseScraper implementa rate limiting, retry automático, rotação de proxies e headers anti-bot
- [x] **FOUND-03**: Usuário pode configurar 3–5 nichos alvo em arquivo de configuração
- [ ] **FOUND-04**: Health monitor detecta e alerta quando scrapers quebram silenciosamente (canary checks)

### Scanner de Produtos

- [ ] **SCAN-01**: Sistema varre e rankeia produtos mais vendidos na Hotmart por nicho configurado
- [x] **SCAN-02**: Sistema varre e rankeia produtos mais vendidos na Kiwify por nicho configurado
- [x] **SCAN-03**: Sistema varre e rankeia produtos com maior gravity score no ClickBank por nicho configurado
- [ ] **SCAN-04**: Ranking é atualizado automaticamente em ciclo periódico (diário)
- [ ] **SCAN-05**: Usuário pode filtrar ranking por plataforma e nicho no dashboard

### Espionagem de Produto

- [ ] **SPY-01**: Sistema extrai copy completa da página de vendas (headlines, sub-headlines, argumentos, CTA, estrutura narrativa)
- [ ] **SPY-02**: Sistema coleta anúncios ativos do produto via Meta Ad Library (criativos e copy)
- [ ] **SPY-03**: Sistema extrai estrutura da oferta (preço, bônus, garantias, upsells, downsells)
- [ ] **SPY-04**: Sistema coleta e classifica reviews do produto separando avaliações positivas (4-5★) e negativas (1-3★)
- [ ] **SPY-05**: Dados de espionagem só são processados pelo LLM quando completude mínima é atingida (data completeness gate)

### Dossiê IA

- [ ] **DOS-01**: IA gera análise explicando por que o produto está vendendo (fatores de sucesso identificados nos dados)
- [ ] **DOS-02**: IA mapeia as dores endereçadas pelo produto com base na copy e reviews coletados
- [ ] **DOS-03**: IA gera template de modelagem com estrutura pronta para criar produto próprio baseado no campeão
- [ ] **DOS-04**: IA atribui score de oportunidade por nicho (quão atrativa é a entrada nesse mercado)
- [ ] **DOS-05**: Dossiê exibe confidence score indicando qualidade/completude dos dados usados na análise

### Radar de Dores (Horário)

- [ ] **RADAR-01**: Sistema monitora Google Trends por nicho a cada hora, com normalização por anchor term estável
- [ ] **RADAR-02**: Sistema coleta perguntas e posts de Reddit e Quora relacionados aos nichos configurados
- [ ] **RADAR-03**: Sistema analisa títulos e comentários de vídeos no YouTube por nicho (com quota management)
- [ ] **RADAR-04**: Sistema coleta comentários de anúncios patrocinados no Meta por nicho
- [ ] **RADAR-05**: Pipeline do radar é idempotente (re-execução não gera duplicatas)
- [ ] **RADAR-06**: Relatório horário consolidado é gerado com as principais dores/desejos detectados por nicho

### Dashboard Web

- [ ] **DASH-01**: Dashboard exibe ranking de produtos campeões filtrável por plataforma e nicho
- [ ] **DASH-02**: Dashboard exibe página individual de dossiê por produto com todos os dados de espionagem e análise IA
- [ ] **DASH-03**: Dashboard exibe feed de dores do mercado com atualização horária por nicho
- [ ] **DASH-04**: Sistema envia alerta quando novo produto campeão entra no radar

### Integração MEGABRAIN

- [ ] **INT-01**: MIS é integrado ao MEGABRAIN como módulo independente (`mis/`) com único ponto de integração (`mis_agent.py`)
- [ ] **INT-02**: Usuário pode invocar análise do MIS via agente/comando dentro do MEGABRAIN

## v2 Requirements

### Expansão de Plataformas

- **SCAN-V2-01**: Scanner da Eduzz (BR)
- **SCAN-V2-02**: Scanner do JVZoo (gringa)
- **SCAN-V2-03**: Scanner do Udemy por categoria
- **SCAN-V2-04**: Scanner do Product Hunt e AppSumo (ferramentas/SaaS)

### Features Avançadas

- **ADV-01**: Exportação de dossiê em PDF
- **ADV-02**: Comparação lado a lado de 2+ produtos concorrentes
- **ADV-03**: Histórico de evolução de produto (tracking de mudanças na copy/oferta ao longo do tempo)
- **ADV-04**: Notificações via WhatsApp/Telegram além do dashboard

## Out of Scope

| Feature | Reason |
|---------|--------|
| Automação de criação do produto final | O sistema inspira; a criação é do usuário — escopo separado |
| Integração com plataformas de pagamento | Fora do objetivo de inteligência de mercado |
| Scraping de grupos privados (Facebook, WhatsApp) | Bloqueado por ToS e LGPD |
| SEO intelligence completo (backlinks, domain authority) | Território do SEMrush/Ahrefs — escopo creep para v1 |
| Monitoramento sub-minuto / real-time | Infra muito cara; horário é suficiente para o caso de uso |
| Interface mobile nativa | Web responsiva suficiente para MVP |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FOUND-01 | Phase 1 | Complete (01-01) |
| FOUND-02 | Phase 1 | Pending |
| FOUND-03 | Phase 1 | Complete |
| FOUND-04 | Phase 1 | Pending |
| SCAN-01 | Phase 2 | Pending |
| SCAN-02 | Phase 2 | Complete |
| SCAN-03 | Phase 2 | Complete |
| SCAN-04 | Phase 2 | Pending |
| SCAN-05 | Phase 5 | Pending |
| SPY-01 | Phase 3 | Pending |
| SPY-02 | Phase 3 | Pending |
| SPY-03 | Phase 3 | Pending |
| SPY-04 | Phase 3 | Pending |
| SPY-05 | Phase 3 | Pending |
| DOS-01 | Phase 3 | Pending |
| DOS-02 | Phase 3 | Pending |
| DOS-03 | Phase 3 | Pending |
| DOS-04 | Phase 3 | Pending |
| DOS-05 | Phase 3 | Pending |
| RADAR-01 | Phase 4 | Pending |
| RADAR-02 | Phase 4 | Pending |
| RADAR-03 | Phase 4 | Pending |
| RADAR-04 | Phase 4 | Pending |
| RADAR-05 | Phase 4 | Pending |
| RADAR-06 | Phase 4 | Pending |
| DASH-01 | Phase 5 | Pending |
| DASH-02 | Phase 5 | Pending |
| DASH-03 | Phase 5 | Pending |
| DASH-04 | Phase 5 | Pending |
| INT-01 | Phase 6 | Pending |
| INT-02 | Phase 6 | Pending |

**Coverage:**
- v1 requirements: 31 total
- Mapped to phases: 31
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-14*
*Last updated: 2026-03-14 after initial definition*
