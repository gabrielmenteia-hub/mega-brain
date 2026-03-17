# Phase 14: BR Scanners - Context

**Gathered:** 2026-03-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Quatro plataformas brasileiras de infoprodutos (Eduzz, Monetizze, PerfectPay, Braip) produzindo dados reais de ranking no sistema — usando o padrão SSR estabelecido pelo v1.0. Cada scanner varre o marketplace público da plataforma por nicho e persiste os produtos rankeados via upsert. Dashboard e cross-platform ranking pertencem à Phase 17.

</domain>

<decisions>
## Implementation Decisions

### Fallback quando sem marketplace

- Se a URL de marketplace não existir, retornar 404, ou bloquear: **retornar lista vazia sem lançar exceção**
- Comportamento: `scan_niche()` retorna `[]` + structlog emite `alert='marketplace_unavailable'` (análogo ao `alert='schema_drift'`)
- Job APScheduler não falha — continua rodando nos próximos ciclos
- Dados antigos são **preservados** no DB mas marcados com `is_stale=True`
- Quando scan bem-sucedido restaura produtos: `is_stale` resetado para `False` automaticamente no upsert

### Coluna is_stale

- Nova coluna `is_stale` (boolean, default `False`) na tabela `products`
- Adicionada via **migration `_007_is_stale.py`** (nova migration, não altera _006)
- Upsert seta `is_stale=False` quando produtos chegam (reset automático)
- Scanner seta `is_stale=True` em todos os produtos da plataforma+nicho quando retorna lista vazia

### Splitting dos planos

- **14-01**: `EduzzScanner` + `MonetizzeScanner` + migration `_007_is_stale`
- **14-02**: `PerfectPayScanner` + `BraipScanner`
- Eduzz e Monetizze entram primeiro (maiores/mais conhecidas, menor incerteza)
- PerfectPay e Braip no segundo plano (URL live a confirmar pelo researcher)

### Cobertura de testes

- **6 testes por scraper** (5 padrão da Phase 02 + 1 novo):
  1. Happy path: retorna lista de produtos com campos obrigatórios
  2. Campos tipados: `price` float, `rank` int, `external_id` não-None
  3. Fallback selector usado quando primary falha
  4. `alert='schema_drift'` emitido quando todos os selectors falham
  5. Upsert DB: inserir + re-run atualiza rank sem duplicar
  6. **is_stale**: upsert com lista vazia → `is_stale=True`; upsert com produtos → `is_stale=False`
- Teste de is_stale dentro de cada `test_X_scanner.py` (não arquivo separado)
- **Fixtures HTML capturados ao vivo** pelo researcher durante implementação, commitados em `mis/tests/fixtures/eduzz/`, `monetizze/`, `perfectpay/`, `braip/`
- Se PerfectPay ou Braip não tiverem marketplace público: testar **só o fallback** (retorno vazio + `is_stale=True`)
- **test_migration_007.py** para a nova migration (padrão do test_migration_006.py)

### Slugs de categoria no config.yaml

- Researcher descobre slugs de cada plataforma via inspeção live dos marketplaces
- Config.yaml: opt-in por nicho (usuário adiciona bloco `eduzz:`, `monetizze:`, etc. — mesmo padrão hotmart/kiwify)
- Se uma plataforma não tiver categoria mapeada para um nicho: **skip com structlog warning** (não falha o job)
- Backward compatible: nichos sem bloco da nova plataforma são simplesmente ignorados

### Claude's Discretion

- Estratégia de scraping (SSR vs SPA) por plataforma — researcher confirma via inspeção live
- `external_id` convention por plataforma (slug de URL, ID numérico, etc.) — researcher decide o campo mais estável
- Horário default do job (dentro da madrugada)
- Implementação interna do reset de is_stale (update em batch vs por produto)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets

- `PlatformScanner` (mis/scanner.py): ABC com `scan_niche()` abstrato — subclasses diretas para cada nova plataforma
- `BaseScraper`: `fetch()` (httpx+tenacity) + `fetch_spa()` (Playwright+stealth) — disponível via `self._base`
- Platform IDs já registrados em `mis/migrations/_006_v2_platforms.py`: Eduzz=4, Monetizze=5, PerfectPay=6, Braip=7
- `mis/platform_ids.py`: constantes de ID por plataforma — adicionar `EDUZZ_PLATFORM_ID = 4` etc.
- `conftest.py`: fixture `tmp_path` com DB real — reutilizar nos 6 testes de cada scanner
- `DOMAIN_DELAYS` em BaseScraper: adicionar entradas para `eduzz.com`, `monetizze.com.br`, `perfectpay.com.br`, `braip.com`
- `run_all_scanners()` em `mis/scanner.py`: já usa `asyncio.gather(return_exceptions=True)` — basta registrar os novos scanners

### Established Patterns

- Fallback selectors em lista ordenada (primary → fallback 1 → fallback 2) — replicar para cada nova plataforma
- `alert='schema_drift'` via structlog quando todos os selectors falham — reutilizar; adicionar `alert='marketplace_unavailable'` para 404/bloqueio
- Testes com fixtures HTML reais em `mis/tests/fixtures/{platform}/` + respx mocking
- `INSERT OR IGNORE` + `url_hash` / `external_id` para upsert idempotente
- Migration pattern: `_00N_name.py` com função `run_migration_00N(db_path)` + `db.conn.commit()` no final

### Integration Points

- `mis/db.py`: adicionar import e chamada de `run_migration_007` (padrão do _006)
- `mis/scanners/__init__.py`: registrar os 4 novos scanners
- `mis/scheduler.py`: `register_scanner_jobs()` já configura jobs por plataforma — basta as classes existirem no registry
- `mis/config.yaml`: adicionar slugs de categoria por nicho para cada nova plataforma após pesquisa live
- `mis/tests/fixtures/`: criar subpastas `eduzz/`, `monetizze/`, `perfectpay/`, `braip/`

</code_context>

<specifics>
## Specific Ideas

- PerfectPay e Braip: researcher deve verificar se têm marketplace público navegável antes de implementar. Se não tiver, o scanner implementa somente o fallback (retorno vazio + is_stale).
- is_stale deve ser resetado automaticamente no upsert — zero atrito operacional.
- 6 testes por scanner (não 5) — is_stale é comportamento novo que merece cobertura explícita.

</specifics>

<deferred>
## Deferred Ideas

- Nenhum — discussão ficou dentro do escopo da Phase 14.

</deferred>

---

*Phase: 14-br-scanners*
*Context gathered: 2026-03-16*
