# Task: Engenharia Reversa de Copy

**Task ID:** GT-TP-005
**Task Name:** Desmontar Copy de Alta Conversão e Extrair Blueprint
**Execution Type:** Agent
**Executor:** copy-decoder
**Squad:** garfield-time

---

## Inputs Obrigatórios

| Campo | Descrição |
|-------|-----------|
| `copy` | O copy a ser analisado (texto completo ou URL) |
| `tipo` | `headline`, `email`, `vsl`, `pagina_vendas`, `ad` |
| `contexto` | Nicho e ticket do produto |

## Preconditions

- [ ] Copy disponível (texto ou URL acessível)
- [ ] Tipo de copy identificado

## Processo de Execução

### FASE 1 — Identificação de Estrutura

1. Identificar a fórmula principal (AIDA / PAS / BAB / outra)
2. Mapear os beats estruturais em sequência
3. Identificar onde cada seção começa e termina
4. Classificar o tipo de lead usado

### FASE 2 — Análise Elemento por Elemento

Para cada elemento do copy:
1. Nomear a função do elemento
2. Identificar o gatilho emocional ativado
3. Avaliar specificity (1-10)
4. Identificar objeção que está sendo superada (se aplicável)

### FASE 3 — Score e Blueprint

1. Score geral de eficácia (1-10) com justificativa
2. Top 3 pontos fortes
3. Top 3 oportunidades de melhoria
4. Blueprint reproduzível (estrutura anotada)

## Acceptance Criteria

- [ ] Fórmula identificada com evidências textuais
- [ ] Todos os beats mapeados
- [ ] Score de specificity para headline e promessa principal
- [ ] Gatilhos emocionais identificados por seção
- [ ] Score geral fundamentado
- [ ] Blueprint estruturado entregue
- [ ] 3+ recomendações de melhoria específicas
