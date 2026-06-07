# Task: Universal Bidirectional Gap Analysis (Autonomous)

## Task Anatomy

| Field | Value |
|-------|-------|
| **Task ID** | `bench-gap` |
| **Version** | `1.0.0` |
| **Status** | `pending` |
| **Responsible Executor** | `bench-analyst` |
| **Execution Type** | `Agent` |
| **Model** | `claude-sonnet-4-20250514` |
| **Haiku Eligible** | `false` |
| **Estimated Duration** | `15-25min` |

## Metadata
```yaml
id: bench-gap
name: "Universal Bidirectional Gap Analysis"
category: benchmark
agent: bench-analyst
elicit: false
autonomous: true
estimated_duration: "15-25min"
description: "Bidirectional gap analysis between any two subjects — identifies what A has that B lacks AND what B has that A lacks, with impact/complexity/priority classification"
```

## Purpose

Produce a comprehensive, bidirectional gap analysis between two subjects of any type
(codebase, LLM, product, company, technology). Unlike one-directional gap identification,
this task explicitly maps gaps in BOTH directions: capabilities Subject A has that Subject B
lacks, AND capabilities Subject B has that Subject A lacks.

Each gap is classified by impact (HIGH/MED/LOW), implementation complexity (LOW/MED/HIGH),
and priority (P0-P3), producing both a human-readable report and a machine-readable JSON.

This task replaces the old `bench-gap-analysis.md` (which was AIOX-centric) with a
universal, type-agnostic bidirectional approach.

## Input

| Input | Type | Required | Source |
|-------|------|----------|--------|
| `subject_a` | string | YES | Pipeline param or elicited |
| `subject_b` | string | YES | Pipeline param or elicited |
| `comparison_type` | string | YES | One of: codebase, llm, product, company, technology |
| `comparison_matrix` | file | YES | Output from `bench-compare` (comparison-matrix.json) |
| `scorecard` | file | YES | Output from `bench-score` (scorecard.json) |
| `inventory_a` | file | YES | Output from `bench-inventory-type` (inventory-a.json) |
| `inventory_b` | file | YES | Output from `bench-inventory-type` (inventory-b.json) |
| `dimension_pack` | string | NO | Dimension pack used for scoring (auto-detected from scorecard) |

## Output

| Output | Format | Destination |
|--------|--------|-------------|
| Gap analysis report | Markdown | `docs/bench/{slug}/gap-analysis.md` |
| Gap analysis data | JSON | `docs/bench/{slug}/gap-analysis.json` |

Where `{slug}` = `{subject_a}-vs-{subject_b}` (kebab-case, lowercase).

## Prerequisites

- [ ] Comparison matrix exists (`comparison-matrix.json`) from `bench-compare`
- [ ] Scorecard exists (`scorecard.json`) from `bench-score`
- [ ] Both inventories exist from `bench-inventory-type`

---

## Veto Conditions

The task MUST NOT execute (or must HALT immediately) if:

1. **No comparison matrix available** -- Cannot identify gaps without prior comparison data. Run `bench-compare` first.
2. **No scorecard available** -- Cannot prioritize gaps without scoring context. Run `bench-score` first.
3. **Missing inventories** -- Cannot determine what each subject has or lacks without inventories from `bench-inventory-type`.
4. **comparison_type not recognized** -- Must be one of: codebase, llm, product, company, technology.
5. **Output file already exists and is less than 24h old** -- Do not overwrite recent analysis unless explicitly requested with `--force`.

---

## Autonomous Execution Protocol

This task runs WITHOUT user interaction. Execute all steps sequentially,
analyze gaps bidirectionally, classify each gap, and write output files.
Report completion with summary statistics.

**CRITICAL RULES:**
- BIDIRECTIONAL: Always analyze in BOTH directions (A→B gaps AND B→A gaps)
- Every gap claim MUST be traceable to comparison matrix or inventory data
- NO invented gaps -- if data is insufficient, state "Insufficient data" not a guess
- Priority assignment must be justified with observable signals
- Impact assessment must reference specific dimensions from the scorecard

---

## Step 1: Load Comparison Artifacts

```
ACTION: Read("docs/bench/{slug}/comparison-matrix.json")
STORE: matrix_data

ACTION: Read("docs/bench/{slug}/scorecard.json")
STORE: scorecard_data

ACTION: Read("docs/bench/{slug}/inventory-a.json")
STORE: inventory_a_data

ACTION: Read("docs/bench/{slug}/inventory-b.json")
STORE: inventory_b_data

EXTRACT from matrix_data:
  - items with equivalence = "FORTE" → shared_capabilities[]
  - items with equivalence = "PARCIAL" → partial_capabilities[]
  - items with equivalence = "SEM_EQUIV" and subject = A → a_only_capabilities[]
  - items with equivalence = "SEM_EQUIV" and subject = B → b_only_capabilities[]

EXTRACT from scorecard_data:
  - dimension_scores[] (for prioritization context)
  - weighted_total_a, weighted_total_b
  - winner_per_dimension[]
```

---

## Step 2: Identify Gaps of Subject A (What B Has That A Lacks)

```
ACTION: For EACH item in b_only_capabilities[]:
  EXTRACT:
    - capability_name
    - capability_description (from inventory_b_data)
    - related_dimension (which scorecard dimension it belongs to)
    - evidence (where in B's inventory/matrix this capability appears)

ACTION: For EACH item in partial_capabilities[] where B is stronger:
  EXTRACT:
    - capability_name
    - what_a_has (partial implementation)
    - what_a_lacks (gap description)
    - delta_description (what B adds beyond A's implementation)

STORE: gaps_of_a[] = b_only + partial_where_b_stronger
```

---

## Step 3: Identify Gaps of Subject B (What A Has That B Lacks)

```
ACTION: For EACH item in a_only_capabilities[]:
  EXTRACT:
    - capability_name
    - capability_description (from inventory_a_data)
    - related_dimension (which scorecard dimension it belongs to)
    - evidence (where in A's inventory/matrix this capability appears)

ACTION: For EACH item in partial_capabilities[] where A is stronger:
  EXTRACT:
    - capability_name
    - what_b_has (partial implementation)
    - what_b_lacks (gap description)
    - delta_description (what A adds beyond B's implementation)

STORE: gaps_of_b[] = a_only + partial_where_a_stronger
```

---

## Step 4: Classify Each Gap (Type-Specific)

For EACH gap in gaps_of_a[] AND gaps_of_b[]:

```
ASSESS impact:
  HIGH: Gap affects a dimension where the subject scores < 50/100
        OR gap is in the highest-weighted dimension
        OR gap represents a core capability for the comparison_type
  MED:  Gap affects a mid-weight dimension
        OR gap is a secondary capability
  LOW:  Gap is in the lowest-weighted dimension
        OR gap is a nice-to-have capability

ASSESS complexity:
  IF comparison_type == "codebase":
    LOW:  Missing feature is isolated (1-2 files, no dependencies)
    MED:  Missing feature requires integration (3-10 files, some dependencies)
    HIGH: Missing feature requires architectural changes (10+ files, deep integration)

  IF comparison_type == "llm":
    LOW:  Missing capability is a parameter/config change (e.g., max tokens)
    MED:  Missing capability requires training/fine-tuning (e.g., new language)
    HIGH: Missing capability requires fundamental model changes (e.g., vision, reasoning)

  IF comparison_type == "product":
    LOW:  Missing feature is a UI/config addition
    MED:  Missing feature requires backend integration
    HIGH: Missing feature requires new infrastructure or partnerships

  IF comparison_type == "company":
    LOW:  Market position gap addressable through marketing/partnerships
    MED:  Gap requires new product/service development
    HIGH: Gap requires M&A, fundamental strategy pivot, or multi-year investment

  IF comparison_type == "technology":
    LOW:  Ecosystem gap fillable by community/plugins
    MED:  Gap requires core library/framework changes
    HIGH: Gap requires specification-level changes or new standards

ASSIGN priority:
  P0: impact=HIGH AND complexity=LOW (critical quick win)
  P1: impact=HIGH AND complexity=MED (high-value investment)
      OR impact=MED AND complexity=LOW (easy improvement)
  P2: impact=MED AND complexity=MED (moderate effort, moderate value)
      OR impact=HIGH AND complexity=HIGH (strategic but hard)
  P3: impact=LOW (regardless of complexity)
      OR impact=MED AND complexity=HIGH (hard for moderate gain)

STORE classification in each gap object:
  gap.impact = HIGH | MED | LOW
  gap.complexity = LOW | MED | HIGH
  gap.priority = P0 | P1 | P2 | P3
  gap.justification = "{reason for classification}"
```

---

## Step 5: Generate Action Items

For EACH gap with priority P0 or P1:

```
GENERATE action_item:
  - title: "Close gap: {capability_name}"
  - description: "{what needs to happen to close this gap}"
  - affected_dimension: "{scorecard dimension}"
  - expected_score_impact: "{estimated improvement in dimension score}"
  - dependencies: ["{other gaps that must be closed first, if any}"]
  - type-specific context:
    IF codebase: target_files, implementation_approach
    IF llm: training_approach, data_requirements
    IF product: feature_spec_needed, integration_points
    IF company: strategic_initiative, investment_required
    IF technology: specification_changes, community_engagement

STORE: action_items[]
```

---

## Step 6: Build Gap Summary Statistics

```
COMPUTE:
  total_gaps_a = gaps_of_a.length
  total_gaps_b = gaps_of_b.length

  gaps_a_by_impact = { HIGH: count, MED: count, LOW: count }
  gaps_b_by_impact = { HIGH: count, MED: count, LOW: count }

  gaps_a_by_priority = { P0: count, P1: count, P2: count, P3: count }
  gaps_b_by_priority = { P0: count, P1: count, P2: count, P3: count }

  gaps_a_by_complexity = { LOW: count, MED: count, HIGH: count }
  gaps_b_by_complexity = { LOW: count, MED: count, HIGH: count }

  most_affected_dimension_a = dimension with most gaps for A
  most_affected_dimension_b = dimension with most gaps for B

STORE: gap_summary
```

---

## Step 7: Write JSON Output

```
ACTION: Write("docs/bench/{slug}/gap-analysis.json", JSON.stringify({
  "metadata": {
    "generated_at": "<ISO-8601>",
    "subject_a": "{subject_a}",
    "subject_b": "{subject_b}",
    "comparison_type": "{comparison_type}",
    "source_artifacts": {
      "comparison_matrix": "comparison-matrix.json",
      "scorecard": "scorecard.json",
      "inventory_a": "inventory-a.json",
      "inventory_b": "inventory-b.json"
    }
  },
  "summary": {
    "total_gaps_a": <number>,
    "total_gaps_b": <number>,
    "gaps_a_by_impact": { "HIGH": <n>, "MED": <n>, "LOW": <n> },
    "gaps_b_by_impact": { "HIGH": <n>, "MED": <n>, "LOW": <n> },
    "gaps_a_by_priority": { "P0": <n>, "P1": <n>, "P2": <n>, "P3": <n> },
    "gaps_b_by_priority": { "P0": <n>, "P1": <n>, "P2": <n>, "P3": <n> },
    "most_affected_dimension_a": "<dimension>",
    "most_affected_dimension_b": "<dimension>"
  },
  "gaps_of_a": [
    {
      "id": "GAP-A-001",
      "capability": "<name>",
      "description": "<what A lacks that B has>",
      "gap_type": "missing | partial",
      "related_dimension": "<scorecard dimension>",
      "impact": "HIGH | MED | LOW",
      "complexity": "LOW | MED | HIGH",
      "priority": "P0 | P1 | P2 | P3",
      "justification": "<reason>",
      "evidence": "<reference to matrix/inventory>",
      "partial_coverage": "<what A already has, if partial>"
    }
  ],
  "gaps_of_b": [
    {
      "id": "GAP-B-001",
      "capability": "<name>",
      "description": "<what B lacks that A has>",
      "gap_type": "missing | partial",
      "related_dimension": "<scorecard dimension>",
      "impact": "HIGH | MED | LOW",
      "complexity": "LOW | MED | HIGH",
      "priority": "P0 | P1 | P2 | P3",
      "justification": "<reason>",
      "evidence": "<reference to matrix/inventory>",
      "partial_coverage": "<what B already has, if partial>"
    }
  ],
  "action_items": [
    {
      "id": "ACTION-001",
      "title": "<action title>",
      "description": "<what needs to happen>",
      "target_subject": "A | B",
      "closes_gap": "GAP-A-001 | GAP-B-001",
      "affected_dimension": "<dimension>",
      "expected_score_impact": "<estimated improvement>",
      "dependencies": []
    }
  ]
}, null, 2))
```

---

## Step 8: Write Markdown Report

```
ACTION: Write("docs/bench/{slug}/gap-analysis.md")

Use template: bench-gap-tmpl.md

CONTENT structure:
  # Gap Analysis: {SUBJECT_A} vs {SUBJECT_B}
  - Metadata header (type, date, sources)
  - Executive Summary (5-line overview of gap landscape)
  - Gaps of {SUBJECT_A} table (what B has that A lacks)
  - Gaps of {SUBJECT_B} table (what A has that B lacks)
  - Classification detail per gap
  - Action Items (P0 and P1 only)
  - Summary statistics
```

---

## Step 9: Validate Outputs

```
ACTION: Verify gap-analysis.json is valid JSON
ACTION: Verify all gap IDs are unique
ACTION: Verify every gap has impact + complexity + priority
ACTION: Verify bidirectionality (both gaps_of_a and gaps_of_b are populated)
ACTION: Verify no invented gaps (every gap traceable to matrix/inventory)

REPORT completion:
  - Total gaps of A: {count} (P0: {n}, P1: {n}, P2: {n}, P3: {n})
  - Total gaps of B: {count} (P0: {n}, P1: {n}, P2: {n}, P3: {n})
  - Action items generated: {count}
  - Most affected dimension for A: {dimension}
  - Most affected dimension for B: {dimension}
```

---

## Type-Specific Gap Examples

### Codebase Gaps
| Gap Type | Example A Gaps | Example B Gaps |
|----------|---------------|---------------|
| Missing feature | No hook system | No squad architecture |
| Missing pattern | No constitutional governance | No task anatomy standard |
| Missing capability | No self-healing CI | No agent persona system |
| Partial coverage | Basic workflows vs advanced | Basic testing vs QA gates |

### LLM Gaps
| Gap Type | Example A Gaps | Example B Gaps |
|----------|---------------|---------------|
| Missing capability | No vision/multimodal | No function calling |
| Missing language | No code generation | No creative writing |
| Missing feature | No streaming | No system prompts |
| Partial coverage | Limited context vs 200K | Limited tools vs 100+ |

### Product Gaps
| Gap Type | Example A Gaps | Example B Gaps |
|----------|---------------|---------------|
| Missing feature | No mobile app | No API access |
| Missing integration | No Slack integration | No GitHub integration |
| Missing tier | No enterprise plan | No free tier |
| Partial coverage | Basic analytics vs advanced | Basic auth vs SSO |

### Company Gaps
| Gap Type | Example A Gaps | Example B Gaps |
|----------|---------------|---------------|
| Market position | No enterprise presence | No SMB presence |
| Innovation | No AI/ML investment | No cloud-native strategy |
| Ecosystem | No partner program | No developer community |
| Partial coverage | Regional vs global | Single product vs suite |

### Technology Gaps
| Gap Type | Example A Gaps | Example B Gaps |
|----------|---------------|---------------|
| Ecosystem | No package manager | No IDE plugins |
| Tooling | No debugger | No profiler |
| Standard | No formal spec | No backward compat guarantee |
| Partial coverage | Limited platforms vs all | Limited docs vs comprehensive |

---

## Acceptance Criteria

The task is complete when ALL of the following are met:

- [ ] **AC-1:** `gap-analysis.json` exists and is valid JSON
- [ ] **AC-2:** `gap-analysis.md` exists and follows the template structure
- [ ] **AC-3:** Gaps are BIDIRECTIONAL (both `gaps_of_a` and `gaps_of_b` populated)
- [ ] **AC-4:** Every gap has impact (HIGH/MED/LOW) classification
- [ ] **AC-5:** Every gap has complexity (LOW/MED/HIGH) classification
- [ ] **AC-6:** Every gap has priority (P0-P3) assignment with justification
- [ ] **AC-7:** Action items exist for all P0 and P1 gaps
- [ ] **AC-8:** All gaps are traceable to comparison matrix or inventory data
- [ ] **AC-9:** Type-specific complexity rules applied correctly for the comparison_type
- [ ] **AC-10:** Summary statistics are accurate and match the detailed gap lists
- [ ] **AC-11:** No invented or estimated gaps -- every gap backed by data

## Error Handling

| Error | Detection | Recovery |
|-------|-----------|----------|
| Comparison matrix not found | File read fails | HALT: "Run bench-compare first" |
| Scorecard not found | File read fails | HALT: "Run bench-score first" |
| Inventory files missing | File read fails | HALT: "Run bench-inventory-type first" |
| JSON parse error | Parse fails | Report specific file and error |
| Zero gaps detected | Both gap lists empty | Warn: "Subjects may be too similar for gap analysis" |
| Unknown comparison_type | Type not in allowed list | HALT: "Unrecognized comparison_type" |

## Integration

| Task | Relationship |
|------|-------------|
| `bench-compare` | Upstream -- provides comparison-matrix.json |
| `bench-score` | Upstream -- provides scorecard.json |
| `bench-inventory-type` | Upstream -- provides inventory JSON files |
| `bench-battle-card` | Downstream -- uses gap highlights for strengths/weaknesses |
| `bench-report` | Downstream -- uses gap summary for executive report |
| `bench-absorb` | Downstream -- uses gaps for absorption roadmap |

---

_Task Version: 1.0.0_
_Pattern: HO-TP-001 (Task Anatomy Standard)_
_Created: 2026-02-17_
_Compliant: Yes_
