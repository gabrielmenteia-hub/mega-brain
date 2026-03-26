# Architecture Research: NEXUS Review Loop

**Domain:** Autonomous AI review layer for creative ad pipeline
**Researched:** 2026-03-26
**Overall confidence:** HIGH (stdlib patterns + existing codebase conventions)

## Executive Summary

NEXUS extends a linear Python pipeline (`pipeline.py`: Claude script -> ElevenLabs audio -> Hedra video) with a parallel review layer of 4 specialized agents. The architecture wraps the existing pipeline as a black box, runs 4 independent review agents concurrently via `concurrent.futures.ThreadPoolExecutor`, aggregates verdicts into a pass/fail decision, and loops back into regeneration on rejection -- all without modifying `pipeline.py` internals.

Key architectural decision: **4 separate agent calls in parallel** rather than a single LLM call scoring 4 criteria. Rationale: each agent can have its own specialized system prompt, rubric depth, and can be independently tested, tuned, or replaced. The cost of 4 parallel calls (~same wall-clock time as 1 due to parallelism) is worth the modularity.

---

## System Components

### Component Map

```
+-------------------------------------------------------------------+
|                        nexus_orchestrator.py                       |
|  (entry point -- state machine: generate -> review -> output)      |
+--------+---------------------------+------------------------------+
         |                           |
         v                           v
+------------------+     +---------------------------+
|  pipeline.py     |     |  review_squad.py          |
|  (EXISTING -     |     |  (ThreadPoolExecutor)     |
|   unchanged)     |     +--+-----+-----+-----+-----+
|                  |        |     |     |     |
|  Claude -> 11L   |        v     v     v     v
|  -> Hedra        |     copy  tech  meta  perf
+------------------+     agent agent agent agent
                               |
                               v
                    +---------------------+
                    | review_verdict.py   |
                    | (aggregator:        |
                    |  all 4 must pass)   |
                    +---------------------+
                               |
                    +----------+----------+
                    |                     |
                    v                     v
           +---------------+    +------------------+
           | output/       |    | feedback_loop.py |
           | approved/     |    | (rejection ->    |
           | reports/      |    |  regen params)   |
           +---------------+    +------------------+
```

### Component Boundaries

| Component | Responsibility | Inputs | Outputs | Depends On |
|-----------|---------------|--------|---------|------------|
| `nexus_orchestrator.py` | Top-level loop: generate -> review -> decide -> output or retry | CLI args, config | Final approved folder | All below |
| `pipeline.py` | Generate creative assets (script, audio, video) -- EXISTING, UNCHANGED | niche, params | `.mp4` + script `.txt` in working dir | External APIs (Claude, ElevenLabs, Hedra) |
| `review_squad.py` | Run 4 review agents in parallel, collect verdicts | Creative assets (paths) | List of `AgentVerdict` | Agent modules |
| `agents/copy_agent.py` | Evaluate script quality (hooks, persuasion, clarity) | Script text | `AgentVerdict` | Anthropic API via instructor |
| `agents/tech_agent.py` | Evaluate technical quality (audio sync, video) | Audio + video paths | `AgentVerdict` | Anthropic API via instructor |
| `agents/meta_compliance_agent.py` | Check Meta Ads policy compliance | Script text + video metadata | `AgentVerdict` | Anthropic API via instructor |
| `agents/performance_agent.py` | Predict ad performance score | All assets | `AgentVerdict` with score | Anthropic API via instructor |
| `review_verdict.py` | Aggregate 4 verdicts into pass/fail + combined feedback | List of `AgentVerdict` | `ReviewResult` (approved bool, feedback dict) | None (pure logic) |
| `feedback_loop.py` | Transform rejection feedback into regeneration params | `ReviewResult` + original params | Modified generation params | None (pure logic) |
| `output_manager.py` | Organize approved assets + write JSON reports | Approved assets + review data | Structured folder output | None (filesystem) |
| `models.py` | Shared dataclasses and Pydantic models | N/A | Type definitions | None |
| `config.py` | Settings via pydantic-settings (.env) | `.env` file | Typed config object | None |

### Key Principle: pipeline.py stays untouched

`pipeline.py` is treated as a callable. The orchestrator invokes it via `subprocess.run()` or by importing its main generation function. This means:
- Zero changes to existing working code
- pipeline.py does not need to know about reviews
- The orchestrator owns the retry loop, not the pipeline

---

## Data Flow

### Happy Path (approved on first try)

```
1. nexus_orchestrator receives (niche, params)
2. calls pipeline.py -> generates script.txt + audio.mp3 + video.mp4
3. passes asset paths to review_squad
4. review_squad runs 4 agents IN PARALLEL via ThreadPoolExecutor
5. Each agent returns AgentVerdict(approved: bool, score: float, feedback: str)
6. review_verdict aggregates: ALL 4 approved? -> ReviewResult(approved=True)
7. output_manager copies to approved/ + writes review_report.json
8. Done
```

### Rejection Path (retry loop)

```
1-5. Same as above
6. review_verdict: agent "copy" rejected -> feedback "hook fraco, sem urgencia"
7. feedback_loop bundles ALL rejection feedback -> new generation params
8. nexus_orchestrator checks: attempt < MAX_RETRIES (default: 3)?
   YES -> go to step 2 with modified params (feedback injected into prompt)
   NO  -> move to rejected/ folder with full audit trail
```

### State Machine

```
INIT -> GENERATING -> REVIEWING -> APPROVED -> OUTPUT_SAVE -> DONE
                        |
                        v (rejected + retries left)
                     FEEDBACK_BUILD -> GENERATING (loop)
                        |
                        v (rejected + no retries left)
                     REJECTED_FINAL -> OUTPUT_SAVE -> DONE
```

State transitions are explicit and logged. No implicit side effects.

---

## Data Structures

### Core Models (models.py)

```python
from dataclasses import dataclass, field
from pathlib import Path
from pydantic import BaseModel, Field

# --- Agent output (Pydantic for instructor enforcement) ---

class AgentScore(BaseModel):
    """Structured output from each review agent via instructor."""
    score: int = Field(ge=1, le=10, description="Quality score 1-10")
    approved: bool = Field(description="Meets minimum threshold?")
    feedback: str = Field(description="Specific actionable feedback if rejected")
    strengths: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)

# --- Internal state (dataclasses for simplicity) ---

@dataclass
class AgentVerdict:
    agent_id: str          # "copy" | "tech" | "meta_compliance" | "performance"
    score: AgentScore
    evaluation_time_s: float

@dataclass
class ReviewResult:
    approved: bool
    verdicts: list[AgentVerdict]
    attempt: int
    timestamp: str
    rejection_reasons: list[str]   # Empty if approved

@dataclass
class CreativeState:
    creative_id: str
    niche: str
    attempt: int
    max_retries: int
    assets: dict[str, Path]        # {"script": Path, "audio": Path, "video": Path}
    reviews: list[ReviewResult]    # History of ALL attempts
    status: str                    # "generating"|"reviewing"|"approved"|"rejected_final"
    generation_params: dict
```

### Why Pydantic for AgentScore, dataclass for the rest

- `AgentScore` is the LLM output model -- instructor requires Pydantic to enforce schema on Claude responses
- `AgentVerdict`, `ReviewResult`, `CreativeState` are internal state -- dataclasses are lighter, no validation needed (we control the data)

---

## Review Loop Design

### Why ThreadPoolExecutor, not asyncio

The 4 review agents each make 1 LLM API call. This is I/O-bound work with exactly 4 tasks.

1. **Simpler than asyncio** -- no async/await infection throughout the codebase
2. **4 workers is trivial** -- no event loop overhead justified
3. **Compatible with requests** -- existing codebase uses `requests`, not `httpx`/`aiohttp`
4. **Matches MEGABRAIN conventions** -- `autonomous_processor.py` uses synchronous patterns with dataclasses

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def run_review_squad(assets: dict[str, Path], config: NexusSettings) -> list[AgentVerdict]:
    agents = [CopyAgent(config), TechAgent(config),
              MetaComplianceAgent(config), PerformanceAgent(config)]

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(agent.review, assets): agent.AGENT_ID for agent in agents}
        verdicts = []
        for future in as_completed(futures):
            agent_id = futures[future]
            try:
                verdict = future.result(timeout=120)
                verdicts.append(verdict)
            except Exception as e:
                verdicts.append(AgentVerdict(
                    agent_id=agent_id,
                    score=AgentScore(score=0, approved=False,
                                     feedback=f"Agent error: {e}", issues=[str(e)]),
                    evaluation_time_s=0.0
                ))
    return verdicts
```

### Why 4 separate agents, not 1 call with 4 criteria

The PROJECT.md specifies "4 critérios: qualidade do copy, qualidade técnica, conformidade Meta Ads, pontuação preditiva de performance." These could be a single LLM call with 4 score fields. We choose 4 separate agents because:

| Factor | Single Call | 4 Agents |
|--------|------------|----------|
| Prompt depth | Shallow per criterion (~200 tokens each) | Deep per criterion (~800+ tokens with rubric) |
| Wall-clock time | ~3s (1 call) | ~3s (4 parallel calls) |
| API cost | ~$0.01 | ~$0.04 |
| Testability | Must mock entire review | Mock individual agents |
| Tunability | Change rubric = change everything | Tune copy agent without touching tech agent |
| Failure isolation | 1 bad criterion = whole review fails to parse | 1 agent crashes, other 3 still produce results |

At $0.03 extra per creative, the modularity is worth it. At 100 creatives/day, that is $3/day.

### Feedback-to-Regeneration Contract

```python
def build_regen_params(original_params: dict, review: ReviewResult) -> dict:
    feedback_block = "\n".join(
        f"- [{v.agent_id}] (score {v.score.score}/10): {v.score.feedback}"
        for v in review.verdicts if not v.score.approved
    )
    new_params = {**original_params}
    new_params["instruction_override"] = (
        f"REGENERACAO (tentativa {review.attempt + 1}). "
        f"O criativo anterior foi reprovado:\n{feedback_block}\n"
        f"Corrija TODOS os pontos acima."
    )
    return new_params
```

Design decisions:
- **All rejection reasons bundled** into single regeneration (avoids whack-a-mole)
- **Feedback is appended** to original prompt, not replacing it
- **Attempt counter in prompt** so LLM knows urgency
- **Only script is regenerated** on retry -- audio/video are deterministic from script

### Retry Strategy

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Max retries | 3 (configurable via `NEXUS_MAX_REVIEW_ATTEMPTS`) | Diminishing returns + API cost control |
| Retry scope | Regenerate script only, then re-run audio + video | Script is where quality lives |
| Backoff | None between retries | LLM APIs don't benefit from backoff |
| Partial approval | NOT supported in v1 | If 3/4 approve but 1 rejects, full regen. Simpler logic. |
| Agent failure | Counts as rejection | Safe default -- unreviewed criteria = unshipped |

### Approval Threshold

All 4 agents must return `approved=True`. Each agent has its own minimum score threshold (configurable):

```python
# Per agent, in their system prompt / config:
COPY_MIN_SCORE = 7
TECH_MIN_SCORE = 6
META_COMPLIANCE_MIN_SCORE = 8  # Strictest -- Meta can ban the account
PERFORMANCE_MIN_SCORE = 6
```

Intentionally strict: false positives (bad creative shipped) cost real ad spend. False negatives (good creative rejected) only cost ~$0.04 in regeneration.

---

## Agent Interface Protocol

Every review agent implements the same interface:

```python
import instructor
from anthropic import Anthropic
from abc import ABC, abstractmethod

class ReviewAgent(ABC):
    AGENT_ID: str       # "copy" | "tech" | "meta_compliance" | "performance"
    SYSTEM_PROMPT: str  # Specialized rubric

    def __init__(self, config):
        self.client = instructor.from_anthropic(Anthropic(api_key=config.anthropic_api_key))
        self.config = config

    def review(self, assets: dict[str, Path]) -> AgentVerdict:
        """Thread-safe review. Each call creates its own API request."""
        start = time.time()
        context = self._build_context(assets)
        score = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            response_model=AgentScore,
            max_tokens=1024,
            system=self.SYSTEM_PROMPT,
            messages=[{"role": "user", "content": context}],
        )
        elapsed = time.time() - start
        return AgentVerdict(agent_id=self.AGENT_ID, score=score, evaluation_time_s=elapsed)

    @abstractmethod
    def _build_context(self, assets: dict[str, Path]) -> str:
        """Build the evaluation prompt from assets. Agent-specific."""
        ...
```

This enables: adding new agents without touching orchestrator, testing agents in isolation, swapping LLM models per agent.

---

## Output Structure

```
output/
  {batch_id}/                    # e.g., 2026-03-26_143022
    approved/
      creative_001/
        script.txt
        audio.mp3
        video.mp4
        review.json              # Final verdict + all agent scores
      creative_002/
        ...
    rejected/
      creative_003/
        script.txt               # Last attempt version
        audio.mp3
        video.mp4
        review_history.json      # ALL attempts with feedback trail
    batch_report.json            # Aggregate: N generated, M approved, K rejected
```

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Async Infection
**What:** Making pipeline.py async, adding aiohttp, converting the whole codebase
**Why bad:** Massive refactor for 4 concurrent tasks. Breaks existing working code.
**Instead:** `ThreadPoolExecutor` for the review step only. Everything else stays synchronous.

### Anti-Pattern 2: Agent-to-Agent Communication
**What:** Letting review agents see each other's verdicts or negotiate
**Why bad:** Ordering dependencies, consensus complexity, GroupThink bias
**Instead:** Agents review independently, verdicts aggregated by pure-logic function.

### Anti-Pattern 3: Modifying pipeline.py Internals
**What:** Adding review hooks inside the generation pipeline
**Why bad:** Couples review to generation. Both become harder to test.
**Instead:** Orchestrator wraps pipeline.py as a black box. Review is post-processing.

### Anti-Pattern 4: Unbounded Retry Loop
**What:** Retrying until approved with no max
**Why bad:** Infinite cost, infinite time. Some creatives are fundamentally unfixable.
**Instead:** Hard cap (default 3), then `rejected/` with full audit trail.

### Anti-Pattern 5: Multi-Agent Framework (CrewAI/AutoGen)
**What:** Using a multi-agent framework for 4 independent scoring calls
**Why bad:** Adds massive dependency for trivial use case. These frameworks are designed for agent collaboration, not independent parallel scoring.
**Instead:** 4 functions in a ThreadPoolExecutor. ~20 lines of code vs ~200 lines of framework config.

### Anti-Pattern 6: Unstructured LLM Output
**What:** Asking Claude to "review this creative" and parsing free-text response
**Why bad:** Fragile regex/string parsing, inconsistent formats across calls
**Instead:** `instructor` with Pydantic `response_model` -- schema-enforced output every time.

---

## Configuration Pattern

```python
from pydantic_settings import BaseSettings

class NexusSettings(BaseSettings):
    # API keys (from .env)
    anthropic_api_key: str
    elevenlabs_api_key: str
    hedra_api_key: str

    # Review thresholds
    min_copy_score: int = 7
    min_technical_score: int = 6
    min_compliance_score: int = 8
    min_performance_score: int = 6
    max_review_attempts: int = 3

    # Paths
    output_dir: str = "output"

    model_config = {"env_file": ".env", "env_prefix": "NEXUS_"}
```

---

## Scalability Considerations

| Concern | At 5 creatives | At 50 creatives | At 500 creatives |
|---------|----------------|-----------------|-------------------|
| API rate limits | No issue | Semaphore (3-5 concurrent creatives) | Queue with backpressure |
| Review latency | ~3s per creative (parallel agents) | ~30s with creative-level concurrency | Need worker pool |
| Disk space | Negligible | ~500MB | Cleanup policy for rejected attempts |
| Cost | ~$0.50 | ~$5 | ~$50, needs budget guard |
| Debugging | Print logs | Structured JSON logs essential | Trace IDs per creative |

For v1 scope (1-10 creatives per batch), the architecture above is sufficient. No premature optimization.

---

## Build Order

Dependencies flow downward. Build in this sequence:

### Wave 1: Foundation (no inter-dependencies)
1. **`models.py`** -- `AgentScore`, `AgentVerdict`, `ReviewResult`, `CreativeState`
2. **`config.py`** -- `NexusSettings` via pydantic-settings
3. **`agents/base_agent.py`** -- ABC interface + shared instructor client
4. **`output_manager.py`** -- folder creation + JSON report writing

**Rationale:** Pure logic / data definitions. Fully unit-testable without API calls.

### Wave 2: Agents (parallel development, independent of each other)
5. **`agents/copy_agent.py`** -- script quality review
6. **`agents/tech_agent.py`** -- technical quality review
7. **`agents/meta_compliance_agent.py`** -- Meta Ads policy check
8. **`agents/performance_agent.py`** -- performance prediction

**Rationale:** Each agent implements `ReviewAgent.review()`. Can be developed and tested against fixture data in parallel.

### Wave 3: Coordination Logic
9. **`review_squad.py`** -- ThreadPoolExecutor runner
10. **`review_verdict.py`** -- pass/fail aggregation
11. **`feedback_loop.py`** -- rejection -> regen params transformer

**Rationale:** Depends on Wave 1 types + Wave 2 interface. Core loop logic.

### Wave 4: Integration
12. **`nexus_orchestrator.py`** -- state machine, calls pipeline + review squad + output manager

**Rationale:** Glue layer. Depends on everything. Build last, test end-to-end.

### Dependency Graph

```
Wave 1: models.py ─────────────────────────┐
         config.py ─────────────────────────┤
         base_agent.py ──────────┐          │
         output_manager.py ──────┤          │
                                 │          │
Wave 2: copy_agent.py ──────────┤          │
         tech_agent.py ─────────┤          │
         meta_compliance.py ────┤          │
         performance_agent.py ──┤          │
                                │          │
Wave 3: review_squad.py ────────┤          │
         review_verdict.py ─────┤──────────┤
         feedback_loop.py ──────┤          │
                                │          │
Wave 4: nexus_orchestrator.py ──┘──────────┘
```

---

## File Structure

```
nexus/
  __init__.py
  nexus_orchestrator.py       # Entry point + state machine
  review_squad.py             # Parallel agent runner (ThreadPoolExecutor)
  review_verdict.py           # Aggregation: all 4 must pass
  feedback_loop.py            # Rejection -> regen params
  output_manager.py           # Folder structure + JSON reports
  models.py                   # AgentScore (Pydantic) + dataclasses
  config.py                   # NexusSettings (pydantic-settings)
  agents/
    __init__.py
    base_agent.py             # ABC interface + instructor client
    copy_agent.py             # Script quality specialist
    tech_agent.py             # Technical quality specialist
    meta_compliance_agent.py  # Meta Ads policy specialist
    performance_agent.py      # Performance prediction specialist
```

Sits alongside (not inside) `pipeline.py`. Orchestrator imports or subprocess-calls pipeline.

---

## Integration with Existing pipeline.py

The existing pipeline.py is NOT rewritten. Integration options:

1. **Import approach** (preferred): If pipeline.py exposes a `generate_creative(niche, params) -> dict` function, import and call it directly
2. **Subprocess approach** (fallback): If pipeline.py is a monolithic script, call via `subprocess.run(["python", "pipeline.py", "--niche", niche])` and read output from filesystem

Either way, the orchestrator treats pipeline.py as a black box with a defined input/output contract.

---

## Sources

- Existing codebase: `autonomous_processor.py` (queue + retry patterns), `task_orchestrator.py` (workflow state patterns)
- `PROJECT.md` -- project scope, constraints, 4-agent requirement
- Python stdlib `concurrent.futures` -- well-documented, stable API (HIGH confidence)
- `instructor` library -- Pydantic-enforced LLM output (HIGH confidence, widely adopted)
- Architecture patterns: Controller-Agent, State Machine (HIGH confidence, established patterns)
