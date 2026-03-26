# Technology Stack

**Project:** NEXUS - Autonomous Review Layer for Creative Pipeline
**Researched:** 2026-03-26
**Overall Confidence:** MEDIUM (training data only, no live verification possible)

## Recommended Stack

### Core Framework

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Python | 3.11+ | Runtime | Already used by pipeline.py. 3.11+ for TaskGroup and ExceptionGroup support in asyncio |
| Pydantic | v2.x (2.6+) | Structured data models | Review scores, criteria, reports all need typed validation. Pydantic v2 is 5-17x faster than v1 and the standard for structured data in Python |
| anthropic | 0.39+ | Claude API client | Direct SDK, no wrapper needed. Pipeline already uses Claude for script generation |

### Structured LLM Output (Critical Choice)

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **instructor** | 1.7+ | Structured output extraction from Claude | Wraps anthropic SDK, adds Pydantic model validation to LLM responses with automatic retry on validation failure. Lighter than pydantic-ai, does exactly one thing well |

**Why instructor over pydantic-ai:** pydantic-ai is a full agent framework (dependency injection, tool use, multi-step agents). NEXUS does not need agents that call tools or make decisions about what to do next -- it needs an LLM to return a structured score card. instructor is the minimal correct tool: it patches the anthropic client to return Pydantic models with retry on schema violation. Less abstraction, less to break, less to learn.

**Why not raw Anthropic tool_use:** Claude's native tool_use can return structured JSON, but you lose automatic Pydantic validation, retry on malformed output, and the ergonomic `response_model=` pattern. instructor adds ~200 lines of wrapper for significant DX improvement.

### Async Pipeline & Retry

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| asyncio (stdlib) | builtin | Async orchestration | No external dependency. Pipeline steps (generate script, generate audio, generate video, review) are sequential per creative but parallelizable across creatives |
| tenacity | 9.0+ | Retry with backoff | Battle-tested retry library. Handles API rate limits (ElevenLabs, Hedra, Claude) and the review-regeneration loop with configurable max attempts |

### File Organization & Reporting

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| pathlib (stdlib) | builtin | Path management | Cross-platform, readable, already Python standard |
| Jinja2 | 3.1+ | Report templating | Review reports in markdown/HTML. Jinja2 is the standard, no reason to reinvent |
| rich | 13.0+ | Console output | Progress bars, tables, colored status for pipeline runs. Optional but high-value DX |

### Configuration

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| python-dotenv | 1.0+ | .env loading | Already in use by pipeline.py for API keys |
| pydantic-settings | 2.0+ | Typed config | Extends Pydantic to load from .env with type validation. Prevents "API key is None" bugs at startup |

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Structured output | instructor | pydantic-ai | Over-engineered for scoring use case. Full agent framework when we need structured extraction. Adds dependency injection, tool registry, agent graph -- none needed here |
| Structured output | instructor | LangChain output parsers | LangChain is heavy (100+ deps), abstracts away Claude-specific features, version churn is extreme |
| Structured output | instructor | Raw tool_use | Works but no auto-retry on schema violation, no Pydantic integration, more boilerplate |
| Agent framework | None (direct) | LangGraph | NEXUS has a fixed pipeline topology (generate -> review -> approve/reject -> regenerate). LangGraph adds graph DSL overhead for what is a simple while loop |
| Agent framework | None (direct) | CrewAI | Multi-agent role-play framework. NEXUS reviewers are not "collaborating agents" -- they are 4 scoring functions with structured output. CrewAI adds unnecessary abstraction |
| Agent framework | None (direct) | AutoGen | Microsoft's multi-agent conversation framework. Same problem: NEXUS is not a conversation, it is a scoring pipeline |
| Retry | tenacity | backoff | tenacity has more features (retry combining, custom callbacks, jitter strategies) and larger community |
| Reporting | Jinja2 | f-strings | Unmaintainable for multi-section review reports |

## What NOT to Use

### LangChain / LangGraph
**Why not:** The #1 trap for Python AI projects. LangChain adds 100+ transitive dependencies, version pinning hell, and abstractions that fight you when you need Claude-specific features. NEXUS has a simple linear pipeline with a conditional loop -- this is a `while not approved` loop, not a graph. Do not bring a framework for what is 20 lines of control flow.

### CrewAI / AutoGen / Multi-Agent Frameworks
**Why not:** These frameworks model agents as autonomous entities that converse, delegate, and make decisions. NEXUS review agents are **scoring functions**: they receive a creative, return a structured score card. There is no agent-to-agent communication, no delegation, no emergent behavior. Using a multi-agent framework here adds complexity with zero benefit.

### pydantic-ai (for this specific project)
**Why not:** Good library, wrong use case. pydantic-ai shines when you need agents with tool use, dependency injection, and multi-step reasoning. NEXUS needs: "call Claude, get a Pydantic model back." instructor does exactly this with less abstraction. If NEXUS later evolves into agents that browse the web, call APIs, or make decisions -- then reconsider pydantic-ai.

### Custom JSON parsing
**Why not:** Writing `json.loads(response.content)` with manual try/except is fragile. LLMs sometimes return markdown-wrapped JSON, extra text before/after, or slightly malformed output. instructor handles all edge cases with retry.

### Celery / Redis queue
**Why not:** Overkill for v1. NEXUS processes batches of creatives sequentially or with asyncio concurrency. There is no distributed worker need. A simple `asyncio.Semaphore` handles concurrency limits for API rate limiting.

## Architecture Pattern: Direct Orchestration

The recommended pattern is **direct orchestration** -- no framework, just typed Python functions composed with asyncio:

```python
# Core pattern: structured review with instructor
import instructor
from anthropic import Anthropic
from pydantic import BaseModel, Field

class ReviewScore(BaseModel):
    """Structured review output -- enforced by instructor"""
    copy_quality: int = Field(ge=1, le=10, description="Script copy quality")
    technical_quality: int = Field(ge=1, le=10, description="Audio/video technical quality")
    meta_compliance: int = Field(ge=1, le=10, description="Meta Ads policy compliance")
    performance_prediction: int = Field(ge=1, le=10, description="Predicted ad performance")
    approved: bool = Field(description="Overall pass/fail")
    feedback: str = Field(description="Specific feedback for regeneration if rejected")

client = instructor.from_anthropic(Anthropic())

# Core loop pattern
async def review_and_regenerate(creative, max_attempts=3):
    for attempt in range(max_attempts):
        review = client.messages.create(
            model="claude-sonnet-4-20250514",
            response_model=ReviewScore,
            max_tokens=1024,
            messages=[{"role": "user", "content": build_review_prompt(creative)}],
        )
        if review.approved:
            return creative, review
        creative = await regenerate(creative, review.feedback)
    return creative, review  # Return last attempt even if not approved
```

## Installation

```bash
# Core dependencies
pip install anthropic instructor pydantic pydantic-settings tenacity python-dotenv

# Optional but recommended
pip install rich jinja2

# Development
pip install pytest pytest-asyncio ruff mypy
```

### requirements.txt

```
anthropic>=0.39.0
instructor>=1.7.0
pydantic>=2.6.0
pydantic-settings>=2.0.0
tenacity>=9.0.0
python-dotenv>=1.0.0
rich>=13.0.0
jinja2>=3.1.0
```

### Dev requirements

```
pytest>=8.0.0
pytest-asyncio>=0.24.0
ruff>=0.8.0
mypy>=1.13.0
```

## Version Confidence

| Package | Recommended Version | Confidence | Notes |
|---------|-------------------|------------|-------|
| anthropic | >=0.39.0 | MEDIUM | Version based on training data (May 2025). Verify latest on PyPI |
| instructor | >=1.7.0 | MEDIUM | Actively developed, API stable. Verify latest |
| pydantic | >=2.6.0 | HIGH | v2 is mature and stable |
| tenacity | >=9.0.0 | MEDIUM | Long-stable library, version may have incremented |
| python-dotenv | >=1.0.0 | HIGH | Mature, rarely changes |
| rich | >=13.0.0 | HIGH | Mature library |
| jinja2 | >=3.1.0 | HIGH | Very stable |

## Sources

- Training data knowledge (May 2025 cutoff) -- no live verification was possible
- instructor: github.com/jxnl/instructor -- Pydantic structured output for LLMs
- pydantic-ai: github.com/pydantic/pydantic-ai -- Full agent framework by Pydantic team
- tenacity: github.com/jd/tenacity -- General-purpose retry library
- Anthropic SDK: github.com/anthropics/anthropic-sdk-python

**Note:** All version recommendations should be verified against PyPI before pinning in requirements.txt. Web search was unavailable during this research session.
