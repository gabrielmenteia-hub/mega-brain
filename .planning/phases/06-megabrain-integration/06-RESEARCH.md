# Phase 6: MEGABRAIN Integration - Research

**Researched:** 2026-03-15
**Domain:** Python module bridge, MEGABRAIN skill system, cross-repo integration, markdown export
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- `/mis-briefing` e skill standalone em `.claude/skills/mis-briefing/SKILL.md` — nao integrado ao /jarvis-briefing
- `mis_agent.py` fica dentro de `mis/` (nao no MEGABRAIN) — versionado junto com o MIS
- Apenas 2 funcoes publicas no MVP: `get_briefing_data() -> dict` e `export_to_megabrain(dest=None) -> dict`
- Sem CLI propria em `mis_agent.py` — arquivo so importado
- Invocacao do skill via Bash tool: `python -c "import sys; sys.path.insert(0, os.environ['MIS_PATH']); from mis.mis_agent import get_briefing_data"`
- Erros retornam dict `{'status': 'error', 'message': '...', 'setup_hint': '...'}` — sem excecoes propagadas
- `run_migrations()` chamado no import do `mis_agent.py`
- Subcomando `export` adicionado ao `mis/__main__.py` com argparse (`--dest` flag)
- Formato de exportacao: Markdown + frontmatter YAML
- Destino padrao do export: `{MEGABRAIN_PATH}/knowledge/mis/`
- Export incremental — nao re-exporta arquivos sem mudanca
- Indice `knowledge/mis/README.md` gerado/atualizado a cada export
- Naming convention: `dossier_{platform}_{product_id}.md` e `pain_{niche}_{YYYYMMDD}.md`
- Variaveis de ambiente a adicionar no MEGABRAIN .env: `MIS_PATH`, `MIS_DB_PATH`, `MEGABRAIN_PATH`
- Documentacao em `CLAUDE.md` do MEGABRAIN — secao "MIS Integration"
- 3 cenarios de teste obrigatorios em `mis/tests/test_mis_agent.py` com SQLite in-memory
- Formato visual JARVIS-style: containers `╔═══╗`, largura padrao MEGABRAIN, barras `████████░░░░`
- Health Score 0-100: scrapers saudaveis=40pts, ciclo completado nas ultimas 2h=30pts, dossies gerados hoje > 0=20pts, sem falha critica de alertas=10pts
- Top-10 produtos campeoes por score de oportunidade decrescente
- Top-5 dores por nicho configurado com nivel de interesse (Alto/Medio/Baixo)
- Secao Alertas exibida somente se houver alertas nao vistos — ate 5 entradas
- Rodape: `Dashboard: http://localhost:8000 | DB: {MIS_DB_PATH}`
- Alerta "Dados antigos" se ultimo ciclo > 2h
- Estado vazio: mensagem sem stack trace
- Export de dossies completos (status=complete) + pain reports dos ultimos 7 dias; dossies incompletos ignorados
- Estrutura de dossie exportado: `## Por que Vende`, `## Copy`, `## Anuncios`, `## Reviews`, `## Template`
- Logging via structlog: `event='export_file', file=path, type=dossier|pain_report`
- Output silencioso durante export; resumo final no terminal
- Destino criado automaticamente se nao existir
- Sem dry-run automatico

### Claude's Discretion

- Estrutura interna de `get_briefing_data()` (como agrega dados dos repositorios)
- Implementacao exata do calculo do Health Score (pesos dos fatores)
- Formato exato do ASCII art do briefing (espacamento, separadores dentro dos containers)
- Como detectar "ciclo mais recente" (query no banco)
- Implementacao do hash para export incremental (MD5 do conteudo vs comparacao de data)

### Deferred Ideas (OUT OF SCOPE)

- Integracao do MIS com `/jarvis-briefing` (mencao proativa de novos campeoes no briefing diario)
- `get_dossier(product_id)` e `search_products(query)` no mis_agent.py
- Auto-export apos cada ciclo do scanner
- Skill `/mis-export` separado
- Contrato formal de API version em mis_agent.py (`__api_version__`)
- Flag `--dry-run` no subcomando export
- Filtros no /mis-briefing por nicho (--nicho) ou quantidade (--top N)
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| INT-01 | MIS integrado ao MEGABRAIN como modulo independente (`mis/`) com unico ponto de integracao (`mis_agent.py`) | Bridge pattern: `mis_agent.py` expoe apenas 2 funcoes publicas; skill invoca via sys.path injection; nenhuma alteracao na estrutura interna do MIS |
| INT-02 | Usuario pode invocar analise do MIS via agente/comando dentro do MEGABRAIN | SKILL.md em `.claude/skills/mis-briefing/` com auto-trigger keywords; skill_indexer.py registra automaticamente no SessionStart; invocacao via `/mis-briefing` |
</phase_requirements>

---

## Summary

Esta fase implementa a camada de integracao entre o MIS (Market Intelligence System) e o MEGABRAIN. O MIS ja esta completamente construido (fases 1-5): banco SQLite com produtos, dossies, pain reports e alertas; repositorios de acesso; dashboard web. Esta fase e exclusivamente sobre expor dados do MIS para o ecossistema MEGABRAIN sem alterar a logica interna do MIS.

O ponto central e o `mis_agent.py`: um arquivo bridge dentro de `mis/` que encapsula toda a logica de acesso ao banco e expoe uma API minima e estavel. O MEGABRAIN nunca acessa o SQLite diretamente — tudo passa por este arquivo. A invocacao e feita via `sys.path.insert` e `python -c` porque o MIS e um repo separado, nao um pacote instalado no ambiente do MEGABRAIN.

O skill `/mis-briefing` e um documento Markdown em `.claude/skills/mis-briefing/SKILL.md` que instrui Claude Code a chamar `mis_agent.get_briefing_data()` via Bash tool e renderizar o resultado no formato visual JARVIS padrao. O subcomando `export` adiciona ao CLI do MIS a capacidade de gerar arquivos Markdown compatíveis com o pipeline de conhecimento do MEGABRAIN em `knowledge/mis/`.

**Primary recommendation:** Implementar na ordem: (1) `mis_agent.py` + testes, (2) subcomando `export` no `__main__.py`, (3) skill SKILL.md, (4) variaveis de ambiente + documentacao CLAUDE.md. Cada entrega e independente e testavel.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| sqlite3 | stdlib | Acesso direto ao DB para queries de briefing | Ja usado em alert_repository.py; evita overhead do sqlite_utils |
| sqlite_utils | instalado | Acesso via get_db() para queries complexas | Padrao do projeto desde Phase 1 |
| structlog | instalado | Logging do export (event='export_file') | Padrao universal do projeto |
| pathlib.Path | stdlib | Manipulacao de caminhos cross-platform | Convencao explicita do CLAUDE.md do projeto |
| hashlib (md5) | stdlib | Hash incremental para detectar mudancas no export | Sem dependencias externas |
| python-dotenv | instalado | Leitura de MIS_DB_PATH e MIS_PATH do .env | Ja usado em config.py do MIS |
| argparse | stdlib | Subcomando `export` no __main__.py | Padrao ja estabelecido (spy, radar, dashboard) |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| datetime (stdlib) | stdlib | Calculo de "ciclo nas ultimas 2h", filtro dos ultimos 7 dias | Timestamps ISO no SQLite |
| os.environ | stdlib | Leitura de MIS_PATH, MEGABRAIN_PATH no skill | Complementa python-dotenv quando rodando via Bash tool |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| MD5 hash do conteudo | Comparacao de data (updated_at) | Hash e mais robusto para detectar mudancas de conteudo real; data pode ser enganosa se registro foi re-gravado sem mudanca |
| sys.path.insert para importar MIS | MIS instalado como pacote pip | pip install requer manutencao de versao; sys.path e zero-overhead para repo local |
| sqlite3 direto para health check | get_db() + sqlite_utils | Alert_repository ja usa sqlite3 direto para WAL safety; consistente manter o mesmo padrao para queries simples |

**Installation:**
```bash
# Sem novas dependencias — tudo usa bibliotecas ja instaladas no MIS
# Verificar que python-dotenv e structlog estao no requirements.txt do MIS (ja estao)
```

---

## Architecture Patterns

### Recommended Project Structure

```
mis/
├── mis_agent.py          # NOVO — bridge MIS/MEGABRAIN (unico arquivo que cruza a fronteira)
├── tests/
│   └── test_mis_agent.py # NOVO — 3 cenarios: DB vazio, DB com dados, export incremental
├── __main__.py           # MODIFICADO — adicionar subcomando 'export'
└── [demais arquivos sem alteracao]

.claude/
└── skills/
    └── mis-briefing/     # NOVO — skill standalone
        └── SKILL.md

.claude/CLAUDE.md         # MODIFICADO — adicionar secao "MIS Integration"

knowledge/
└── mis/                  # CRIADO automaticamente no primeiro export
    ├── README.md          # indice gerado pelo export
    ├── dossier_hotmart_42.md
    └── pain_marketing-digital_20260315.md

.env (MEGABRAIN)          # MODIFICADO — adicionar MIS_PATH, MIS_DB_PATH, MEGABRAIN_PATH
```

### Pattern 1: Bridge via sys.path injection

**What:** O skill invoca `mis_agent.py` sem que o MIS seja um pacote instalado. Claude Code executa um comando Bash que injeta o caminho do MIS no sys.path antes de importar.

**When to use:** Quando dois repos precisam se comunicar sem dependencia de packaging. Padrao estabelecido pelo CONTEXT.md.

**Example:**
```python
# Invocacao pelo skill (via Bash tool no Claude Code):
python -c "
import sys, os
sys.path.insert(0, os.environ['MIS_PATH'])
from mis.mis_agent import get_briefing_data
import json
result = get_briefing_data()
print(json.dumps(result))
"
```

### Pattern 2: Bridge retorna sempre dict com status

**What:** `mis_agent.py` nunca propaga excecoes. Retorna `{'status': 'ok', 'data': ...}` ou `{'status': 'error', 'message': '...', 'setup_hint': '...'}`. O skill verifica o status antes de renderizar.

**When to use:** Padrao obrigatorio definido no CONTEXT.md para todas as funcoes publicas do bridge.

**Example:**
```python
# mis/mis_agent.py — estrutura de retorno
def get_briefing_data() -> dict:
    try:
        db_path = os.environ.get("MIS_DB_PATH")
        if not db_path:
            return {
                "status": "error",
                "message": "MIS_DB_PATH nao configurado",
                "setup_hint": "Adicione MIS_DB_PATH ao .env do MEGABRAIN"
            }
        run_migrations(db_path)
        # ... agregacao de dados ...
        return {"status": "ok", "data": {...}}
    except Exception as exc:
        return {"status": "error", "message": str(exc), "setup_hint": "..."}
```

### Pattern 3: Export incremental com hash MD5

**What:** Antes de escrever um arquivo de export, calcular MD5 do conteudo gerado. Se o arquivo ja existe e o hash bate, pular. Se e novo ou hash diferente, escrever.

**When to use:** Chamado por `export_to_megabrain()` para cada dossier e pain report.

**Example:**
```python
import hashlib
from pathlib import Path

def _write_if_changed(dest_path: Path, content: str) -> bool:
    """Returns True if file was written, False if skipped (unchanged)."""
    new_hash = hashlib.md5(content.encode()).hexdigest()
    if dest_path.exists():
        existing_hash = hashlib.md5(dest_path.read_bytes()).hexdigest()
        if new_hash == existing_hash:
            return False
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(content, encoding="utf-8")
    return True
```

### Pattern 4: Subcomando argparse seguindo padrao estabelecido

**What:** Adicionar `export` como novo subparser em `__main__.py`, seguindo exatamente o mesmo padrao de `spy`, `radar` e `dashboard`.

**When to use:** Unico padrao de CLI no projeto.

**Example:**
```python
# mis/__main__.py — adicionar ao bloco de subparsers
export_parser = subparsers.add_parser(
    "export",
    help="Export dossiers and pain reports to MEGABRAIN knowledge base",
)
export_parser.add_argument(
    "--dest",
    metavar="PATH",
    default=None,
    help="Destination directory (default: MEGABRAIN_PATH/knowledge/mis/)",
)

# ... no dispatch:
elif args.command == "export":
    _handle_export(args)
```

### Pattern 5: SKILL.md com instrucoes de invocacao

**What:** O SKILL.md nao e codigo Python — e um documento Markdown que instrui Claude Code sobre como usar o skill. O skill executa Python via Bash tool.

**When to use:** Padrao universal de skills no MEGABRAIN (referencia: `.claude/skills/jarvis-briefing/SKILL.md`).

**Key properties do SKILL.md:**
- Header com `Auto-Trigger:` e `Keywords:` para o `skill_router.py` detectar automaticamente
- Secao "Pre-requisitos" documentando variaveis de ambiente necessarias
- Instrucoes de como chamar `mis_agent.py` via Bash tool
- Template visual do output esperado (JARVIS-style)

### Anti-Patterns to Avoid

- **Acessar SQLite diretamente no skill:** O skill NUNCA deve ter queries SQL — tudo passa pelo `mis_agent.py`. Viola o contrato de fronteira unica.
- **Propagar excecoes do mis_agent.py:** Toda funcao publica deve ter try/except abrangente e retornar dict com status. Um erro no MIS nao deve quebrar a sessao do MEGABRAIN.
- **Importar mis_agent.py em nivel de modulo no skill:** O skill chama Python via subprocess/Bash tool, nao importa diretamente. Repos separados.
- **Re-exportar arquivos sem mudanca:** Export incremental e obrigatorio — sem ele o `knowledge/mis/` vai acumular arquivos com timestamps antigos sem valor.
- **Criar CLAUDE.md dentro de mis/:** Politica explicita do projeto — apenas 2 CLAUDE.md validos (root e .claude/CLAUDE.md).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Hash para export incremental | Sistema de timestamps customizado | `hashlib.md5` stdlib | Timestamps sao enganosos; hash detecta mudanca real de conteudo |
| Parsing de dossier_json | Leitura direta de colunas | `json.loads(dossier_json)` ja em `dossier_repository.get_dossier_by_product_id()` | Logica ja implementada e testada |
| Deteccao de "ciclo recente" | Logica de tempo customizada | Query `SELECT MAX(cycle_at) FROM pain_reports` + `datetime.fromisoformat()` | Banco ja armazena `cycle_at` ISO em todos os pain_reports |
| Status de saude dos scrapers | Novo sistema de monitoramento | `health_monitor.run_platform_canary()` existente | Ja implementado em Phase 1 com logging estruturado |
| Criacao de diretorios de destino | Guards manuais | `Path.mkdir(parents=True, exist_ok=True)` | Padrao stdlib — sem verificacao manual necessaria |

**Key insight:** O MIS ja tem toda a logica de acesso a dados encapsulada em repositorios. O `mis_agent.py` e apenas um agregador que chama funcoes ja testadas — nao deve duplicar logica de acesso ao banco.

---

## Common Pitfalls

### Pitfall 1: MIS_PATH vs MIS_DB_PATH confusao

**What goes wrong:** `MIS_PATH` aponta para o diretorio raiz do MIS (pai de `mis/`), nao para o diretorio `mis/`. O sys.path.insert deve receber `MIS_PATH` para que `from mis.mis_agent import ...` funcione.

**Why it happens:** Nomenclatura pode confundir — "MIS_PATH" parece que e o caminho para o modulo Python, mas na verdade e o caminho para o repo.

**How to avoid:** Documentar claramente no SKILL.md: `MIS_PATH = caminho para /Users/gabriel/mis-repo` (o pai de `mis/`). O import e `from mis.mis_agent import ...`, nao `from mis_agent import ...`.

**Warning signs:** `ModuleNotFoundError: No module named 'mis'` — significa que MIS_PATH esta apontando para dentro do repo em vez do repo raiz.

### Pitfall 2: run_migrations() no import pode ser lento ou falhar

**What goes wrong:** `mis_agent.py` chama `run_migrations(db_path)` ao ser importado. Se `MIS_DB_PATH` nao estiver configurado, isso falha no momento do import, gerando mensagem de erro obscura.

**Why it happens:** A migracao e idempotente mas requer acesso ao arquivo de banco. Se o path esta errado, o erro vem antes de qualquer logica de negocio.

**How to avoid:** Verificar `MIS_DB_PATH` antes de chamar `run_migrations()`. Retornar `{'status': 'error', 'message': 'MIS_DB_PATH nao configurado'}` se ausente. A migracao deve ser chamada dentro de um try/except no nivel do `get_briefing_data()`, nao no modulo global.

**Warning signs:** `OperationalError: unable to open database file` no import do mis_agent.

### Pitfall 3: get_db() vs sqlite3.connect() no mis_agent

**What goes wrong:** `get_db()` usa `isolation_level=None` (autocommit) e WAL. Para leituras no `mis_agent.py`, isso e correto. Mas o `export_to_megabrain()` nao escreve no banco — so le e grava arquivos. Usar get_db() para leituras e adequado.

**Why it happens:** Alert_repository usa sqlite3.connect direto por causa de conflitos de WAL em escrita multi-conexao. `mis_agent.py` e read-only no banco, entao get_db() e safe.

**How to avoid:** Usar `get_db()` para leituras no bridge (consistente com dossier_repository e pain_repository). Reservar sqlite3.connect direto para operacoes de escrita.

### Pitfall 4: Pain reports sem niche_id disponivel no bridge

**What goes wrong:** `pain_repository.get_latest_report()` requer `niche_id` (int), nao `niche_slug`. O mis_agent precisa resolver slug -> id antes de chamar o repositorio.

**Why it happens:** A API do repositorio usa IDs internos para join com a tabela niches. O config.yaml expoe slugs.

**How to avoid:** No `get_briefing_data()`, iterar `config.settings.niches` para obter slugs, depois fazer query `SELECT id FROM niches WHERE slug = ?` para obter o niche_id antes de chamar `get_latest_report()`.

### Pitfall 5: Frontmatter YAML com campos especiais

**What goes wrong:** Campos como `score: 8.5` sao floats validos em YAML. Mas campos como `product_id: 1234abcd` podem ser interpretados como string ou int dependendo do parser. `niche: marketing-digital` com hifen pode precisar de aspas.

**Why it happens:** PyYAML tem regras de quoting automatico que nem sempre sao obvias para valores com hifens, pontos ou valores que parecem numeros.

**How to avoid:** Usar `yaml.dump()` com `default_flow_style=False` para gerar frontmatter ou construir o frontmatter manualmente como string f-string — mais previsivel para o pipeline do MEGABRAIN que vai parsear esses arquivos.

---

## Code Examples

Verified patterns from existing codebase:

### Leitura de niche_id a partir de slug (query direta)

```python
# Padrao do pain_repository.py (linha 62-65) — ja validado em producao
niche_row = db.execute(
    "SELECT id FROM niches WHERE slug = ?", [niche_slug]
).fetchone()
niche_id = niche_row[0] if niche_row else None
```

### Top-N produtos por opportunity_score (adaptacao de list_dossiers_by_rank)

```python
# Baseado em dossier_repository.list_dossiers_by_rank — usando order_by opportunity_score
products = list_dossiers_by_rank(
    db_path=db_path,
    order_by="opportunity_score",  # coluna existente na tabela dossiers
    order_dir="desc",
    per_page=10,  # top-10 conforme CONTEXT.md
    page=1,
)
```

### Deteccao de ciclo mais recente (query no banco)

```python
# Query direta — pain_reports.cycle_at e ISO string
import sqlite3
from datetime import datetime, timezone, timedelta

with sqlite3.connect(db_path) as conn:
    row = conn.execute(
        "SELECT MAX(cycle_at) FROM pain_reports"
    ).fetchone()
last_cycle = row[0] if row and row[0] else None

if last_cycle:
    last_cycle_dt = datetime.fromisoformat(last_cycle)
    if last_cycle_dt.tzinfo is None:
        last_cycle_dt = last_cycle_dt.replace(tzinfo=timezone.utc)
    age_hours = (datetime.now(timezone.utc) - last_cycle_dt).total_seconds() / 3600
    data_stale = age_hours > 2
```

### Contagem de dossies gerados hoje

```python
# Usando coluna created_at adicionada em _005 migration
import sqlite3
from datetime import datetime, timezone

today_start = datetime.now(timezone.utc).replace(
    hour=0, minute=0, second=0, microsecond=0
).isoformat()

with sqlite3.connect(db_path) as conn:
    row = conn.execute(
        "SELECT COUNT(*) FROM dossiers WHERE created_at >= ? AND status = 'complete'",
        [today_start]
    ).fetchone()
dossiers_today = row[0] if row else 0
```

### Estrutura de frontmatter YAML para export

```python
# Construcao manual — mais previsivel que yaml.dump para frontmatter
def _render_dossier_md(product: dict, dossier: dict) -> str:
    lines = [
        "---",
        f"source: mis",
        f"type: dossier",
        f"platform: {product['platform_slug']}",
        f"niche: {product['niche_slug']}",
        f"score: {dossier.get('opportunity_score', 0)}",
        f"date: {dossier.get('created_at', '')[:10]}",
        f"product_id: {product['id']}",
        "---",
        "",
        f"# {product['title']}",
        "",
        "## Por que Vende",
        # ... extrair de dossier_json
    ]
    return "\n".join(lines)
```

### Invocacao assincronca de run_canary_check no contexto sincrono do mis_agent

```python
# health_monitor.run_canary_check() e async — no mis_agent (sincrono) usar asyncio.run()
import asyncio
from mis.health_monitor import run_canary_check

try:
    canary_ok = asyncio.run(run_canary_check())
except Exception:
    canary_ok = False
```

### Estrutura do SKILL.md (baseado em jarvis-briefing como referencia)

```markdown
# MIS BRIEFING - Market Intelligence Summary

> **Auto-Trigger:** quando usuario pede briefing do MIS ou status de mercado
> **Keywords:** "mis briefing", "produtos campeoes", "radar de mercado"
> **Prioridade:** MEDIA

## Pre-requisitos

- `mis/` instalado em `MIS_PATH`
- `MIS_PATH` e `MIS_DB_PATH` configurados no `.env` do MEGABRAIN
- Pelo menos 1 ciclo de scanner executado

## Execucao

[instrucoes para Claude Code executar via Bash tool]
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Import direto entre repos | sys.path.insert + python -c | Decisao do CONTEXT.md | Mantém repos independentes sem packaging overhead |
| Skills com codigo Python inline | SKILL.md como instrucoes para Claude Code | Padrao MEGABRAIN v2.0 | Claude Code executa via Bash tool, nao inline |
| Dossier com ads_json como TEXT | ads_json TEXT para MVP | Phase 03 decision | Flexibilidade para JSON nao estruturado |

---

## Open Questions

1. **Comportamento de run_canary_check() no mis_agent sincrono**
   - What we know: `run_canary_check()` e `async` — requer `asyncio.run()` em contexto sincrono
   - What's unclear: Se ja existe um event loop rodando quando mis_agent e importado (ex: dentro do dashboard FastAPI)
   - Recommendation: No MVP, o mis_agent sera chamado via `python -c` (processo separado), entao `asyncio.run()` e seguro. Se futuramente for chamado de dentro do dashboard, adicionar `asyncio.get_event_loop().run_until_complete()` com fallback.

2. **opportunity_score pode ser NULL para produtos sem dossie**
   - What we know: `list_dossiers_by_rank` faz LEFT JOIN — produtos sem dossie aparecem com `opportunity_score=None`
   - What's unclear: O briefing deve mostrar apenas produtos COM dossie, ou todos os top-10 por rank?
   - Recommendation: Filtrar para `has_dossier=True` no mis_agent. O briefing e sobre "produtos campeoes com analise IA", nao ranking bruto.

3. **Formato de `language` no config.yaml**
   - What we know: CONTEXT.md diz "idioma das dores conforme configuracao `language` do nicho no config.yaml"
   - What's unclear: O config.yaml atual nao tem campo `language` por nicho — tem `relevance_language` dentro do bloco `radar`
   - Recommendation: Usar `niche['radar']['relevance_language']` como proxy para `language`. O planner deve mapear isso explicitamente no PLAN.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (pytest-asyncio) com asyncio_mode = auto |
| Config file | `mis/pytest.ini` — `asyncio_mode = auto`, `testpaths = tests`, `timeout = 10` |
| Quick run command | `cd mis && python -m pytest tests/test_mis_agent.py -x` |
| Full suite command | `cd mis && python -m pytest tests/ -x` |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INT-01 | `get_briefing_data()` retorna dict com status='ok' e estrutura correta (DB vazio) | unit | `python -m pytest tests/test_mis_agent.py::test_get_briefing_data_empty_db -x` | Wave 0 |
| INT-01 | `get_briefing_data()` retorna top-10 produtos e pain reports (DB com dados) | unit | `python -m pytest tests/test_mis_agent.py::test_get_briefing_data_with_data -x` | Wave 0 |
| INT-01 | `export_to_megabrain()` nao re-exporta arquivos sem mudanca | unit | `python -m pytest tests/test_mis_agent.py::test_export_incremental -x` | Wave 0 |
| INT-02 | SKILL.md existe em `.claude/skills/mis-briefing/SKILL.md` | smoke | `python -c "from pathlib import Path; assert Path('.claude/skills/mis-briefing/SKILL.md').exists()"` | Wave 0 |
| INT-02 | mis_agent.py importavel via sys.path.insert | unit | `python -m pytest tests/test_mis_agent.py -x` | Wave 0 |

### Sampling Rate

- **Per task commit:** `cd mis && python -m pytest tests/test_mis_agent.py -x`
- **Per wave merge:** `cd mis && python -m pytest tests/ -x`
- **Phase gate:** Full suite green antes de `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `mis/tests/test_mis_agent.py` — cobre INT-01 (3 cenarios obrigatorios) e INT-02
- [ ] Fixture de DB populado com produtos + dossiers + pain_reports + alertas para testes com dados

*(Infraestrutura de testes existente (pytest.ini, conftest.py, db_path fixture) ja cobre o resto — sem novos arquivos de config necessarios)*

---

## Sources

### Primary (HIGH confidence)

- Inspecao direta de `mis/dossier_repository.py` — assinaturas de `list_dossiers_by_rank()` e `get_dossier_by_product_id()` verificadas
- Inspecao direta de `mis/alert_repository.py` — `get_unseen_count()` verificado
- Inspecao direta de `mis/pain_repository.py` — `get_latest_report()` e `get_historical_reports()` verificados
- Inspecao direta de `mis/health_monitor.py` — `run_canary_check()` e `run_platform_canary()` verificados
- Inspecao direta de `mis/config.py` — estrutura de `config.settings.niches` verificada
- Inspecao direta de `mis/__main__.py` — padrao de subcomandos argparse verificado
- Inspecao direta de `mis/db.py` — `run_migrations()` e `get_db()` verificados
- Inspecao direta de `.claude/skills/jarvis-briefing/SKILL.md` — padrao visual JARVIS verificado (largura 120 chars, containers `╔═══╗`, barras `████░░░░`)
- Inspecao direta de `mis/tests/conftest.py` — fixture `db_path` e `temp_config_yaml` verificados
- Inspecao direta de `mis/pytest.ini` — configuracao de testes verificada
- Inspecao direta de `mis/config.yaml` — campos reais de configuracao verificados (incluindo `relevance_language` em vez de `language`)
- `.planning/phases/06-megabrain-integration/06-CONTEXT.md` — todas as decisoes de implementacao

### Secondary (MEDIUM confidence)

- `.planning/STATE.md` — historico de decisoes arquiteturais das fases anteriores (confirmam padroes: structlog, sqlite3 direto vs sqlite_utils, etc.)

### Tertiary (LOW confidence)

- Nenhum

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — tudo usa bibliotecas ja instaladas e verificadas no codebase
- Architecture: HIGH — bridge pattern e SKILL.md pattern ja existem no projeto
- Pitfalls: HIGH — derivados de inspecao direta do codigo existente, nao especulacao
- Test infrastructure: HIGH — pytest.ini e conftest.py verificados diretamente

**Research date:** 2026-03-15
**Valid until:** 2026-04-15 (stack e estavel; nenhuma dependencia externa volatil)
