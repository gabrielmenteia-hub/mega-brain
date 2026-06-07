# RESUME SESSION - Recuperação de Contexto

## Trigger
`/resume` ou ao iniciar nova conversa

## Objetivo
Recuperar o contexto COMPLETO da última sessão para continuar de onde parou.

## Execução

### 1. Localizar Última Sessão
Ler `.Codex/sessions/LATEST-SESSION.md` para encontrar a sessão mais recente.

### 2. Carregar Contexto
Ler o arquivo de sessão completo e extrair:
- Estado da missão
- Fase atual
- Pendências
- Próximos passos
- Decisões tomadas
- Notas importantes

### 3. Apresentar Resumo de Retomada

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  🔄 RETOMANDO SESSÃO                                                         │
│                                                                              │
│  Última atividade: [DATA/HORA]                                              │
│  Duração desde última sessão: [X horas/dias]                                │
│                                                                              │
│  📍 ONDE PARAMOS:                                                            │
│  Missão: [NOME]                                                              │
│  Fase: [N] de 5 - [NOME_FASE]                                               │
│  Progresso: [X]%                                                             │
│                                                                              │
│  📋 PENDÊNCIAS HERDADAS:                                                     │
│  - [Pendência 1]                                                             │
│  - [Pendência 2]                                                             │
│                                                                              │
│  ➡️ PRÓXIMO PASSO PLANEJADO:                                                 │
│  [Descrição do próximo passo]                                                │
│                                                                              │
│  💡 DECISÕES ANTERIORES:                                                     │
│  - [Decisão relevante]                                                       │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 4. Perguntar Confirmação
"Quer continuar de onde paramos ou precisa de algo diferente?"

### 5. Listar Sessões Antigas (Opcional)
Se usuário pedir, listar todas as sessões disponíveis:
```
/resume list - mostra todas as sessões salvas
/resume [SESSION-ID] - carrega sessão específica
```

## Output
Contexto recuperado + resumo visual + confirmação do usuário
