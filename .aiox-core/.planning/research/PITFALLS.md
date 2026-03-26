# Domain Pitfalls

**Domain:** Autonomous AI review layer for creative ad pipeline
**Researched:** 2026-03-26

## Critical Pitfalls

### Pitfall 1: LLM Scoring Drift
**What goes wrong:** Claude's scoring becomes inconsistent across calls. Same creative gets 8/10 in one run, 5/10 in another.
**Why it happens:** LLM temperature, prompt sensitivity, and context window position all affect scoring.
**Consequences:** Pipeline approves bad creatives or rejects good ones. Trust collapses.
**Prevention:**
- Set temperature=0 for review calls
- Include 2-3 calibration examples in the scoring prompt (few-shot anchoring)
- Define explicit rubrics per criterion ("8/10 means: clear hook in first 3 seconds, addresses pain point, includes CTA")
- Log all scores for drift analysis
**Detection:** Score standard deviation across identical inputs > 1.5 points

### Pitfall 2: Regeneration Loop Produces Worse Output
**What goes wrong:** Each regeneration attempt gets progressively worse. By attempt 3, the creative is generic mush.
**Why it happens:** Feedback like "improve copy quality" is too vague. The LLM over-corrects or converges to safe/boring content.
**Consequences:** Max attempts reached with declining quality. Wasted API credits.
**Prevention:**
- Feedback must be specific and actionable: "The hook lacks urgency. Add a time-sensitive element in the first sentence."
- Pass the ORIGINAL creative as reference, not just the latest version
- Consider "best of N" pattern: generate 3 variants, review all, pick best
**Detection:** Track scores across attempts. If attempt 3 scores lower than attempt 1, the loop is counterproductive.

### Pitfall 3: Over-Engineering the Agent Layer
**What goes wrong:** Team reaches for CrewAI/LangGraph/AutoGen for what is fundamentally a scoring function.
**Why it happens:** "AI agents" hype makes every LLM call feel like it needs a framework.
**Consequences:** 2-4 weeks building agent infrastructure with zero benefit over a simple function.
**Prevention:** Start with instructor + Pydantic. If you need agent-to-agent communication or tool use, THEN evaluate frameworks.
**Detection:** If your "agent" is: receive input, call LLM, return structured output -- it is a function, not an agent.

### Pitfall 4: No Review Prompt Versioning
**What goes wrong:** Someone tweaks the scoring prompt, pipeline starts rejecting everything. No way to know what changed.
**Why it happens:** Prompts stored as inline strings in code with no version tracking.
**Consequences:** Quality regression with no audit trail.
**Prevention:**
- Store prompts as separate files (e.g., prompts/review_v1.md)
- Log prompt version alongside each review result
- Gate prompt changes behind a review process
**Detection:** Review quality metrics shift suddenly after a code change.

## Moderate Pitfalls

### Pitfall 5: API Rate Limit Cascade
**What goes wrong:** Regeneration loop multiplies API calls. 10 creatives x 3 attempts = 30 Claude + 30 ElevenLabs + 30 Hedra calls.
**Prevention:**
- Calculate worst-case API calls before batch starts
- tenacity with exponential backoff for each API
- asyncio.Semaphore to cap concurrent calls
- Save partial results, support resume from checkpoint

### Pitfall 6: Reviewing the Wrong Thing
**What goes wrong:** Review evaluates script text but not actual video/audio output. Technical quality issues invisible to text-only review.
**Prevention:**
- v1: accept that Claude reviews script quality only (text-based)
- Clearly label which criteria are text-reviewable vs need multimodal
- Plan for v2: multimodal review (Claude with vision)

### Pitfall 7: Inconsistent Creative Bundle State
**What goes wrong:** After regeneration, script is v2 but audio is still from v1. Mismatched bundle saved as "approved."
**Prevention:**
- Creative bundle is atomic: if script regenerated, audio AND video must regenerate
- Use a CreativeBundle Pydantic model that enforces completeness
- Validate bundle consistency before review

### Pitfall 8: Silent Failures in Existing Pipeline
**What goes wrong:** pipeline.py fails silently. Review layer receives garbage input and scores it.
**Prevention:**
- Input validation before review: file exists, file size > 0, script length > minimum
- Wrap pipeline.py calls with explicit error handling
- Fail fast with clear error messages

## Minor Pitfalls

### Pitfall 9: Output Folder Naming Collisions
**What goes wrong:** Two batch runs in the same second overwrite each other.
**Prevention:** Batch ID format: {date}_{time}_{random_suffix}

### Pitfall 10: Large Video Files in Git
**What goes wrong:** Output .mp4 files accidentally committed.
**Prevention:** Ensure output/ is in .gitignore.

### Pitfall 11: Hardcoded Model Names
**What goes wrong:** Claude model name hardcoded. Model deprecated, pipeline breaks.
**Prevention:** Model name in config (pydantic-settings), not inline string.

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Structured review model | Scoring drift (Pitfall 1) | Few-shot examples, temperature=0 |
| Regeneration loop | Worse output per attempt (Pitfall 2) | Specific feedback, pass original as reference |
| Integration with pipeline.py | Silent failures (Pitfall 8) | Input validation layer |
| Output organization | Naming collisions (Pitfall 9) | Timestamp + random suffix |
| Batch processing | Rate limit cascade (Pitfall 5) | Calculate worst-case calls, use semaphore |
| Prompt engineering | No versioning (Pitfall 4) | Prompts as files, version tracked |
