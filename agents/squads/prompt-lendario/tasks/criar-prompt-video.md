# Task: Criar Prompt de Vídeo

```yaml
task_name: "Criar Prompt para IA de Geração de Vídeo"
status: pending
responsible_executor: prompt-chief
execution_type: Hybrid
estimated_time: "10-20min"
input:
  - descrição da cena ou conceito
  - plataforma alvo (Kling, Sora, Runway, Pika, Luma)
  - duração desejada (3s, 5s, 10s...)
  - uso final (ad, reel, intro, b-roll...)
output:
  - prompt de vídeo otimizado para a plataforma
  - configurações técnicas recomendadas
  - 2 variações de câmera/movimento
acceptance_criteria:
  - Cena, câmera e movimento definidos
  - Duração especificada
  - Estilo visual e mood claros
  - Parâmetros específicos da plataforma incluídos
quality_gate: PL-QP-001
```

---

## Anatomia de um Prompt de Vídeo Lendário

```
[CENA]      → O que acontece / o que está em cena
[CÂMERA]    → Tipo de shot e ângulo
[MOVIMENTO] → Como a câmera ou sujeito se move
[DURAÇÃO]   → Tempo em segundos
[ESTILO]    → Estética visual, referências cinematográficas
[MOOD]      → Clima emocional e paleta
[TÉCNICA]   → Qualidade técnica e especificações
```

---

## Gramática por Plataforma

### KLING (v1.5 / v2.0)
**Strengths:** Movimentos realistas, personagens consistentes, física de fluidos
**Ideal para:** Produto, pessoa, natureza, slow motion

**Estrutura:**
```
[descrição de cena detalhada], [câmera], [movimento],
[estilo cinematográfico], [iluminação], [mood]
```

**Tokens de alto impacto:**
`slow motion` | `cinematic` | `smooth camera movement`
`dramatic lighting` | `photorealistic` | `high quality`
`dolly shot` | `tracking shot` | `aerial view`

---

### RUNWAY GEN-3 ALPHA
**Strengths:** Qualidade cinematográfica, controle de câmera, transições
**Ideal para:** Comerciais, shorts cinematográficos, fashion

**Estrutura com tags de câmera:**
```
[SCENE: descrição]
[CAMERA: tipo de shot]
[MOTION: movimento específico]
[LIGHTING: tipo de luz]
[MOOD: clima]
[STYLE: referência visual]
```

**Comandos de câmera:**
`static shot` | `slow push in` | `pull back` | `pan left/right`
`crane up` | `handheld` | `drone shot` | `orbit`

---

### PIKA (v1.5 / v2.0)
**Strengths:** Animação de imagens, consistência de personagem
**Ideal para:** Reels, transformações, product reveals

**Modificadores de movimento:**
`zoom in slowly` | `gentle sway` | `rotate 360`
`camera orbits around subject` | `subtle breathing motion`

---

### LUMA DREAM MACHINE
**Strengths:** Realismo físico, reflexos, materiais
**Ideal para:** Produtos, arquitetura, natureza

**Estrutura:** Frase narrativa com foco em física e materiais

---

### SORA (OpenAI)
**Strengths:** Cenas complexas, consistência temporal, câmera avançada
**Ideal para:** Narrativas, múltiplos personagens, ambientes complexos

**Estrutura:** Descrição cinematográfica detalhada em linguagem natural

---

## Workflow de Execução

### FASE 1 — Briefing

Se insuficiente, perguntar:

```
Para criar o prompt de vídeo perfeito:

1. O QUE: O que acontece no vídeo? (cena, personagem, ação)
2. PLATAFORMA: Kling, Runway, Pika, Luma ou Sora?
3. DURAÇÃO: 3s, 5s, 10s ou outro?
4. USO: Anúncio, reel, intro, b-roll, storytelling?
5. CÂMERA: Tem preferência de movimento? (drone, close, wide shot...)
6. ESTILO: Referência cinematográfica? (filme, marca, fotógrafo...)
```

---

### FASE 2 — Construção

**Template Universal:**
```
[Sujeito + ação detalhada], [ambiente/locação],
[câmera: tipo de shot + ângulo],
[movimento: como câmera/sujeito se move],
[iluminação: hora do dia, tipo, intensidade],
[estilo: referência cinematográfica],
[mood: clima emocional],
[qualidade: resolução, técnica],
duração: [X] segundos
```

**Para produto:**
```
[produto] on [superfície/ambiente], product reveal shot,
camera slowly orbits around product,
[iluminação de produto — soft box, rim light...],
luxury brand aesthetic, hyperrealistic, photographic quality,
smooth motion, 4K cinematic
```

**Para pessoa/personagem:**
```
[pessoa + descrição física + roupa], [ação/expressão],
[ambiente],
[câmera: close-up / medium shot / wide],
[movimento de câmera],
cinematic lighting, [mood], [referência de estilo]
```

---

### FASE 3 — Output Final

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROMPT PRINCIPAL ([plataforma]):
[prompt otimizado]

CONFIGURAÇÕES RECOMENDADAS:
- Duração: [X]s
- Modo: [Standard/Pro/Cinematic]
- Aspect ratio: [16:9 / 9:16 / 1:1]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Variação 1 — câmera diferente:**
`[prompt com movimento de câmera alternativo]`

**Variação 2 — mood diferente:**
`[prompt com estética visual alternativa]`

**Dica de iteração:**
[O que ajustar se movimento estiver errado / cena não saiu como esperado]
