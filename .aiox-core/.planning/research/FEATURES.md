# Feature Landscape

**Domain:** Autonomous AI Creative Review Pipeline for Meta Ads
**Researched:** 2026-03-26 (enriched pass)
**Overall Confidence:** MEDIUM (training data + project context; web search unavailable for live verification)

---

## Table Stakes

Features the system MUST have. Without these, the pipeline has no value over the current linear flow.

| # | Feature | Why Expected | Complexity | Notes |
|---|---------|--------------|------------|-------|
| TS-1 | **Copy Quality Gate** | Scripts with grammar errors, weak hooks, or incoherent structure produce bad creatives at scale. Cheapest gate (text-only, zero API cost beyond LLM). | Low | LLM-as-judge on script text. Rubric: hook strength (first 3s), clarity, emotional resonance, CTA presence/strength. Return structured score + feedback. |
| TS-2 | **Meta Ads Policy Compliance Gate** | Meta rejects ~20% of ads for policy violations. Catching violations BEFORE audio/video generation saves ElevenLabs + Hedra credits. The relationship/infidelity niche is HIGH RISK for Meta policy flags. | Medium | Must encode Meta Advertising Standards: no misleading claims, no before/after implications, no personal attributes ("Are you struggling with..."), no sensationalized language. See "Meta Policy Details" section below. |
| TS-3 | **Structured Verdict Schema** | Without machine-parseable output, the regeneration loop cannot act on feedback. Every agent must return the same schema. | Low | Pydantic model: `{verdict: "pass"|"fail", score: 0-100, issues: [{category, severity, description, suggestion}]}`. Use `instructor` library for structured extraction. |
| TS-4 | **Regeneration Loop with Feedback Injection** | Core value proposition. Without auto-retry, this is just a report generator, not an autonomous pipeline. | Medium | On fail: extract agent feedback, inject into prompt for next generation. Feedback must be specific enough to change the output. |
| TS-5 | **Circuit Breaker (Max Retries)** | Without a limit, a systematically bad prompt burns unlimited API credits in an infinite retry loop. | Low | Default: 3 attempts. After max retries, quarantine creative with full failure report for human triage. NEVER run unbounded. |
| TS-6 | **Cost-Aware Gate Sequencing** | ElevenLabs and Hedra have per-use costs ($0.05-0.50+ per generation). Script-level checks MUST run BEFORE media generation. This is the highest-ROI architectural decision. | Medium | Split pipeline: generate script -> review script (gates 1-2) -> if pass, generate audio+video -> review media (gates 3-4). Prevents wasting credits on scripts that will fail review. |
| TS-7 | **Organized Output Directory** | Stated deliverable. Without this, user still manually sorts files. | Low | `output/{batch_id}/approved/`, `output/{batch_id}/rejected/`, `output/{batch_id}/reports/`. Each creative paired with its review report. |
| TS-8 | **Review Report per Creative** | Auditability. User needs to know WHY a creative was approved and what scores it got. Also useful for learning what prompt patterns work. | Low | JSON + markdown report: scores per gate, pass/fail per criterion, retry history, final verdict. Saved alongside .mp4. |
| TS-9 | **Fail-Fast Gate Ordering** | Running all 4 agents on every creative is wasteful. If copy fails policy, no point scoring video quality. | Low | Order: (1) Policy Compliance, (2) Copy Quality, (3) Technical Quality, (4) Performance Prediction. Short-circuit on fail at any stage. |
| TS-10 | **.env-Based Configuration** | Pipeline already uses .env for API keys. Extending the existing pattern maintains consistency. | Low | Add review thresholds, max retries, niche config to existing .env pattern. |

## Differentiators

Features that elevate beyond basic pass/fail. Not all required for v1 MVP, but provide significant quality uplift.

| # | Feature | Value Proposition | Complexity | Notes |
|---|---------|-------------------|------------|-------|
| DF-1 | **Predictive Performance Score** | Estimate engagement before spending ad budget. Even a heuristic rubric (hook + emotion + CTA + pacing) is more than most advertisers have pre-launch. | Medium | NOT ML (no training data yet). LLM-as-judge with rubric: hook (0-25), emotional resonance (0-25), clarity (0-25), CTA strength (0-25). Calibrate with real Meta data in v2. |
| DF-2 | **Technical Quality Gate (Audio/Video)** | Catch ElevenLabs artifacts (clipping, pauses, pronunciation) and Hedra artifacts (lip-sync drift, frozen frames). | High | Audio: Whisper re-transcription + WER comparison, silence gap detection, audio level check. Video: duration/resolution check + LLM vision on sampled keyframes. Start simple, iterate. |
| DF-3 | **Niche-Specific Compliance Rules** | The relationship niche has EXTRA Meta sensitivity. Generic checks miss niche landmines (implying you can "catch a cheater", health claims about emotional recovery). | Low | YAML config per niche with forbidden phrases, required disclaimers, sensitivity flags. Load via `--niche` parameter. |
| DF-4 | **Per-Criterion Regeneration Prompts** | Generic "try again" produces similar output. Targeted feedback ("the hook needs to be a question, not a statement") produces meaningfully different regenerations. | Medium | Route structured feedback to the specific prompt section. Requires feedback to include both the problem and a concrete suggestion. |
| DF-5 | **Creative Versioning** | Track v1 (rejected) -> v2 (rejected) -> v3 (approved). Builds a dataset for understanding what makes creatives succeed. | Low | Append version history to report: `[{version: 1, verdict: "fail", issues: [...]}, {version: 2, verdict: "pass", scores: {...}}]`. |
| DF-6 | **Configurable Score Thresholds** | Different campaigns need different bars. A/B test campaigns accept 70+; hero creatives need 90+. | Low | `--min-score 80` or per-gate thresholds in config. Default: 70 overall, 60 minimum per gate. |
| DF-7 | **Dry-Run Mode** | Review scripts without generating audio/video. Validates prompt strategies before spending API credits. | Low | `--dry-run` flag. Runs only script-level gates (policy + copy quality). Zero ElevenLabs/Hedra cost. Trivial to add once script review exists. |
| DF-8 | **Batch Processing** | Generate N script variations, review each independently, output approved set. Essential for ad testing at scale. | Medium | `--batch N` flag. Parallel where possible (asyncio.Semaphore bounded by API rate limits). |
| DF-9 | **Batch Summary Report** | After batch: X generated, Y approved, Z rejected, average scores, common failure reasons, estimated cost. | Low | Aggregate individual reports into markdown summary. |
| DF-10 | **Prompt Evolution Log** | Track which prompt patterns consistently produce passing creatives. Over time, builds a "winning prompt" library. | Low | Log: original prompt, niche, angle, scores, pass/fail. After N runs, surface patterns. |

## Anti-Features (v1)

Things to deliberately NOT build. Each has a clear rationale for exclusion.

| # | Anti-Feature | Why Avoid | What to Do Instead |
|---|--------------|-----------|-------------------|
| AF-1 | **Meta Ads Auto-Upload** | Adds Meta Marketing API complexity, OAuth flows, campaign structure assumptions, risk of auto-publishing. Massive scope for marginal time savings. | Deliver organized folder. Manual upload. v3+. |
| AF-2 | **Web Dashboard / UI** | System is autonomous and CLI-driven. UI adds frontend stack, hosting, auth, maintenance with no quality improvement. | CLI output + markdown reports. Simple HTML report generator if needed later. |
| AF-3 | **Agent-to-Agent Conversation** | Review is scoring, not debate. Multi-agent chat adds latency, unpredictability, and token cost. Agents disagree unproductively. | 4 scoring criteria in structured prompts. Independent evaluations, not a conversation. |
| AF-4 | **ML-Based Performance Prediction** | No training data. Building a real model requires historical Meta performance data (CTR, conversions). Premature. | LLM-as-judge with heuristic rubric (DF-1). Collect scores now, build model in v2+. |
| AF-5 | **Database / Persistent Storage** | No persistence need in v1. File system is sufficient. Adding a DB is infrastructure overhead. | JSON files in output folder. Flat file structure. |
| AF-6 | **Real-Time Video Analysis (Frame-by-Frame)** | Computationally expensive, needs CV libraries. Most Hedra artifacts are gross (frozen video) or too subtle for automated detection. | Duration/resolution/filesize checks + LLM vision on 3-5 sampled keyframes. |
| AF-7 | **Multi-Platform Compliance** | Each platform has different policies. Supporting TikTok, Google, etc. multiplies the compliance rule surface. | Meta-only for v1. Abstract compliance interface for future platforms. |
| AF-8 | **Human-in-the-Loop Approval** | Defeats the purpose. Human checkpoints reintroduce the bottleneck the system eliminates. | Fully autonomous with circuit breaker. Humans review only quarantined creatives (max-retry failures). |
| AF-9 | **Custom LLM Fine-Tuning** | Prompt engineering with structured output (instructor) is sufficient for v1. Fine-tuning requires data collection, training infrastructure. | Well-crafted scoring rubrics in prompts. |
| AF-10 | **Retroactive Learning from Meta Performance** | Requires Meta Ads API integration, data pipeline, attribution modeling. v2 feature. | Track scores now, correlate with actual performance later. |
| AF-11 | **Creative Asset Library / DAM** | Asset management is a separate product. Adds DB, search, tagging requirements. | Naming conventions + flat folder structure. File system is the "DAM". |

## Feature Dependencies

```
                    TS-3 (Structured Verdict)
                    /                        \
                   v                          v
    TS-4 (Regen Loop)                  TS-9 (Fail-Fast Ordering)
         |                                    |
         v                                    v
    TS-5 (Circuit Breaker)             TS-6 (Cost-Aware Sequencing)
         |                                    |
         v                                    |
    DF-5 (Versioning)                         |
         |                              requires both:
         v                             TS-1 (Copy Quality) +
    DF-10 (Prompt Evolution)           TS-2 (Policy Compliance)


    TS-7 (Output Dir) -----> TS-8 (Review Reports)

    DF-8 (Batch Processing) -----> DF-9 (Batch Summary)

    DF-1 (Performance Score) -----> DF-6 (Threshold Config)
```

### Critical Path for MVP

```
TS-3 -> TS-2 -> TS-1 -> TS-9 -> TS-6 -> TS-4 -> TS-5 -> TS-7 -> TS-8
```

The structured verdict (TS-3) is the foundation. Everything depends on it.

## MVP Recommendation

### Phase 1: Script-Level Review (Before Generation) -- HIGHEST ROI

Build these FIRST because they prevent wasted API credits on scripts destined to fail:

1. **TS-3** - Structured Verdict Schema (Pydantic + instructor)
2. **TS-2** - Policy Compliance Gate (catches Meta rejections before spending on audio/video)
3. **TS-1** - Copy Quality Gate (catches weak scripts)
4. **TS-6** - Cost-Aware Sequencing (split pipeline: review BEFORE media generation)
5. **DF-7** - Dry-Run Mode (free to add once script review exists)

### Phase 2: Full Pipeline Loop

6. **TS-4** - Regeneration Loop with feedback injection
7. **TS-5** - Circuit Breaker (max 3 retries)
8. **TS-9** - Fail-Fast Gate Ordering
9. **TS-7** - Output Directory structure
10. **TS-8** - Review Reports
11. **TS-10** - .env config

### Phase 3: Scale and Intelligence

12. **DF-8** - Batch Processing
13. **DF-1** - Predictive Performance Score
14. **DF-3** - Niche-Specific Rules
15. **DF-5** - Creative Versioning
16. **DF-9** - Batch Summary Report

### Defer to v2+

- **DF-2** (Technical Quality Gate) - complex audio/video analysis tooling
- **DF-4** (Per-Criterion Regen) - needs stable loop first
- **DF-10** (Prompt Evolution) - needs data from many runs

---

## Meta Ads Policy: Key Rules for the Compliance Agent

**Confidence: MEDIUM** (based on known Meta Advertising Standards; policies update frequently -- verify against current Meta Business Help Center before implementation)

### High-Risk Areas for the Relationship/Infidelity Niche

| Policy Area | Rule | Example Violation | Detection Approach |
|-------------|------|-------------------|--------------------|
| **Personal Attributes** (Section 4.1) | Ads must not assert or imply personal attributes | "Are you dealing with infidelity?" / "If your husband cheated..." | Regex for second-person questions about personal situations |
| **Sensational Content** | No sensationalized or exaggerated claims | "This ONE trick saved my marriage" / "Shocking truth about cheaters" | Pattern match for superlatives, clickbait, ALL-CAPS |
| **Before/After** | No before/after comparisons for personal situations | "Before: crying every night. After: confident and free" | Pattern match for before/after structure |
| **Health/Wellness Claims** | No unsubstantiated health claims | "Heal your trauma in 7 days" / "Scientifically proven recovery" | Flag healing timelines, scientific claims without citations |
| **Misleading Content** | No deceptive or false claims | "100% guaranteed results" / "Every woman who tried this..." | Flag absolute guarantees, universal claims |
| **Discrimination** | No targeting based on personal characteristics | Content implying knowledge of user's relationship status | Check for assumptions about viewer's personal life |

### Implementation Approach: YAML Rule Config

```yaml
# Example: compliance-rules/meta-ads-base.yaml
forbidden_patterns:
  personal_attributes:
    - "are you .*(struggling|dealing|suffering)"
    - "if you.*(cheated|betrayed|hurt)"
    - "do you feel.*(alone|broken|lost)"
  sensational:
    - "(shocking|unbelievable|you won't believe)"
    - "this (one|simple) (trick|secret|method)"
  before_after:
    - "(before|antes).*(after|agora|depois|hoje)"
  health_claims:
    - "(cure|heal|recover|curar|sarar) .* in \\d+ (days|weeks|dias|semanas)"
    - "(scientifically|clinically) (proven|tested)"
    - "guaranteed (results|recovery|healing)"
required_elements:
  cta_present: true
  disclaimer_if_testimonial: true
```

The compliance agent should combine YAML pattern matching (fast, deterministic) with LLM judgment (catches nuanced violations that regex misses). Run patterns first, LLM second.

---

## Sources and Confidence

| Finding | Source | Confidence |
|---------|--------|------------|
| Meta Ads policy areas (personal attributes, sensational content) | Training data (Meta Advertising Standards) | MEDIUM -- policies update frequently |
| LLM-as-judge for creative scoring | Training data (established pattern) | HIGH -- well-documented approach |
| Cost-aware gate sequencing | First principles (ElevenLabs/Hedra have real per-use costs) | HIGH -- obvious optimization |
| Regeneration loop with feedback injection | Training data (standard agentic loop pattern) | HIGH |
| Niche-specific compliance sensitivity | Project context (PROJECT.md) | HIGH |
| instructor library for structured output | Training data | HIGH -- standard Python tool for this |
| Feature complexity estimates | Engineering judgment | MEDIUM |

**Key Gap:** Could not verify current Meta Advertising Standards (2026) via web search. Policy compliance rules MUST be validated against the latest Meta Business Help Center before implementation. Policies change quarterly.
