# Task: Benchmark de Produto Campeão

**Task ID:** GT-TP-001
**Task Name:** Analisar Produto Campeão do Mercado
**Execution Type:** Agent
**Executor:** product-diagnostician + offer-architect
**Squad:** garfield-time

---

## Inputs Obrigatórios

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `produto` | Nome ou URL do produto a analisar | "Método X — curso de emagrecimento" |
| `nicho` | Nicho do produto | "Emagrecimento", "Marketing Digital" |
| `ticket` | Preço do produto | "R$997", "R$15k" |
| `contexto_adicional` | Qualquer informação extra sobre o produto | "É VSL, vende via Facebook Ads" |

## Preconditions

- [ ] Nome/URL do produto identificado
- [ ] Nicho definido
- [ ] Ticket aproximado conhecido

## Processo de Execução

### FASE 1 — Diagnóstico Inicial (product-diagnostician)

1. Classificar tipo de produto (curso, mentoria, comunidade, SaaS)
2. Identificar mecanismo central de transformação
3. Classificar nível de sofisticação da audiência (1-5 de Schwartz)
4. Mapear funil de entrada detectado
5. Identificar ângulo de posicionamento

### FASE 2 — Análise de Oferta (offer-architect)

1. Aplicar Value Equation ao produto
2. Desmontar o value stack completo
3. Avaliar estrutura de garantia
4. Analisar precificação vs. valor percebido
5. Identificar força e fraquezas da Grand Slam Offer

### FASE 3 — Síntese e Padrões Reproduzíveis

1. Extrair os 3-5 padrões mais replicáveis
2. Identificar o que diferencia este produto dos concorrentes
3. Listar o que NÃO funciona / pontos fracos detectados
4. Recomendar próximos passos de análise (se necessário)

## Outputs

| Output | Formato | Localização |
|--------|---------|-------------|
| Relatório de Benchmark | Markdown | `.aiox/squad-runtime/garfield-time/benchmarks/{produto}.md` |
| Value Equation Score | Tabela | Inline no relatório |
| Padrões Reproduzíveis | Lista estruturada | Inline no relatório |

## Template de Output

```markdown
## 📊 BENCHMARK: {Nome do Produto}

### Classificação
- Tipo: {tipo}
- Mecanismo: {mecanismo central}
- Sofisticação da Audiência: Nível {N}
- Ticket: {valor}

### Value Equation Score
| Variável | Score (1-10) | Observação |
|----------|-------------|------------|
| Dream Outcome | | |
| Perceived Likelihood | | |
| Time Delay (inverso) | | |
| Effort (inverso) | | |
| **TOTAL** | | |

### Estrutura da Oferta
- Core Offer: {o que é}
- Value Stack: {itens}
- Garantia: {tipo e condições}
- Upsells: {se detectados}

### Funil de Entrada
- Canal de aquisição: {canal}
- Porta de entrada: {lead magnet ou direto}
- Sequência: {passos detectados}

### Padrões Reproduzíveis
1. {padrão 1}
2. {padrão 2}
3. {padrão 3}

### Pontos Fracos / Oportunidades
- {oportunidade 1}
- {oportunidade 2}

### Próximos Passos Recomendados
- [ ] {ação 1}
- [ ] {ação 2}
```

## Acceptance Criteria

- [ ] Tipo de produto classificado com evidência
- [ ] Value Equation score com score para cada variável
- [ ] Value stack completo desmontado
- [ ] Funil de entrada mapeado
- [ ] Mínimo 3 padrões reproduzíveis identificados
- [ ] Pelo menos 2 pontos fracos/oportunidades identificados
- [ ] Próximos passos definidos
