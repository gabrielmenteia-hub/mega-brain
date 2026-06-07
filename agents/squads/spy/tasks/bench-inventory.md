# Task: Universal Subject Inventory (Autonomous)

## Task Anatomy

| Field | Value |
|-------|-------|
| **Task ID** | `bench-inventory` |
| **Version** | `2.0.0` |
| **Status** | `active` |
| **Responsible Executor** | `bench-analyst` |
| **Execution Type** | `Agent` |
| **Estimated Duration** | `3-8min` |

## Metadata
```yaml
id: bench-inventory
name: "Universal Subject Inventory"
category: benchmark-core
agent: bench-analyst
elicit: false
autonomous: true
estimated_duration: "3-8min"
description: "Autonomous inventory scan of any subject based on comparison type. Produces machine-readable inventory used as input for matrix and scoring phases."
```

## Purpose

Scan and inventory a single subject based on its comparison type.
Produces structured JSON and Markdown inventories used as baseline for all
subsequent benchmark phases (matrix, scoring, gap analysis).

This task is **type-aware** — behavior changes based on `comparison_type` from
the detection phase (`bench-detect.md`).

## Autonomous Execution Protocol

This task runs WITHOUT user interaction. Execute all steps sequentially,
collect data using the appropriate methods for the comparison type,
generate outputs, report completion.

---

## Prerequisites

- [ ] Subject identified (name, URL, path, or identifier)
- [ ] Comparison type determined (from `bench-detect.md` or explicit input)
- [ ] Data source config available (from `bench-data-sources.yaml`)

## Inputs

```yaml
inputs:
  subject_name:
    type: string
    required: true
    description: "Subject identifier (name, URL, or path)"

  comparison_type:
    type: enum
    required: true
    values: [codebase, llm, product, company, technology]
    description: "Comparison type from bench-detect phase"

  data_source_config:
    type: object
    required: true
    description: "Data source strategy from bench-data-sources.yaml"

  output_dir:
    type: string
    required: true
    description: "Output directory for inventory files"
```

---

## Step 1: Route by Comparison Type

```
ACTION: Read comparison_type
ROUTE:
  codebase  → Execute Steps 2A-7A (Codebase Inventory)
  llm       → Execute Steps 2B-7B (LLM Inventory)
  product   → Execute Steps 2C-7C (Product Inventory)
  company   → Execute Steps 2D-7D (Company Inventory)
  technology → Execute Steps 2E-7E (Technology Inventory)
```

FAIL_CONDITION: Unknown comparison_type → HALT with error.

---

# TYPE A: CODEBASE INVENTORY

## Step 2A: Ensure Local Clone

```
IF subject_name is a local path AND path exists:
  ACTION: Bash("ls {subject_name}")
  STORE: subject_root = subject_name

ELSE IF subject_name is a GitHub URL:
  ACTION: Bash("git clone {subject_name} .bench-repos/{slug}")
  STORE: subject_root = .bench-repos/{slug}

ELSE IF subject_name is a known AIOX self-reference ("aiox", "self", "."):
  STORE: subject_root = "." (current project root)

ELSE:
  HALT: "Cannot inventory codebase without local path or repo URL."
```

## Step 3A: Scan Agent Definitions

```
ACTION: Glob("{subject_root}/**/agents/*.md")
STORE: agent_files[]
```

If agent files found, for EACH file in `agent_files[]`:

```
ACTION: Read(file_path, limit=80)
EXTRACT from YAML block:
  - agent.id (or filename without extension)
  - agent.name
  - agent.title
  - agent.tier (if present)
  - commands[] → count and list command names
  - dependencies.tasks[] → list (if present)

STORE in agents_inventory[]:
  {
    "id": "<agent.id>",
    "name": "<agent.name>",
    "title": "<agent.title>",
    "tier": "<agent.tier>",
    "commands": ["cmd1", "cmd2", ...],
    "command_count": <number>,
    "dependencies": { "tasks": [...] },
    "source_file": "<relative path>"
  }
```

## Step 4A: Scan Workflow Definitions

```
ACTION: Glob("{subject_root}/**/workflows/*.yaml") + Glob("{subject_root}/**/workflows/*.md")
STORE: workflow_files[]
```

For EACH file in `workflow_files[]`:

```
ACTION: Read(file_path, limit=100)
EXTRACT:
  - workflow.id (or filename)
  - workflow.name
  - workflow.type (if present)
  - phases/steps count
  - agents involved (unique list)

STORE in workflows_inventory[]:
  {
    "id": "<workflow.id>",
    "name": "<workflow.name>",
    "type": "<workflow.type>",
    "total_steps": <number>,
    "agents_involved": ["agent1", "agent2"],
    "source_file": "<relative path>"
  }
```

## Step 5A: Scan Tasks and Additional Structure

```
ACTION: Glob("{subject_root}/**/tasks/*.md")
STORE: task_files[]
METRIC: total_tasks = task_files.length

ACTION: Glob("{subject_root}/**/templates/*.md")
METRIC: total_templates = count

ACTION: Glob("{subject_root}/**/checklists/*.md")
METRIC: total_checklists = count

ACTION: Glob("{subject_root}/**/rules/*.md")
METRIC: total_rules = count
```

For a SAMPLE of up to 10 tasks (first 10 alphabetically):

```
ACTION: Read(file_path, limit=30)
EXTRACT: id, category, agent, elicit (from metadata block)
```

Build category distribution.

## Step 6A: Scan Squads/Extensions (if applicable)

```
ACTION: Glob("{subject_root}/squads/*/config.yaml") OR Glob("{subject_root}/squads/*/squad.yaml")
STORE: squad_files[]

For EACH squad:
  ACTION: Glob("{subject_root}/squads/{name}/agents/*.md") → agent_count
  ACTION: Glob("{subject_root}/squads/{name}/tasks/*.md") → task_count
  ACTION: Glob("{subject_root}/squads/{name}/workflows/*.yaml") → workflow_count
```

## Step 7A: Compile Codebase Inventory

```
STORE: inventory = {
  "subject": subject_name,
  "comparison_type": "codebase",
  "generatedAt": "<ISO-8601>",
  "method": "autonomous-filesystem-scan",
  "root": subject_root,
  "totals": {
    "agents": agents_inventory.length,
    "total_commands": sum(agent.command_count),
    "workflows": workflows_inventory.length,
    "total_workflow_steps": sum(workflow.total_steps),
    "tasks": total_tasks,
    "templates": total_templates,
    "checklists": total_checklists,
    "rules": total_rules,
    "squads": squad_files.length
  },
  "agents": agents_inventory[],
  "workflows": workflows_inventory[],
  "task_distribution": { by_category },
  "squads": squads_inventory[]
}
```

GOTO: Write Outputs

---

# TYPE B: LLM INVENTORY

## Step 2B: Identify LLM

```
ACTION: Normalize subject_name to canonical model identifier
STORE: model_id = normalized name (e.g., "claude-3.5-sonnet", "gpt-4o")
STORE: provider = inferred provider (e.g., "Anthropic", "OpenAI", "Google", "Meta")
```

## Step 3B: Collect Specifications via Web

```
ACTION: WebSearch("{model_id} specifications parameters context window pricing {current_year}")
EXTRACT:
  - parameter_count (if public)
  - context_window (tokens)
  - max_output_tokens
  - training_cutoff
  - release_date
  - pricing_input ($/MTok)
  - pricing_output ($/MTok)

STORE: specs = { parameter_count, context_window, max_output, training_cutoff, release_date, pricing }
```

## Step 4B: Collect Benchmark Scores

```
ACTION: WebSearch("{model_id} benchmark scores MMLU HumanEval SWE-bench {current_year}")
EXTRACT per benchmark:
  - benchmark_name
  - score
  - source_url
  - date_reported

STORE: benchmarks[] = [
  { "name": "MMLU", "score": 88.7, "source": "url", "date": "2025-03" },
  ...
]
```

Note: Only record scores with verifiable sources. Mark unverifiable as `null`.

## Step 5B: Collect Capabilities

```
ACTION: WebSearch("{model_id} capabilities features multimodal tool-use {current_year}")
EXTRACT:
  - supports_vision: boolean
  - supports_audio: boolean
  - supports_tools: boolean
  - supports_structured_output: boolean
  - supports_streaming: boolean
  - api_available: boolean

STORE: capabilities = { ... }
```

## Step 6B: Collect Availability

```
ACTION: WebSearch("{model_id} API availability regions rate limits")
EXTRACT:
  - api_endpoint (if public)
  - rate_limits (RPM, TPM)
  - regions
  - access_type (public/waitlist/enterprise)

STORE: availability = { ... }
```

## Step 7B: Compile LLM Inventory

```
STORE: inventory = {
  "subject": subject_name,
  "comparison_type": "llm",
  "generatedAt": "<ISO-8601>",
  "method": "web-research",
  "model_id": model_id,
  "provider": provider,
  "specs": specs,
  "benchmarks": benchmarks[],
  "capabilities": capabilities,
  "availability": availability,
  "sources_consulted": [list of URLs used]
}
```

GOTO: Write Outputs

---

# TYPE C: PRODUCT INVENTORY

## Step 2C: Identify Product

```
ACTION: Normalize subject_name to product identifier
STORE: product_name = normalized
STORE: product_url = inferred or provided URL
```

## Step 3C: Collect Core Features

```
ACTION: WebSearch("{product_name} features capabilities {current_year}")
ACTION: WebFetch("{product_url}/features" OR "{product_url}", "Extract complete feature list")
EXTRACT:
  - feature_categories[] (groupings)
  - features[] per category (name, description, tier)

STORE: features = { categories: [...], total_count: N }
```

## Step 4C: Collect Pricing

```
ACTION: WebSearch("{product_name} pricing plans {current_year}")
ACTION: WebFetch("{product_url}/pricing", "Extract all pricing tiers, prices, and included features")
EXTRACT:
  - plans[] (name, price_monthly, price_annual, key_features, limits)
  - free_tier: boolean
  - enterprise_custom: boolean

STORE: pricing = { plans: [...], free_tier, enterprise_custom }
```

## Step 5C: Collect Integrations

```
ACTION: WebSearch("{product_name} integrations API marketplace plugins")
EXTRACT:
  - integration_count
  - api_available: boolean
  - webhook_support: boolean
  - marketplace: boolean
  - notable_integrations[]

STORE: integrations = { ... }
```

## Step 6C: Collect Reviews and Ratings

```
ACTION: WebSearch("{product_name} G2 review rating {current_year}")
EXTRACT:
  - g2_rating (if available)
  - capterra_rating (if available)
  - review_count
  - notable_pros[]
  - notable_cons[]

STORE: reviews = { ... }
```

## Step 7C: Compile Product Inventory

```
STORE: inventory = {
  "subject": subject_name,
  "comparison_type": "product",
  "generatedAt": "<ISO-8601>",
  "method": "web-research",
  "product_name": product_name,
  "product_url": product_url,
  "features": features,
  "pricing": pricing,
  "integrations": integrations,
  "reviews": reviews,
  "sources_consulted": [list of URLs used]
}
```

GOTO: Write Outputs

---

# TYPE D: COMPANY INVENTORY

## Step 2D: Identify Company

```
ACTION: Normalize subject_name to company identifier
STORE: company_name = normalized
STORE: company_url = inferred or provided URL
```

## Step 3D: Collect Company Profile

```
ACTION: WebSearch("{company_name} company profile founded employees headquarters")
EXTRACT:
  - founded_year
  - headquarters
  - employee_count (approximate)
  - ceo / leadership
  - industry
  - description

STORE: profile = { ... }
```

## Step 4D: Collect Financial Data

```
ACTION: WebSearch("{company_name} funding revenue valuation {current_year}")
EXTRACT:
  - total_funding (if public)
  - last_round (type, amount, date)
  - valuation (if public)
  - revenue_estimate (if public)
  - public_traded: boolean
  - ticker (if public)

STORE: financials = { ... }
NOTE: Mark every value with confidence (verified/estimated/unknown)
```

## Step 5D: Collect Products and Market

```
ACTION: WebSearch("{company_name} products market share customers")
EXTRACT:
  - products[] (name, category, description)
  - market_position (leader/challenger/niche)
  - notable_customers[] (if public)
  - customer_count_estimate

STORE: market = { ... }
```

## Step 6D: Collect Recent News

```
ACTION: WebSearch("{company_name} news announcements {current_year}")
EXTRACT:
  - recent_news[] (title, date, source_url, summary)
  - Limit to 5 most recent/relevant items

STORE: news = { items: [...] }
```

## Step 7D: Compile Company Inventory

```
STORE: inventory = {
  "subject": subject_name,
  "comparison_type": "company",
  "generatedAt": "<ISO-8601>",
  "method": "web-research",
  "company_name": company_name,
  "company_url": company_url,
  "profile": profile,
  "financials": financials,
  "market": market,
  "news": news,
  "sources_consulted": [list of URLs used]
}
```

GOTO: Write Outputs

---

# TYPE E: TECHNOLOGY INVENTORY

## Step 2E: Identify Technology

```
ACTION: Normalize subject_name to technology identifier
STORE: tech_name = normalized
STORE: tech_type = inferred category (framework/language/database/tool/runtime)
```

## Step 3E: Collect Core Specs

```
ACTION: WebSearch("{tech_name} documentation version latest {current_year}")
EXTRACT:
  - current_version
  - initial_release_date
  - license
  - language (implementation language)
  - paradigm (if applicable)
  - repository_url

STORE: specs = { ... }
```

## Step 4E: Collect GitHub Stats (if applicable)

```
IF repository_url is GitHub:
  ACTION: WebSearch("{tech_name} github stars contributors")
  EXTRACT:
    - stars
    - forks
    - open_issues
    - contributors
    - last_commit_date
    - commit_frequency (commits/month estimate)

  STORE: github_stats = { ... }
```

## Step 5E: Collect Ecosystem Data

```
ACTION: WebSearch("{tech_name} ecosystem packages plugins libraries")
EXTRACT:
  - package_count (npm/PyPI/crates.io/etc.)
  - notable_packages[] (top 5-10)
  - official_plugins[]
  - tooling[] (CLI tools, IDE extensions, etc.)

STORE: ecosystem = { ... }
```

## Step 6E: Collect Community and Adoption

```
ACTION: WebSearch("{tech_name} adoption usage statistics Stack Overflow {current_year}")
EXTRACT:
  - stackoverflow_questions (approximate count)
  - discord_members OR slack_members (if applicable)
  - job_postings_estimate
  - notable_adopters[] (companies using it)
  - npm_weekly_downloads OR equivalent (if applicable)

STORE: community = { ... }
```

## Step 7E: Compile Technology Inventory

```
STORE: inventory = {
  "subject": subject_name,
  "comparison_type": "technology",
  "generatedAt": "<ISO-8601>",
  "method": "web-research + github-stats",
  "tech_name": tech_name,
  "tech_type": tech_type,
  "specs": specs,
  "github_stats": github_stats,
  "ecosystem": ecosystem,
  "community": community,
  "sources_consulted": [list of URLs used]
}
```

GOTO: Write Outputs

---

## Write Outputs

```
ACTION: Generate subject slug from subject_name (lowercase, hyphens, max 40 chars)
STORE: subject_slug = slugify(subject_name)

ACTION: Write("{output_dir}/inventory-{subject_slug}.json", JSON.stringify(inventory, null, 2))
ACTION: Write("{output_dir}/inventory-{subject_slug}.md", render_markdown(inventory))
```

The Markdown output follows this structure:

```markdown
# Inventory: {subject_name}

**Type:** {comparison_type}
**Generated:** {ISO-8601}
**Method:** {method}

## Summary

| Metric | Value |
|--------|-------|
| {key metrics per type} |

## Detail

{type-specific detail sections}

## Sources

{list of sources consulted with URLs}
```

---

## Outputs

| File | Location | Format |
|------|----------|--------|
| Subject inventory (JSON) | `{output_dir}/inventory-{subject_slug}.json` | JSON |
| Subject inventory (MD) | `{output_dir}/inventory-{subject_slug}.md` | Markdown |

---

## Veto Conditions

The task MUST NOT execute (or must HALT) if:

1. **No subject provided** — `subject_name` is empty or not provided.
2. **Unknown comparison type** — `comparison_type` is not one of the 5 valid types.
3. **Codebase: no local clone and no repo URL** — Cannot inventory a codebase without filesystem access.
4. **Codebase: zero files found** — Subject root exists but contains no recognizable structure.
5. **Web types: all web requests fail** — Cannot inventory LLM/product/company/technology without web access.
6. **Data source config missing** — `data_source_config` not provided or invalid for the comparison type.

---

## Verification

- [ ] JSON output is valid (parseable without errors)
- [ ] Markdown output has consistent heading hierarchy
- [ ] All counts are from real data (no estimates for codebase type)
- [ ] Web-sourced data includes source URLs
- [ ] Inventory covers all relevant dimensions for the comparison type
- [ ] Subject slug is valid for filesystem paths
- [ ] Output files written to correct `output_dir`
- [ ] Method field accurately reflects how data was collected

---

## Backward Compatibility

For codebase type with `subject_name` pointing to an AIOX installation, this task
produces output equivalent to the legacy `bench-inventory` v1.0 (agent inventory,
workflow inventory, task counts, squad counts). The JSON structure is a superset
of the old format — all fields from v1.0 are present under `totals`, `agents`,
and `workflows` keys.
