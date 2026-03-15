# Phase 5: Dashboard - Context

**Gathered:** 2026-03-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Interface web que expõe toda a inteligência gerada pelo MIS — rankings de produtos campeões, dossiês de espionagem e análise IA, e feed de dores do mercado — sem necessidade de tocar em código. Controle dos jobs e scrapers permanece no CLI (python -m mis). Dashboard é somente leitura de dados.

</domain>

<decisions>
## Implementation Decisions

### Stack e inicialização
- FastAPI + Jinja2 + HTMX (já fixado pelo roadmap — server-side rendering, sem React/Vue)
- Iniciado via `python -m mis dashboard --port 8000` (subcomando do __main__.py existente)
- Sem autenticação — uso pessoal local (localhost)
- Sem endpoints JSON por agora — só HTML (API JSON é v2)

### Visual e tema
- Dark mode como padrão
- Estilo minimalista/funcional — foco em dados, sem design system customizado pesado
- CSS via Tailwind ou Bootstrap (Claude escolhe o mais adequado)

### Navegação e estrutura de páginas
- Navbar com 3 itens: **Ranking** | **Feed de Dores** | **Alertas**
- Página inicial: Ranking de Produtos
- Dossiê é sub-página do Ranking (/dossier/{id})
- Link para /health discreto no rodapé

### Acesso a dados (arquitetura)
- FastAPI acessa SQLite via repositórios existentes (`product_repository.py`) + novos repositórios para dossiers e pain_reports
- Não acessa o DB diretamente nos route handlers
- Padrão consistente com o resto do projeto

### Ranking de Produtos
- Layout: tabela com linhas (não cards)
- Colunas: posição (#), nome do produto, plataforma, nicho, score de oportunidade (IA)
- Filtros: dropdowns de Plataforma e Nicho no topo — HTMX recarrega a tabela sem reload
- Sem busca textual, sem sidebar de filtros
- Ordenação: colunas clicáveis (posição, score) para ordenar ASC/DESC
- Paginação: configurável (10/20/50 por página)
- Timestamp da última atualização visível no topo da tabela
- Produtos sem dossiê: aparecem com badge "Pendente" — clique abre página com status
- Clique no produto navega para /dossier/{id}

### Página de Dossiê Individual
- Header fixo: nome do produto, plataforma, posição no ranking, score de oportunidade, confidence score
  - Ex: "Oportunidade: 8.2 | Confiabilidade: Alta (85%)"
- Layout: tabs horizontais — **Visão Geral** | **Copy** | **Anúncios** | **Reviews** | **Template**
- Tab padrão ao abrir: Visão Geral (análise IA — por que está vendendo, dores endereçadas)
- Tab Reviews: síntese IA no topo + lista de reviews individuais com rating
- Tab Anúncios: cards com copy do anúncio, plataforma (Meta) e data
- Tab Template: texto formatado com botão "Copiar para clipboard"
- Navegação entre dossiês: setas anterior/próximo para navegar pelo ranking sem voltar para a lista
- Produtos com dossiê pendente: página exibe dados já coletados (copy, ads) com status "Análise em andamento"

### Feed de Dores do Mercado
- Layout: abas por nicho configurado, cada aba mostra o relatório mais recente
- Conteúdo de cada relatório: top 5 dores com título + descrição + nível de interesse (alto/médio/baixo)
- Timestamp: data e hora exatos + tempo relativo (ex: "15/03 14:00 — há 2 horas")
- Contador de sinais: "Baseado em 47 sinais coletados" visível em cada relatório
- Links para fontes: cada dor exibe 2-3 links para posts/vídeos que a embasam
- Histórico: selector de data/hora para navegar em relatórios das últimas 24-48h
- Busca textual: filtra dores em todos os relatórios históricos do nicho
- Filtro por nível de interesse: checkboxes alto/médio/baixo no relatório atual
- Feed é read-only — sem interações além de leitura e filtros

### Sistema de Alertas
- Trigger: produto que entra no top 20 de qualquer plataforma pela primeira vez (threshold padrão: 20)
- Página dedicada "Alertas" como terceiro item do navbar
- Badge de contador no navbar com polling — atualiza sem abrir a página de alertas
- Cada alerta contém: produto, nicho, posição alcançada, data, link "Ver dossiê" → /dossier/{id}
- Alertas permanecem com status "Visto/Não visto" (não somem)
- Alertas não vistos: badge no navbar; vistos ficam esmaecidos na página
- Retenção: alertas expiram após 7 dias automaticamente

### Página de Saúde (/health)
- Link discreto no rodapé
- Exibe: status dos scrapers (resultados canary checks do health_monitor), última execução de cada job, erros recentes
- Read-only — sem controles de start/stop

### Claude's Discretion
- Estrutura interna de arquivos em mis/web/ (routes, templates, static)
- CSS framework específico (Tailwind vs Bootstrap) dentro do dark mode
- Implementação do polling do badge de alertas (intervalo, endpoint)
- Design exato das páginas (spacing, cores dentro do dark mode)
- Paginação: implementação técnica (HTMX ou server-side)
- Intervalo do selector de histórico (ex: de hora em hora ou granularidade livre)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `mis/product_repository.py`: upsert_product() e save_batch() — padrão de repositório a ser seguido para novos repositórios (dossier_repository.py, pain_repository.py)
- `mis/db.py`: get_db() e run_migrations() — conexão SQLite via sqlite-utils com WAL mode e FK habilitados
- `mis/health_monitor.py`: run_canary_check() — usado pela página /health para exibir status dos scrapers
- `mis/scheduler.py`: get_scheduler() — APScheduler singleton compartilhado; dashboard pode consultá-lo para exibir status de jobs
- `mis/config.py`: config.settings — nichos configurados disponíveis para popular as abas do feed de dores
- `mis/__main__.py`: ponto de entrada CLI existente — adicionar subcomando `dashboard` aqui

### Established Patterns
- Repositório de acesso ao DB: módulo separado (ex: product_repository.py) com funções puras que recebem db_path — manter esse padrão para dossier_repository.py e pain_repository.py
- MIS_DB_PATH env var: fonte do path do DB em toda a codebase — web deve ler a mesma var
- structlog: logging padrão do projeto — usar também no web layer
- Migrações (_001 → _004): banco de dados já tem todas as tabelas necessárias (products, dossiers, pain_signals, pain_reports via migration 004)

### Integration Points
- `__main__.py` → adicionar subcomando `dashboard` que inicia o servidor FastAPI
- `mis/web/` → novo módulo a ser criado (FastAPI app, routes, Jinja2 templates, static files)
- DB existente lido diretamente (sqlite-utils) pelos novos repositórios web
- `health_monitor.run_canary_check()` chamado pela rota /health
- `config.settings.niches` para popular tabs do feed de dores dinamicamente

</code_context>

<specifics>
## Specific Ideas

- Navegação entre dossiês com setas anterior/próximo para percorrer o ranking sem voltar para a lista
- Contar sinais base de cada relatório ("Baseado em 47 sinais coletados")
- Badge de alertas no navbar com polling automático — usuário vê novo campeão sem precisar abrir a página

</specifics>

<deferred>
## Deferred Ideas

- Gráfico de linha de evolução do score de oportunidade por nicho ao longo do tempo — requer tracking histórico de scores (não disponível no schema atual); candidato a v2
- Botão "Reanalisar" no dossiê para re-disparar spy pipeline — operação de escrita fora do escopo do dashboard read-only desta fase
- Notificações via WhatsApp/Telegram (já em v2 Requirements: ADV-04)
- Export de dossiê em PDF (já em v2 Requirements: ADV-01)
- Comparação lado a lado de 2+ produtos (já em v2 Requirements: ADV-02)
- API JSON endpoints /api/products, /api/dossier/{id} — v2 quando houver consumidor externo
- Interface mobile nativa (já em Out of Scope: web responsiva suficiente)

</deferred>

---

*Phase: 05-dashboard*
*Context gathered: 2026-03-15*
