# Phase 20: Niche Data Model - Research

**Researched:** 2026-03-17
**Domain:** SQLite schema migration + seed data (nichos/subnichos + slug mappings por plataforma)
**Confidence:** HIGH

---

## Summary

A Phase 20 introduz uma hierarquia nicho/subnicho no banco MIS. Atualmente a tabela `niches` armazena nichos planos (3 linhas: marketing-digital, emagrecimento, financas-pessoais) com um único `slug` global — sem distinção de plataforma e sem subnichos. O v3.0 requer 4 nichos fixos com ~40 subnichos, cada um mapeado para um slug específico por plataforma (ex: `weight-loss` no ClickBank, `emagrecimento` no Hotmart).

A abordagem mais limpa é um par de tabelas novas (`niches_v3`, `subniches`) criadas por migration `_008`, sem tocar na tabela `niches` legada — preservando todos os produtos e dados v1.0/v2.0 existentes que referenciam `niche_id`. Os slugs por plataforma são melhor armazenados em uma tabela de mapeamento `subniche_platform_slugs` (relação N:M entre subnicho e plataforma) ou como JSON blob embutido no registro do subnicho. A segunda opção (JSON blob) é mais simples de implementar com sqlite-utils, mas dificulta queries filtradas; a tabela de mapeamento permite `WHERE platform_slug = 'clickbank'` direto em SQL. Dado que Phase 21 (Manual Search Engine) vai precisar de lookups por plataforma, a tabela de mapeamento é recomendada.

A data layer já usa o padrão sqlite-utils + `INSERT OR IGNORE` para idempotência (ver `_006_v2_platforms.py`). Migration `_008` deve seguir esse padrão exato. Um `niche_repository.py` expondo `list_niches()`, `list_subniches(niche_slug)` e `get_platform_slug(subniche_id, platform_slug)` será o contrato que Phase 21 vai consumir.

**Primary recommendation:** Criar `_008_niche_v3.py` com 3 tabelas novas (`niches_v3`, `subniches`, `subniche_platform_slugs`), populá-las com seed data inline na própria migration via `INSERT OR IGNORE`, e expor `niche_repository.py` com 3 funções de query. Não alterar tabela `niches` legada.

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| NICHE-01 | Sistema define 4 nichos fixos (Relacionamento, Saúde, Finanças, Renda Extra) com ~40 subnichos pré-configurados e mapeados por plataforma | Migration `_008` cria as tabelas e insere o seed data completo via `INSERT OR IGNORE` |
| NICHE-02 | Cada subnicho tem slug de busca específico por plataforma (ex: "weight-loss" no ClickBank, "emagrecimento" no Hotmart) | Tabela `subniche_platform_slugs` com FK para `subniches.id` e `platforms.id` (platforms já existe com 12 linhas) |
</phase_requirements>

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| sqlite-utils | 3.x (já instalado) | Criação de tabelas, queries, `INSERT OR IGNORE` | Padrão existente em todo o projeto MIS |
| Python stdlib (sqlite3) | 3.14 | Conexão direta para migrations sem overhead | Padrão existente |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest + tmp_path | existente | Testes unitários de migration (in-memory DB) | Todos os testes de migration |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Tabela `subniche_platform_slugs` | JSON blob em `subniches.platform_slugs` | JSON é mais simples mas impede `WHERE platform_slug = ?` em SQL puro; tabela relacional é necessária para Phase 21 |
| Migration inline seed | YAML seed file separado | YAML exige loader extra; inline é auto-contido e segue o padrão `_006_v2_platforms.py` |
| Novas tabelas separadas | Alterar `niches` existente | Alterar `niches` quebraria FKs de todos os produtos v1.0/v2.0 (niche_id) |

**Installation:** Nenhuma instalação necessária — sqlite-utils já está no ambiente.

---

## Architecture Patterns

### Recommended Project Structure (arquivos novos)
```
mis/
├── migrations/
│   └── _008_niche_v3.py          # nova migration: 3 tabelas + seed data
├── niche_repository.py           # novo: query functions (list_niches, list_subniches, get_platform_slug)
├── db.py                         # ALTERAR: adicionar _run_008 na cadeia
└── tests/
    └── test_migration_008.py     # novo: testes idempotency + contagem + slug lookup
```

### Pattern 1: Migration com Seed Inline (padrão do projeto)
**What:** A migration cria as tabelas com `CREATE TABLE IF NOT EXISTS` equivalente (sqlite-utils `if "table" not in db.table_names()`), depois faz seed com `INSERT OR IGNORE` usando IDs fixos.
**When to use:** Sempre que dados de referência fazem parte do schema (não dados de usuário).
**Example:**
```python
# Source: padrão de _006_v2_platforms.py no projeto
def run_migration_008(db_path: str) -> None:
    db = sqlite_utils.Database(db_path)

    if "niches_v3" not in db.table_names():
        db["niches_v3"].create(
            {"id": int, "name": str, "slug": str},
            pk="id",
            not_null={"name", "slug"},
        )
        db["niches_v3"].create_index(["slug"], unique=True)

    if "subniches" not in db.table_names():
        db["subniches"].create(
            {"id": int, "niche_id": int, "name": str, "slug": str},
            pk="id",
            not_null={"name", "slug", "niche_id"},
            foreign_keys=[("niche_id", "niches_v3", "id")],
        )
        db["subniches"].create_index(["niche_id", "slug"], unique=True)

    if "subniche_platform_slugs" not in db.table_names():
        db["subniche_platform_slugs"].create(
            {"subniche_id": int, "platform_id": int, "search_slug": str},
            pk=["subniche_id", "platform_id"],
            foreign_keys=[
                ("subniche_id", "subniches", "id"),
                ("platform_id", "platforms", "id"),
            ],
        )

    # INSERT OR IGNORE para cada nicho, subnicho e mapeamento
    for niche_id, name, slug in _NICHES_V3:
        db.execute(
            "INSERT OR IGNORE INTO niches_v3 (id, name, slug) VALUES (?, ?, ?)",
            (niche_id, name, slug),
        )
    # ... subnichos e slugs por plataforma
```

### Pattern 2: Repository Layer
**What:** Módulo `niche_repository.py` com funções puras que recebem `db_path` ou `db: sqlite_utils.Database` e retornam listas de dicts — mesmo padrão de `product_repository.py` e `dossier_repository.py`.
**When to use:** Toda vez que código de negócio precisa consultar nichos/subnichos.
**Example:**
```python
# Source: padrão de product_repository.py e dossier_repository.py no projeto
def list_niches(db_path: str) -> list[dict]:
    """Return all v3 niches as list of {id, name, slug}."""
    db = sqlite_utils.Database(db_path)
    rows = db.execute("SELECT id, name, slug FROM niches_v3 ORDER BY id").fetchall()
    return [{"id": r[0], "name": r[1], "slug": r[2]} for r in rows]


def list_subniches(db_path: str, niche_slug: str) -> list[dict]:
    """Return all subniches for a given niche slug."""
    db = sqlite_utils.Database(db_path)
    rows = db.execute(
        """
        SELECT s.id, s.name, s.slug
          FROM subniches s
          JOIN niches_v3 n ON n.id = s.niche_id
         WHERE n.slug = ?
         ORDER BY s.id
        """,
        [niche_slug],
    ).fetchall()
    return [{"id": r[0], "name": r[1], "slug": r[2]} for r in rows]


def get_platform_slug(db_path: str, subniche_id: int, platform_slug: str) -> str | None:
    """Return the search slug for a subniche on a specific platform, or None."""
    db = sqlite_utils.Database(db_path)
    row = db.execute(
        """
        SELECT sps.search_slug
          FROM subniche_platform_slugs sps
          JOIN platforms pl ON pl.id = sps.platform_id
         WHERE sps.subniche_id = ?
           AND pl.slug = ?
        """,
        [subniche_id, platform_slug],
    ).fetchone()
    return row[0] if row else None
```

### Anti-Patterns to Avoid
- **Alterar tabela `niches` existente:** A tabela `niches` tem `niche_id` referenciado em `products`, `pains`. Qualquer ALTER TABLE DROP/RENAME nessa tabela quebra FKs silenciosamente no SQLite (não tem constraint enforcement no ALTER). Usar tabelas novas é o caminho seguro.
- **Slug único global por subnicho:** O mesmo conceito "emagrecimento" tem slug diferente em cada plataforma (`weight-loss` no ClickBank, `saude-e-fitness` no Hotmart). Usar um único slug seria errado.
- **Carregar slugs de config.yaml em runtime:** config.yaml tem 3 nichos v1/v2 no formato antigo. Misturar fontes de verdade (config.yaml + DB) é uma armadilha de sincronização. Os slugs v3 devem viver apenas no banco, seed pela migration.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Idempotência de INSERT | lógica manual de "SELECT + INSERT se vazio" | `INSERT OR IGNORE` com PK explícita | Padrão atomico do SQLite; já usado em `_006_v2_platforms.py` |
| Criação condicional de tabela | `DROP TABLE IF EXISTS` + `CREATE TABLE` | `if "table" not in db.table_names()` + `db["table"].create(...)` | sqlite-utils já faz isso; DROP destrói dados |
| Lookup de slugs em código | dicionário hardcoded em cada scanner | `get_platform_slug(db_path, subniche_id, platform_slug)` do repositório | Centraliza a fonte de verdade; Phase 21 pode alterar slugs sem tocar código de scanner |

**Key insight:** O sqlite-utils já resolve criação idempotente de tabelas e inserções seguras. A tentação de resolver no YAML deve ser resistida — o banco é a fonte de verdade para Phase 21+.

---

## Common Pitfalls

### Pitfall 1: SQLite ignora FK constraints por default
**What goes wrong:** `PRAGMA foreign_keys` está OFF por default. FK violations em `subniche_platform_slugs` (platform_id inexistente) passam silenciosamente se a migration rodar antes de `_006` inserir as plataformas.
**Why it happens:** SQLite não enforça FKs sem o PRAGMA explícito.
**How to avoid:** A migration `_008` deve ser registrada DEPOIS de `_006` e `_007` em `db.py`. A cadeia já começa com `PRAGMA foreign_keys=ON` em `get_db()` — mas as migrations usam `sqlite_utils.Database(db_path)` direto sem o PRAGMA. Adicionar `db.execute("PRAGMA foreign_keys=ON")` no início de `_008` é boa prática.
**Warning signs:** Inserção de `subniche_platform_slugs` com platform_id=99 (inexistente) não lança erro.

### Pitfall 2: `CREATE INDEX` duplicado em re-run
**What goes wrong:** sqlite-utils lança exceção se tentar criar um índice que já existe.
**Why it happens:** `db["table"].create_index(...)` não verifica existência por default.
**How to avoid:** Criar o índice dentro do bloco `if "table" not in db.table_names()` — assim só executa na primeira vez. Padrão já correto em `_001_initial.py`.
**Warning signs:** `OperationalError: index already exists`.

### Pitfall 3: Seed data com IDs não-fixos
**What goes wrong:** Se o seed não especifica `id` explícito, o SQLite usa autoincrement e IDs mudam entre ambientes/reinstalações.
**Why it happens:** Banco novo vs. banco com dados prévios geram sequências diferentes.
**How to avoid:** Definir IDs fixos nos `_NICHES_V3`, `_SUBNICHES`, etc. — exatamente como `_PLATFORMS` em `_006`. Phase 21 vai referenciar `subniche_id` em queries; IDs devem ser estáveis.
**Warning signs:** Slugs lookups retornam None em banco recém-criado mas funcionam em banco antigo.

### Pitfall 4: config.py valida "3-5 nichos" — vai quebrar ao mudar config.yaml
**What goes wrong:** `config.py` linha 62: `if not (3 <= len(niches) <= 5): raise ValueError`. Se config.yaml for atualizado para 4 nichos v3, a validação passa. Mas se alguém remover os nichos antigos, os testes que usam `temp_config_yaml` (3 nichos) ainda passam — o problema é apenas de escopo da Phase 20.
**Why it happens:** config.yaml e o banco são fontes separadas. Phase 20 não muda config.yaml — deixa para Phase 21 decidir se config.yaml é descontinuado.
**How to avoid:** Phase 20 NÃO altera config.yaml. Os 4 nichos v3 vivem apenas no banco via migration `_008`.

### Pitfall 5: Subnicho sem slug mapeado para plataforma que não suporta filtragem
**What goes wrong:** Plataformas como PerfectPay, Eduzz, Monetizze têm `null` em config.yaml porque não têm marketplace público. O seed de `subniche_platform_slugs` não deve inserir linhas com `search_slug = NULL` — essas plataformas simplesmente não terão entradas na tabela de mapeamento.
**Why it happens:** O schema de `subniche_platform_slugs` tem `search_slug` como NOT NULL implícito.
**How to avoid:** No seed data, inserir apenas mapeamentos onde há slug válido. `get_platform_slug()` retorna `None` para plataformas não mapeadas — Phase 21 trata isso como "scanner não aplicável para este subnicho".

---

## Code Examples

### Seed data canônico (referência para a migration)

Os 4 nichos com IDs fixos:
```python
# Source: definido neste research + STATE.md decisions
_NICHES_V3 = [
    (1, "Relacionamento", "relacionamento"),
    (2, "Saúde",          "saude"),
    (3, "Finanças",       "financas"),
    (4, "Renda Extra",    "renda-extra"),
]
```

Os ~40 subnichos com IDs fixos (10-12 por nicho):
```python
_SUBNICHES = [
    # Relacionamento (niche_id=1)
    (101, 1, "Reconquista",                  "reconquista"),
    (102, 1, "Sedução masculina",             "seducao-masculina"),
    (103, 1, "Relacionamento feminino",       "relacionamento-feminino"),
    (104, 1, "Casamento e família",           "casamento-e-familia"),
    (105, 1, "Autoestima e confiança",        "autoestima-e-confianca"),
    (106, 1, "Comunicação e influência",      "comunicacao-e-influencia"),
    (107, 1, "Traição e ciúmes",              "traicao-e-ciumes"),
    (108, 1, "Divórcio e recomeço",           "divorcio-e-recomeco"),
    (109, 1, "Relacionamento à distância",    "relacionamento-a-distancia"),
    (110, 1, "Atração e linguagem corporal",  "atracao-e-linguagem-corporal"),
    # Saúde (niche_id=2)
    (201, 2, "Emagrecimento",                 "emagrecimento"),
    (202, 2, "Diabetes e glicemia",           "diabetes-e-glicemia"),
    (203, 2, "Ansiedade e sono",              "ansiedade-e-sono"),
    (204, 2, "Ganho de massa",                "ganho-de-massa"),
    (205, 2, "Saúde feminina",                "saude-feminina"),
    (206, 2, "Cabelo e pele",                 "cabelo-e-pele"),
    (207, 2, "Dor crônica e coluna",          "dor-cronica-e-coluna"),
    (208, 2, "Tireoide e hormônios",          "tireoide-e-hormonios"),
    (209, 2, "Detox e alimentação saudável",  "detox-e-alimentacao-saudavel"),
    (210, 2, "Saúde masculina",               "saude-masculina"),
    (211, 2, "Visão e audição",               "visao-e-audicao"),
    (212, 2, "Pressão alta e colesterol",     "pressao-alta-e-colesterol"),
    # Finanças (niche_id=3)
    (301, 3, "Renda extra online",            "renda-extra-online"),
    (302, 3, "Investimentos para iniciantes", "investimentos-para-iniciantes"),
    (303, 3, "Sair das dívidas",              "sair-das-dividas"),
    (304, 3, "Day trade e cripto",            "day-trade-e-cripto"),
    (305, 3, "Empreendedorismo",              "empreendedorismo"),
    (306, 3, "Imóveis e renda passiva",       "imoveis-e-renda-passiva"),
    (307, 3, "Finanças para MEI",             "financas-para-mei"),
    (308, 3, "Aposentadoria e independência", "aposentadoria-e-independencia"),
    (309, 3, "Concursos públicos",            "concursos-publicos"),
    (310, 3, "Importação e revenda",          "importacao-e-revenda"),
    # Renda Extra (niche_id=4)
    (401, 4, "Tráfego pago",                  "trafego-pago"),
    (402, 4, "Afiliados",                     "afiliados"),
    (403, 4, "Marketing de conteúdo",         "marketing-de-conteudo"),
    (404, 4, "Dropshipping",                  "dropshipping"),
    (405, 4, "Serviços freelancer",           "servicos-freelancer"),
    (406, 4, "Social media",                  "social-media"),
    (407, 4, "Vendas pelo WhatsApp",          "vendas-pelo-whatsapp"),
    (408, 4, "Edição de vídeo e design",      "edicao-de-video-e-design"),
    (409, 4, "Copywriting",                   "copywriting"),
    (410, 4, "Consultoria e mentoria online", "consultoria-e-mentoria-online"),
    (411, 4, "YouTube e criação de conteúdo", "youtube-e-criacao-de-conteudo"),
    (412, 4, "Precificação e vendas locais",  "precificacao-e-vendas-locais"),
]
```

Slugs por plataforma (amostra — a migration precisa do conjunto completo):
```python
# Source: config.yaml existente + definições do additional_context
# (subniche_id, platform_slug, search_slug)
_PLATFORM_SLUGS = [
    # Subnicho 201: Emagrecimento
    (201, "hotmart",       "saude-e-fitness"),
    (201, "clickbank",     "health"),
    (201, "kiwify",        "saude"),
    (201, "braip",         "encapsulados"),
    (201, "udemy",         "Health & Fitness"),
    (201, "gumroad",       "health"),
    (201, "appsumo",       "health-fitness"),
    # Subnicho 101: Reconquista
    (101, "hotmart",       "relacionamentos"),
    (101, "clickbank",     "relationships"),
    (101, "kiwify",        "relacionamentos"),
    # ... (migration terá todos os mapeamentos)
]
```

### Teste de migration (padrão do projeto)
```python
# Source: padrão de test_migration_006.py
def test_4_niches_v3_inserted(db_path):
    run_migrations(db_path)  # inclui _008
    db = sqlite_utils.Database(db_path)
    count = next(db.execute("SELECT COUNT(*) FROM niches_v3"))[0]
    assert count == 4

def test_subniche_count_at_least_40(db_path):
    run_migrations(db_path)
    db = sqlite_utils.Database(db_path)
    count = next(db.execute("SELECT COUNT(*) FROM subniches"))[0]
    assert count >= 40

def test_platform_slug_lookup(db_path):
    run_migrations(db_path)
    db = sqlite_utils.Database(db_path)
    row = db.execute(
        """SELECT sps.search_slug
             FROM subniche_platform_slugs sps
             JOIN subniches s ON s.id = sps.subniche_id
             JOIN platforms pl ON pl.id = sps.platform_id
            WHERE s.slug = 'emagrecimento' AND pl.slug = 'clickbank'"""
    ).fetchone()
    assert row is not None
    assert row[0] == "health"

def test_migration_idempotent(db_path):
    run_migrations(db_path)
    run_migration_008(db_path)  # segunda vez — não deve levantar
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Nichos planos em `niches` (3 linhas, slug único global) | Hierarquia `niches_v3` + `subniches` com `subniche_platform_slugs` | Phase 20 (v3.0) | Permite pesquisa por subnicho com slug correto por plataforma |
| Nichos configurados em config.yaml | Nichos como dados no banco (seed via migration) | Phase 20 (v3.0) | Banco é fonte de verdade — sem dependência de arquivo YAML em runtime |

**Deprecated/outdated:**
- Tabela `niches` (linhas v1/v2): continua existindo para preservar FKs de `products` e `pains`. Não deletar. Simplesmente não é usada pelos fluxos v3.
- `config.yaml` niches block: continua sendo lido pelos scanners v1/v2 (que não são afetados pela Phase 20). Phase 20 não altera `config.yaml`.

---

## Open Questions

1. **Slugs por plataforma para todos os 42 subnichos — definição completa**
   - What we know: config.yaml tem slugs para 3 nichos amplos (marketing, emagrecimento, financas) mapeados para as 12 plataformas. Os padrões de null (PerfectPay, Eduzz, Monetizze) e slugs genéricos (JVZoo usa `"84"` para tudo) estão documentados.
   - What's unclear: Os slugs específicos para os 42 subnichos novos nas plataformas BR (Hotmart, Kiwify, Braip) e internacionais (ClickBank, Udemy, Gumroad, AppSumo, JVZoo). Relacionamento/Renda Extra não existiam no config.yaml anterior.
   - Recommendation: O planner deve incluir um task de "definição + validação de slugs" como Wave 0 antes de escrever o seed data completo. Uma abordagem: mapear os nichos de Relacionamento e Renda Extra para as categorias mais próximas disponíveis por plataforma (ex: ClickBank `self-help` para relacionamento), com fallback para o slug genérico do nicho-pai quando não há categoria específica.

2. **Produto existente com `niche_id` legado — impacto no ranking unificado**
   - What we know: `list_unified_ranking()` usa `JOIN niches n ON n.id = p.niche_id` — referencia tabela `niches` antiga.
   - What's unclear: Se Phase 21 vai migrar produtos existentes para `subniche_id` (FK para `subniches`) ou se o campo de pesquisa será separado dos produtos existentes.
   - Recommendation: Phase 20 não precisa resolver isso — apenas expor o modelo de dados. Phase 21 decide se produtos v1/v2 são "órfãos" ou recebem um `subniche_id` de compatibilidade.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (existente) |
| Config file | `mis/tests/conftest.py` (fixture `db_path` via `tmp_path`) |
| Quick run command | `python -m pytest mis/tests/test_migration_008.py -x -q` |
| Full suite command | `python -m pytest mis/tests/ -x -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| NICHE-01 | 4 nichos inseridos em `niches_v3` | unit | `pytest mis/tests/test_migration_008.py::test_4_niches_v3_inserted -x` | Wave 0 |
| NICHE-01 | >= 40 subnichos inseridos em `subniches` | unit | `pytest mis/tests/test_migration_008.py::test_subniche_count_at_least_40 -x` | Wave 0 |
| NICHE-01 | `list_subniches("saude")` retorna >= 10 entradas | unit | `pytest mis/tests/test_niche_repository.py::test_list_subniches_saude -x` | Wave 0 |
| NICHE-02 | slug `emagrecimento` + `clickbank` retorna `"health"` | unit | `pytest mis/tests/test_migration_008.py::test_platform_slug_lookup -x` | Wave 0 |
| NICHE-02 | `get_platform_slug(subniche_id, "hotmart")` retorna valor não-nulo para subnicho com mapeamento | unit | `pytest mis/tests/test_niche_repository.py::test_get_platform_slug_hotmart -x` | Wave 0 |
| NICHE-01+02 | Migration `_008` é idempotente (segunda chamada não lança) | unit | `pytest mis/tests/test_migration_008.py::test_migration_idempotent -x` | Wave 0 |
| NICHE-01+02 | `run_migrations()` em banco existente v1/v2 não destrói dados | integration | `pytest mis/tests/test_migration_008.py::test_existing_products_preserved -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest mis/tests/test_migration_008.py mis/tests/test_niche_repository.py -x -q`
- **Per wave merge:** `python -m pytest mis/tests/ -x -q`
- **Phase gate:** Full suite green antes de `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `mis/tests/test_migration_008.py` — cobre NICHE-01 e NICHE-02
- [ ] `mis/tests/test_niche_repository.py` — cobre queries `list_niches`, `list_subniches`, `get_platform_slug`

*(Infraestrutura de test (pytest, conftest.py, fixture `db_path`) ja existe — nenhuma instalação nova necessária)*

---

## Sources

### Primary (HIGH confidence)
- `mis/db.py` — cadeia de migrations existente (_001 a _007), padrão `run_migrations()`
- `mis/migrations/_001_initial.py` — padrão `if "table" not in db.table_names()` + `create_index`
- `mis/migrations/_006_v2_platforms.py` — padrão `INSERT OR IGNORE` com IDs fixos + seed data inline
- `mis/migrations/_007_is_stale.py` — padrão `add_column` idempotente
- `mis/product_repository.py` — padrão repository layer (funções retornam dicts)
- `mis/config.py` — slugs por plataforma existentes (v1/v2), VALID_PLATFORMS
- `mis/config.yaml` — mapeamentos de slugs existentes para 3 nichos e 12 plataformas
- `mis/platform_ids.py` — IDs fixos das 12 plataformas (usados como FK em `subniche_platform_slugs`)
- `mis/tests/conftest.py` e `test_migration_006.py` — padrão de teste de migration

### Secondary (MEDIUM confidence)
- `.planning/STATE.md` — decisão arquitetural: "hierarquia nicho/subnicho substitui config.yaml de nichos livres — slugs por plataforma embutidos no schema"
- `.planning/REQUIREMENTS.md` — NICHE-01 e NICHE-02 requirements oficiais
- `.planning/ROADMAP.md` — success criteria da Phase 20

### Tertiary (LOW confidence)
- Nenhuma

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — sqlite-utils e padrão de migrations estão 100% verificados no código existente
- Architecture: HIGH — padrão de 3 tabelas + repository layer é diretamente derivado do código existente
- Pitfalls: HIGH — identificados diretamente no código e schema existentes
- Seed data slugs (relacionamento/renda-extra por plataforma): MEDIUM — slugs para nichos novos precisam ser validados empiricamente nas plataformas

**Research date:** 2026-03-17
**Valid until:** 2026-04-17 (stack estável; sqlite-utils não tem breaking changes frequentes)
