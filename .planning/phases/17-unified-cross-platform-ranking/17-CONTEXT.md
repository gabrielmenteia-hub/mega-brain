# Phase 17: Unified Cross-Platform Ranking - Context

**Gathered:** 2026-03-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Nova view `/ranking/unified` que exibe produtos de múltiplas plataformas ordenados por unified score (percentile normalizado por nicho). Inclui filtro por nicho, toggle "multi-platform only" e badge de plataforma com rank bruto. O `/ranking` existente (por plataforma) não muda.

</domain>

<decisions>
## Implementation Decisions

### Unified Score — Cálculo e Escopo
- Percentile calculado **in-memory em Python**, por request, sobre todos os produtos com rank válido
- Escopo: **por nicho** — percentile reflete posição relativa dentro do nicho selecionado
- Quando filtro de nicho ativo, percentile é recalculado apenas para os produtos daquele nicho
- Busca todos os produtos do nicho no DB, calcula percentile, ordena, depois pagina (nunca por página)
- Plataformas com **< 5 produtos** no nicho são excluídas do cálculo (evita distorção de percentiles espaçados)

### Unified Score — Normalização por rank_type
- `positional` (Hotmart, Kiwify, BR scanners): `percentile = (1 - rank/total) * 100` — rank #1 → score alto
- `gravity` (ClickBank, JVZoo): `percentile = valor / max_valor * 100` — gravity maior → score alto
- `upvotes` (Product Hunt): `percentile = valor / max_valor * 100`
- `enrollment` (Udemy): `percentile = valor / max_valor * 100`

### Unified Score — Display
- Número float com **1 casa decimal** (ex: `87.4`)
- Ordenação padrão: **unified score descendente**
- Tiebreaker: rank bruto da plataforma original (menor posicional vence)
- Produtos com `rank=NULL` **excluídos silenciosamente** (sem rank = sem posição válida)
- Quando nicho tem dados de apenas 1 plataforma: mostrar normalmente com aviso no topo da tabela ("Dados de 1 plataforma")

### Colunas da Tabela Unificada
| Coluna | Conteúdo |
|--------|----------|
| # | Posição no ranking unificado |
| Produto | Título + link para /dossier/{id} |
| Plataforma | Badge `[H] Hotmart` + `⚠️` se stale |
| Score | Percentile float (ex: `87.4`) |
| Rank Original | Rank bruto formatado por rank_type (ex: `#3`, `42.1 gravity`, `#87 upvotes`) |

### Multi-Platform Detection
- Toggle "multi-platform only" filtra para produtos com título normalizado presente em 2+ plataformas
- Normalização: lowercase, remoção de acentos, trim — executada **em Python** no momento da query (sem coluna no DB)
- Quando toggle ativo: todos os registros individuais aparecem (uma linha por plataforma para o mesmo título)
- Com filtro de nicho ativo: match de título feito **dentro do nicho filtrado** (não global)
- Filtro "plataforma" **não existe** no /ranking/unified — a view é cross-platform por design

### Navegação e Integração
- Tabs no topo da página de ranking: **"Por Plataforma"** (atual `/ranking`) e **"Unificado"** (`/ranking/unified`)
- Tab ativa indicada por classe CSS (text-white + border-bottom) via `request.url.path` no Jinja2
- URL: `/ranking/unified` (path separado, conforme success criteria)
- Template: `unified.html` (extends `base.html`) + `unified_table.html` (partial HTMX)
- Rota de partial: `/ranking/unified/table` — mesmo padrão do `/ranking/table`
- Clicar em produto → `/dossier/{id}` (mesmo comportamento do /ranking existente)

### Dados Stale
- Produtos com `is_stale=True` **incluídos** na view com indicador visual
- Visual: linha com `text-gray-500` (opacidade reduzida) + `⚠️` na célula de plataforma
- Produtos stale **participam normalmente** do cálculo do percentile (última posição conhecida)

### Estrutura da Função Python
- `list_unified_ranking(db_path, niche, multi_platform_only, per_page, page)` em `mis/product_repository.py`
- Retorna lista de dicts com: `id`, `title`, `platform_name`, `platform_slug`, `niche_name`, `unified_score`, `rank`, `rank_type`, `is_stale`, `has_dossier`

### Claude's Discretion
- Implementação exata da normalização de acentos (unicodedata.normalize ou similar)
- Constante `MIN_PRODUCTS_PER_PLATFORM` (default 5) como constante no topo do módulo
- Formatação do rank original por rank_type (ex: gravity com 1 decimal, positional como inteiro)
- Estrutura interna dos testes e fixtures

</decisions>

<specifics>
## Specific Ideas

- Success criteria do ROADMAP exige explicitamente `/ranking/unified` como URL — manter
- O campo `rank_type` já está no DB (migration _006) — a normalização pode ser feita sem joins extras
- O padrão de partial HTMX está estabelecido em `ranking.html` + `ranking_table.html` — reusar exatamente

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `mis/web/templates/base.html` — layout base com dark theme Tailwind
- `mis/web/templates/ranking.html` + `ranking_table.html` — template e partial a serem adaptados para unified
- `mis/web/routes/ranking.py` — `_get_ranking_context()` + padrão de is_htmx + partial route como referência direta
- `mis/product_repository.py` — onde `list_unified_ranking()` será adicionada
- `mis/dossier_repository.py:list_dossiers_by_rank()` — referência de query SQL com filtros de plataforma/nicho

### Established Patterns
- HTMX: `hx-get`, `hx-target`, `hx-include` nos selects para recarregar partial sem full page reload
- Dark theme: `bg-gray-800`, `text-gray-200`, `border-gray-700`, `text-blue-400` para links
- Badge inline: `<span class="bg-yellow-600 text-xs px-1 rounded ml-1">Pendente</span>` — adaptar para `⚠️` stale
- Paginação com `per_page` selector: `10 / 20 / 50`

### Integration Points
- `mis/web/routes/ranking.py` — adicionar duas novas rotas: `GET /ranking/unified` e `GET /ranking/unified/table`
- `mis/web/templates/ranking.html` — adicionar tabs no topo (Por Plataforma | Unificado)
- `mis/product_repository.py` — adicionar `list_unified_ranking()`
- `mis/migrations/_006_v2_platforms.py` — `rank_type` já disponível no DB, sem nova migração necessária

</code_context>

<deferred>
## Deferred Ideas

- Peso por plataforma proporcional ao volume de dados — backlog v3.0
- Z-score normalização para plataformas com outliers extremos — backlog
- Persistência do toggle multi-platform no localStorage — backlog
- Filtro por plataforma dentro do /ranking/unified — backlog (conflita com o design cross-platform intencional)

</deferred>

---

*Phase: 17-unified-cross-platform-ranking*
*Context gathered: 2026-03-17*
