# Phase 6: MEGABRAIN Integration - Context

**Gathered:** 2026-03-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Criar o ponto de integração limpo entre o MIS e o MEGABRAIN: um bridge (`mis_agent.py`) que expõe dados do MIS para o ecossistema MEGABRAIN, um skill `/mis-briefing` para consumo visual dentro do Claude Code, um subcomando `export` no CLI para exportar dossiês e relatórios de dores para o pipeline de conhecimento do MEGABRAIN, e a documentação da integração no CLAUDE.md.

O `mis/` já existe e funciona. Esta fase não adiciona novos scrapers, novas fontes, nem integração com JARVIS além do skill standalone. O bridge é exclusivamente de leitura e exportação — sem disparo de operações no MIS a partir do MEGABRAIN.

</domain>

<decisions>
## Implementation Decisions

### /mis-briefing — Conteúdo e Estrutura

- **Acionamento**: skill standalone `/mis-briefing`; não integrado ao /jarvis-briefing existente
- **Dados de produtos**: top-10 produtos campeões do último ciclo completo, ordenados por score de oportunidade (IA) decrescente
- **Campos por produto**: posição (#), nome, plataforma, nicho, score de oportunidade
- **Seção Pain Radar**: top-5 dores por nicho configurado, com nível de interesse (Alto/Médio/Baixo); idioma das dores conforme configuração `language` do nicho no config.yaml (pt-BR para nichos pt, en para nichos gringa)
- **Seção Alertas**: exibida somente se houver alertas não vistos — até 5 novos campeões com produto, nicho, posição e data
- **Status de saúde**: uma linha por scraper (✅ OK / ⚠ FALHA) + timestamp da última execução, usando `health_monitor.run_canary_check()` existente
- **Health Score (0-100)**: scrapers saudáveis=40pts, ciclo completado nas últimas 2h=30pts, dossiês gerados hoje > 0=20pts, sem falha crítica de alertas=10pts
- **Frescor dos dados**: timestamp do último ciclo visível; alerta ⚠ "Dados antigos" se o último ciclo for > 2h
- **Rodapé**: `Dashboard: http://localhost:8000 | DB: {MIS_DB_PATH}`
- **Formato visual**: JARVIS-style com ASCII art — containers `╔═══╗`, largura padrão MEGABRAIN, barras de progresso `████████░░░░` — consistente com `/jarvis-briefing` existente
- **Sem argumentos no MVP**: sem filtro por nicho, sem `--top N`; tudo configurado via config.yaml
- **Acesso a dados**: via `mis_agent.py` — o skill nunca acessa o SQLite diretamente
- **Estado vazio**: exibe mensagem `"MIS não encontrado. Execute python -m mis para inicializar."` sem stack trace
- **Acesso ao DB**: skill chama Python via Bash tool — `python -c "import sys; sys.path.insert(0, os.environ['MIS_PATH']); from mis.mis_agent import get_briefing_data; ..."`

### Invocação — Skill

- **Tipo**: Skill em `.claude/skills/mis-briefing/SKILL.md` (não entrada no AGENT-INDEX.yaml)
- **Auto-trigger keywords**: "mis briefing", "produtos campeões", "radar de mercado"
- **Auto-registro**: via `skill_indexer.py` hook no SessionStart — seguir padrão existente
- **Localização**: repo MEGABRAIN em `.claude/skills/mis-briefing/`
- **Pré-requisitos documentados no SKILL.md**: `mis/` instalado, `MIS_PATH` e `MIS_DB_PATH` configurados no `.env`, pelo menos 1 ciclo de scanner executado
- **Não aparece no /jarvis-briefing**: skill independente

### Formato de Exportação (`python -m mis export`)

- **Trigger**: subcomando explícito `export` adicionado ao `mis/__main__.py` — não automático após ciclos
- **Conteúdo exportado**: dossiês completos (status=complete) + pain reports dos últimos 7 dias; dossiês incompletos (failed/pending) são ignorados
- **Formato**: Markdown com frontmatter YAML + seções estruturadas
- **Frontmatter de cada arquivo**: `source: mis`, `type: dossier|pain_report`, `platform`, `niche`, `score`, `date`, `product_id`
- **Estrutura de dossiê exportado**: seções `## Por que Vende`, `## Copy`, `## Anúncios`, `## Reviews`, `## Template`
- **Destino padrão**: `{MEGABRAIN_PATH}/knowledge/mis/` (lido do `.env` do MEGABRAIN)
- **Flag --dest**: permite sobrescrever o destino padrão (`python -m mis export --dest /outro/caminho`)
- **Naming convention**: `dossier_{platform}_{product_id}.md` e `pain_{niche}_{YYYYMMDD}.md`
- **Export incremental**: compara hash/data — só exporta arquivos novos ou alterados; sem re-exportar já existentes
- **Índice**: gera/atualiza `knowledge/mis/README.md` com data do export, contagem por plataforma/nicho
- **Output no terminal**: silencioso durante export; resumo ao final — `"Exported: 12 dossiers, 3 pain reports to knowledge/mis/"`
- **Logging**: structlog — `event='export_file', file=path, type=dossier|pain_report`
- **Sem dry-run automático**: escreve diretamente; sem preview + confirmação
- **Destino criado automaticamente** se não existir

### mis_agent.py — Bridge

- **Localização**: `mis/mis_agent.py` — dentro do repo MIS; versionado junto com o MIS
- **Escopo MVP estrito**: apenas 2 funções públicas:
  - `get_briefing_data() -> dict` — retorna dados estruturados para o briefing
  - `export_to_megabrain(dest=None) -> dict` — executa a exportação
- **Sem CLI própria**: arquivo só importado, sem `argparse`, sem `main()`
- **Tratamento de erros**: retorna dicionário com status — `{'status': 'ok', 'data': ...}` ou `{'status': 'error', 'message': '...', 'setup_hint': '...'}`; sem exceções propagadas
- **Inicialização**: chama `run_migrations()` do `mis/db.py` ao ser importado — garante banco atualizado, idempotente
- **Configuração**: lê `MIS_DB_PATH` do `.env` (mesma variável usada pelo resto do MIS)
- **Import pelo skill**: `python -c "import sys; sys.path.insert(0, os.environ['MIS_PATH']); from mis.mis_agent import get_briefing_data"` — MIS_PATH no `.env` do MEGABRAIN
- **Versionamento**: sem contrato formal de API version — mis_agent.py atualiza junto com mudanças no MIS

### Configuração de Ambiente (MEGABRAIN .env)

- Adicionar ao `.env` do MEGABRAIN:
  - `MIS_PATH` — caminho absoluto para o diretório raiz do MIS (pai de `mis/`)
  - `MIS_DB_PATH` — caminho absoluto para o arquivo `mis.db`
  - `MEGABRAIN_PATH` — caminho do MEGABRAIN (para o export resolver `knowledge/mis/`)

### Documentação — CLAUDE.md do MEGABRAIN

- Adicionar seção **"MIS Integration"** no CLAUDE.md com:
  - O que é o MIS e onde fica (2-3 linhas)
  - Como importar `mis_agent.py` com exemplo de código (incluindo nota sobre `MIS_PATH`)
  - Assinaturas das funções: `get_briefing_data() -> dict` e `export_to_megabrain(dest=None) -> dict`

### Testes

- `mis/tests/test_mis_agent.py` — SQLite em memória, 3 cenários obrigatórios:
  - DB vazio: `get_briefing_data()` retorna estrutura correta com listas vazias, status='ok'
  - DB com dados: `get_briefing_data()` retorna top-10 produtos e pain reports corretos
  - Export incremental: `export_to_megabrain()` não re-exporta arquivos já existentes sem mudança

### Claude's Discretion

- Estrutura interna de `get_briefing_data()` (como agrega dados dos repositórios)
- Implementação exata do cálculo do Health Score (pesos dos fatores)
- Formato exato do ASCII art do briefing (espaçamento, separadores dentro dos containers)
- Como detectar "ciclo mais recente" (query no banco)
- Implementação do hash para export incremental (MD5 do conteúdo vs comparação de data)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `mis/alert_repository.py`: `get_unseen_count()` — para a seção de alertas do briefing
- `mis/dossier_repository.py`: `list_dossiers_by_rank()` — para o top-10 de produtos
- `mis/pain_repository.py`: `get_latest_report()`, `get_historical_reports()` — para a seção Pain Radar
- `mis/health_monitor.py`: `run_canary_check()` — para o status de saúde dos scrapers
- `mis/db.py`: `run_migrations()`, `get_db()` — conexão SQLite; chamar run_migrations() no import do mis_agent
- `mis/config.py`: `config.settings.niches` — para iterar nichos e obter `language` de cada um
- `mis/__main__.py`: padrão de subcomandos com argparse — adicionar subcomando `export` seguindo o mesmo padrão de `dashboard`
- `.claude/skills/jarvis-briefing/SKILL.md`: referência de padrão visual JARVIS (containers ASCII, largura, Health Score)

### Established Patterns
- Repositório de acesso ao DB: funções puras que recebem `db_path` — manter em `mis_agent.py`
- `MIS_DB_PATH` env var: source of truth para o caminho do banco
- structlog: logging padrão do projeto — usar também no export
- CLI subcomandos via argparse: padrão de `spy`, `radar`, `dashboard` no `__main__.py`
- `.claude/skills/{nome}/SKILL.md`: estrutura de skill existente (jarvis-briefing como referência)

### Integration Points
- `mis/__main__.py` → adicionar subcomando `export` com argparse (`--dest`)
- `mis/mis_agent.py` → novo arquivo na raiz de `mis/` (bridge)
- `.claude/skills/mis-briefing/SKILL.md` → novo skill no MEGABRAIN
- `.claude/CLAUDE.md` → adicionar seção "MIS Integration"
- `.env` (MEGABRAIN) → adicionar `MIS_PATH`, `MIS_DB_PATH`, `MEGABRAIN_PATH`
- `mis/tests/test_mis_agent.py` → novo arquivo de testes

</code_context>

<specifics>
## Specific Ideas

- O briefing deve ser visualmente consistente com o `/jarvis-briefing` existente — mesmos containers `╔═══╗`, mesma largura, mesmo estilo de Health Score
- Rodapé com link direto para o dashboard: `Dashboard: http://localhost:8000`
- O export gera um `README.md` índice em `knowledge/mis/` para facilitar navegação humana e do pipeline

</specifics>

<deferred>
## Deferred Ideas

- Integração do MIS com `/jarvis-briefing` (menção proativa de novos campeões no briefing diário) — integração mais profunda para fase futura
- `get_dossier(product_id)` e `search_products(query)` no mis_agent.py — funções adicionais do bridge para v2
- Auto-export após cada ciclo do scanner — disparo automático sem intervenção manual
- Skill `/mis-export` separado para disparar exportação de dentro do MEGABRAIN
- Contrato formal de API version em mis_agent.py (`__api_version__`)
- Flag `--dry-run` no subcomando export
- Filtros no /mis-briefing por nicho (--nicho) ou quantidade (--top N)

</deferred>

---

*Phase: 06-megabrain-integration*
*Context gathered: 2026-03-15*
