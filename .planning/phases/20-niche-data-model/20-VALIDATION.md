---
phase: 20
phase-slug: niche-data-model
date: 2026-03-17
nyquist_compliant: false
---

# Validation Strategy: Phase 20 — Niche Data Model

## What This Phase Must Prove

1. Banco contém 4 nichos e ~40 subnichos acessíveis via query
2. Cada subnicho retorna slug específico por plataforma
3. Migration aplicável em banco existente sem destruir dados v1.0/v2.0

## Test Approach

- Unit tests com SQLite em memória (tmp_path fixture)
- Seed data verificado via queries diretas
- Migration aplicada sobre DB com dados v1/v2 pré-existentes

## Validation Architecture

### Automated
- `test_migration_008_creates_tables` — verifica tabelas niches_v3, subniches, subniche_platform_slugs
- `test_seed_4_niches` — confirma 4 nichos no banco
- `test_seed_subniches_count` — confirma ~40 subnichos por nicho
- `test_slug_lookup_by_platform` — query por platform_id retorna slug correto
- `test_migration_idempotent` — rodar migration 2x não duplica dados
- `test_existing_data_preserved` — produtos/pains v1/v2 intactos após migration

### Manual
- Nenhum item requer verificação manual nesta fase
