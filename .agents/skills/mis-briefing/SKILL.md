# MIS BRIEFING — Market Intelligence Status

> **Auto-Trigger:** "mis briefing", "produtos campeões", "radar de mercado"
> **Keywords:** mis briefing, produtos campeões, radar de mercado, market intelligence
> **Prioridade:** MÉDIA

---

## Conceito

Gera briefing visual dos dados do Market Intelligence System (MIS): produtos campeões, radar de dores e saúde dos scrapers.

---

## Trigger

`/mis-briefing`

## Pré-requisitos

- `mis/` instalado (repo MIS acessível)
- `MIS_PATH` configurado no `.env` do MEGABRAIN (caminho absoluto ao repo MIS)
- `MIS_DB_PATH` configurado no `.env` do MEGABRAIN (caminho absoluto ao `mis.db`)
- Pelo menos 1 ciclo de scanner executado (`python -m mis spy --url <URL>`)

---

## Execução

### 1. Carregar Dados do MIS

```bash
python -c "
import sys, os
sys.path.insert(0, os.environ['MIS_PATH'])
from mis.mis_agent import get_briefing_data
import json
data = get_briefing_data()
print(json.dumps(data, default=str, ensure_ascii=False))
"
```

Se retornar `status='error'`: exibir mensagem de erro + setup_hint. Não prosseguir.

Se MIS_PATH não estiver no ambiente: exibir `"MIS não encontrado. Configure MIS_PATH no .env e execute python -m mis para inicializar."`

### 2. Calcular e Formatar o Briefing

Usar os dados retornados para montar o briefing visual com containers JARVIS-style (largura 120 chars):

```
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║  MIS — MARKET INTELLIGENCE BRIEFING                                                              {ISO_TIMESTAMP}    ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║  HEALTH SCORE: {score}/100  [{barra_16_blocos}]                                                                     ║
║  {OK / FALHA} por scraper  |  Último ciclo: {last_cycle ou "N/A"}  {(DADOS ANTIGOS) se data_stale}                 ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║  TOP-10 PRODUTOS CAMPEOES                                                                                            ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║  #1  {nome}  [{plataforma}]  [{nicho}]  Score: {score}                                                              ║
║  ...                                                                                                                 ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║  PAIN RADAR — TOP-5 DORES POR NICHO                                                                                 ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║  [{nicho}]                                                                                                           ║
║    1. [{Alto/Medio/Baixo}] {descricao da dor}                                                                       ║
║  ...                                                                                                                 ║
[SECAO ALERTAS — apenas se unseen_alerts > 0]
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║  NOVOS CAMPEOES ({N} alertas nao vistos)                                                                            ║
║    - {produto} | {nicho} | #{posicao} | {data}                                                                      ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║  Dashboard: http://localhost:8000  |  DB: {db_path}                                                                 ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

**Regras de formatação:**
- Barra de progresso do Health Score: 16 blocos — `int(score/100 * 16)` blocos `█`, restante `░`
- Lista vazia de produtos: exibir `║  Nenhum produto encontrado. Execute os scanners primeiro.`
- Lista vazia de dores: exibir `║  Nenhum relatorio disponivel para este nicho.`
- Secao Alertas: omitida completamente se `unseen_alerts == 0`
- Estado de erro: substituir o container por mensagem simples — `"MIS nao encontrado. Execute python -m mis para inicializar."`

### 3. Exibir

Imprimir o briefing diretamente no chat. Nao salvar em arquivo (diferente do jarvis-briefing).

---

## Saida Esperada

Briefing visual completo com:
- Health Score e status dos scrapers
- Top-10 produtos campeoes com score de oportunidade
- Top-5 dores por nicho com nivel de interesse
- Alertas de novos campeoes (se houver)
- Link para dashboard e caminho do DB
