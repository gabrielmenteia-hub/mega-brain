# Phase 13: Infrastructure + Tech Debt — Research

**Researched:** 2026-03-16
**Domain:** SQLite schema migrations, Python module constants, documentation sign-off
**Confidence:** HIGH

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| INFRA-01 | Migration `_006_v2_platforms.py` cria rows para todas as 16 plataformas com `INSERT OR IGNORE` (elimina FK constraint violation em produção) | Confirmed: `_001_initial.py` cria `platforms` table mas não insere rows. Todas as migrations existentes (001-005) estabelecem o padrão `INSERT OR IGNORE`. FK violation ocorre quando scanner tenta inserir `products.platform_id` que não existe em `platforms`. |
| INFRA-02 | `mis/platform_ids.py` centraliza todos os IDs de plataforma como constantes nomeadas (elimina risco de collision entre scanners) | Confirmed: Atualmente cada scanner define sua constante local (`HOTMART_PLATFORM_ID = 1`, `CLICKBANK_PLATFORM_ID = 2`, `KIWIFY_PLATFORM_ID = 3`). `mis/platform_ids.py` não existe. |
| INFRA-03 | Campo `rank_type` adicionado à tabela `products` para identificar a semântica do rank por plataforma | Confirmed: `products` table em `_001_initial.py` tem apenas `rank_score: float`. Campo `rank_type` ausente. Migration de ALTER TABLE + UPDATE necessária. |
| DEBT-01 | `nyquist_compliant: false` corrigido em todos os 12 VALIDATION.md | Confirmed: `grep -r "nyquist_compliant: false"` retorna 12 arquivos em `.planning/phases/01-foundation/` até `12-meta-ads-pain-radar/`. Todos precisam atualizar frontmatter e o checklist de sign-off. |
| DEBT-02 | Docstring `radar/__init__.py:141` atualizada de "5 jobs" → "6 jobs" | Confirmed: Linha 141 lê `"""Register the 5 Pain Radar jobs in APScheduler singleton.` — desatualizado desde Phase 12 (meta_ads adicionado como 6º job). |
</phase_requirements>

---

## Summary

Phase 13 é inteiramente sobre pré-condições e liquidação de tech debt — nenhuma lógica de negócio nova, apenas fundação para as Phases 14-17. As cinco tarefas são cirúrgicas e bem delimitadas: uma migration, um novo módulo de constantes, um ALTER TABLE + UPDATE, 12 edições de frontmatter YAML, e uma edição de docstring.

O risco principal é a migration INFRA-01: inserir 16 plataformas requer que os IDs sejam coordenados com `platform_ids.py` (INFRA-02). Os dois devem ser desenvolvidos juntos — a migration define os IDs numéricos, `platform_ids.py` expõe as constantes nomeadas. A ordem correta de execução é: migration 006 primeiro (define IDs no DB), depois `platform_ids.py` (espelha esses IDs como constantes Python), depois migration de `rank_type` (INFRA-03).

DEBT-01 e DEBT-02 são mecânicos: edições de texto que não requerem nenhuma mudança de código Python. O sign-off do nyquist envolve (1) verificar que os testes da fase passam, (2) atualizar `nyquist_compliant: false` → `true` e `wave_0_complete: false` → `true` no frontmatter, (3) marcar o checklist de sign-off como completo.

**Primary recommendation:** Implementar INFRA-01 + INFRA-02 em uma única tarefa (são interdependentes), INFRA-03 como tarefa separada, DEBT-01 como varredura automatizada das 12 fases, DEBT-02 como edição pontual de uma linha.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| sqlite_utils | 3.x (already installed) | Criar migration, ALTER TABLE | Já é a ORM de migração do projeto — todos os 005 migrations usam |
| sqlite3 | stdlib | Fallback para raw SQL quando sqlite_utils não tem conveniência | Já usado em `_run_cleanup()` e outros |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | 8.4.2 (already installed) | Testes das migrations novas | Padrão do projeto — `mis/pytest.ini` configurado |
| pytest-asyncio | 0.24.0 (already installed) | Testes async se necessário | Já no conftest, mas INFRA não tem async |

**Installation:** Nenhuma instalação nova necessária — stack 100% já disponível.

---

## Architecture Patterns

### Recommended Project Structure (Phase 13 additions)

```
mis/
├── platform_ids.py          # NEW — INFRA-02: constantes nomeadas de platform IDs
├── migrations/
│   ├── _006_v2_platforms.py # NEW — INFRA-01: INSERT OR IGNORE 16 plataformas
│   └── __init__.py          # UPDATE — adicionar import run_migration_006
├── db.py                    # UPDATE — adicionar chamada _run_006 em run_migrations()
└── radar/__init__.py        # UPDATE — DEBT-02: "5 jobs" → "6 jobs" na docstring

.planning/phases/
├── 01-foundation/01-VALIDATION.md         # UPDATE frontmatter + sign-off
├── 02-platform-scanners/02-VALIDATION.md  # UPDATE frontmatter + sign-off
│   ... (10 mais) ...
└── 12-meta-ads-pain-radar/12-VALIDATION.md # UPDATE frontmatter + sign-off
```

### Pattern 1: Migration `INSERT OR IGNORE` com registros de plataforma

**What:** A migration 006 insere rows de plataformas usando `INSERT OR IGNORE` para que seja idempotente. Cada row tem `id` fixo (inteiro), `name`, `slug`, `base_url`, `rank_type`.

**When to use:** Qualquer migration que precisa pré-popular tabelas de lookup sem risco de duplicação em ambientes já inicializados.

**Example:**
```python
# Source: padrão estabelecido no codebase (mis/migrations/_005_alerts.py)
def run_migration_006(db_path: str) -> None:
    db = sqlite_utils.Database(db_path)

    PLATFORMS = [
        (1,  "Hotmart",      "hotmart",      "https://hotmart.com",      "positional"),
        (2,  "ClickBank",    "clickbank",    "https://clickbank.com",    "gravity"),
        (3,  "Kiwify",       "kiwify",       "https://kiwify.com.br",    "positional"),
        # ... 13 mais
    ]

    db.execute("""
        CREATE TABLE IF NOT EXISTS platforms (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            base_url TEXT,
            rank_type TEXT,
            created_at TEXT
        )
    """)  # idempotente — sem erro se já existe

    for row in PLATFORMS:
        db.execute(
            "INSERT OR IGNORE INTO platforms (id, name, slug, base_url, rank_type, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (*row, datetime.utcnow().isoformat())
        )
```

### Pattern 2: Módulo de constantes `platform_ids.py`

**What:** Arquivo Python simples com constantes nomeadas espelhando os IDs definidos na migration 006. Zero lógica — apenas dados.

**When to use:** Qualquer scanner novo importa daqui em vez de definir constante local.

**Example:**
```python
# Source: padrão observado em hotmart.py, clickbank.py, kiwify.py (constantes locais hoje)
# mis/platform_ids.py
"""Centralized platform ID constants for MIS scanners.

These IDs correspond to the rows inserted by migration _006_v2_platforms.py.
Import from here instead of defining local constants in each scanner.

Usage:
    from mis.platform_ids import HOTMART_PLATFORM_ID, EDUZZ_PLATFORM_ID
"""

HOTMART_PLATFORM_ID = 1
CLICKBANK_PLATFORM_ID = 2
KIWIFY_PLATFORM_ID = 3
EDUZZ_PLATFORM_ID = 4
MONETIZZE_PLATFORM_ID = 5
PERFECTPAY_PLATFORM_ID = 6
BRAIP_PLATFORM_ID = 7
PRODUCT_HUNT_PLATFORM_ID = 8
UDEMY_PLATFORM_ID = 9
JVZOO_PLATFORM_ID = 10
GUMROAD_PLATFORM_ID = 11
APPSUMO_PLATFORM_ID = 12
# ... até 16
```

### Pattern 3: ALTER TABLE via sqlite_utils para `rank_type`

**What:** Migration 006 (ou separada) adiciona coluna `rank_type` à tabela `products` e depois faz UPDATE para preencher com base no `platform_id`. sqlite_utils tem `.add_column()` que é idempotente via try/except.

**When to use:** Adicionar coluna a tabela existente sem recriar dados.

**Example:**
```python
# Source: padrão existente em _005_alerts.py lines 64-67
if "products" in db.table_names():
    existing_cols = {col.name for col in db["products"].columns}
    if "rank_type" not in existing_cols:
        db["products"].add_column("rank_type", str)

    # Backfill: preenche rank_type com base no platform_id
    db.execute("""
        UPDATE products SET rank_type = (
            SELECT p.rank_type FROM platforms p
            WHERE p.id = products.platform_id
        )
        WHERE rank_type IS NULL
    """)
```

**Note:** O `rank_type` deve ser preenchido na tabela `platforms` (pela migration 006) antes de ser propagado para `products`. A ordem de execução em `db.run_migrations()` garante isso.

### Pattern 4: Nyquist sign-off via edição de frontmatter YAML

**What:** Cada VALIDATION.md tem frontmatter YAML com `nyquist_compliant: false`. O sign-off requer:
1. Confirmar que o test suite da fase passa
2. Alterar `nyquist_compliant: false` → `nyquist_compliant: true`
3. Alterar `wave_0_complete: false` → `wave_0_complete: true`
4. Marcar os 6 itens do checklist "Validation Sign-Off" como `[x]`
5. Alterar `**Approval:** pending` → `**Approval:** signed off YYYY-MM-DD`

**When to use:** Final de cada fase de implementação — após todos os testes passarem.

### Anti-Patterns to Avoid

- **IDs hardcoded nos scanners:** Nunca definir `PLATFORM_ID = N` em arquivo de scanner. Sempre importar de `mis.platform_ids`.
- **Migration sem `INSERT OR IGNORE`:** Usar `INSERT OR REPLACE` ou `INSERT` sem guard fará a migration falhar na segunda execução. Sempre `INSERT OR IGNORE`.
- **`rank_type` em `products` sem preencher em `platforms`:** O campo em `products` é derivado — a fonte da verdade é a tabela `platforms`. Backfill via JOIN/subquery, não hardcode por platform_id.
- **DROP TABLE em migration:** Nunca. Todas as migrations do projeto são aditivas. ALTER TABLE + ADD COLUMN é o padrão para mudanças em tabelas existentes.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Idempotência da migration | Script de check manual se tabela existe | `CREATE TABLE IF NOT EXISTS` + `INSERT OR IGNORE` | Padrão SQLite nativo, zero overhead |
| ADD COLUMN idempotente | DROP+RECREATE tabela | `sqlite_utils.Table.add_column()` + check de colunas existentes | Preserva dados; padrão já usado em `_005_alerts.py` |
| Verificação de nyquist em lote | Edição manual arquivo por arquivo | Script bash `sed` ou edição multi-arquivo com Read+Edit tool | 12 arquivos — automatizar evita esquecimento |

**Key insight:** Todas as ferramentas necessárias estão no codebase existente. Phase 13 é 100% "usar o que já existe corretamente" — não há novos patterns a inventar.

---

## Common Pitfalls

### Pitfall 1: `rank_type` na tabela `platforms` vs `products`

**What goes wrong:** Developer adiciona `rank_type` em `products` mas não em `platforms`, ou vice-versa. O success criterion #3 exige `rank_type` preenchido *por plataforma no DB* — a semântica é da plataforma, não do produto individual.

**Why it happens:** O `rank_type` é uma propriedade da plataforma (Hotmart usa posição, ClickBank usa gravity), mas precisa estar acessível via query em `products`. Dois locais possíveis causam confusão.

**How to avoid:** A fonte da verdade é `platforms.rank_type`. O campo `products.rank_type` (se necessário para performance) é derivado via backfill. Para as queries de Phase 17 (unified ranking), um JOIN `products JOIN platforms ON products.platform_id = platforms.id` acessa `platforms.rank_type` diretamente — adicionar `rank_type` em `products` pode ser desnecessário. Verificar se Phase 17 precisa do campo em `products` ou se um JOIN é suficiente.

**Warning signs:** Se a migration de `products.rank_type` faz UPDATE via subquery mas `platforms` não tem o campo ainda, o UPDATE silenciosamente deixa todos `NULL`.

### Pitfall 2: Coordenação de IDs entre migration e `platform_ids.py`

**What goes wrong:** A migration define `(4, 'Eduzz', ...)` mas `platform_ids.py` define `EDUZZ_PLATFORM_ID = 5` — mismatch silencioso que causa FK violations.

**Why it happens:** Os dois arquivos são criados separadamente e nenhum valida o outro em runtime.

**How to avoid:** Criar ambos na mesma tarefa de implementação. Adicionar um comentário explícito em `platform_ids.py`: `# These IDs MUST match migration _006_v2_platforms.py`. Adicionar um teste de integração que lê a tabela `platforms` e valida que cada constante de `platform_ids.py` corresponde a um row existente.

**Warning signs:** FK violation ao inserir produto (`FOREIGN KEY constraint failed`) — indica que o platform_id não existe em `platforms`.

### Pitfall 3: Nyquist sign-off mecânico vs substantivo

**What goes wrong:** Developer marca `nyquist_compliant: true` sem verificar que os testes da fase passam de fato, ou sem atualizar o Per-Task Verification Map para refletir status real.

**Why it happens:** DEBT-01 parece uma tarefa burocrática de edição de texto — é fácil "completar" sem verificar.

**How to avoid:** Para cada fase, executar o `quick run command` listado no VALIDATION.md e confirmar que todos os testes passam antes de alterar o frontmatter. O success criterion #4 (`grep -r "nyquist_compliant: false"` retorna zero resultados) é verificável mecanicamente após as edições.

**Warning signs:** Se qualquer teste da fase está falhando quando o sign-off é feito, a compliance é falsa. Verificar com `cd mis && python -m pytest tests/ -x -q` antes de qualquer sign-off.

### Pitfall 4: `rank_type` como campo livre vs enum

**What goes wrong:** Valores inconsistentes inseridos em `platforms.rank_type` — "positional", "position", "pos", "Positional" todos representando a mesma semântica.

**Why it happens:** SQLite não tem enum nativo. Sem constraint, qualquer string é aceita.

**How to avoid:** Definir os valores canônicos uma vez (na migration ou em `platform_ids.py`) e usar exatamente esses valores. Valores recomendados baseados no success criterion: `positional`, `gravity`, `enrollment`, `upvotes`. Phase 17 (percentile normalization) precisará tratar o campo como enum para normalização correta.

---

## Code Examples

Verified patterns from existing codebase:

### Migration com INSERT OR IGNORE (padrão existente)

```python
# Source: mis/migrations/_005_alerts.py — idempotência via IF NOT EXISTS + ADD COLUMN
if "dossiers" in db.table_names():
    existing_cols = {col.name for col in db["dossiers"].columns}
    if "created_at" not in existing_cols:
        db["dossiers"].add_column("created_at", str)
```

### db.py run_migrations() — sequência de chamadas

```python
# Source: mis/db.py lines 34-38
def run_migrations(db_path: str) -> None:
    _run_001(db_path)
    _run_002(db_path)
    _run_003(db_path)
    _run_004(db_path)
    _run_005(db_path)
    # Phase 13 adiciona: _run_006(db_path)
```

### Constante local em scanner (padrão ATUAL a ser substituído)

```python
# Source: mis/scanners/hotmart.py line 36 — padrão a eliminar
HOTMART_PLATFORM_ID = 1  # definido localmente — INFRA-02 move para mis/platform_ids.py

# Após INFRA-02:
from mis.platform_ids import HOTMART_PLATFORM_ID  # importar da fonte única de verdade
```

### Test de migration (padrão para test_migration_006)

```python
# Source: mis/tests/test_migration_003.py — template para test_migration_006
def test_migration_idempotent(db_path):
    """Running run_migration_006() twice must not raise any exception."""
    run_migrations(db_path)
    run_migration_006(db_path)
    run_migration_006(db_path)  # Should not raise

def test_all_16_platforms_inserted(db_path):
    """After run_migration_006(), all 16 platforms must exist in DB."""
    run_migrations(db_path)
    run_migration_006(db_path)
    db = sqlite_utils.Database(db_path)
    count = db.execute("SELECT COUNT(*) FROM platforms").fetchone()[0]
    assert count == 16
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| IDs hardcoded em cada scanner | Constantes em `mis/platform_ids.py` | Phase 13 (INFRA-02) | 13 novos scanners (Phases 14-16) importam de fonte única |
| 3 plataformas na DB (Hotmart, ClickBank, Kiwify) | 16 plataformas via migration 006 | Phase 13 (INFRA-01) | FK violations eliminadas ao iniciar `python -m mis` |
| `rank_score: float` sem semântica | `rank_type: str` em `platforms` + backfill | Phase 13 (INFRA-03) | Percentile normalization em Phase 17 pode tratar gravity diferente de positional |
| `nyquist_compliant: false` em 12 fases | `nyquist_compliant: true` após sign-off | Phase 13 (DEBT-01) | Compliance documentada — indica processo TDD seguido |
| Docstring "5 jobs" desatualizada | "6 jobs" após Phase 12 | Phase 13 (DEBT-02) | Documentação interna correta para futuros contribuidores |

**Deprecated/outdated:**
- Constantes locais (`HOTMART_PLATFORM_ID = 1` em `scanners/hotmart.py`): Após INFRA-02, o padrão correto é importar de `mis.platform_ids`. Os scanners existentes não precisam ser atualizados agora (não é requisito desta fase), mas novos scanners DEVEM usar o módulo centralizado.

---

## Open Questions

1. **`rank_type` em `products` ou apenas em `platforms`?**
   - What we know: Success criterion #3 diz "Cada plataforma no DB tem campo `rank_type` preenchido" — refere-se à tabela `platforms`. Phase 17 fará percentile normalization por plataforma.
   - What's unclear: Se o campo `rank_type` precisa estar desnormalizado em `products` para queries rápidas, ou se um JOIN com `platforms` é suficiente para Phase 17.
   - Recommendation: Adicionar apenas em `platforms` por ora. O planner decide se INFRA-03 também adiciona em `products`. Se Phase 17 precisar, uma migration separada pode ser criada lá.

2. **Quais são as 16 plataformas e seus IDs canônicos?**
   - What we know: v1.0 tem 3 (Hotmart=1, ClickBank=2, Kiwify=3). v2.0 adiciona: Eduzz, Monetizze, PerfectPay, Braip (BR), Product Hunt, Udemy (INTL API-based), JVZoo, Gumroad, AppSumo (INTL high-friction).
   - That's 12 plataformas confirmadas. "16" mencionado no success criterion pode incluir plataformas reservadas ou contar diferente.
   - Recommendation: Contar: 3 (v1.0) + 4 (BR) + 2 (INTL API) + 3 (INTL high-friction) = 12. O número "16" no success criterion provavelmente é aspiracional ou inclui plataformas de teste. O planner deve clarificar — se são exatamente 12 plataformas v2.0, inserir 12 rows é correto.

3. **Scanners v1.0 devem ser atualizados para importar de `platform_ids.py`?**
   - What we know: `hotmart.py`, `clickbank.py`, `kiwify.py` têm constantes locais. INFRA-02 requer que scanners NOVOS possam importar da fonte central — não exige retroativamente refatorar os scanners v1.0.
   - Recommendation: Não refatorar v1.0 scanners nesta fase. O módulo `platform_ids.py` deve exportar as mesmas constantes numéricas que os scanners existentes já usam — zero breaking change.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.4.2 + pytest-asyncio 0.24.0 |
| Config file | `mis/pytest.ini` |
| Quick run command | `cd mis && python -m pytest tests/ -x -q --timeout=10` |
| Full suite command | `cd mis && python -m pytest tests/ -v --timeout=30` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INFRA-01 | `run_migration_006()` cria 16 platforms sem FK violation | unit | `cd mis && python -m pytest tests/test_migration_006.py -x -q` | ❌ Wave 0 |
| INFRA-01 | Migration idempotente (execução dupla sem erro) | unit | `cd mis && python -m pytest tests/test_migration_006.py::test_migration_idempotent -x` | ❌ Wave 0 |
| INFRA-01 | `python -m mis dashboard` inicia sem FK violation | smoke | `cd mis && python -c "from mis.db import run_migrations; run_migrations(':memory:')"` | N/A (inline) |
| INFRA-02 | `from mis.platform_ids import EDUZZ_PLATFORM_ID` não levanta ImportError | unit | `cd mis && python -m pytest tests/test_platform_ids.py -x -q` | ❌ Wave 0 |
| INFRA-02 | Constantes em `platform_ids.py` correspondem aos IDs na DB | unit | `cd mis && python -m pytest tests/test_platform_ids.py::test_ids_match_db -x` | ❌ Wave 0 |
| INFRA-03 | `platforms.rank_type` preenchido para todas as plataformas após migration | unit | `cd mis && python -m pytest tests/test_migration_006.py::test_rank_type_populated -x` | ❌ Wave 0 |
| DEBT-01 | `grep -r "nyquist_compliant: false"` retorna zero nos VALIDATION.md | smoke | `grep -r "nyquist_compliant: false" .planning/phases/ --include="*.md" \| wc -l` (expect 0) | N/A (grep) |
| DEBT-02 | Docstring linha 141 de `radar/__init__.py` contém "6 jobs" | unit | `cd mis && python -m pytest tests/test_radar_docstring.py -x -q` (ou inline grep) | ❌ Wave 0 (opcional) |

### Sampling Rate

- **Per task commit:** `cd mis && python -m pytest tests/ -x -q --timeout=10`
- **Per wave merge:** `cd mis && python -m pytest tests/ -v --timeout=30`
- **Phase gate:** Full suite green + `grep -r "nyquist_compliant: false" .planning/phases/ --include="*.md"` retorna zero

### Wave 0 Gaps

- [ ] `mis/tests/test_migration_006.py` — testes para INFRA-01 e INFRA-03 (all platforms inserted, idempotent, rank_type populated)
- [ ] `mis/tests/test_platform_ids.py` — testes para INFRA-02 (import works, IDs match DB, all 12+ constants present)
- [ ] `mis/platform_ids.py` — o módulo em si (criado na Wave 1, referenciado nos testes Wave 0)

DEBT-01 e DEBT-02 não requerem arquivos de teste novos — verificados por grep ou inspeção direta.

---

## Sources

### Primary (HIGH confidence)

- `mis/migrations/_001_initial.py` — schema das tabelas `platforms` e `products`, confirma ausência de rows pré-inseridos
- `mis/migrations/_005_alerts.py` — padrão `IF NOT EXISTS` + `add_column()` idempotente
- `mis/db.py` — sequência de migrations existente (001-005), local de inserção de `_run_006`
- `mis/scanners/hotmart.py`, `clickbank.py`, `kiwify.py` — confirmação de que IDs são hardcoded localmente
- `mis/radar/__init__.py:141` — confirma docstring "5 Pain Radar jobs" (DEBT-02)
- `.planning/phases/*/VALIDATION.md` (12 arquivos) — confirma `nyquist_compliant: false` em todos
- `.planning/milestones/v1.0-MILESTONE-AUDIT.md` — lista oficial do tech debt identificado

### Secondary (MEDIUM confidence)

- `.planning/REQUIREMENTS.md` — definição autoritativa dos 5 requisitos de Phase 13
- `.planning/ROADMAP.md` — success criteria verbatim para Phase 13
- `.planning/STATE.md` — decisions log confirmando necessidade de `platform_ids.py` e `rank_type`

### Tertiary (LOW confidence)

- Estimativa "16 plataformas" — ROADMAP menciona 16 mas contagem confirmada é 12 (3 v1.0 + 9 v2.0). Pode haver 4 plataformas adicionais não documentadas.

---

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — todo o stack é o stack existente do projeto, nenhuma biblioteca nova
- Architecture: HIGH — todos os patterns são do codebase existente (migrations 001-005 como templates)
- Pitfalls: HIGH — identificados por inspeção direta do código e dos success criteria

**Research date:** 2026-03-16
**Valid until:** 2026-06-16 (stack estável — SQLite, sqlite_utils, pytest não mudam APIs frequentemente)
