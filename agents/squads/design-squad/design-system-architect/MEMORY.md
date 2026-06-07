# MEMORY: Design System Architect

> Atualizado: 2026-05-05 | Fonte: DS-main benchmark + dossiers

---

## Base de Conhecimento

### Dossiers de Referência
- `knowledge/dossiers/themes/DOSSIER-DESIGN-SYSTEMS-BENCHMARK.md` — catálogo completo dos 39 DS open-source (tiers, stacks, padrões arquiteturais)
- `knowledge/dossiers/themes/DOSSIER-DESIGN-SYSTEM-CLONING.md` — técnica de extração/replicação via AI e design.md

### Pessoas Relacionadas
- `agents/squads/design-squad/brad-frost/` — criador de Atomic Design
- `agents/squads/design-squad/dan-mall/` — DS leadership e org

---

## Referências Técnicas Rápidas

### Repos Tier S locais (após clone)
```
d:/MEGABRAIN/DS-main/DS-main/
├── material-ui/      # Google/MUI — 98k stars
├── material-web/     # Google oficial — Material 3 WC
├── carbon/           # IBM — monorepo multi-framework
├── fluentui/         # Microsoft — M365 + Office
├── primer-react/     # GitHub — 270+ packages
├── primer-primitives/# GitHub — tokens via Style Dictionary
├── polaris-react/    # Shopify — admin DS
├── polaris-tokens/   # Shopify — tokens-as-package canônico
├── lightning-design-system/ # Salesforce — pioneiro tokens (2014)
├── ant-design/       # Alibaba — 93k stars, Asia dominant
├── govuk-frontend/   # UK Gov — referência a11y
├── shadcn-ui/        # Vercel — 80k stars, copy-paste
├── radix-ui/         # WorkOS — headless primitives base
├── mantine/          # Community — 100+ componentes polidos
├── chakra-ui/        # Community — a11y-first 39k stars
├── headless-ui/      # Tailwind Labs — React + Vue
└── spectrum-design-data/ # Adobe — único com MCP server
```

### Decisões Rápidas
| Cenário | Recomendação |
|---------|-------------|
| B2B enterprise denso | carbon, cloudscape, patternfly |
| SaaS com brand visual | shadcn-ui + radix-ui + tema |
| Web Components puros | material-web, spectrum-web-components, porsche |
| Tokens multi-plataforma | polaris-tokens (modelo canônico) |
| Acessibilidade | govuk-frontend, porsche (WCAG 2.2 AA) |
| AI/MCP consumption | spectrum-design-data, técnica design.md |
| Headless primitives | radix-ui → shadcn, headless-ui (Tailwind) |

---

## Estado do Benchmark Local

- **Manifest:** `d:/MEGABRAIN/DS-main/DS-main/repos.tsv` — 39 repos
- **Clonados:** Tier S (17 repos) via `clone-tier-s.sh` — executar quando necessário
- **Atualização:** `bash d:/MEGABRAIN/DS-main/DS-main/update.sh`
