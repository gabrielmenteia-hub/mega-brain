# DS — Design Systems Benchmarks

Coleção de **39 design systems open-source web-first** de referência mundial + comunitários dominantes, usados como benchmark para estudo de **arquitetura DS, design tokens, primitives, componentes web e documentação**: Big Tech, Governamentais, Enterprise/SaaS, Asia, Auto e Headless/Community.

Não contém código próprio — todos são clones shallow (`--depth 1`) para análise. Total: **~5.5 GB** (vs ~70 GB com histórico full).

**Escopo:** DS para **web** (HTML/CSS/JS/React/Vue/Web Components) — referência de **empresas grandes** OU **comunidades dominantes** OU **bases massivas** (shadcn-ui, radix, mantine). Não inclui DS native (iOS/Android/macOS) ou docs-only sem library de componentes. Exceção: `geist-font` (typeface) mantido por relevância para o ecossistema Vercel/Geist.

## Projetos

| # | Projeto | Empresa | Tags | Stack | Diferencial |
|---|---------|---------|------|-------|-------------|
| 1 | [material-ui](./material-ui) | Google (impl. MUI) | `react` `material-design` `most-popular` | TS/React | 98k stars; implementação canônica de Material Design |
| 2 | [carbon](./carbon) | IBM | `enterprise` `monorepo` `multi-framework` | React + Web Components + SCSS | Monorepo modular: `@carbon/{react,web-components,styles,colors,themes,grid,icons}` |
| 3 | [fluentui](./fluentui) | Microsoft | `react` `web-components` `microsoft-365` | TS + React (v8/v9) + WC | Usado em todo Microsoft 365 e Office; v9 é stable, v8 mature |
| 4 | [primer-react](./primer-react) | GitHub | `react` `primer` `github-ui` | TS/React | DS do próprio GitHub; 270+ packages no monorepo |
| 5 | [primer-css](./primer-css) | GitHub | `css` `scss` `ktlo` | SCSS | Implementação CSS do Primer (KTLO mode) |
| 6 | [primer-primitives](./primer-primitives) | GitHub | `tokens` `style-dictionary` `dtcg-ish` | TS + JSON | Color/typography/spacing primitives via Style Dictionary |
| 7 | [polaris-react](./polaris-react) | Shopify | `react` `e-commerce` `deprecated` | TS/React | Shopify admin DS (deprecated 2025-10 em favor de Polaris Web Components) |
| 8 | [polaris-tokens](./polaris-tokens) | Shopify | `tokens` `multi-platform` | npm + RubyGems | **Modelo canônico** de tokens-as-package: JS/JSON/CSS/SCSS/Android/iOS/Sketch/Adobe Swatch |
| 9 | [lightning-design-system](./lightning-design-system) | Salesforce | `enterprise` `pioneer` `tokens-origin` | JS/SCSS/MDX | Pioneiro do conceito "design tokens" (cunhado aqui em 2014) |
| 10 | [gestalt](./gestalt) | Pinterest | `react` `accessibility-first` | React (TS) | DS de produtos Pinterest; foco forte em a11y |
| 11 | [uber-baseweb](./uber-baseweb) | Uber | `react` `styletron` `themable` | TS + Styletron | Base design language em React; ladle playground |
| 12 | [react-spectrum](./react-spectrum) | Adobe | `react` `adaptive` `accessibility` | React + Hooks | React Aria + React Stately monorepo (Adobe) |
| 13 | [spectrum-css](./spectrum-css) | Adobe | `css` `framework-agnostic` | CSS-only | CSS-only Spectrum; importado pelo Spectrum Web Components |
| 14 | [spectrum-web-components](./spectrum-web-components) | Adobe | `web-components` `lit` | TS + Lit | Adobe Web Components implementation |
| 15 | [spectrum-design-data](./spectrum-design-data) | Adobe | `tokens` `mcp-server` `json-schema` | TS + JS + Rust | **Único DS com MCP server** (`@adobe/spectrum-design-data-mcp`) |
| 16 | [ant-design](./ant-design) | Alibaba (Ant Group) | `react` `china` `enterprise` | React (TS) | ~93k stars; dominante na Ásia; vasta lib enterprise |
| 17 | [tdesign](./tdesign) | Tencent | `multi-framework` `multi-platform` | Vue/React/WeChat/Flutter | Hub principal multi-platform da Tencent |
| 18 | [tdesign-react](./tdesign-react) | Tencent | `react` `china` | TS/React | TDesign React 16+ desktop |
| 19 | [tdesign-vue-next](./tdesign-vue-next) | Tencent | `vue3` `china` | Vue 3 | TDesign Vue 3 desktop |
| 20 | [govuk-design-system](./govuk-design-system) | UK Government | `gov` `accessibility` `nunjucks` | Nunjucks + SCSS | Site DS do GOV.UK; consome `govuk-frontend` |
| 21 | [govuk-frontend](./govuk-frontend) | UK Government | `gov` `frontend-package` | Nunjucks + SCSS + JS | Componentes/styles consumidos pelo govuk-design-system |
| 22 | [uswds](./uswds) | US Government | `gov` `usa` `bootstrap-style` | CSS/JS | US Web Design System (Federal government) |
| 23 | [pajamas](./pajamas) | GitLab | `vue` `gitlab-ui` `dtcg-tokens` | Vue + GitLab UI | DS oficial do GitLab; clonado de **GitLab.com** (não GitHub) |
| 24 | [boosted](./boosted) | Orange (FR) | `bootstrap-fork` `accessibility` `branded` | SCSS + JS | Bootstrap fork acessível com branding Orange |
| 25 | [canvas-kit](./canvas-kit) | Workday | `react` `enterprise` `compound-components` | TS/React | DS Workday; pattern de Compound Components |
| 26 | [paste](./paste) | Twilio | `react` `tokens` `themes` | TS + React + Figma | Foundations + primitives + themes architecture limpa |
| 27 | [clay](./clay) | Liferay | `web-components` `lexicon` `monorepo` | SCSS + React | Clay UI implementação do Lexicon Experience Language |
| 28 | [porsche-design-system](./porsche-design-system) | Porsche | `auto` `web-components` `wcag-2.2-aa` | TS + Web Components | Auto/luxury; WCAG 2.2 AA strict; Tailwind CSS |
| 29 | [geist-font](./geist-font) | Vercel | `font` `variable-font` `dev-tools` | HTML + Python build | Geist Sans/Mono/Pixel — typeface family **oficial** Vercel |
| 30 | [geist-ui](./geist-ui) | geist-org (community) | `react` `vercel-style` `community-port` `last-push-2024` | TS/React | React port comunitário do design Vercel (4.5k stars). **NÃO oficial**, parado em 2024-07. Mantido como **referência visual/arquitetural** do estilo Geist |
| 31 | [shadcn-ui](./shadcn-ui) | shadcn (Vercel) | `react` `tailwind` `radix-based` `dominant-2024-2026` | TS/React + Tailwind | **80k+ stars**. Convenção "copy-paste components" usada pelo sinkra-hub e milhares de projetos. Não é DS tradicional, é **convenção** |
| 32 | [radix-ui](./radix-ui) | WorkOS (Radix) | `react` `headless` `primitives` `unstyled` | TS/React | **Headless primitives canônicos** — base do shadcn-ui, Linear, Vercel. 16k stars |
| 33 | [headless-ui](./headless-ui) | Tailwind Labs | `react` `vue` `headless` `tailwind-official` | TS/React + Vue | Headless oficial Tailwind. 27k stars. React + Vue support |
| 34 | [mantine](./mantine) | Comunidade (mantinedev) | `react` `ui-kit` `polished` `enterprise-ready` | TS/React | DS comunitário **mais polido** 2025-2026. 28k stars. 100+ componentes prod-ready |
| 35 | [chakra-ui](./chakra-ui) | Comunidade (chakra-ui) | `react` `accessibility-first` `theme-system` | TS/React | DS comunitário **a11y-first**. 39k stars. Fundação Park UI / Ark UI / Saas-UI |
| 36 | [heroui](./heroui) | Comunidade (heroui-inc) | `react` `tailwind` `vercel-style` `nextui-rebrand` | TS/React + Tailwind | NextUI rebranded como HeroUI. 25k stars. **Vercel-style ATIVO** (substitui geist-ui parado) |
| 37 | [material-web](./material-web) | Google (oficial) | `web-components` `material-3` `google-official` | Lit + TS | **Material 3 OFICIAL Google** — Web Components implementation. Diferente do material-ui (3rd party) |
| 38 | [cloudscape](./cloudscape) | AWS | `react` `aws-console` `enterprise-cloud` | TS/React | DS oficial **AWS Console**. 3.6k stars. Referência cloud enterprise dense-information |
| 39 | [patternfly](./patternfly) | Red Hat | `multi-framework` `enterprise` `redhat` | React + Web Components + CSS | DS open-source oficial Red Hat. Multi-framework, OpenShift base |

## Categorias

### Por origem

- **Big Tech (FAANG-level):** material-ui (Google impl), material-web (Google oficial), fluentui (Microsoft), primer-* (GitHub), polaris-* (Shopify), spectrum-* + react-spectrum (Adobe), gestalt (Pinterest), uber-baseweb (Uber), cloudscape (AWS)
- **Enterprise B2B:** carbon (IBM), lightning-design-system (Salesforce), canvas-kit (Workday), paste (Twilio), clay (Liferay), pajamas (GitLab), patternfly (Red Hat)
- **China/Asia:** ant-design (Alibaba), tdesign* (Tencent)
- **Governamentais:** govuk-* (UK), uswds (US), boosted (Orange/France)
- **Auto/Luxury:** porsche-design-system
- **Type/Brand:** geist-font (Vercel oficial), geist-ui (community port)
- **Comunidade dominante:** shadcn-ui, mantine, chakra-ui, heroui
- **Headless/Primitives:** radix-ui (WorkOS), headless-ui (Tailwind Labs)

### Por tech stack

- **React-first:** material-ui, primer-react, polaris-react, react-spectrum, fluentui, gestalt, uber-baseweb, ant-design, tdesign-react, canvas-kit, paste, geist-ui, shadcn-ui, mantine, chakra-ui, heroui, cloudscape
- **Headless / Unstyled:** radix-ui, headless-ui, react-spectrum (via react-aria)
- **Web Components:** carbon (parcial), spectrum-web-components, fluentui (parcial), porsche-design-system, clay, material-web, patternfly (parcial), nordhealth (não incluído)
- **Multi-framework:** carbon, tdesign, fluentui (v9 + v8 + WC), patternfly (React + WC + CSS), headless-ui (React + Vue)
- **CSS-only:** spectrum-css, primer-css, boosted (Bootstrap fork)
- **Vue:** tdesign-vue-next, pajamas
- **Nunjucks/Server:** govuk-design-system, govuk-frontend

### Por padrão arquitetural

- **Tokens-as-package:** polaris-tokens (10 platforms), primer-primitives, spectrum-design-data, carbon (`@carbon/themes`+`@carbon/colors`)
- **Primitives token-backed:** gestalt, paste
- **Compound Components:** canvas-kit (Workday)
- **MCP integration:** spectrum-design-data (único — referência para AI consumption)
- **Style Dictionary pipeline:** primer-primitives, polaris-tokens, spectrum-design-data
- **DTCG-aligned tokens.json:** polaris-tokens (parcial), spectrum-design-data, primer-primitives, pajamas

### Por tier de fama

- **Tier S (referência mundial absoluta):** material-ui, material-web, carbon, fluentui, ant-design, polaris-*, lightning-design-system, primer-*, govuk-*, shadcn-ui, radix-ui, mantine, chakra-ui
- **Tier A (muito famoso):** spectrum-* + react-spectrum, gestalt, uber-baseweb, tdesign*, pajamas, headless-ui, heroui, cloudscape, patternfly
- **Tier B (importante mas nicho):** canvas-kit, paste, clay, boosted, porsche-design-system, uswds

### Por densidade visual (perfil de uso)

- **Brand-driven / marketing-friendly:** porsche-design-system, paste, polaris-*, gestalt, geist-ui, heroui, shadcn-ui (theme-driven)
- **Neutral / dense (B2B / power-user):** material-ui, carbon, fluentui, lightning-design-system, ant-design, canvas-kit, pajamas, cloudscape, patternfly
- **Government-conservative:** govuk-*, uswds, boosted

## Famosos NÃO incluídos (e por quê)

| DS | Empresa | Por quê |
|----|---------|---------|
| Atlassian Atlaskit | Atlassian | Web-focado mas vive em Bitbucket; visualmente muito denso (B2B power-user) — referência arquitetural ok, visual não |
| Encore | Spotify | Privado/interno — apenas blog posts |
| Hawkins | Netflix | Privado/interno — apenas Netflix Tech Blog |
| DLS | Airbnb | Privado/interno (pioneiro do termo "design language system") |
| HIG | Apple | Apenas guidelines, sem source code público |
| SAP Fiori | SAP | Apenas portal de design, sem source code dedicado |
| Mailchimp Patterns | Mailchimp | Apenas docs em ux.mailchimp.com |
| Heroku Heroki | Salesforce | Interno |
| Stripe (interno) | Stripe | Interno; Stripe Elements é UI-kit pagamento, não DS geral |
| Audi UI | Audi | Archived 2024 — referência morta |
| BBC GEL | BBC | Documentação Nunjucks/HTML, não library web moderna |
| Apple Fluent UI Apple | Microsoft | Native Swift (UIKit/AppKit) — fora do escopo web |
| Vercel Geist (DS oficial completo) | Vercel | Cores, componentes, layout em [vercel.com/geist](https://vercel.com/geist) **sem repo público oficial**. `geist-font` (typeface oficial) e `geist-ui` (community port) estão incluídos como referência |

## Referência derivada

Este catálogo foi montado a partir da pesquisa documentada em:
- `sinkra-hub/docs/research/2026-04-27-design-systems-empresas-grandes-github/`

## Manutenção

```bash
./update.sh
```

Lê `repos.tsv`, **clona shallow** (`--depth 1 --single-branch --filter=blob:none`) o que falta e dá `pull --ff-only --depth 1` no que já existe. Tudo em paralelo.

Legenda: `[+]` clonado · `[↑]` atualizado · `[=]` up-to-date · `[x]` erro

### Por que shallow?

Estes repos servem para **leitura/estudo de arquitetura, tokens, componentes web** — não para contribuição. Histórico git completo é dispensável e multiplica espaço por 50-100x em monorepos pesados. Ganho: **45GB → ~3.5GB**.

Se precisar do histórico de algum repo:
```bash
git -C carbon fetch --unshallow
```

### Suporta hosts além de GitHub

`update.sh` aceita qualquer URL git. Por isso `pajamas` (GitLab.com) está no manifest — não é GitHub-only.

## Notas

- **39 repos** clonados, web-focado
- **Tamanho estimado:** ~5.5 GB
- **Atualização recomendada:** mensal
- **Convenção de nomes:** kebab-case sem org prefix
- Para o catálogo "irmão" de AI agents, ver `../OS/`

### Atlassian Atlaskit — nota

Excluído deliberadamente. Visualmente otimizado para B2B power-user denso (Jira/Confluence) — interface neutra e cinza, **subordinada ao conteúdo**, não pra brand. Bom como **referência arquitetural** (`@atlaskit/primitives`, design tokens) — não como **referência visual**. Se um dia quiser, está em `bitbucket.org/atlassian/atlassian-frontend-mirror`.
