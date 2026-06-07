# Conversation Simulator Squad

Squad para simulação de conversas com Coach IA para desenvolvimento de comunicação masculina assertiva.

## O que faz

Simula conversas com personagens femininas IA, analisa cada mensagem do usuário em 5 dimensões e entrega feedback em tempo real fundamentado em 89 conceitos extraídos de 6 livros especializados.

## Pipeline de uma conversa

```
[Usuário envia mensagem]
        │
        ▼
session-manager     ← salva mensagem (T-02)
        │
   ┌────┴────┐
   ▼         ▼
character  knowledge         ← paralelo (T-03 || T-04)
-engine    -retriever
   │         │
   └────┬────┘
        ▼
  coach-analyzer             ← analisa em 5 dimensões (T-05)
        │
        ▼
  feedback-writer            ← narrativa do Coach (T-06)
        │
        ▼
  progress-tracker           ← XP + skills (T-07, T-08)
        │
        ▼
[Resposta completa ao usuário]
```

## Agentes

| Agente | Tier | Papel |
|--------|------|-------|
| `simulation-chief` | 1 — Chief | Orquestra todo o fluxo |
| `character-engine` | 2 — Specialist | Personagens IA com personalidades distintas |
| `coach-analyzer` | 2 — Specialist | Análise multidimensional (5 scores) |
| `knowledge-retriever` | 2 — Specialist | Busca semântica nos 89 conceitos |
| `progress-tracker` | 2 — Specialist | XP, níveis e skills |
| `feedback-writer` | 3 — Executor | Narrativa do Coach |
| `session-manager` | 3 — Executor | Estado e histórico da sessão |

## Personagens disponíveis

| ID | Nome | Personalidade | Dificuldade |
|----|------|---------------|-------------|
| `casual_fun` | Camila, 24 | Extrovertida, espontânea | Média |
| `intellectual` | Marina, 28 | Introspectiva, conversas profundas | Alta |
| `high_value` | Isabela, 26 | Exigente, frame forte | Muito Alta |
| `girl_next_door` | Julia, 23 | Simpática, genuína | Baixa |

## Cenários

| ID | Cenário |
|----|---------|
| `match_no_app` | Primeira mensagem no Tinder/Bumble |
| `primeira_mensagem` | Continuação do match |
| `primeiro_encontro` | Conversa no encontro |
| `testes_e_objecoes` | Shit tests e objeções |
| `escalacao` | Escalação de interesse |

## Modos de treino

| Modo | Descrição | Plano |
|------|-----------|-------|
| LIVRE | Coach analisa depois de enviar | FREE, PRO, MASTER |
| GUIADO | Coach analisa antes de enviar | PRO, MASTER |
| DESAFIO | Sem dicas, avaliação no final | PRO, MASTER |

## Comandos

```
*simulate [cenário] [personagem] [modo]   → Iniciar sessão
*end                                       → Encerrar sessão
*status                                    → Estado atual da sessão
*progress                                  → Ver XP e skills
*library [query]                           → Buscar conceitos
```

## Exemplos de uso

```
*simulate testes_e_objecoes high_value guiado
*simulate match_no_app casual_fun livre
*simulate primeiro_encontro intellectual desafio
*library "como responder shit test"
```

## Dimensões de análise

| Dimensão | O que mede |
|----------|-----------|
| Confiança | Tonalidade assertiva, ausência de hedging |
| Frame | Manutenção de liderança, não ceder à pressão |
| Calibração | Timing correto, leitura da situação |
| Polaridade | Energia masculina, tensão sexual |
| Assertividade | Clareza de intenção, diretividade |

## Estrutura de arquivos

```
conversation-simulator/
├── config.yaml
├── README.md
├── agents/
│   ├── simulation-chief.md
│   ├── character-engine.md
│   ├── coach-analyzer.md
│   ├── knowledge-retriever.md
│   ├── progress-tracker.md
│   ├── feedback-writer.md
│   └── session-manager.md
├── tasks/
│   ├── T-01-create-session.md
│   ├── T-02-receive-user-message.md
│   ├── T-03-generate-character-response.md
│   ├── T-04-retrieve-relevant-concepts.md
│   ├── T-05-analyze-user-message.md
│   ├── T-06-write-coach-feedback.md
│   ├── T-07-compute-session-xp.md
│   ├── T-08-update-user-progress.md
│   ├── T-09-end-session.md
│   └── T-10-preview-coach-analysis.md
└── workflows/
    ├── WF-01-main-conversation.yaml
    ├── WF-02-guided-mode.yaml
    ├── WF-03-start-session.yaml
    └── WF-04-end-session.yaml
```

## Base de conhecimento (pré-requisito)

Este squad requer a base de conhecimento já processada:
- `unified_knowledge_base.json` — 89 conceitos unificados
- Qdrant collection `seduction_knowledge` populada com embeddings

Gerados pelos scripts: `unified_knowledge_processor.py` e `vector_db_setup.py`

## Score mínimo de qualidade: 7.0 / 10.0
