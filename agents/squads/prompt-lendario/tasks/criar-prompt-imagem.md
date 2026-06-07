# Task: Criar Prompt de Imagem

```yaml
task_name: "Criar Prompt para IA de Geração de Imagem"
status: pending
responsible_executor: prompt-chief
execution_type: Hybrid
estimated_time: "10-15min"
input:
  - descrição do que precisa ser gerado
  - plataforma alvo (Midjourney, DALL-E, Flux, SD, Ideogram)
  - uso final (anúncio, capa, thumbnail, produto, editorial...)
  - referências visuais ou estilo desejado
output:
  - prompt otimizado para a plataforma escolhida
  - parâmetros técnicos incluídos
  - 3 variações sugeridas
acceptance_criteria:
  - Sujeito, estilo e composição definidos
  - Parâmetros técnicos da plataforma incluídos
  - Tokens de poder relevantes
  - Aspect ratio especificado
  - Pelo menos 2 variações entregues
quality_gate: PL-QP-001
```

---

## Gramática por Plataforma

### MIDJOURNEY v6.1
**Estrutura:** `[sujeito], [estilo], [iluminação], [composição], [mood], [técnica], [parâmetros]`

**Parâmetros essenciais:**
- `--ar 16:9` | `--ar 9:16` | `--ar 1:1` | `--ar 4:3` (aspect ratio)
- `--style raw` (menos opinionado, mais fotorrealista)
- `--q 2` (qualidade máxima)
- `--v 6.1` (versão atual)
- `--no [elemento]` (excluir elementos)
- `--chaos 0-100` (variação)
- `--weird 0-3000` (estilo não convencional)

**Tokens de alto impacto:**
`cinematic` | `photorealistic` | `editorial photography` | `hyperdetailed`
`dramatic lighting` | `golden hour` | `soft box lighting` | `rim lighting`
`bokeh` | `shallow depth of field` | `macro` | `wide angle`
`film grain` | `analog` | `color grading` | `muted tones`

---

### DALL-E 3
**Estrutura:** Frase natural e descritiva + estilo no final

**Diferenças:** DALL-E 3 entende linguagem natural melhor.
Escrever como descrição de cena, não lista de tokens.

**Tokens de alto impacto:**
`photographic style` | `illustration` | `oil painting` | `watercolor`
`wide angle shot` | `close-up` | `studio lighting` | `natural light`
`professional photography` | `cinematic lighting`

---

### FLUX (Schnell / Dev / Pro)
**Estrutura:** Similar ao Midjourney mas sem parâmetros `--`

**Tokens de alto impacto:**
`sharp focus` | `intricate details` | `8k resolution` | `ultra-detailed`
`professional photography` | `volumetric lighting` | `photorealistic`
`RAW photo` | `DSLR` | `HDR`

---

### STABLE DIFFUSION
**Estrutura:** `[positivo] --- [negativo]`

**Positive tokens:** mesmos do Flux + qualidade técnica
**Negative tokens:** `blurry, bad anatomy, deformed, ugly, low quality, watermark, text`

---

## Workflow de Execução

### FASE 1 — Briefing

Se insuficiente, perguntar:

```
Para criar o prompt perfeito de imagem:

1. O QUE: O que precisa aparecer na imagem? (sujeito principal)
2. PLATAFORMA: Midjourney, DALL-E 3, Flux ou outra?
3. USO: Onde a imagem vai? (anúncio, capa, post, produto...)
4. ESTILO: Fotorrealista, ilustração, editorial, 3D, arte...
5. ASPECT RATIO: 1:1 (quadrado), 16:9 (paisagem), 9:16 (vertical/stories)
6. REFERÊNCIA: Tem alguma imagem de referência ou estilo de fotógrafo?
```

---

### FASE 2 — Construção por Plataforma

**Para Midjourney:**

```
[sujeito detalhado], [ação ou pose se aplicável],
[estilo fotográfico ou artístico],
[iluminação — tipo, direção, intensidade],
[composição — ângulo, distância],
[ambiente ou fundo],
[mood ou paleta de cores],
[técnica ou textura],
[referência de fotógrafo ou artista se relevante]
--ar [ratio] --style raw --q 2 --v 6.1
```

**Para DALL-E 3:**

```
[Descrição narrativa da cena em 2-3 frases.
Inclua sujeito, ação, ambiente, iluminação e mood.
Mencione estilo artístico ao final.]
```

**Para Flux:**

```
[sujeito], [estilo], [iluminação], [composição],
[mood], [qualidade técnica], [detalhes específicos]
RAW photo, sharp focus, ultra-detailed, 8k resolution
```

---

### FASE 3 — Output Final

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROMPT PRINCIPAL:
[prompt otimizado]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Após o prompt principal:

**Variação 1 — [diferença principal]:**
`[prompt variação]`

**Variação 2 — [diferença principal]:**
`[prompt variação]`

**Variação 3 — [diferença principal]:**
`[prompt variação]`

**Dica de iteração:**
[O que ajustar se o resultado não for o esperado]
