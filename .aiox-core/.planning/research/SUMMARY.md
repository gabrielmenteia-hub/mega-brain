# Research Summary: NEXUS

**Domain:** Autonomous AI review layer for creative ad pipeline (Meta Ads)
**Researched:** 2026-03-26
**Overall confidence:** MEDIUM (training data only -- web search/fetch unavailable for live verification)

## Executive Summary

NEXUS adds an autonomous quality gate to an existing Python creative pipeline (Claude scripts -> ElevenLabs audio -> Hedra video). The review layer evaluates each creative on 4 criteria (copy quality, technical quality, Meta Ads compliance, performance prediction), rejects with specific feedback, and triggers regeneration until approved or max attempts exhausted.

The recommended stack is deliberately minimal: **instructor** for structured LLM output (not a full agent framework), **Pydantic v2** for typed data models, **tenacity** for retry logic, and **asyncio** for concurrency. The key architectural insight is that NEXUS review "agents" are scoring functions, not autonomous agents -- they receive input, call Claude, return a typed score card. No agent framework (CrewAI, LangGraph, AutoGen) is needed or recommended.

The biggest technical risks are LLM scoring drift (inconsistent scores across calls) and regeneration quality degradation (each attempt gets worse). Both are mitigated by prompt engineering discipline: temperature=0, few-shot calibration examples, specific/actionable feedback, and passing the original creative as reference during regeneration.

The existing pipeline.py should be composed with (not replaced by) the review layer. A new nexus.py orchestrator wraps pipeline functions and adds the review-regenerate loop, preserving backward compatibility.

## Key Findings

**Stack:** instructor + Pydantic v2 + tenacity + asyncio. No agent framework needed.
**Architecture:** Direct orchestration pattern -- typed functions composed with asyncio, not agent graphs.
**Critical pitfall:** LLM scoring drift makes review unreliable without few-shot anchoring and temperature=0.

## Implications for Roadmap

Based on research, suggested phase structure:

1. **Foundation: Review Data Model + Config** - Define Pydantic models (ReviewScore, CreativeBundle, NexusSettings) and scoring rubrics
   - Addresses: Structured review output, typed configuration
   - Avoids: Unstructured output pitfall, hardcoded model names pitfall

2. **Core: Review Engine** - instructor integration, single-creative review with 4 criteria
   - Addresses: Structured LLM scoring, pass/fail decision, feedback extraction
   - Avoids: Over-engineering pitfall (start simple, no framework)

3. **Loop: Regeneration Cycle** - Review-regenerate loop with max attempts, feedback routing
   - Addresses: Automatic regeneration on rejection
   - Avoids: Infinite loop pitfall, quality degradation pitfall

4. **Output: Organization + Reporting** - Folder structure, review reports, batch summary
   - Addresses: Organized output, auditability
   - Avoids: Naming collision pitfall

5. **Integration: Pipeline Composition** - Wire review layer into existing pipeline.py
   - Addresses: End-to-end autonomous flow
   - Avoids: Silent failure pitfall (add input validation)

**Phase ordering rationale:**
- Models before engine (engine depends on typed models)
- Engine before loop (loop composes review + regeneration)
- Output after loop (needs review results to organize)
- Integration last (needs all components working independently first)

**Research flags for phases:**
- Phase 2: May need deeper research on instructor + Anthropic SDK compatibility (verify version)
- Phase 3: Regeneration prompt engineering is the hardest part -- needs experimentation, not just implementation
- Phase 5: pipeline.py structure unknown -- may need refactoring to expose importable functions

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | instructor and Pydantic are well-established, but exact latest versions unverified |
| Features | HIGH | Requirements are clear from PROJECT.md, feature landscape is straightforward |
| Architecture | HIGH | Direct orchestration is a well-known pattern, no novel architecture needed |
| Pitfalls | HIGH | LLM scoring inconsistency and regeneration degradation are well-documented challenges |

## Gaps to Address

- **Exact library versions:** pip install versions should be verified against PyPI before pinning
- **pipeline.py structure:** Need to read the actual file to assess integration complexity
- **Hedra API limitations:** Unknown if Hedra supports batch/async calls or has strict rate limits
- **Multimodal review feasibility:** v1 is text-only review; need to research Claude vision capabilities for video frame analysis in v2
- **Cost modeling:** Need real API pricing to estimate per-batch cost at different scales
