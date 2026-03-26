# Task: Criar Produto Modelado

**Task ID:** GT-TP-004
**Task Name:** Criar Info Produto Baseado em Padrões Milionários
**Execution Type:** Hybrid (Agent + Human approval)
**Executor:** garfield-chief orquestra todos
**Squad:** garfield-time

---

## Inputs Obrigatórios

| Campo | Descrição |
|-------|-----------|
| `nicho` | Nicho do produto |
| `expertise` | O que o produtor sabe / resultado que entrega |
| `avatar_descricao` | Quem é o cliente ideal |
| `ticket_alvo` | Ticket alvo do produto |
| `benchmarks` | Produtos de referência já analisados |

## Preconditions

- [ ] Avatar mapeado (GT-TP-001 ou ask-methodologist)
- [ ] Pelo menos 2 benchmarks analisados
- [ ] Funil modelado (GT-TP-003) ou definido

## Processo de Execução

### FASE 1 — Definição da Grand Slam Offer (offer-architect)

1. Definir a promessa principal (número + prazo + mecanismo)
2. Criar o mecanismo único com nome proprietário
3. Montar o value stack completo com valores individuais
4. Definir estrutura de garantia
5. Definir precificação com ancoragem

**CHECKPOINT QG-GT-004:** Usuário aprova a oferta antes de prosseguir

### FASE 2 — Copy e Narrativa (copy-decoder + market-seducer)

1. Criar headline principal (3 variações)
2. Definir o Domino da mensagem
3. Estruturar a origin story do produtor
4. Criar o lead da página de vendas
5. Desenvolver estrutura completa de copy (PAS ou AIDA)

### FASE 3 — Adaptação BR (br-market-strategist)

1. Calibrar tom para o mercado BR
2. Confirmar estratégia de WhatsApp
3. Ajustar parcelamento e precificação BR
4. Identificar cases BR necessários para prova social

### FASE 4 — Funil Completo (launch-strategist)

1. Confirmar sequência de lançamento
2. Criar sequência de emails do PLC
3. Definir sequência do open cart
4. Estruturar close cart

### FASE 5 — Documento Final de Produto

Entregar o "Produto Blueprint" completo.

## Template de Produto Blueprint

```markdown
# PRODUTO BLUEPRINT: {Nome do Produto}

## A Oferta
- **Nome do Produto:** {nome com marca própria}
- **Mecanismo Único:** {nome proprietário do método}
- **Promessa Principal:** {resultado em prazo com mecanismo}
- **Ticket:** R${X} (parcelado em {Y}x de R${Z})

## Value Stack
| Item | Valor Individual | Função |
|------|-----------------|--------|
| Core: {nome} | R${X} | Entrega principal |
| Bônus 1: {nome} | R${X} | Resolve objeção: {qual} |
| Bônus 2: {nome} | R${X} | Resolve objeção: {qual} |
| Bônus 3: {nome} | R${X} | Amplifica: {qual desejo} |
| **Total Percebido** | **R${total}** | |
| **Preço** | **R${real}** | {X}% do valor percebido |

## Garantia
{Tipo, duração e condições}

## Headline Principal
1. {headline 1}
2. {headline 2}
3. {headline 3}

## Narrativa Central
- **Domino:** {o argumento central}
- **Origin Story:** {resumo da história}
- **Future Pacing:** {como o avatar se imagina após o produto}

## Funil
{Estrutura resumida do funil}

## Adaptações BR
- Parcelamento: {estrutura}
- WhatsApp: {como usar no funil}
- Cases BR necessários: {lista}
```

## Acceptance Criteria

- [ ] Promessa principal com número + prazo + mecanismo nomeado
- [ ] Value stack com 5+ itens e valores individuais
- [ ] Price-to-value ratio >= 10x
- [ ] Garantia estruturada
- [ ] 3 variações de headline
- [ ] Domino identificado e validado
- [ ] Origin story estruturada
- [ ] Funil completo definido
- [ ] Adaptações BR incorporadas
- [ ] Produto Blueprint entregue
