# Requirements: NEXUS

**Defined:** 2026-03-26
**Core Value:** Criativos aprovados sem intervenção humana — o pipeline gera, o squad revisa, o loop regenera até aprovar, e o output chega organizado e auditável.

## v1 Requirements

### Foundation

- [ ] **FND-01**: Sistema define modelos Pydantic tipados (ReviewScore, CreativeBundle, NexusConfig) como base de dados de todo o pipeline
- [ ] **FND-02**: Toda configuração (MAX_RETRIES, thresholds por agente, model IDs) é carregada de variáveis de ambiente via .env, sem hardcode
- [ ] **FND-03**: Cada dimensão de revisão possui rubrica estruturada com critérios objetivos e exemplos few-shot para calibração

### Review Engine

- [ ] **REV-01**: 4 agentes revisores rodam em paralelo via ThreadPoolExecutor (copy quality, Meta compliance, technical quality, performance score)
- [ ] **REV-02**: Cada agente retorna veredicto tipado via instructor: aprovado/reprovado + score numérico + feedback específico e acionável
- [ ] **REV-03**: Pipeline implementa gate de custo — script é revisado ANTES de gerar áudio (ElevenLabs) e vídeo (Hedra)
- [ ] **REV-04**: Agente de qualidade técnica analisa o .mp4 gerado (análise multimodal via Claude vision)

### Loop

- [ ] **LOOP-01**: Na regeneração, cada agente reprovador fornece feedback específico que é injetado no prompt de reescrita do script
- [ ] **LOOP-02**: Circuit breaker limita tentativas por criativo (padrão: 3); ao esgotar, criativo é movido para quarantine/ com relatório completo
- [ ] **LOOP-03**: Reprova no copy gate regenera apenas o script — áudio e vídeo NÃO são recriados até o script ser aprovado

### Output

- [ ] **OUT-01**: Criativos aprovados (todos os agentes passaram) são salvos em pasta approved/ prontos para upload manual
- [ ] **OUT-02**: Cada criativo gera um relatório JSON com scores por dimensão, feedback recebido e histórico de tentativas
- [ ] **OUT-03**: Ao final do batch, pipeline gera resumo com: total aprovados/reprovados/quarantined, custo estimado em créditos de API, tempo de execução

### Integration

- [ ] **INT-01**: nexus.py orquestra pipeline.py como caixa-preta, sem modificar o arquivo original — backward compatibility total
- [ ] **INT-02**: nexus.py é executável via CLI com os mesmos argumentos de pipeline.py (--image, --niche, --hooks)

## v2 Requirements

### Performance & Scale

- **PERF-01**: Processamento assíncrono com asyncio para múltiplos criativos em paralelo
- **PERF-02**: Cache de veredictos para scripts idênticos (evitar chamadas duplicadas)

### Intelligence

- **INTEL-01**: Aprendizado com aprovações/reprovações históricas para refinar rubricas
- **INTEL-02**: Análise de performance retroativa do Meta Ads conectada ao pipeline

### Distribution

- **DIST-01**: Upload automático para Meta Ads Manager via API após aprovação
- **DIST-02**: Export para Google Drive / pasta compartilhada para distribuição ao time

## Out of Scope

| Feature | Reason |
|---------|--------|
| Interface web / dashboard | Revisão é 100% autônoma — sem UI necessária em v1 |
| Upload automático no Meta Ads | Reduz escopo v1; pasta local é suficiente |
| Aprendizado com performance do Meta | Requer histórico de dados; v2+ |
| Múltiplos nichos em paralelo | Scale feature; não é o problema central de v1 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FND-01 | Phase 1 | Pending |
| FND-02 | Phase 1 | Pending |
| FND-03 | Phase 1 | Pending |
| REV-01 | Phase 2 | Pending |
| REV-02 | Phase 2 | Pending |
| REV-03 | Phase 2 | Pending |
| REV-04 | Phase 2 | Pending |
| LOOP-01 | Phase 3 | Pending |
| LOOP-02 | Phase 3 | Pending |
| LOOP-03 | Phase 3 | Pending |
| OUT-01 | Phase 4 | Pending |
| OUT-02 | Phase 4 | Pending |
| OUT-03 | Phase 4 | Pending |
| INT-01 | Phase 5 | Pending |
| INT-02 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 15 total
- Mapped to phases: 15
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-26*
*Last updated: 2026-03-26 after initial definition*
