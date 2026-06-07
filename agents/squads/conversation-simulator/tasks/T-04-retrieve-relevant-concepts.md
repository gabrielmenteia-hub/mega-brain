# T-04 — retrieve-relevant-concepts

**ID:** T-04
**Executor:** knowledge-retriever
**Workflow:** WF-01 (paralelo com T-03)

## Propósito
Buscar os conceitos mais relevantes da base de conhecimento para o contexto da mensagem atual.

## Inputs
- `user_message` — texto da mensagem do usuário
- `history_last_3` — últimos 3 turnos da conversa (contexto)
- `user_level` — nível atual do usuário (1-6)
- `scenario` — cenário da sessão (para filtro)

## Steps
1. Montar query combinando mensagem + contexto recente
2. Gerar embedding da query (OpenAI text-embedding-3-small)
3. Executar busca no Qdrant com filtros:
   - `nivel_minimo` ≤ `user_level`
   - `cenario` = cenário da sessão
4. Retornar top-3 conceitos por score de similaridade
5. Se Qdrant indisponível → usar fallback por keyword

## Output
```json
{
  "concepts": [
    {
      "id": "frame_control_001",
      "nome": "Frame Control",
      "score_similaridade": 0.89,
      "principio": "...",
      "aplicacao_pratica": "...",
      "red_flags": [...],
      "green_flags": [...]
    }
  ],
  "fallback_used": false
}
```

## Condições de Bloqueio
- Qdrant indisponível → fallback automático (não bloqueia)
