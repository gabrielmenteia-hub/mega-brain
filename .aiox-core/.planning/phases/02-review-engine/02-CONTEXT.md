# Phase 2: Review Engine - Context

**Gathered:** 2026-05-05
**Status:** Ready for planning
**Source:** Architectural decision from /gsd:discuss-phase conversation

<domain>
## Phase Boundary

Phase 2 entrega os 4 agentes revisores que avaliam criativos (script, .mp4) contra as rubricas da Phase 1 e retornam veredictos estruturados. O cost gate bloqueia geração de áudio/vídeo quando o script reprova.

</domain>

<decisions>
## Implementation Decisions

### Arquitetura de Execução — DECISÃO CRÍTICA

**Decisão:** Agentes revisores rodam como **subagentes do Claude Code** via `Agent` tool, NÃO como scripts Python autônomos com `anthropic` SDK.

**Por quê:** O usuário escolheu explicitamente não usar ANTHROPIC_API_KEY no `.env`. O sistema roda dentro de sessões Claude Code, que já autentica via assinatura. Scripts Python autônomos exigiriam key separada para cada chamada à API.

**Implicações para o plano:**
- Remover dependências: `instructor`, `anthropic` SDK
- Substituir `ThreadPoolExecutor` por chamadas paralelas ao `Agent` tool
- Output tipado vem de parsing estruturado das respostas dos subagentes (Pydantic)
- `/nexus-review` implementado como Claude Code skill (não `python nexus.py`)
- `.mp4` analysis usa vision capability do subagente (Claude já tem isso nativamente)

### Paralelismo

Os 4 agentes revisores são spawned em paralelo (uma única mensagem com 4 `Agent` tool calls simultâneos). Equivalente ao `ThreadPoolExecutor` original, mas orquestrado pelo Claude Code.

### Output Estruturado

Cada subagente retorna JSON dentro de blocos de código que o orquestrador parseia para `AgentScore` (Pydantic, já definido na Phase 1). Sem `instructor` — parsing direto.

### Cost Gate

Lógica implementada em Python puro (sem API): se score de copy < threshold, pipeline não aciona ElevenLabs nem Hedra. Gate é decisão binária baseada no `AgentScore` parseado.

### Entrypoint

Skill `/nexus-review` no Claude Code. Usuário submete criativo, skill orquestra os 4 subagentes, agrega scores, aplica gate, reporta resultado.

### Claude's Discretion

- Estrutura interna dos prompts dos subagentes
- Formato exato do JSON retornado pelos subagentes
- Tratamento de timeouts/erros em subagentes
- Estrutura do arquivo skill (SKILL.md + skill.py ou apenas prompt)

</decisions>

<specifics>
## Specific Ideas

- `AgentScore` e `CreativeBundle` da Phase 1 continuam como modelos de dados centrais
- `ALL_RUBRICS` da Phase 1 alimentam os system prompts dos subagentes
- O orquestrador `/nexus-review` lê o criativo (script text + caminho do .mp4) e distribui para os 4 agentes especializados
- Cada agente recebe: rubrica específica + conteúdo do criativo + instrução para retornar JSON estruturado

</specifics>

<deferred>
## Deferred Ideas

- Execução standalone fora do Claude Code (exigiria ANTHROPIC_API_KEY — decisão consciente de não usar)
- Interface web para submissão (Phase 3)
- Batch processing de múltiplos criativos (Phase 4)

</deferred>

---

*Phase: 02-review-engine*
*Context gathered: 2026-05-05 via conversa arquitetural*
