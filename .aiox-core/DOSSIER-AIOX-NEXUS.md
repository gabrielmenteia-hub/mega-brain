---
nome: NEXUS - AI-Powered Meta Ads Review Pipeline
versao: 1.0
fase: 01-Foundation (CONCLUÍDA)
data_criacao: 2026-03-19
data_atualizacao: 2026-04-10
status: ✅ PRONTO PARA FASE 2
---

# 📋 DOSSIER: NEXUS v1 - Review Rubrics Foundation

## 🎯 Visão Geral

**NEXUS** é um sistema inteligente de review para campanhas de Meta Ads que combina:
- **Rubrics estruturadas** com critérios objetivos
- **Agentes de IA** para avaliação automática
- **Thresholds configuráveis** para controle de qualidade
- **Testes rigorosos** com cobertura 100%

A **Fase 01 (Foundation)** estabeleceu a base: modelos tipados e 4 rubricas de review calibradas para evitar drift de scoring.

---

## 📊 ESTADO ATUAL

| Dimensão | Status | Detalhe |
|----------|--------|---------|
| **Fase 01** | ✅ COMPLETA | 2 planos executados, 0 desvios |
| **Testes** | ✅ 16/16 GREEN | Cobertura estrutural + threshold alignment |
| **Commits** | ✅ 6 atômicos | test RED → feat GREEN → docs |
| **Documentação** | ✅ COMPLETA | Plans, Summaries, Validation, Verification |
| **Próxima Fase** | 📅 PRONTA | Phase 2: Review Agents (bloqueio: ANTHROPIC_API_KEY) |

---

## 🏗️ ARQUITETURA

```
NEXUS v1 (4 fases, 7 planos)
│
├── Phase 01: Foundation (CONCLUÍDA ✅)
│   ├── 01-01: Modelos + Config
│   │   └── AgentScore, CreativeBundle, NexusConfig
│   │
│   └── 01-02: Review Rubrics (VOCÊ ESTÁ AQUI)
│       ├── COPY_RUBRIC (threshold=7)
│       ├── TECH_RUBRIC (threshold=6)
│       ├── COMPLIANCE_RUBRIC (threshold=8 — mais rigoroso)
│       └── PERFORMANCE_RUBRIC (threshold=6)
│
├── Phase 02: Review Agents (PRONTA — aguardando ANTHROPIC_API_KEY)
│   ├── 02-01: Agent Calibration (few-shot examples)
│   ├── 02-02: Scoring Pipeline (instructor + LLM)
│   └── 02-03: Quality Gates (thresholds + quarantine)
│
├── Phase 03: Web UI (PLANEJADA)
│   ├── 03-01: Dashboard + Submission
│   ├── 03-02: Review Queue + Real-time Feedback
│   └── 03-03: Reporting + Audit Trail
│
└── Phase 04: Advanced Features (PLANEJADA)
    ├── 04-01: Multi-language Support
    ├── 04-02: Custom Rubric Builder
    └── 04-03: Analytics + Benchmarking
```

---

## 📚 AS 4 RUBRICAS

### 1️⃣ COPY RUBRIC (Copywriting)

**Threshold:** 7/10 (aprovado se ≥ 7)

**Critérios** (peso total = 1.0):

| Critério | Peso | Descrição | Níveis (10/8/6/4/2) |
|----------|------|-----------|-------------------|
| **Hook** | 0.3 | Captura atenção nos primeiros 3s | Excelente → Ausente |
| **CTA** | 0.3 | Call-to-Action claro e urgente | Específico → Vago |
| **Length Fit** | 0.2 | Comprimento apropriado para o medium | Otimizado → Inviável |
| **Persuasion** | 0.2 | Técnicas de persuasão aplicadas | Múltiplas → Nenhuma |

**Few-Shot Example (Aprovado):**
```
Input: "Descubra como triplicar sua renda em 30 dias. 
        5 técnicas testadas que funcionam. Saiba mais ➜"
Expected Score: 8.2/10 (aprovado)
Reasoning: Hook forte + CTA urgente + comprimento ideal
```

**Few-Shot Example (Reprovado):**
```
Input: "Veja nosso produto aqui"
Expected Score: 4/10 (reprovado)
Reasoning: Hook fraco, CTA vago, sem persuasão
```

---

### 2️⃣ TECH RUBRIC (Qualidade Técnica)

**Threshold:** 6/10 (aprovado se ≥ 6)

**Critérios** (peso total = 1.0):

| Critério | Peso | Descrição | Níveis (10/8/6/4/2) |
|----------|------|-----------|-------------------|
| **Visual Quality** | 0.35 | Resolução, cores, composição | 4K HDR → Pixelado |
| **Audio Quality** | 0.35 | Clareza, volume, sem ruídos | Cristalino → Inaudível |
| **Sync** | 0.2 | Sincronização áudio-vídeo | Perfeita → Dessincronizado |
| **Format Compliance** | 0.1 | Respeita specs Meta (aspect ratio, etc) | Compliant → Inválido |

**Few-Shot Example (Aprovado):**
```
Input: Vídeo 1920x1080, 16:9, áudio limpo, sincronizado
Expected Score: 8.5/10 (aprovado)
Reasoning: Alta qualidade visual + áudio cristalino + formato correto
```

**Few-Shot Example (Reprovado):**
```
Input: Vídeo 640x480, áudio baixo, 5s out of sync
Expected Score: 4.5/10 (reprovado)
Reasoning: Qualidade técnica inadequada
```

---

### 3️⃣ COMPLIANCE RUBRIC (Conformidade Meta Ads)

**Threshold:** 8/10 (MAIS RIGOROSO — bans são irreversíveis)

**Critérios** (peso total = 1.0):

| Critério | Peso | Descrição | Níveis (10/8/6/4/2) |
|----------|------|-----------|-------------------|
| **Prohibited Content** | 0.4 | Zero violações de policy Meta | Limpo → Violações graves |
| **Targeting Alignment** | 0.3 | Segmentação legítima (sem enganação) | Alinhado → Manipulador |
| **Disclosure** | 0.2 | Divulgações (preço, promos, sponsorship) | Completo → Omitido |
| **Community Standards** | 0.1 | Respeita normas comunitárias | Seguro → Ofensivo |

**Few-Shot Example (Aprovado):**
```
Input: Anúncio de webinar com preço transparente, sem claims exagerados
Expected Score: 9/10 (aprovado)
Reasoning: Sem violações, disclosure claro, targeting legítimo
```

**Few-Shot Example (Reprovado):**
```
Input: "Ganhe R$10k em 24 horas" (claim falso) + targeting oculto
Expected Score: 2/10 (reprovado)
Reasoning: Violação clara de policy + misleading targeting
```

---

### 4️⃣ PERFORMANCE RUBRIC (Potencial de Performance)

**Threshold:** 6/10 (aprovado se ≥ 6)

**Critérios** (peso total = 1.0):

| Critério | Peso | Descrição | Níveis (10/8/6/4/2) |
|----------|------|-----------|-------------------|
| **Scroll-Stopping** | 0.3 | Capacidade de interromper scroll | Muito alto → Ignorado |
| **Engagement Potential** | 0.3 | Likelihood de comentários/shares | Alto → Baixo |
| **Click Intent** | 0.25 | Clareza de proposição + CTA | Óbvio → Confuso |
| **Audience Match** | 0.15 | Alinhamento com targeting | Perfeito → Desalinhado |

**Few-Shot Example (Aprovado):**
```
Input: Vídeo com abertura impactante, pergunta provocativa, CTA claro
Expected Score: 7.8/10 (aprovado)
Reasoning: Alto potencial de scroll-stop + engagement + click intent claro
```

**Few-Shot Example (Reprovado):**
```
Input: Vídeo estático, sem CTA, mensagem vaga
Expected Score: 4/10 (reprovado)
Reasoning: Baixo scroll-stopping, engagement fraco, intent confuso
```

---

## 📁 ESTRUTURA DE ARQUIVOS

```
.aiox-core/
├── nexus/
│   ├── models.py              # AgentScore, CreativeBundle (Phase 01-01)
│   ├── config.py              # NexusConfig com thresholds (Phase 01-01)
│   │
│   └── rubrics/               # 4 Rubricas estruturadas (Phase 01-02)
│       ├── __init__.py        # Export central: ALL_RUBRICS
│       ├── copy_rubric.py     # COPY_RUBRIC
│       ├── tech_rubric.py     # TECH_RUBRIC
│       ├── compliance_rubric.py  # COMPLIANCE_RUBRIC
│       └── performance_rubric.py # PERFORMANCE_RUBRIC
│
├── tests/
│   └── test_rubrics.py        # 6 testes estruturais (weights, anchors, thresholds)
│
└── .planning/
    └── phases/01-foundation/
        ├── 01-01-PLAN.md
        ├── 01-01-SUMMARY.md
        ├── 01-02-PLAN.md
        ├── 01-02-SUMMARY.md
        ├── 01-RESEARCH.md
        ├── 01-VALIDATION.md
        └── 01-VERIFICATION.md
```

---

## ✅ COBERTURA DE TESTES

**16/16 testes GREEN** — Suite completa passa em < 1 segundo.

### Testes Estruturais (6 testes em `test_rubrics.py`)

```python
✅ test_copy_rubric_structure()
✅ test_tech_rubric_structure()
✅ test_compliance_rubric_structure()
✅ test_performance_rubric_structure()
✅ test_weights_sum_to_one()      # Invariante: sum(weights) = 1.0 ± 0.01
✅ test_threshold_consistency()    # Invariante: expected_approved = (score >= threshold)
```

### Testes de Modelos + Config (10 testes em `test_models.py` + `test_config.py`)

```python
✅ test_agent_score_creation()
✅ test_creative_bundle_structure()
✅ test_nexus_config_defaults()
... (7 testes adicionais de validação)
```

---

## 🚀 PRÓXIMOS PASSOS

### Imediato (Phase 2 — Review Agents)

**Bloqueio:** Necessário `ANTHROPIC_API_KEY` no `.env`  
(Setup concluído — você forneceu OpenAI + Voyage, falta apenas Anthropic para Phase 2)

**O que será feito:**
1. **02-01**: Calibração de agentes via few-shot examples (usar rubricas como system prompts)
2. **02-02**: Pipeline de scoring (instructor LLM + estrutura JSON)
3. **02-03**: Quality gates (quarantine de criativos abaixo dos thresholds)

**Dependência:** Phase 2 importará `from nexus.rubrics import ALL_RUBRICS` para alimentar os prompts dos agentes.

### Curto Prazo (Phase 3 — Web UI)

- Dashboard de submission de criativos
- Queue de review em tempo real
- Feedback estruturado (score breakdown + recomendações)
- Audit trail completo

---

## 🔑 DECISÕES ARQUITETURAIS

### 1. **Rubricas como Plain Dicts** (não Pydantic)

**Decisão:** Rubricas implementadas como dicts Python estruturados, não modelos Pydantic.

**Por quê:** 
- Mais fácil iterar e ajustar critérios
- Embutem diretamente em prompts do instructor LLM
- Menos overhead de serialização

**Tradeoff:** Perder validação em tempo de execução (aceitável — testes estruturais cobrem).

---

### 2. **Numeric Level Keys** (10, 8, 6, 4, 2)

**Decisão:** Keys dos levels são int, não float ou string.

**Por quê:**
- Clareza ao fazer lookup em dicts
- Não ambiguidade com strings
- Representa escala discreta (não contínua)

**Exemplo:**
```python
levels = {
    10: "Excelente",
    8: "Bom",
    6: "Aceitável",
    4: "Fraco",
    2: "Inaceitável"
}
```

---

### 3. **Compliance Threshold = 8** (Mais Rigoroso)

**Decisão:** Threshold de compliance é 8/10, enquanto outros são 6-7.

**Por quê:**
- Bans de conta Meta são **irreversíveis**
- Zero tolerância a violações de policy
- Melhor rejeitarem 1 criativo legítimo do que deixarem 1 violação passar

**Impacto:** Compliance é o gatekeep mais rigoroso do pipeline.

---

### 4. **Few-Shot Examples em PT-BR**

**Decisão:** Exemplos de few-shot calibração estão em português.

**Por quê:**
- Alinhamento com público-alvo real (campanhas PT)
- Máxima relevância durante calibração dos agentes
- Semântica mais precisa para o LLM em idioma-alvo

---

## 📈 MÉTRICAS DE SUCESSO

| Métrica | Target | Status |
|---------|--------|--------|
| Testes Estruturais | 100% pass | ✅ 16/16 |
| Threshold Consistency | 100% | ✅ Validado |
| Weight Invariants | sum = 1.0 ± 0.01 | ✅ Validado |
| Documentação | Completa | ✅ Completa |
| Commits Atômicos | 100% | ✅ 2 commits (test + feat) |
| Pronto para Phase 2 | Sim | ✅ Sim |

---

## 🔗 REFERÊNCIAS RÁPIDAS

### Como Usar as Rubricas (Phase 2)

```python
from nexus.rubrics import ALL_RUBRICS

# Acessar uma rubrica específica
copy_rubric = ALL_RUBRICS['copy']
compliance_rubric = ALL_RUBRICS['compliance']

# Usar como system prompt em instructor LLM
rubric_context = copy_rubric['description']
criteria = copy_rubric['criteria']
examples = copy_rubric['few_shot_examples']

# Validar score contra threshold
from nexus.config import NEXUS_CONFIG
if score >= NEXUS_CONFIG.min_copy_score:
    print("APROVADO")
else:
    print("REPROVADO")
```

### Arquivos Críticos

- **[nexus/rubrics/__init__.py](nexus/rubrics/__init__.py)** — Export central
- **[tests/test_rubrics.py](tests/test_rubrics.py)** — Cobertura estrutural
- **[.planning/phases/01-foundation/01-02-SUMMARY.md](.planning/phases/01-foundation/01-02-SUMMARY.md)** — Execução completa

---

## 📝 HISTÓRICO DE EXECUÇÃO

| Data | Fase | Status | Commits |
|------|------|--------|---------|
| 2026-03-26 | 01-01 | ✅ CONCLUÍDA | cee05de, 1f71993, febf684 |
| 2026-03-26 | 01-02 | ✅ CONCLUÍDA | 868815a, a0b14fb, 6a234b7 |
| 2026-04-10 | Setup | ✅ .env configurado | — |

---

## 🎬 PRÓXIMA AÇÃO

**Senhor, Phase 01 está 100% completa e validada.**

Para prosseguir com Phase 2 (Review Agents):

```bash
# 1. Confirme ANTHROPIC_API_KEY no .env
cat .env | grep ANTHROPIC_API_KEY

# 2. Execute Phase 2
/gsd:execute-phase 2
```

**Bloqueio atual:** Aguardando ANTHROPIC_API_KEY para calibração de agentes.  
**Estimativa:** Phase 2 concluída em ~8-10 min (3 planos, testes + feat + docs).

---

**Dossier criado:** 2026-04-10  
**Versão:** 1.0  
**Status:** ✅ PRONTO PARA OPERAÇÃO
