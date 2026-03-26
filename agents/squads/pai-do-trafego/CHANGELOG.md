# CHANGELOG — Pai do Tráfego Squad

## [1.0.0] — 2026-03-19

### Added
- `config.yaml` — Configuração completa do squad (hybrid, incremental, 5 quality gates)
- `agents/pdt-chief.md` — Orchestrator com routing lógico e enforcement de gates
- `agents/market-auditor.md` — Tier 0: avatar, awareness (Schwartz), ângulos, benchmark
- `agents/dr-master.md` — Tier 1: USP, mecanismo único, HSO/PAS/DIC/BAB (Brunson, Halbert, Kennedy)
- `agents/offer-architect.md` — Tier 2: framing, value stack (Hormozi), matriz de ângulos por formato
- `agents/hook-writer.md` — Tier 3: banco de hooks UGC/DTC, 6 tipos, quality filters (Savannah Sanchez)
- `agents/static-creative.md` — Tier 3: copy Meta estático + carrossel + briefing visual (Bencivenga, Ogilvy)
- `agents/tiktok-creative.md` — Tier 3: roteiros com timestamp, diretrizes nativas TikTok (Tom Breeze)
- `agents/lp-funnel.md` — Tier 3: squeeze pages, pré-lançamento, ad scent (Brunson, Jeff Walker)
- `agents/creative-critic.md` — Tool: review em 6 dimensões, compliance Meta/TikTok, P0/P1/P2
- `agents/metrics-optimizer.md` — Tool: diagnóstico por funil, hipóteses de iteração (Cody Plofker)
- `README.md` — Documentação completa do squad

### Architecture
- Tipo: Hybrid (Expert agents + Pipeline workflow)
- Modo: Incremental (checkpoint após cada agente)
- 5 Quality Gates (PDT-QG-001 a 005)
- Loop de iteração: metrics-optimizer → Tier 3 → creative-critic
