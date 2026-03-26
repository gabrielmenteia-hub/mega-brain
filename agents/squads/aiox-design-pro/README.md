# Design Pro Squad

Squad especializado em **web design, landing pages e UI/UX para venda de infoprodutos**.

---

## Visao Geral

O Design Pro Squad combina especialistas em conversao, arquitetura de UX, design visual e copy persuasivo para criar landing pages e interfaces de alta performance para cursos online, ebooks, mentorias e outros produtos digitais.

**Tipo:** Expert Squad
**Modelo:** Opus (raciocinio criativo e estrategico)
**Versao:** 1.0.0

---

## Agentes

| Agente | Tier | Especialidade |
|--------|------|---------------|
| `design-pro-chief` | Orchestrator | Roteamento e coordenacao |
| `conversion-diagnostician` | 0 | Analise de brief, persona e metas de conversao |
| `ux-architect` | 1 | Estrutura de pagina, fluxo e arquitetura de informacao |
| `visual-designer` | 1 | Hierarquia visual, tipografia, cores e layout |
| `conversion-copywriter` | 1 | Headlines, CTAs e copy persuasivo |
| `infoproduct-specialist` | 3 | Padroes especificos de vendas de infoprodutos |
| `mobile-optimizer` | 3 | Responsividade e performance mobile |

---

## Ativacao

```
@design-pro-chief
```

### Comandos Principais

| Comando | Descricao |
|---------|-----------|
| `*create-landing` | Criar landing page completa do zero |
| `*sales-page` | Criar sales page para infoproduto |
| `*analyze` | Analisar brief/produto antes de criar |
| `*ui-review` | Auditar pagina existente |
| `*help` | Mostrar todos os comandos |

### Ativacao por Especialista

```
@design-pro:conversion-diagnostician   # Analise e diagnostico
@design-pro:ux-architect               # Estrutura e fluxo
@design-pro:visual-designer            # Design visual
@design-pro:conversion-copywriter      # Headlines e copy
@design-pro:infoproduct-specialist     # Sales page de infoproduto
@design-pro:mobile-optimizer           # Mobile e performance
```

---

## Workflows

| Workflow | Descricao |
|----------|-----------|
| `wf-create-landing-page.yaml` | Criacao completa de landing page (6 fases) |
| `wf-audit-existing-page.yaml` | Auditoria de pagina existente |

---

## Tasks

| Task | Executor | Descricao |
|------|----------|-----------|
| `create-landing-page.md` | Hybrid | Criacao guiada de landing page |
| `analyze-brief.md` | Agent | Analise de brief e persona |
| `create-sales-page.md` | Agent | Sales page completa para infoproduto |
| `audit-ux.md` | Hybrid | Auditoria de UX e conversao |

---

## Checklists

- `landing-page-checklist.md` — Validacao completa de landing page
- `conversion-checklist.md` — Checklist de conversao por secao
- `mobile-checklist.md` — Validacao mobile/responsividade

---

## Casos de Uso

1. **Curso Online** — Landing page para lancamento de curso com VSL, prova social e CTA
2. **Ebook/PDF** — Pagina de captura de lead com proposta de valor clara
3. **Mentoria** — Sales page premium com qualificacao de lead
4. **Workshop/Evento** — Pagina de inscricao com urgencia e escassez
5. **Membership** — Pagina de assinatura com comparacao de planos

---

## Instalacao

```bash
npm run install:squad design-pro
```

---

_Squad Version: 1.0.0 | Criado: 2026-03-07_
