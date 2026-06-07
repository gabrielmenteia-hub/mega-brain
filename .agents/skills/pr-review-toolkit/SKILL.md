# PR Review Toolkit Skill

> **Auto-Trigger:** Quando usuário pedir análise de PR, revisão de pull request, análise de comentários, hunting de falhas
> **Keywords:** "PR", "pull request", "revisar PR", "análise de PR", "PR review", "comment analyzer", "silent failure"
> **Prioridade:** ALTA
> **Namespace:** [OFFICIAL]
> **Tools:** Read, Glob, Grep, Bash, Task

## Quando NÃO Ativar

- Code review geral sem contexto de PR
- Criação de PRs (usar git workflow)
- Perguntas sobre PRs sem análise
- Quando usuário explicitamente pedir skill diferente

---

## Core Purpose

Bundle of 6 specialized agents for comprehensive PR analysis. Provides deep inspection
of comments, tests, silent failures, type design, code quality, and simplification opportunities.

---

## The 6 Specialized Agents

### 1. Comment Analyzer

**Focus:** PR comment triage

- Categorizes comments by severity
- Identifies blocking vs non-blocking
- Summarizes discussion threads
- Highlights unresolved items
- Tracks comment resolution status

### 2. PR Test Analyzer

**Focus:** Test coverage validation

- Identifies untested code paths
- Suggests missing test cases
- Validates test quality
- Checks edge case coverage
- Reviews test naming/structure

### 3. Silent Failure Hunter

**Focus:** Hidden bug detection

- Finds swallowed exceptions
- Identifies missing error handling
- Detects async/await issues
- Spots race conditions
- Finds resource leaks

### 4. Type Design Analyzer

**Focus:** Type system quality

- Reviews type definitions
- Identifies type safety issues
- Suggests better type patterns
- Checks generic usage
- Validates interface design

### 5. Code Reviewer

**Focus:** General code quality

- Style consistency
- Best practices adherence
- Pattern compliance
- Documentation quality
- Naming conventions

### 6. Code Simplifier

**Focus:** Complexity reduction

- Identifies over-engineering
- Suggests simplifications
- Removes dead code
- Consolidates duplicates
- Improves readability

---

## Agent Activation

Each agent can be invoked individually or as a full suite:

| Command | Agents Activated |
|---------|------------------|
| `/pr-review:full` | All 6 agents |
| `/pr-review:comments` | Comment Analyzer |
| `/pr-review:tests` | PR Test Analyzer |
| `/pr-review:failures` | Silent Failure Hunter |
| `/pr-review:types` | Type Design Analyzer |
| `/pr-review:quality` | Code Reviewer |
| `/pr-review:simplify` | Code Simplifier |

---

## Output Format

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                         PR REVIEW TOOLKIT REPORT                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  PR: #[number] - [title]                                                     ║
║  Agents Run: [list]                                                          ║
║  Files Analyzed: [N]                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌─ COMMENT ANALYZER ──────────────────────────────────────────────────────────┐
│  Blocking: [N]  |  Suggestions: [N]  |  Resolved: [N]                       │
│                                                                             │
│  BLOCKING ITEMS:                                                            │
│  - [item description] @ file:line                                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─ SILENT FAILURE HUNTER ─────────────────────────────────────────────────────┐
│  Potential Issues Found: [N]                                                │
│                                                                             │
│  ⚠️  [issue description]                                                    │
│      Location: file:line                                                    │
│      Risk: [HIGH | MEDIUM | LOW]                                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─ TEST ANALYZER ─────────────────────────────────────────────────────────────┐
│  Coverage Delta: [+/-X%]                                                    │
│  Missing Tests: [N]                                                         │
│                                                                             │
│  SUGGESTED TESTS:                                                           │
│  - [test case description]                                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─ TYPE DESIGN ANALYZER ──────────────────────────────────────────────────────┐
│  Type Issues: [N]                                                           │
│                                                                             │
│  RECOMMENDATIONS:                                                           │
│  - [recommendation]                                                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─ CODE SIMPLIFIER ───────────────────────────────────────────────────────────┐
│  Simplification Opportunities: [N]                                          │
│                                                                             │
│  SUGGESTIONS:                                                               │
│  - [simplification suggestion]                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─ SUMMARY ───────────────────────────────────────────────────────────────────┐
│  ✅ Ready to merge: [YES | NO | NEEDS WORK]                                 │
│  📋 Action items: [N]                                                       │
│  ⏱️  Estimated fix time: [estimate]                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Example Prompts This Skill Handles

- "Analise o PR #123 completamente"
- "Review the pull request for silent failures"
- "Verifique os comentários não resolvidos no PR"
- "Hunt for async issues in this PR"
- "Simplifique o código deste pull request"
- "Check test coverage for PR changes"

---

## Integration Notes

This skill is part of the **Codex Official Skills** collection.
Namespace: `[OFFICIAL]` - Distinguishes from Mega Brain custom skills.

For custom Mega Brain skills, see: `/.Codex/skills/`
