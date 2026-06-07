# Task: Full Framework Benchmark

## Task Anatomy

| Field | Value |
|-------|-------|
| **Task ID** | `bench-framework` |
| **Version** | `1.1.0` |
| **Status** | `pending` |
| **Responsible Executor** | `bench-analyst` |
| **Execution Type** | `Agent` |
| **Model** | `claude-sonnet-4-20250514` |
| **Haiku Eligible** | `false` |
| **Estimated Duration** | `30-60min` |

## Metadata
```yaml
id: bench-framework
name: "Full Framework Benchmark"
category: benchmark
agent: bench-analyst
elicit: true
estimated_duration: "30-60min"
description: "Complete competitive benchmark pipeline: inventory, recon, compare, score, analyze, report"
```

## Purpose

Execute the full benchmark pipeline against a competing AI orchestration framework.
Produces all standard benchmark artifacts (JSON + MD) in `docs/bench/{competitor}/`.

## Prerequisites

- [ ] Competitor identified (name, repo URL or docs URL)
- [ ] At least ONE data source available (repo, docs, or web)
- [ ] AIOX local codebase accessible for self-inventory

## Inputs

```yaml
inputs:
  competitor_name:
    type: string
    required: true
    description: "Competitor identifier (e.g., 'bmad', 'pai', 'cursor-rules')"
    elicit: true
    prompt: "Which framework do you want to benchmark against?"

  competitor_sources:
    type: object
    required: true
    description: "Data sources for competitor analysis"
    elicit: true
    prompt: "What sources should I use?"
    properties:
      repo_url:
        type: string
        description: "GitHub repository URL"
      docs_url:
        type: string
        description: "Documentation URL (or llms-full.txt)"
      local_path:
        type: string
        description: "Path to cloned repo (if available locally)"

  scenarios:
    type: array
    required: false
    default: ["greenfield-fullstack", "brownfield-fullstack"]
    description: "Workflow scenarios to benchmark"
    elicit: true
    prompt: "Which scenarios? (default: greenfield + brownfield fullstack)"

  include_absorption:
    type: boolean
    default: true
    description: "Generate feature absorption roadmap?"
```

## Pipeline

### Phase 1: AIOX Self-Inventory (5min)

**Goal:** Snapshot current AIOX state for baseline comparison.

**Steps:**
1. Scan `.aiox-core/development/agents/*.md`:
   - Extract: id, title, commands (name + count), tier, whenToUse
   - Count total agents, total commands
2. Scan `.aiox-core/development/workflows/*.yaml`:
   - Extract: id, phases, agents involved, steps count
   - Count total workflows, total steps
3. Scan `.aiox-core/development/tasks/*.md`:
   - Extract: id, category, agent, elicit flag
   - Count total tasks
4. Scan `squads/`:
   - List all squads with agent/task counts

**Output:**
- `docs/bench/{competitor}/appendix-aiox-agent-command-inventory.json`
- `docs/bench/{competitor}/appendix-aiox-workflow-sequence-inventory.json`

### Phase 2: Competitor Recon (10min)

**Goal:** Extract competitor structure from LOCAL filesystem analysis.

**CRITICAL RULE: ALWAYS CLONE LOCALLY**

Every benchmark MUST work from a locally cloned repository. Never estimate, infer, or guess
competitor data from documentation alone. The clone provides ground truth.

```
STEP 2.0: Ensure local clone exists

IF local_path provided AND exists:
  ACTION: Verify path exists via Bash("ls {local_path}")
  STORE: competitor_root = local_path

ELSE IF repo_url provided:
  ACTION: Bash("git clone {repo_url} ../bench/{competitor_name}")
  STORE: competitor_root = ../bench/{competitor_name}
  NOTE: Clone goes to ../bench/ OUTSIDE the project directory

ELSE:
  HALT: "Cannot benchmark without local repository. Provide repo_url or local_path."
```

**Steps (ALL from local filesystem):**
1. **Discover structure:**
   ```
   ACTION: Bash("find {competitor_root} -type f -name '*.md' -o -name '*.yaml' -o -name '*.ts' -o -name '*.js' | head -300")
   ACTION: Bash("ls -la {competitor_root}/.claude/ 2>/dev/null || ls -la {competitor_root}/")
   IDENTIFY: Where agents, workflows, skills, hooks, tools live
   ```

2. **Scan agent definitions:**
   ```
   ACTION: Glob("{competitor_root}/**/agents/*.md")
   For EACH: Read(file, limit=80) → extract name, role, commands
   COUNT: total agents, total commands per agent
   ```

3. **Scan workflows/skills:**
   ```
   ACTION: Glob("{competitor_root}/**/workflows/*.md") + Glob("{competitor_root}/**/skills/*/SKILL.md")
   For EACH skill dir: count .md files, count .ts files
   COUNT: total workflows, total skills
   ```

4. **Scan hooks/lifecycle:**
   ```
   ACTION: Glob("{competitor_root}/**/hooks/*.ts") + Glob("{competitor_root}/**/hooks/*.hook.ts")
   For EACH: Read first 20 lines → extract hook name, event trigger
   COUNT: total hooks by event type
   ```

5. **Scan tools/scripts:**
   ```
   ACTION: Glob("{competitor_root}/**/*.ts") → count
   ACTION: Glob("{competitor_root}/**/*.js") → count
   ```

6. **Count everything:**
   ```
   All counts MUST come from Glob/Bash on LOCAL files.
   NEVER estimate. If a file can't be read, report "unreadable" not an estimate.
   ```

**Output:**
- `docs/bench/{competitor}/appendix-exhaustive-agents-workflows-raw.json`

### Phase 3: Comparative Matrices (10min)

**Goal:** Build 1:1 mappings between AIOX and competitor.

**Steps:**
1. **Agent Matrix:**
   - Map each competitor agent to AIOX equivalent
   - Classify: Forte / Parcial / Sem equivalente
   - Note key differences for each mapping
   - Identify AIOX agents without competitor equivalent (differentials)
   - Identify competitor agents without AIOX equivalent (gaps)

2. **Command Matrix:**
   - Map competitor commands to AIOX commands
   - Group by agent
   - Note coverage percentage

3. **Workflow Matrix:**
   - Map competitor workflows to AIOX workflows
   - Compare step counts, agent involvement, decision points
   - Note structural differences

**Output:**
- `docs/bench/{competitor}/{competitor}-vs-aiox-agents-command-matrix.md`
- `docs/bench/{competitor}/{competitor}-vs-aiox-workflow-step-matrix.md`
- `docs/bench/{competitor}/{competitor}-vs-aiox-comparativo-completo.md`

### Phase 4: Quantitative Scoring (5min)

**Goal:** Score both frameworks on 5 standardized axes per scenario.

**Steps:**
1. For each scenario in `scenarios`:
   - Count structural metrics (steps, agents, decision points, gate files, validation files)
   - Score each axis 0-100 based on observable signals
   - Calculate delta (AIOX - Competitor)
2. Document scoring method and signals used
3. Note confidence level for competitor scores (executed vs baseline)

**Scoring Rules:**
- If competitor was executed locally: label "installed benchmark"
- If competitor from docs only: label "baseline benchmark"
- Always disclose method in output

**Output:**
- `docs/bench/{competitor}/benchmark-aiox-vs-{competitor}-scenarios.json`
- `docs/bench/{competitor}/benchmark-aiox-vs-{competitor}-scenarios.md`

### Phase 5: Gap Analysis & Absorption (10min)

**Goal:** Identify what AIOX should absorb from competitor.

**Steps:**
1. **Gap Identification:**
   - List competitor features without AIOX equivalent
   - Classify by category (agent, workflow, task, tooling, governance)
   - Assess impact (HIGH/MEDIUM/LOW)

2. **Feature Absorption Analysis:**
   - For each gap, assess:
     - Technical description (what it does)
     - Value for AIOX (why it matters)
     - Implementation complexity (LOW/MEDIUM/HIGH)
     - Priority (P0/P1/P2/P3)
   - Generate prioritized roadmap

3. **Gap Closure Backlog:**
   - Create executable backlog items
   - Each item has: title, description, category, priority, estimated effort

**Output:**
- `docs/bench/{competitor}/{competitor}-features-para-aiox.md`
- `docs/bench/{competitor}/roadmap-{competitor}-features-para-aiox.md`
- `docs/bench/{competitor}/aiox-gap-closure-backlog-executable.json`
- `docs/bench/{competitor}/aiox-gap-closure-backlog-executable.md`

### Phase 6: Deep Analysis Artifacts (10min)

**Goal:** Produce traceability and migration artifacts.

**Steps:**
1. **Traceability Map (AIOX):**
   - Map each AIOX command to its executing task
   - Map each task to its output artifacts
   - Assign confidence score (high/medium/low)
   - Identify unmapped commands (gaps)

2. **Migration Playbook:**
   - For users coming FROM competitor TO AIOX
   - Map each competitor concept to AIOX equivalent
   - Step-by-step migration guide
   - Common pitfalls and solutions

3. **Exhaustive Comparison:**
   - Combined agent + workflow + task comparison
   - Full detail, no summarization

**Output:**
- `docs/bench/{competitor}/aiox-command-task-artifact-traceability-deep.md`
- `docs/bench/{competitor}/appendix-command-task-artifact-traceability.json`
- `docs/bench/{competitor}/{competitor}-to-aiox-migration-playbook-deep.md`
- `docs/bench/{competitor}/comparacao-exaustiva-agentes-workflows-tasks.md`

## Output Summary

After full pipeline execution, the following artifacts exist in `docs/bench/{competitor}/`:

| # | File | Type | Format |
|---|------|------|--------|
| 1 | `appendix-aiox-agent-command-inventory.json` | Inventory | JSON |
| 2 | `appendix-aiox-workflow-sequence-inventory.json` | Inventory | JSON |
| 3 | `appendix-exhaustive-agents-workflows-raw.json` | Recon | JSON |
| 4 | `{competitor}-vs-aiox-agents-command-matrix.md` | Matrix | MD |
| 5 | `{competitor}-vs-aiox-workflow-step-matrix.md` | Matrix | MD |
| 6 | `{competitor}-vs-aiox-comparativo-completo.md` | Comparison | MD |
| 7 | `benchmark-aiox-vs-{competitor}-scenarios.json` | Benchmark | JSON |
| 8 | `benchmark-aiox-vs-{competitor}-scenarios.md` | Benchmark | MD |
| 9 | `{competitor}-features-para-aiox.md` | Absorption | MD |
| 10 | `roadmap-{competitor}-features-para-aiox.md` | Roadmap | MD |
| 11 | `aiox-gap-closure-backlog-executable.json` | Backlog | JSON |
| 12 | `aiox-gap-closure-backlog-executable.md` | Backlog | MD |
| 13 | `aiox-command-task-artifact-traceability-deep.md` | Traceability | MD |
| 14 | `appendix-command-task-artifact-traceability.json` | Traceability | JSON |
| 15 | `{competitor}-to-aiox-migration-playbook-deep.md` | Migration | MD |
| 16 | `comparacao-exaustiva-agentes-workflows-tasks.md` | Exhaustive | MD |

## Veto Conditions

The pipeline MUST NOT execute (or must HALT at the failing phase) if:

1. **No competitor identified** -- `competitor_name` is empty or not provided. Cannot run any phase without a target.
2. **Zero data sources available** -- No `repo_url`, `docs_url`, or `local_path` provided. At least ONE source is mandatory for recon.
3. **AIOX codebase not accessible** -- `.aiox-core/development/agents/` directory missing or empty. Self-inventory (Phase 1) would produce empty baseline.
4. **Phase 1 produces zero agents** -- If AIOX self-scan finds 0 agents, the comparison baseline is corrupt. HALT and investigate.
5. **Phase 2 produces zero competitor data** -- If all recon methods fail and no competitor structure is extracted, subsequent phases have nothing to compare against.

## Acceptance Criteria

The task is complete when ALL of the following are met:

- [ ] **AC-1:** All 16 output files listed in Output Summary exist in `docs/bench/{competitor}/`
- [ ] **AC-2:** All JSON files are valid (parseable without errors)
- [ ] **AC-3:** All MD files have consistent heading hierarchy (no skipped levels)
- [ ] **AC-4:** Agent command matrix covers 100% of detected agents from both frameworks
- [ ] **AC-5:** Workflow matrix covers 100% of detected workflows from both frameworks
- [ ] **AC-6:** Quantitative scoring discloses method (installed vs baseline benchmark)
- [ ] **AC-7:** Confidence level noted for every competitor data point derived from docs-only
- [ ] **AC-8:** Gap analysis includes both AIOX gaps AND AIOX differentials
- [ ] **AC-9:** Feature absorption roadmap has priority (P0-P3) for every item
- [ ] **AC-10:** No invented data or inflated scores -- all claims cite source
- [ ] **AC-11:** Artifacts follow naming pattern consistent with existing benchmarks in `docs/bench/`
- [ ] **AC-12:** Final validation passes `bench-quality-checklist.md` (if available)

## Quality Criteria

- [ ] All JSON files are valid and parseable
- [ ] All MD files follow consistent heading structure
- [ ] Scoring method disclosed in benchmark reports
- [ ] Confidence level noted for competitor data
- [ ] Sources cited for every claim
- [ ] No invented data or inflated scores
- [ ] Both AIOX gaps AND differentials documented
- [ ] Artifacts match the naming pattern from reference benchmarks in `docs/bench/`
