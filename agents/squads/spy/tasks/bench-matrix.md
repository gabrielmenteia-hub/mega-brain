# Task: Universal Comparison Matrix

## Task Anatomy

| Field | Value |
|-------|-------|
| **Task ID** | `bench-matrix` |
| **Version** | `1.0.0` |
| **Status** | `active` |
| **Responsible Executor** | `bench-analyst` |
| **Execution Type** | `Agent` |
| **Estimated Duration** | `5-10min` |

## Metadata
```yaml
id: bench-matrix
name: "Universal Comparison Matrix"
category: benchmark-core
agent: bench-analyst
elicit: false
autonomous: true
estimated_duration: "5-10min"
description: "Build feature/capability comparison matrix between two subjects based on their inventories and comparison type"
```

## Purpose

Produce a structured comparison matrix between two inventoried subjects.
The matrix maps every significant element from Subject A to its equivalent
(or lack thereof) in Subject B, using the universal 3-level equivalence system:
**Forte / Parcial / Sem Equivalente**.

This task is **type-aware** — the structure and content of the matrix changes
based on `comparison_type`.

## Autonomous Execution Protocol

This task runs WITHOUT user interaction. It consumes the inventory outputs
from two `bench-inventory` runs and produces comparison matrices.

---

## Prerequisites

- [ ] `inventory-{subject_a_slug}.json` exists in `{output_dir}`
- [ ] `inventory-{subject_b_slug}.json` exists in `{output_dir}`
- [ ] Comparison type determined (from `bench-detect.md`)
- [ ] Dimensions loaded (from `bench-dimension-packs.yaml`)

## Inputs

```yaml
inputs:
  inventory_a:
    type: object
    required: true
    description: "Parsed inventory JSON for Subject A"

  inventory_b:
    type: object
    required: true
    description: "Parsed inventory JSON for Subject B"

  comparison_type:
    type: enum
    required: true
    values: [codebase, llm, product, company, technology]

  dimensions:
    type: array
    required: true
    description: "Dimension pack for the comparison type"

  output_dir:
    type: string
    required: true
    description: "Output directory for matrix files"
```

---

## Step 1: Load and Validate Inventories

```
ACTION: Read("{output_dir}/inventory-{subject_a_slug}.json")
STORE: inv_a = parsed JSON

ACTION: Read("{output_dir}/inventory-{subject_b_slug}.json")
STORE: inv_b = parsed JSON

VALIDATE:
  - inv_a.comparison_type == inv_b.comparison_type == comparison_type
  - Both inventories have non-empty data for their type

FAIL_CONDITION: Type mismatch → HALT. Cannot compare inventories of different types.
```

---

## Step 2: Route by Comparison Type

```
ROUTE:
  codebase  → Execute Step 3A (Codebase Matrix)
  llm       → Execute Step 3B (LLM Matrix)
  product   → Execute Step 3C (Product Matrix)
  company   → Execute Step 3D (Company Matrix)
  technology → Execute Step 3E (Technology Matrix)
```

---

## Step 3A: Codebase Comparison Matrix

### 3A.1: Agent Matrix

For each agent in `inv_a.agents[]`, find best match in `inv_b.agents[]`:

```
ALGORITHM:
  1. Exact id match → Forte candidate (verify with command overlap)
  2. Role/title similarity match → Forte candidate
  3. Command overlap > 60% → Parcial candidate
  4. No match → Sem Equivalente

SCORING (Paridade 1-5):
  5/5: Same id/role + command overlap > 80%
  4/5: Same role + command overlap > 60%
  3/5: Similar role + command overlap > 40%
  2/5: Weak similarity, different scope
  1/5: No meaningful equivalent

STORE in agent_matrix[]:
  {
    "subject_a_agent": "<id>",
    "subject_b_agent": "<id or 'none'>",
    "equivalence": "Forte|Parcial|Sem Equivalente",
    "paridade": <1-5>,
    "delta": "<specific differences>"
  }
```

ALSO run reverse: for each agent in `inv_b` not yet matched, record as gap.

### 3A.2: Workflow Matrix

Same algorithm as agents, but for workflows:

```
ALGORITHM:
  1. Name/type match → Forte candidate
  2. Purpose match by step analysis → Parcial candidate
  3. No match → Sem Equivalente

STORE in workflow_matrix[]:
  {
    "subject_a_workflow": "<id>",
    "subject_b_workflow": "<id or 'none'>",
    "equivalence": "Forte|Parcial|Sem Equivalente",
    "paridade": <1-5>,
    "a_steps": <count>,
    "b_steps": <count>,
    "delta": "<specific differences>"
  }
```

### 3A.3: Structural Comparison

```
STORE in structural_comparison:
  {
    "metric": ["agents", "commands", "workflows", "tasks", "templates", "rules"],
    "subject_a": [count_a for each],
    "subject_b": [count_b for each],
    "delta": [a - b for each]
  }
```

---

## Step 3B: LLM Comparison Matrix

### 3B.1: Specifications Matrix

```
STORE in specs_matrix[]:
  - context_window: { a_value, b_value, advantage }
  - max_output: { a_value, b_value, advantage }
  - pricing_input: { a_value, b_value, advantage }
  - pricing_output: { a_value, b_value, advantage }
  - training_cutoff: { a_value, b_value, advantage }
```

### 3B.2: Benchmark Scores Matrix

```
For EACH benchmark present in BOTH inventories:
STORE in benchmarks_matrix[]:
  {
    "benchmark": "<name>",
    "subject_a_score": <score or null>,
    "subject_b_score": <score or null>,
    "delta": <a - b or "N/A">,
    "advantage": "A|B|TIE|UNKNOWN"
  }
```

### 3B.3: Capabilities Matrix

```
For EACH capability (vision, audio, tools, structured_output, streaming):
STORE in capabilities_matrix[]:
  {
    "capability": "<name>",
    "subject_a": <true|false|"unknown">,
    "subject_b": <true|false|"unknown">,
    "equivalence": "Forte|Parcial|Sem Equivalente"
  }
```

---

## Step 3C: Product Comparison Matrix

### 3C.1: Feature Matrix

```
ACTION: Build unified feature list from both inventories
For EACH feature category:
  For EACH feature:
    STORE:
      {
        "category": "<category>",
        "feature": "<name>",
        "subject_a": "Yes|No|Partial|Unknown",
        "subject_b": "Yes|No|Partial|Unknown",
        "notes": "<differences>"
      }
```

### 3C.2: Pricing Matrix

```
ACTION: Align pricing tiers by closest match
For EACH tier pair:
  STORE:
    {
      "tier_a": "<name>",
      "tier_b": "<name>",
      "price_a_monthly": <amount>,
      "price_b_monthly": <amount>,
      "delta": "<a - b>",
      "value_assessment": "<which offers more for the price>"
    }
```

### 3C.3: Integration Matrix

```
STORE:
  {
    "total_a": <count>,
    "total_b": <count>,
    "shared_integrations": [list],
    "a_only": [list],
    "b_only": [list]
  }
```

---

## Step 3D: Company Comparison Matrix

### 3D.1: Profile Matrix

```
STORE in profile_matrix:
  - founded: { a, b }
  - employees: { a, b, delta }
  - headquarters: { a, b }
  - funding: { a, b, delta }
  - valuation: { a, b, delta }
```

### 3D.2: Product Portfolio Matrix

```
For EACH product from either company:
  STORE:
    {
      "product": "<name>",
      "company_a": "Yes|No|Similar (<name>)",
      "company_b": "Yes|No|Similar (<name>)",
      "notes": "<competitive positioning>"
    }
```

### 3D.3: Market Position Matrix

```
STORE:
  {
    "dimension": ["market share", "brand recognition", "growth rate", "innovation"],
    "subject_a": [assessment for each],
    "subject_b": [assessment for each],
    "advantage": [A|B|TIE for each]
  }
```

---

## Step 3E: Technology Comparison Matrix

### 3E.1: Specifications Matrix

```
STORE in specs_matrix:
  - version: { a, b }
  - initial_release: { a, b }
  - license: { a, b }
  - language: { a, b }
  - paradigm: { a, b }
```

### 3E.2: Ecosystem Matrix

```
STORE:
  - package_count: { a, b, delta }
  - github_stars: { a, b, delta }
  - contributors: { a, b, delta }
  - notable_packages_overlap: [shared]
  - a_only_notable: [list]
  - b_only_notable: [list]
```

### 3E.3: Community and Adoption Matrix

```
STORE:
  - stackoverflow_questions: { a, b, delta }
  - npm_downloads: { a, b, delta }  (if applicable)
  - job_postings: { a, b, delta }
  - notable_adopters_a: [list]
  - notable_adopters_b: [list]
```

---

## Step 4: Compute Summary Statistics

```
ACTION: Count equivalence distribution across all matrix entries

STORE: summary = {
  "total_comparisons": <count>,
  "forte_count": <count>,
  "parcial_count": <count>,
  "sem_equivalente_count": <count>,
  "subject_a_advantages": [list of areas where A leads],
  "subject_b_advantages": [list of areas where B leads],
  "tied_areas": [list of areas with no clear advantage]
}
```

---

## Step 5: Identify Gaps (Bidirectional)

```
ACTION: From matrix data, extract:

STORE: gaps_a = {
  "description": "Things Subject A has that Subject B lacks",
  "items": [
    { "item": "<name>", "category": "<category>", "impact": "HIGH|MEDIUM|LOW" }
  ]
}

STORE: gaps_b = {
  "description": "Things Subject B has that Subject A lacks",
  "items": [
    { "item": "<name>", "category": "<category>", "impact": "HIGH|MEDIUM|LOW" }
  ]
}
```

---

## Step 6: Write Outputs

### 6.1: JSON Output

```
ACTION: Compile all matrices into single JSON:

STORE: matrix_output = {
  "subject_a": subject_a_name,
  "subject_b": subject_b_name,
  "comparison_type": comparison_type,
  "generatedAt": "<ISO-8601>",
  "matrices": { <type-specific matrices from Step 3> },
  "summary": summary,
  "gaps": { "a_advantages": gaps_a, "b_advantages": gaps_b }
}

ACTION: Write("{output_dir}/comparison-matrix.json", JSON.stringify(matrix_output, null, 2))
```

### 6.2: Markdown Output

```
ACTION: Render matrix as Markdown document:

# {Subject A} vs {Subject B} — Comparison Matrix

**Type:** {comparison_type}
**Generated:** {ISO-8601}

## Summary

| Metric | Value |
|--------|-------|
| Total comparisons | {count} |
| Forte equivalence | {count} ({percentage}%) |
| Parcial equivalence | {count} ({percentage}%) |
| Sem equivalente | {count} ({percentage}%) |

## {Type-Specific Matrix Tables}

{Rendered tables from Step 3, using markdown table format}

## Gaps: {Subject A} Advantages
{Items from gaps_a}

## Gaps: {Subject B} Advantages
{Items from gaps_b}

## Objective Reading
{3-5 bullet points, brutally honest assessment}

ACTION: Write("{output_dir}/comparison-matrix.md", rendered_markdown)
```

---

## Outputs

| File | Location | Format |
|------|----------|--------|
| Comparison matrix (JSON) | `{output_dir}/comparison-matrix.json` | JSON |
| Comparison matrix (MD) | `{output_dir}/comparison-matrix.md` | Markdown |

---

## Veto Conditions

The task MUST HALT if:

1. **Missing inventory** — Either `inventory-{subject_a}.json` or `inventory-{subject_b}.json` does not exist or is empty.
2. **Type mismatch** — Inventories have different `comparison_type` values. Cannot cross-compare a codebase against an LLM.
3. **Empty inventories** — Both inventories contain zero data points. Nothing to compare.
4. **Invalid dimensions** — Dimension pack not loaded or empty for the comparison type.

---

## Verification

- [ ] JSON output is valid (parseable)
- [ ] Markdown tables render correctly (consistent column counts)
- [ ] Every element from Subject A inventory appears in the matrix (100% coverage)
- [ ] Every element from Subject B inventory appears in the matrix (100% coverage)
- [ ] Equivalence levels use standard vocabulary: Forte / Parcial / Sem Equivalente
- [ ] Paridade scores (where used) are 1-5 with justification
- [ ] Bidirectional gaps documented (both A advantages and B advantages)
- [ ] Summary statistics are mathematically correct
- [ ] No invented data — every claim traces to inventory source
- [ ] Sources cited for every data point derived from web research
