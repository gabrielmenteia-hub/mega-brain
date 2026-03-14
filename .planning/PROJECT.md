# Market Intelligence System (MIS)

## What This Is

Sistema de inteligência de mercado integrado ao MEGABRAIN que varre automaticamente produtos e infoprodutos campeões de vendas no Brasil e no exterior, executa espionagem completa de cada produto encontrado, e gera relatórios horários das dores, problemas e desejos que o mercado está buscando. Os resultados são exibidos em um dashboard web e consolidados em dossiês gerados por IA para modelagem de produtos próprios.

## Core Value

Entregar ao usuário, sem esforço manual, o mapa completo do que está vendendo e por que está vendendo — para que ele possa modelar e lançar seus próprios produtos com máxima vantagem competitiva.

## Requirements

### Validated

(None yet — ship to validate)

### Active

**Módulo 1 — Scanner de Produtos Campeões**
- [ ] Varredura de best-sellers na Hotmart, Kiwify e Eduzz (Brasil)
- [ ] Varredura de best-sellers no ClickBank, JVZoo, Udemy, Teachable, Product Hunt e AppSumo (gringa)
- [ ] Filtro por múltiplos nichos configuráveis (3–5 nichos simultâneos)
- [ ] Ranqueamento por volume de vendas, engajamento ou tendência de crescimento
- [ ] Atualização periódica automática do ranking

**Módulo 2 — Espionagem de Produto**
- [ ] Extração e análise da copy/página de vendas (headlines, argumentos, estrutura da oferta)
- [ ] Mapeamento de anúncios rodando (criativos, textos, plataformas onde anunciam)
- [ ] Extração de estrutura de oferta (preço, bônus, garantias, upsells, downsells)
- [ ] Coleta e síntese de reviews e objeções (o que compradores elogiam e reclamam)
- [ ] Geração de dossiê completo do produto (PDF/dashboard)

**Módulo 3 — Radar de Dores do Mercado**
- [ ] Monitoramento horário do Google Trends e buscas relacionadas ao nicho
- [ ] Scraping de Reddit, Quora e fóruns relevantes (perguntas e problemas postados)
- [ ] Análise de comentários em anúncios (dores expostas em posts patrocinados)
- [ ] Análise de títulos e comentários de vídeos no YouTube por nicho
- [ ] Relatório horário consolidado das principais dores/desejos identificados

**Interface & Integração**
- [ ] Dashboard web para visualização de produtos, dossiês e relatórios de dores
- [ ] Integração como agente/pipeline dentro do MEGABRAIN
- [ ] Notificações/alertas quando novo produto campeão é detectado

### Out of Scope

- Automação de criação do produto final — o sistema modela e inspira, a criação é do usuário
- Integração com plataformas de pagamento para vender diretamente — fora do escopo
- Monitoramento de redes sociais fechadas (grupos privados do Facebook, etc.) — bloqueado por TOS

## Context

- Integrado ao MEGABRAIN como módulo de inteligência de mercado
- Usuário tem 12 anos em vendas online e negócios de 9 dígitos — conhece profundamente o mercado de infoprodutos brasileiro e internacional
- Principais plataformas BR: Hotmart, Kiwify, Eduzz
- Principais plataformas internacionais: ClickBank, JVZoo, Udemy, Teachable, Product Hunt, AppSumo
- Fontes de dores do mercado: Google Trends, Reddit, Quora, comentários de anúncios, YouTube
- Output principal: Dossiê completo gerado por IA + Dashboard web

## Constraints

- **Acesso a dados**: Hotmart/Kiwify/Eduzz não têm API pública robusta — scraping ou uso de APIs não-oficiais necessário
- **Rate limiting**: Google, Reddit e YouTube têm limites de requisição — arquitetura deve respeitar rate limits
- **Frequência**: Radar de dores atualiza a cada 1 hora — pipeline deve ser leve o suficiente para esse ciclo
- **Stack**: Integrado ao MEGABRAIN — Python como linguagem principal, compatível com a arquitetura existente
- **Legalidade**: Scraping de páginas públicas é permitido; dados pessoais de compradores nunca coletados

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Dashboard web separado do MEGABRAIN CLI | UX para consumo rápido de dados visuais requer interface dedicada | — Pending |
| Scraping vs APIs oficiais para plataformas BR | APIs inexistentes ou muito limitadas — scraping é o caminho viável | — Pending |
| Ciclo horário para radar de dores | Frequência suficiente para capturar tendências sem sobrecarregar APIs | — Pending |

---
*Last updated: 2026-03-14 after initialization*
