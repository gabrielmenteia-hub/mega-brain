# Task: Executive Report Consolidation (Autonomous)

## Task Anatomy

| Field | Value |
|-------|-------|
| **Task ID** | `bench-report` |
| **Version** | `1.0.0` |
| **Status** | `pending` |
| **Responsible Executor** | `bench-analyst` |
| **Execution Type** | `Agent` |
| **Model** | `claude-sonnet-4-20250514` |
| **Haiku Eligible** | `false` |
| **Estimated Duration** | `10-20min` |

## Metadata
```yaml
id: bench-report
name: "Executive Report Consolidation"
category: benchmark
agent: bench-analyst
elicit: false
autonomous: true
estimated_duration: "10-20min"
description: "Consolidate all benchmark artifacts into a comprehensive executive report with scoring summary, dimension analysis, gap highlights, and strategic recommendations"
```

## Purpose

Consolidate ALL benchmark artifacts produced by the universal bench pipeline into a
single, comprehensive executive report. This is the final deliverable of any benchmark
comparison — a narrative document that synthesizes inventories, matrices, scorecards,
gap analyses, and battle cards into a cohesive story for stakeholders.

The report follows a structured format designed for executive consumption:
1. Executive Summary (5-line maximum)
2. Key Metrics at a glance
3. Scorecard summary with weighted totals
4. Per-dimension deep analysis
5. Gap highlights (top 5 per direction)
6. Strategic recommendations
7. Methodology disclosure

This task works for ANY comparison type (codebase, LLM, product, company, technology).

## Input

| Input | Type | Required | Source |
|-------|------|----------|--------|
| `subject_a` | string | YES | Pipeline param |
| `subject_b` | string | YES | Pipeline param |
| `comparison_type` | string | YES | One of: codebase, llm, product, company, technology |
| `inventory_a` | file | YES | `docs/bench/{slug}/inventory-a.json` |
| `inventory_b` | file | YES | `docs/bench/{slug}/inventory-b.json` |
| `comparison_matrix` | file | YES | `docs/bench/{slug}/comparison-matrix.json` |
| `scorecard` | file | YES | `docs/bench/{slug}/scorecard.json` |
| `gap_analysis` | file | YES | `docs/bench/{slug}/gap-analysis.json` |
| `battle_card` | file | NO | `docs/bench/{slug}/battle-card.md` |

## Output

| Output | Format | Destination |
|--------|--------|-------------|
| Executive report | Markdown | `docs/bench/{slug}/executive-report.md` |

Where `{slug}` = `{subject_a}-vs-{subject_b}` (kebab-case, lowercase).

## Prerequisites

- [ ] Inventory files exist for both subjects
- [ ] Comparison matrix exists from `bench-compare`
- [ ] Scorecard exists from `bench-score`
- [ ] Gap analysis exists from `bench-gap`
- [ ] Battle card recommended but not blocking

---

## Veto Conditions

The task MUST NOT execute (or must HALT immediately) if:

1. **Missing inventories** -- Cannot report without baseline data for both subjects.
2. **Missing comparison matrix** -- Cannot provide dimension analysis without comparison data.
3. **Missing scorecard** -- Cannot produce scorecard summary or dimension scores without scoring data.
4. **Missing gap analysis** -- Cannot highlight gaps without gap data. Run `bench-gap` first.
5. **comparison_type not recognized** -- Must be one of: codebase, llm, product, company, technology.
6. **Output file already exists and is less than 24h old** -- Do not overwrite unless `--force` specified.

---

## Autonomous Execution Protocol

This task runs WITHOUT user interaction. Load all artifacts, synthesize narrative,
and produce the executive report.

**CRITICAL RULES:**
- Every claim in the report MUST trace to a specific artifact (scorecard, matrix, gaps, inventory)
- NO invented data or inflated assessments
- Executive Summary MUST NOT exceed 5 lines
- Dimension analysis must cite actual scores and specific signals
- Gap highlights limited to top 5 per direction (by priority)
- Recommendations must be actionable and type-appropriate
- Methodology section must be transparent about data sources and confidence
- Write in a professional, objective tone appropriate for executive stakeholders

---

## Step 1: Load All Artifacts

```
ACTION: Read("docs/bench/{slug}/inventory-a.json")
STORE: inv_a

ACTION: Read("docs/bench/{slug}/inventory-b.json")
STORE: inv_b

ACTION: Read("docs/bench/{slug}/comparison-matrix.json")
STORE: matrix

ACTION: Read("docs/bench/{slug}/scorecard.json")
STORE: scorecard

ACTION: Read("docs/bench/{slug}/gap-analysis.json")
STORE: gaps

OPTIONAL:
  ACTION: Read("docs/bench/{slug}/battle-card.md")
  STORE: battle_card (or null if not found)

VALIDATE:
  - All required files loaded successfully
  - JSON files parse without errors
  - Scorecard has at least 1 dimension
  - Gap analysis has both directions populated
```

---

## Step 2: Generate Executive Summary

```
COMPOSE executive_summary (EXACTLY 5 lines or fewer):

Line 1: What was compared and why
  "This report presents a {comparison_type} benchmark comparing {subject_a} and {subject_b}."

Line 2: Overall result
  "{overall_winner} leads with a weighted score of {winner_score}/100 vs {loser_score}/100 ({delta} point margin)."

Line 3: Key strength of the winner
  "{winner}'s primary advantage is in {top_dimension} ({winner_score_dim}/100 vs {loser_score_dim}/100)."

Line 4: Key strength of the runner-up
  "{loser} competes strongly in {counter_dimension} ({loser_counter_score}/100 vs {winner_counter_score}/100)."

Line 5: Gap landscape
  "Gap analysis identifies {gaps_of_a_count} gaps for {subject_a} and {gaps_of_b_count} gaps for {subject_b}, with {p0_count} critical-priority items."

STORE: executive_summary
```

---

## Step 3: Build Key Metrics Table

```
EXTRACT key metrics from inventories and scorecard:

metrics = [
  { name: "Overall Winner", value: "{winner} by {delta} pts" },
  { name: "Dimensions Analyzed", value: "{dim_count}" },
  { name: "A Dimension Wins", value: "{a_wins} of {dim_count}" },
  { name: "B Dimension Wins", value: "{b_wins} of {dim_count}" },
  { name: "Ties", value: "{tie_count}" },
  { name: "Gaps (A)", value: "{gaps_of_a_count} ({p0_a} critical)" },
  { name: "Gaps (B)", value: "{gaps_of_b_count} ({p0_b} critical)" },
  { name: "Comparison Type", value: "{comparison_type}" },
  { name: "Confidence Level", value: "{confidence}" }
]

Type-specific additions:
  IF codebase: add "Total Components (A)", "Total Components (B)"
  IF llm: add "Model Size (A)", "Model Size (B)"
  IF product: add "Category", "Price Range"
  IF company: add "Market Segment", "Revenue Range"
  IF technology: add "Maturity Level (A)", "Maturity Level (B)"

STORE: key_metrics[]
```

---

## Step 4: Build Scorecard Summary

```
EXTRACT from scorecard:
  FOR EACH dimension:
    - name, weight, score_a, score_b, delta, winner

  SORT by weight (descending) for presentation

  COMPUTE:
    - weighted_total_a
    - weighted_total_b
    - total_delta
    - overall_winner

FORMAT as table:
  | Dimension | Weight | {SUBJECT_A} | {SUBJECT_B} | Delta | Winner |
  |-----------|--------|-------------|-------------|-------|--------|
  {rows sorted by weight}
  | **TOTAL** | 100% | **{total_a}** | **{total_b}** | **{delta}** | **{winner}** |

STORE: scorecard_summary_table
```

---

## Step 5: Generate Per-Dimension Analysis

```
FOR EACH dimension in scorecard (sorted by weight descending):

  COMPOSE analysis_section:
    ### {DIM_NAME} (Weight: {WEIGHT}%)

    **{SUBJECT_A}: {SCORE_A}/100** | **{SUBJECT_B}: {SCORE_B}/100** | Delta: {DELTA}

    {2-4 sentences analyzing this dimension}

    Key signals:
    - {signal_1}: {observation from matrix or inventory}
    - {signal_2}: {observation from matrix or inventory}
    - {signal_3}: {observation from matrix or inventory}

    {IF gap_analysis has gaps in this dimension:}
    Notable gaps in this dimension:
    - {gap_description} ({impact} impact, {priority} priority)

  RULES for analysis text:
    - MUST reference actual scores (not vague "X is better")
    - MUST cite at least 2 specific signals from matrix/inventory
    - MUST note if confidence is lower for one subject
    - If delta < 5: note that subjects are closely matched in this dimension
    - If delta > 20: note the significant gap and its primary driver

STORE: dimension_analyses[]
```

---

## Step 6: Extract Gap Highlights

```
FROM gap_analysis:

  TOP 5 gaps of Subject A (sorted by priority ASC, then impact DESC):
    FOR EACH:
      - gap_id, capability, description, impact, complexity, priority
      - related_dimension
    LIMIT: 5

  TOP 5 gaps of Subject B (sorted by priority ASC, then impact DESC):
    FOR EACH:
      - gap_id, capability, description, impact, complexity, priority
      - related_dimension
    LIMIT: 5

FORMAT each as table:
  | # | Capability | Impact | Complexity | Priority | Dimension |
  |---|-----------|--------|------------|----------|-----------|
  {top 5 rows}

STORE: gap_highlights_a, gap_highlights_b
```

---

## Step 7: Generate Strategic Recommendations

```
GENERATE recommendations (3-5 items, prioritized):

FOR subject_a:
  Based on P0/P1 gaps of A:
    recommendation = "Address {gap} to improve {dimension} score."
  Based on strongest dimensions:
    recommendation = "Leverage advantage in {dimension} for competitive positioning."

FOR subject_b:
  Based on P0/P1 gaps of B:
    recommendation = "Address {gap} to improve {dimension} score."
  Based on strongest dimensions:
    recommendation = "Leverage advantage in {dimension} for competitive positioning."

GENERAL recommendations:
  Based on overall analysis:
    recommendation = "{type-specific strategic advice}"

Type-specific recommendation patterns:
  IF codebase:
    - "Prioritize absorbing {feature} from {other} (P0, {complexity} complexity)"
    - "Maintain competitive edge in {dimension} through continued investment"
  IF llm:
    - "Capability gap in {area} limits use cases for {scenario}"
    - "Strength in {area} makes {subject} preferred for {use_case}"
  IF product:
    - "Feature gap in {area} may affect adoption in {market_segment}"
    - "Integration advantage positions {subject} well for {ecosystem}"
  IF company:
    - "Market position gap in {segment} requires strategic investment"
    - "Innovation lead in {area} provides {timeframe} competitive moat"
  IF technology:
    - "Ecosystem gap in {area} may slow adoption for {use_case}"
    - "Tooling advantage accelerates developer onboarding"

STORE: recommendations[]
```

---

## Step 8: Build Methodology Section

```
COMPOSE methodology:

  ## Methodology

  ### Data Sources
  - **{SUBJECT_A}:** {source_description from inventory metadata}
  - **{SUBJECT_B}:** {source_description from inventory metadata}

  ### Scoring Method
  - Dimension pack: {dimension_pack_name} ({dimension_count} dimensions)
  - Weights: {list dimension weights}
  - Score range: 0-100 per dimension
  - Method: {scorecard.method_description}

  ### Confidence Level
  - **{SUBJECT_A}:** {confidence_a} ({reason: e.g., "local codebase scan"})
  - **{SUBJECT_B}:** {confidence_b} ({reason: e.g., "documentation-based"})

  ### Artifacts Used
  | Artifact | File | Status |
  |----------|------|--------|
  | Inventory A | inventory-a.json | loaded |
  | Inventory B | inventory-b.json | loaded |
  | Comparison Matrix | comparison-matrix.json | loaded |
  | Scorecard | scorecard.json | loaded |
  | Gap Analysis | gap-analysis.json | loaded |
  | Battle Card | battle-card.md | {loaded | not available} |

  ### Limitations
  - {Any known limitations of the data or method}
  - {Any dimensions where confidence is particularly low}

STORE: methodology_section
```

---

## Step 9: Assemble Executive Report

```
ACTION: Write("docs/bench/{slug}/executive-report.md")

Use template: bench-report-tmpl.md

ASSEMBLE sections in order:
  1. Title & metadata header
  2. Executive Summary (from Step 2)
  3. Key Metrics table (from Step 3)
  4. Scorecard Summary table (from Step 4)
  5. Per-Dimension Analysis (from Step 5)
  6. Gap Highlights - Subject A (from Step 6)
  7. Gap Highlights - Subject B (from Step 6)
  8. Strategic Recommendations (from Step 7)
  9. Methodology (from Step 8)
  10. Appendix: Source Artifacts list
```

---

## Step 10: Validate Output

```
ACTION: Read the generated executive-report.md
VERIFY:
  - Executive Summary is <= 5 lines
  - Key Metrics table present and complete
  - Scorecard summary matches scorecard.json data
  - Every dimension has its own analysis section
  - Gap highlights show top 5 per direction maximum
  - Recommendations are actionable (not vague)
  - Methodology section is transparent
  - No remaining template placeholders
  - All markdown tables are syntactically valid
  - Document length is appropriate (target: 150-350 lines)

REPORT completion:
  - Report length: {lines} lines
  - Dimensions analyzed: {count}
  - Gap highlights: {count_a} for A, {count_b} for B
  - Recommendations: {count}
  - Overall winner: {subject} by {delta} points
  - Confidence: {level}
```

---

## Acceptance Criteria

The task is complete when ALL of the following are met:

- [ ] **AC-1:** `executive-report.md` exists at `docs/bench/{slug}/executive-report.md`
- [ ] **AC-2:** Executive Summary present and does NOT exceed 5 lines
- [ ] **AC-3:** Key Metrics table includes overall winner, dimension counts, gap counts
- [ ] **AC-4:** Scorecard Summary table matches scorecard.json data exactly
- [ ] **AC-5:** Every dimension from the scorecard has a dedicated analysis section
- [ ] **AC-6:** Each dimension analysis cites at least 2 specific signals
- [ ] **AC-7:** Gap highlights show top 5 per direction, sorted by priority
- [ ] **AC-8:** Strategic Recommendations are actionable (3-5 items)
- [ ] **AC-9:** Methodology section discloses data sources, scoring method, and confidence
- [ ] **AC-10:** No template placeholders remaining (all {VARS} resolved)
- [ ] **AC-11:** All claims traceable to specific artifacts (no invented data)
- [ ] **AC-12:** Document is professional and appropriate for executive stakeholders

## Quality Validation

After generation, validate:

- [ ] All markdown headings follow consistent hierarchy (no skipped levels)
- [ ] All tables are valid markdown tables
- [ ] Scores in report match scores in scorecard.json
- [ ] Gap counts in report match counts in gap-analysis.json
- [ ] Recommendations don't contradict the scorecard data
- [ ] Executive Summary is genuinely concise (not 5 long paragraphs)
- [ ] No broken references or placeholder text

---

## Error Handling

| Error | Detection | Recovery |
|-------|-----------|----------|
| Required artifact missing | File read fails | HALT: "Run {task} first" with specific task name |
| JSON parse error | Parse fails | Report specific file and error location |
| Scorecard has 0 dimensions | Empty dimensions array | HALT: "Scorecard is empty, re-run bench-score" |
| Gap analysis empty | Both gap lists empty | WARN: proceed with "No gaps identified" section |
| Battle card not found | File read fails | WARN: proceed without battle card reference |
| Inconsistent data | Scores don't match across artifacts | WARN: note discrepancy in methodology section |
| Report too long | Line count > 400 | Trim dimension analyses to 3 sentences each |
| Report too short | Line count < 100 | Expand dimension analyses with more signals |

## Integration

| Task | Relationship |
|------|-------------|
| `bench-inventory-type` | Upstream -- provides inventory data |
| `bench-compare` | Upstream -- provides comparison matrix |
| `bench-score` | Upstream -- provides scorecard |
| `bench-gap` | Upstream -- provides gap analysis |
| `bench-battle-card` | Upstream (optional) -- provides battle card for cross-reference |
| Pipeline orchestrator | This is the FINAL task in the benchmark pipeline |

---

_Task Version: 1.0.0_
_Pattern: HO-TP-001 (Task Anatomy Standard)_
_Created: 2026-02-17_
_Compliant: Yes_
