# Phase 17: Unified Cross-Platform Ranking - Research

**Researched:** 2026-03-17
**Domain:** Python in-memory percentile normalization + FastAPI/HTMX dashboard (SQLite read layer)
**Confidence:** HIGH — baseado em leitura direta do codebase existente, sem dependências externas novas

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- Unified score: float 0-100 com 1 casa decimal, calculado in-memory em Python por request
- Escopo percentile: por nicho (recalculado quando filtro de nicho ativo)
- Busca todos os produtos do nicho no DB, calcula percentile, ordena, depois pagina (nunca por página)
- Plataformas com < 5 produtos no nicho excluídas do cálculo
- rank=NULL excluídos silenciosamente
- Positional rank_type: `percentile = (1 - rank/total) * 100`
- Gravity/upvotes/enrollment: `percentile = valor / max_valor * 100`
- Ordenação padrão: unified score descendente
- Tiebreaker: rank bruto da plataforma original (menor posicional vence)
- Produtos com dados de apenas 1 plataforma: mostrar com banner "Dados de 1 plataforma"
- Multi-platform detection: normalized title match em Python (lowercase, sem acentos, trim)
- Match dentro do nicho filtrado (não global)
- Toggle "multi-platform only": exibe todos os registros individuais (uma linha por plataforma)
- Navegação: tabs "Por Plataforma" | "Unificado" no topo da página ranking
- URL: `/ranking/unified` + partial `/ranking/unified/table`
- Templates: `unified.html` (extends base.html) + `unified_table.html` (HTMX partial)
- Sem filtro de plataforma na unified view (apenas nicho + toggle multi-platform)
- Tab ativa: classe CSS via `request.url.path`
- Stale products: incluídos, linha dimmed (text-gray-500) + ⚠️ na célula de plataforma
- Stale products participam normalmente do cálculo do percentile
- `list_unified_ranking()` em `mis/product_repository.py`
- Parâmetros: `db_path, niche, multi_platform_only, per_page, page`
- Retorna lista de dicts com: `id, title, platform_name, platform_slug, niche_name, unified_score, rank, rank_type, is_stale, has_dossier`

### Claude's Discretion

- Implementação exata da normalização de acentos (unicodedata.normalize ou similar)
- Constante `MIN_PRODUCTS_PER_PLATFORM` (default 5) como constante no topo do módulo
- Formatação do rank original por rank_type (ex: gravity com 1 decimal, positional como inteiro)
- Estrutura interna dos testes e fixtures

### Deferred Ideas (OUT OF SCOPE)

- Peso por plataforma proporcional ao volume de dados — backlog v3.0
- Z-score normalização para plataformas com outliers extremos — backlog
- Persistência do toggle multi-platform no localStorage — backlog
- Filtro por plataforma dentro do /ranking/unified — backlog
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DASH-V2-01 | View `/ranking/unified` exibe top produtos por nicho consolidados de todas as plataformas usando normalização por percentil | SQL query + Python percentile engine + FastAPI route + unified.html template |
| DASH-V2-02 | View unificada filtra por nicho (obrigatório) e suporta toggle "multi-platform only" (produtos em 2+ plataformas) | `list_unified_ranking(niche, multi_platform_only)` + normalized title matching em Python |
| DASH-V2-03 | View unificada exibe badges de plataforma, unified score e rank bruto por plataforma | unified_table.html com colunas: platform badge, unified_score, rank original formatado |
</phase_requirements>

---

## Summary

Esta phase é puramente de **dashboard/presentation layer** — os dados já estão no DB (criados por phases 13-16). Não há novos scanners, migrações ou schemas. O trabalho é: (1) query SQL para buscar produtos com rank_type join, (2) normalização percentile em Python in-memory, (3) duas rotas FastAPI, (4) dois templates Jinja2/HTMX seguindo o padrão exato do `/ranking` existente.

O codebase já tem tudo o que é necessário como referência direta: `ranking.py` define o padrão de rota + partial, `ranking.html`/`ranking_table.html` definem o padrão de template HTMX, e `dossier_repository.py` define o padrão de query SQL com joins. A nova função `list_unified_ranking()` vai em `product_repository.py` — o mesmo módulo já aberto.

**Primary recommendation:** Implementar em 1 plano único (17-01) com TDD: RED (testes para `list_unified_ranking()` + percentile logic) → GREEN (implementação) → templates + rotas + tabs navigation.

---

## Standard Stack

### Core (já no projeto — sem instalações)

| Library | Version | Purpose | Confirmação |
|---------|---------|---------|-------------|
| sqlite_utils | existente | Query layer SQLite | Usado em todo `dossier_repository.py` |
| FastAPI | existente | Rotas web | Padrão em `ranking.py` |
| Jinja2 | existente | Templates HTML | `base.html`, `ranking.html` |
| HTMX | 2.0.8 (CDN) | Partial swaps sem full reload | `base.html` linha 11 |
| Tailwind CSS | CDN | Dark theme styling | `base.html` linha 7 |
| unicodedata | stdlib Python | Normalização de acentos (NFKD) | Stdlib, sem instalar |
| pytest + pytest-asyncio | existente | Testes | conftest.py, padrão em todos os testes |

### Instalação necessária

Nenhuma. Todos os packages já estão no ambiente.

---

## Architecture Patterns

### Padrão HTMX Partial Estabelecido

O padrão já existe em `ranking.py` e deve ser replicado exatamente:

```python
# mis/web/routes/ranking.py — PADRÃO A REPLICAR
@router.get("/ranking", response_class=HTMLResponse)
async def ranking(request: Request, ...) -> HTMLResponse:
    context = _get_ranking_context(...)
    if is_htmx(request):                           # HX-Request: true header
        return templates.TemplateResponse(request=request, name="ranking_table.html", context=context)
    return templates.TemplateResponse(request=request, name="ranking.html", context=context)

@router.get("/ranking/table", response_class=HTMLResponse)
async def ranking_table(request: Request, ...) -> HTMLResponse:
    context = _get_ranking_context(...)
    return templates.TemplateResponse(request=request, name="ranking_table.html", context=context)
```

Para unified, o padrão é idêntico com rotas `/ranking/unified` e `/ranking/unified/table`.

**DIFERENÇA IMPORTANTE:** A rota `/ranking/unified` NÃO tem o `if is_htmx` redirect para o partial — HTMX updates sempre apontam para `/ranking/unified/table` diretamente via `hx-get`. O `is_htmx` check pode ser removido ou mantido por consistência defensiva.

### Função `list_unified_ranking()` — Estrutura Interna

```
1. SQL query: todos os produtos do nicho com rank IS NOT NULL
   JOIN platforms (para rank_type, name, slug)
   JOIN niches (para niche_name)
   LEFT JOIN dossiers (para has_dossier)

2. Agrupar produtos por platform_slug, filtrar plataformas com < MIN_PRODUCTS_PER_PLATFORM

3. Calcular unified_score por plataforma e rank_type:
   - positional: max_rank = total do grupo, score = (1 - rank/max_rank) * 100
   - gravity/upvotes/enrollment: max_val = max do grupo, score = val/max_val * 100

4. Se multi_platform_only:
   - Normalizar títulos (lowercase, NFKD, strip)
   - Identificar títulos presentes em 2+ platforms
   - Filtrar apenas esses produtos

5. Ordenar por unified_score DESC, tiebreaker por rank ASC

6. Detectar se apenas 1 plataforma tem dados (warning_single_platform)

7. Paginar com LIMIT/OFFSET (in-memory após cálculo)

8. Retornar lista de dicts + metadata
```

### SQL Query Base

```sql
-- Source: padrão de dossier_repository.py, adaptado para unified
SELECT
    p.id,
    p.title,
    p.url,
    pl.name         AS platform_name,
    pl.slug         AS platform_slug,
    pl.rank_type    AS rank_type,
    n.name          AS niche_name,
    n.slug          AS niche_slug,
    p.rank,
    p.is_stale,
    CASE WHEN d.id IS NOT NULL THEN 1 ELSE 0 END AS has_dossier
FROM products p
JOIN platforms pl ON pl.id = p.platform_id
JOIN niches    n  ON n.id  = p.niche_id
LEFT JOIN dossiers d ON d.product_id = p.id
WHERE n.slug = ?          -- niche filter obrigatório para escopo percentile
  AND p.rank IS NOT NULL  -- excluir sem rank
ORDER BY pl.slug, p.rank  -- agrupado por plataforma para facilitar cálculo
```

**Quando niche=None:** Buscar todos os nichos (sem WHERE n.slug). O percentile então é global — mesma lógica, maior dataset.

### Cálculo Percentile por rank_type

```python
# Source: decisões do CONTEXT.md
MIN_PRODUCTS_PER_PLATFORM = 5  # constante no topo do módulo

def _compute_unified_scores(platform_rows: list[dict]) -> list[dict]:
    """Calcula unified_score para um grupo de produtos da mesma plataforma."""
    rank_type = platform_rows[0]["rank_type"]
    total = len(platform_rows)

    if rank_type == "positional":
        # rank #1 = melhor → score alto
        for row in platform_rows:
            row["unified_score"] = round((1 - row["rank"] / total) * 100, 1)
    else:
        # gravity, upvotes, enrollment — valor maior = score alto
        max_val = max(row["rank"] for row in platform_rows)
        for row in platform_rows:
            row["unified_score"] = round((row["rank"] / max_val) * 100, 1) if max_val > 0 else 0.0

    return platform_rows
```

### Normalização de Títulos (Multi-Platform Detection)

```python
import unicodedata

def _normalize_title(title: str) -> str:
    """Lowercase, remove acentos (NFKD), strip whitespace."""
    normalized = unicodedata.normalize("NFKD", title)
    ascii_str = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_str.lower().strip()
```

### Estrutura de Templates

```
mis/web/templates/
├── unified.html          # extends base.html, inclui filtros + #unified-table-wrapper
└── unified_table.html    # tabela pura com 5 colunas unified
```

**unified.html** — diferenças em relação a `ranking.html`:
- Sem filtro de plataforma
- Toggle checkbox "multi-platform only" (input type=checkbox, name=multi_platform_only)
- Banner condicional "Dados de 1 plataforma" se `warning_single_platform`
- `hx-get="/ranking/unified/table"` nos selects

**unified_table.html** — diferenças em relação a `ranking_table.html`:
- Coluna "Plataforma" com badge `[H]` + `⚠️` se is_stale
- Coluna "Score" com `unified_score` (float 1 decimal)
- Coluna "Rank Original" com formatação por rank_type
- Linha stale: classe `text-gray-500`
- Posição: `loop.index + offset` (posição unificada, não rank bruto)

### Tabs de Navegação em `ranking.html`

```html
<!-- Adicionar ao topo de ranking.html ANTES do h1 atual -->
<div class="flex gap-1 mb-4 border-b border-gray-700">
  <a href="/ranking"
     class="px-4 py-2 text-sm {% if '/ranking/unified' not in request.url.path %}text-white border-b-2 border-blue-500{% else %}text-gray-400 hover:text-white{% endif %}">
    Por Plataforma
  </a>
  <a href="/ranking/unified"
     class="px-4 py-2 text-sm {% if '/ranking/unified' in request.url.path %}text-white border-b-2 border-blue-500{% else %}text-gray-400 hover:text-white{% endif %}">
    Unificado
  </a>
</div>
```

**ATENÇÃO:** As tabs devem aparecer em AMBOS os templates (`ranking.html` e `unified.html`) para que a navegação funcione em qualquer direção. Ou extrair para um partial `ranking_tabs.html` e incluir com `{% include %}`.

---

## Don't Hand-Roll

| Problema | Não construir | Usar em vez | Por que |
|---------|-------------|-------------|---------|
| Normalização de acentos | regex manual | `unicodedata.normalize("NFKD")` + encode ascii | Stdlib, testada, cobre Unicode edge cases |
| Paginação SQL | loop Python | LIMIT/OFFSET após ordenação in-memory | Consistência com padrão do projeto |
| Detecção HTMX | parse de headers | `is_htmx(request)` já em `ranking.py` | Já implementado, não duplicar |
| Query parametrizada | f-string SQL | params list + `db.execute(sql, params)` | Previne SQL injection (padrão `dossier_repository.py`) |
| Validação order_dir | none | `"ASC" if order_dir.lower() != "desc" else "DESC"` | Padrão estabelecido em `list_dossiers_by_rank()` |

---

## Common Pitfalls

### Pitfall 1: Paginação Antes do Cálculo Percentile
**O que dá errado:** Aplicar LIMIT/OFFSET diretamente no SQL antes de calcular percentile. O score seria calculado apenas sobre uma página, distorcendo todos os percentiles.
**Por que acontece:** Confundir o SQL de fetch com a query de apresentação.
**Como evitar:** Buscar TODOS os produtos do nicho com rank IS NOT NULL, calcular percentile sobre o conjunto completo, DEPOIS paginar em Python.
**Sinal de alerta:** Qualquer LIMIT no SQL principal de `list_unified_ranking()`.

### Pitfall 2: Plataformas com < MIN_PRODUCTS_PER_PLATFORM Distorcem Percentiles
**O que dá errado:** Plataforma com 2 produtos: produto rank=1 vira unified_score=100, produto rank=2 vira 0. Isso infla artificialmente produtos de plataformas com poucos dados.
**Como evitar:** Agrupar por platform_slug, contar produtos por grupo ANTES de calcular scores. Excluir grupos com count < MIN_PRODUCTS_PER_PLATFORM. Produtos dessas plataformas são descartados silenciosamente do resultado.

### Pitfall 3: rank=NULL Para Scanners Fallback
**O que dá errado:** EduzzScanner, MonetizzeScanner (fallback-only) podem ter produtos com rank=NULL no DB. Se incluídos, o cálculo de percentile positional `(1 - rank/total)` lança TypeError.
**Como evitar:** WHERE p.rank IS NOT NULL no SQL — já definido nas decisões.

### Pitfall 4: max_val=0 Para rank_type gravity/upvotes/enrollment
**O que dá errado:** Divisão por zero se todos os produtos de uma plataforma têm rank=0 (improvável mas possível em dados sujos).
**Como evitar:** Guard `if max_val > 0 else 0.0` no cálculo do score.

### Pitfall 5: Multi-Platform Toggle com Niche=None
**O que dá errado:** Com niche=None, o match de títulos é global cross-niche. Produto "Marketing Basics" em Marketing e em Saúde (por engano) seria marcado como multi-platform quando são produtos diferentes.
**Como evitar:** Multi-platform detection sempre dentro do escopo do nicho filtrado. Se niche=None, o match é global — aceitar esse comportamento ou documentar no banner.

### Pitfall 6: Tabs em Templates Separados Causam Inconsistência
**O que dá errado:** Tabs só em `ranking.html` → user em `/ranking/unified` não vê as tabs. Tabs duplicadas em `ranking.html` e `unified.html` → manutenção dupla.
**Como evitar:** Extrair tabs para `ranking_tabs.html` e usar `{% include "ranking_tabs.html" %}` em ambos os templates.

### Pitfall 7: HTMX Include do Toggle
**O que dá errado:** O checkbox `multi_platform_only` não é incluído no `hx-include` dos outros selects, então toggle é perdido ao mudar nicho/per_page.
**Como evitar:** Adicionar `[name='multi_platform_only']` no `hx-include` de todos os elementos de filtro.

---

## Code Examples

### Padrão de Query com Join (verificado em `dossier_repository.py`)

```python
# Source: mis/dossier_repository.py:list_dossiers_by_rank()
params: list = []
where_clauses: list[str] = []
if niche:
    where_clauses.append("n.slug = ?")
    params.append(niche)
where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

sql = f"""
    SELECT p.id, p.title, pl.name AS platform_name, pl.slug AS platform_slug,
           pl.rank_type, n.name AS niche_name, p.rank, p.is_stale,
           CASE WHEN d.id IS NOT NULL THEN 1 ELSE 0 END AS has_dossier
    FROM products p
    JOIN platforms pl ON pl.id = p.platform_id
    JOIN niches    n  ON n.id  = p.niche_id
    LEFT JOIN dossiers d ON d.product_id = p.id
    {where_sql}
    AND p.rank IS NOT NULL
    ORDER BY pl.slug, p.rank ASC
"""
cursor = db.execute(sql, params)
columns = [desc[0] for desc in cursor.description]
rows = cursor.fetchall()
results = [dict(zip(columns, row)) for row in rows]
```

### Padrão de Rota HTMX (verificado em `ranking.py`)

```python
# Source: mis/web/routes/ranking.py
def is_htmx(request: Request) -> bool:
    return request.headers.get("HX-Request") == "true"

@router.get("/ranking/unified", response_class=HTMLResponse)
async def unified_ranking(
    request: Request,
    niche: str | None = None,
    multi_platform_only: bool = False,
    per_page: int = 20,
    page: int = 1,
) -> HTMLResponse:
    db_path = request.app.state.db_path
    templates = request.app.state.templates
    context = _get_unified_context(db_path, niche, multi_platform_only, per_page, page)
    if is_htmx(request):
        return templates.TemplateResponse(request=request, name="unified_table.html", context=context)
    return templates.TemplateResponse(request=request, name="unified.html", context=context)
```

### Padrão de Badge Stale (verificado em `ranking_table.html`)

```html
<!-- Source: mis/web/templates/ranking_table.html — adaptado para stale -->
<tr class="border-b border-gray-800 hover:bg-gray-900 transition-colors
           {% if product.is_stale %}text-gray-500{% endif %}">
  ...
  <td class="px-4 py-3 text-gray-300">
    {{ product.platform_name }}
    {% if product.is_stale %}<span title="Dados desatualizados">⚠️</span>{% endif %}
  </td>
```

### Formatação do Rank Original por rank_type

```python
# Claude's discretion — implementação sugerida
def format_rank(rank, rank_type: str) -> str:
    if rank is None:
        return "-"
    if rank_type == "positional":
        return f"#{int(rank)}"
    elif rank_type == "gravity":
        return f"{float(rank):.1f} gravity"
    elif rank_type == "upvotes":
        return f"#{int(rank)} upvotes"
    elif rank_type == "enrollment":
        return f"{int(rank)} alunos"
    return str(rank)
```

---

## State of the Art

| Abordagem Antiga | Abordagem Atual | Quando Mudou | Impacto |
|-----------------|-----------------|--------------|---------|
| rank como posição única semântica | rank_type por plataforma | Phase 13 (migration _006) | Habilita percentile normalizado |
| is_stale inexistente | is_stale column (migration _007) | Phase 14 | Produtos stale identificáveis no ranking |
| Apenas /ranking por plataforma | /ranking/unified cross-platform | Phase 17 | Entrega principal v2.0 |
| HTMX 1.x | HTMX 2.0.8 (CDN) | Phase 5 (base.html) | `hx-include` sintaxe CSS selector funciona igual |

---

## Open Questions

1. **Toggle multi_platform_only como query param boolean no FastAPI**
   - O que sabemos: FastAPI converte `?multi_platform_only=true` para bool via query param
   - O que pode ser ambíguo: Checkbox HTML unchecked não envia o campo (ausência = False). `hx-include` inclui `[name='multi_platform_only']` mas checkbox unchecked não aparece na URL
   - Recomendação: Usar `value="1"` no checkbox e `multi_platform_only: int = 0` no FastAPI, converter com `bool(multi_platform_only)`. Ou usar `str | None` e testar presença.

2. **`request.url.path` no contexto Jinja2**
   - O que sabemos: FastAPI templates têm acesso ao `request` object no template quando passado no context
   - Como `ranking.py` passa context: sem `request` explícito, mas `TemplateResponse(request=request, ...)` injeta automaticamente no template como `request`
   - Recomendação: Usar `{{ request.url.path }}` diretamente no Jinja2 — funciona com FastAPI Jinja2 templates.

---

## Validation Architecture

> `nyquist_validation: true` em `.planning/config.json` — seção obrigatória.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest + pytest-asyncio (existente) |
| Config file | `mis/tests/conftest.py` — fixture `db_path(tmp_path)` |
| Quick run command | `pytest mis/tests/test_unified_ranking.py -x -q` |
| Full suite command | `pytest mis/tests/ -x -q` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DASH-V2-01 | `list_unified_ranking()` retorna produtos ordenados por unified_score DESC | unit | `pytest mis/tests/test_unified_ranking.py::test_unified_score_order -x` | ❌ Wave 0 |
| DASH-V2-01 | Percentile positional: rank #1 = score alto | unit | `pytest mis/tests/test_unified_ranking.py::test_percentile_positional -x` | ❌ Wave 0 |
| DASH-V2-01 | Percentile gravity: valor maior = score alto | unit | `pytest mis/tests/test_unified_ranking.py::test_percentile_gravity -x` | ❌ Wave 0 |
| DASH-V2-01 | rank=NULL excluído silenciosamente | unit | `pytest mis/tests/test_unified_ranking.py::test_null_rank_excluded -x` | ❌ Wave 0 |
| DASH-V2-01 | Plataforma com < 5 produtos excluída do cálculo | unit | `pytest mis/tests/test_unified_ranking.py::test_min_products_threshold -x` | ❌ Wave 0 |
| DASH-V2-02 | Filtro por nicho retorna apenas produtos do nicho | unit | `pytest mis/tests/test_unified_ranking.py::test_niche_filter -x` | ❌ Wave 0 |
| DASH-V2-02 | Toggle multi_platform_only retorna apenas produtos em 2+ plataformas | unit | `pytest mis/tests/test_unified_ranking.py::test_multi_platform_filter -x` | ❌ Wave 0 |
| DASH-V2-02 | Normalização de título: lowercase + sem acentos + trim | unit | `pytest mis/tests/test_unified_ranking.py::test_title_normalization -x` | ❌ Wave 0 |
| DASH-V2-03 | Cada produto tem platform_name, unified_score, rank, rank_type | unit | `pytest mis/tests/test_unified_ranking.py::test_result_fields -x` | ❌ Wave 0 |
| DASH-V2-03 | Produto stale tem is_stale=True no resultado | unit | `pytest mis/tests/test_unified_ranking.py::test_stale_included -x` | ❌ Wave 0 |
| DASH-V2-01 | Nicho com 1 plataforma: warning_single_platform=True retornado | unit | `pytest mis/tests/test_unified_ranking.py::test_single_platform_warning -x` | ❌ Wave 0 |
| DASH-V2-01 | Paginação: page=2, per_page=5 retorna slice correto | unit | `pytest mis/tests/test_unified_ranking.py::test_pagination -x` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest mis/tests/test_unified_ranking.py -x -q`
- **Per wave merge:** `pytest mis/tests/ -x -q`
- **Phase gate:** Full suite green antes de `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `mis/tests/test_unified_ranking.py` — cobre todos os 12 cenários acima (arquivo novo)
- [ ] Nenhum gap em conftest.py — fixture `db_path` existente é suficiente

*(Framework, conftest.py e padrões de DB fixture já existem — apenas o arquivo de teste é novo)*

---

## Sources

### Primary (HIGH confidence)

- `mis/web/routes/ranking.py` — padrão de rota HTMX + `is_htmx()` + `_get_ranking_context()`
- `mis/dossier_repository.py` — padrão SQL com JOIN platforms/niches + params list + cursor.description
- `mis/web/templates/ranking.html` — padrão HTMX selects + `hx-include` + `hx-target`
- `mis/web/templates/ranking_table.html` — estrutura de tabela + badge condicional
- `mis/web/templates/base.html` — dark theme Tailwind classes, HTMX 2.0.8 CDN
- `mis/migrations/_006_v2_platforms.py` — rank_type por plataforma (positional/gravity/upvotes/enrollment)
- `mis/product_repository.py` — onde `list_unified_ranking()` será adicionada
- `mis/tests/conftest.py` + `mis/tests/test_gumroad_scanner.py` — padrão de fixture de testes

### Secondary (MEDIUM confidence)

- Python stdlib `unicodedata` — NFKD normalization para remoção de acentos (conhecimento de training, verificado por uso padrão universal)
- FastAPI query param bool conversion — comportamento padrão documentado (training knowledge, LOW risk)

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — lido diretamente do codebase existente
- Architecture: HIGH — padrão replicado de ranking.py existente, sem novidade arquitetural
- SQL query: HIGH — adaptado de dossier_repository.py existente com adição de rank_type join
- Percentile math: HIGH — fórmulas definidas nas decisões do usuário, simples aritmética Python
- Pitfalls: HIGH — identificados por análise do código + edge cases das decisões

**Research date:** 2026-03-17
**Valid until:** 2026-04-17 (stack estável, sem dependências externas novas)
