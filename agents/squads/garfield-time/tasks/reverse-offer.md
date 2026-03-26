# Task: Engenharia Reversa de Oferta e Copy

**Task ID:** GT-TP-002
**Task Name:** Desmontar Oferta e Copy de Produto Milionário
**Execution Type:** Agent
**Executor:** offer-architect + copy-decoder + market-seducer
**Squad:** garfield-time

---

## Inputs Obrigatórios

| Campo | Descrição |
|-------|-----------|
| `produto` | Produto a ser desmontado |
| `url_ou_descricao` | URL da página de vendas ou descrição do copy |
| `foco` | `oferta`, `copy`, `ambos` |

## Preconditions

- [ ] Diagnóstico inicial feito (GT-TP-001) ou produto já classificado
- [ ] URL ou descrição do copy disponível

## Processo de Execução

### FASE 1 — Engenharia Reversa da Oferta (offer-architect)

1. Desmontar o value stack item por item
2. Identificar a promessa principal (número + prazo + mecanismo)
3. Analisar estrutura da garantia
4. Calcular o price-to-value ratio
5. Identificar upsells e order bumps

### FASE 2 — Engenharia Reversa do Copy (copy-decoder)

1. Identificar a fórmula de copy usada (AIDA, PAS, etc.)
2. Analisar o headline principal com score de specificity
3. Mapear os beats da VSL ou estrutura da página de vendas
4. Identificar gatilhos emocionais usados por seção
5. Mapear como cada objeção principal é tratada
6. Analisar o CTA e urgência

### FASE 3 — Análise de Narrativa e Influência (market-seducer)

1. Identificar o Domino central da mensagem
2. Mapear a origin story usada
3. Analisar os open loops e como são fechados
4. Avaliar o future pacing presente
5. Identificar os mental triggers da sequência

### FASE 4 — Síntese: Blueprint Reproduzível

1. Montar blueprint da oferta (estrutura replicável)
2. Montar blueprint do copy (fórmula e beats)
3. Extrair as 5 melhores práticas identificadas
4. Identificar o que pode ser melhorado

## Outputs

| Output | Formato |
|--------|---------|
| Blueprint da Oferta | Estrutura comentada |
| Blueprint do Copy | Fórmula + beats identificados |
| Mapa de Gatilhos | Lista por seção |
| 5 Melhores Práticas | Lista acionável |

## Acceptance Criteria

- [ ] Value stack completo desmontado com valores individuais
- [ ] Fórmula de copy identificada com evidências
- [ ] Domino da mensagem identificado
- [ ] Todos os gatilhos emocionais mapeados por seção
- [ ] Blueprint reproduzível gerado
- [ ] 5 melhores práticas listadas
- [ ] Fraquezas identificadas
