# Mobile Checklist

**ID:** DP-CL-002
**Versao:** 1.0
**Aplicacao:** Validacao de responsividade e performance mobile
**Score minimo:** 70/100

---

## SECAO 1: TIPOGRAFIA MOBILE (20 pontos)

| # | Item | PASS | FAIL | Pts |
|---|------|------|------|-----|
| 1.1 | Corpo de texto >= 16px no mobile | | | /4 |
| 1.2 | Headline principal >= 28px no mobile | | | /4 |
| 1.3 | Line-height do body >= 1.5 | | | /4 |
| 1.4 | Contraste de texto vs fundo >= 4.5:1 (WCAG AA) | | | /4 |
| 1.5 | Nenhum texto em italico longo (dificulta leitura mobile) | | | /4 |

**Score Secao 1: ___ / 20**

---

## SECAO 2: LAYOUT E GRID (25 pontos)

| # | Item | PASS | FAIL | Pts |
|---|------|------|------|-----|
| 2.1 | Sem scroll horizontal em 375px de largura | | | /5 |
| 2.2 | Padding lateral >= 16px em todas as secoes | | | /5 |
| 2.3 | Grade multi-coluna colapsa para coluna unica no mobile | | | /5 |
| 2.4 | Nenhum elemento com largura fixa > 375px | | | /5 |
| 2.5 | Secoes empilhadas verticalmente sem sobreposicao | | | /5 |

**Score Secao 2: ___ / 25**

---

## SECAO 3: INTERACAO E TOQUE (25 pontos)

| # | Item | PASS | FAIL | Pts |
|---|------|------|------|-----|
| 3.1 | Botoes de CTA com altura >= 48px | | | /5 |
| 3.2 | Area tocavel de links e botoes >= 44x44px | | | /5 |
| 3.3 | Espaco de 8px+ entre elementos tocaveis adjacentes | | | /5 |
| 3.4 | Campos de formulario com altura >= 48px | | | /5 |
| 3.5 | Teclado correto ativado por tipo (email para campo email) | | | /5 |

**Score Secao 3: ___ / 25**

---

## SECAO 4: PERFORMANCE (30 pontos)

| # | Item | PASS | PARCIAL | FAIL | Pts |
|---|------|------|---------|------|-----|
| 4.1 | LCP estimado < 2.5s em 4G (ou < 3s com conexao media) | | | | /6 |
| 4.2 | Imagens hero com dimensoes definidas (evita CLS) | | | | /6 |
| 4.3 | Imagens below-the-fold com lazy loading | | | | /6 |
| 4.4 | Video sem autoplay com som (iOS bloqueia) | | | | /6 |
| 4.5 | Sem layout shift visivel durante carregamento | | | | /6 |

**Score Secao 4: ___ / 30**

---

## SCORE FINAL

| Secao | Score | Maximo |
|-------|-------|--------|
| 1. Tipografia | ___ | 20 |
| 2. Layout | ___ | 25 |
| 3. Interacao | ___ | 25 |
| 4. Performance | ___ | 30 |
| **TOTAL** | **___** | **100** |

---

## Itens Criticos (Blocking)

| # | Item |
|---|------|
| C1 | Pagina legivel sem zoom em 375px |
| C2 | CTA tocavel sem erro em iPhone/Android |
| C3 | Sem scroll horizontal |
| C4 | Video nao quebra no iOS Safari |

---

_Checklist Version: 1.0_
