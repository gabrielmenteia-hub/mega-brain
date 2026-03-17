# Phase 19: Code Quality Cleanup - Research

**Researched:** 2026-03-17
**Domain:** Python code quality, Jinja2 HTML templates, documentation
**Confidence:** HIGH

## Summary

Phase 19 is a focused tech debt cleanup with 4 discrete, non-interactive items identified from the v2.0 audit. Each item is a small, contained change: one Python guard clause in `scanner.py`, one HTML template styling change in `unified_table.html`, one doc correction in `REQUIREMENTS.md`, and one documentation addition (docstring or README) describing fallback scanner behavior.

No new libraries, no schema migrations, no infrastructure changes. All four items are independent and can be executed in a single plan wave. The scope is strictly cosmetic/documentation/defensive-code — no behavioral changes to the runtime system.

**Primary recommendation:** Execute all 4 items in one plan (19-01), structured as a single wave with 4 atomic tasks. No TDD required — changes are trivially verifiable by code inspection and `grep`.

## Standard Stack

### Core (already present, no new installs)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib | 3.x | Guard clause syntax | Built-in |
| Jinja2 | already in project | Template rendering | Project standard |
| Tailwind CSS (CDN) | already in base.html | Badge styling classes | Project standard — `base.html` loads Tailwind via CDN |
| structlog | already in project | Structured logging | Established project pattern |

**Installation:** No new packages required.

## Architecture Patterns

### Item 1: Null Slug Guard in `scanner.py`

**Location:** `mis/scanner.py`, function `run_all_scanners()`, dispatch loop at lines 260–273.

**Current code (line 260):**
```python
for platform_name, platform_slug in platforms.items():
    scanner_cls = SCANNER_MAP.get(platform_name)
    if scanner_cls is None:
        log.warning(...)
        continue
    key = f"{niche_slug}.{platform_name}"
    ...
```

**The gap:** `platform_slug` can be `None` when `config.yaml` has a null entry (e.g., `eduzz: null`). Per the Phase 14-02 decision: "config.yaml null entries for perfectpay/eduzz/monetizze are explicit opt-in — absence would mean scanner ignored by scheduler." However, a null slug passed to `scan_niche()` as `platform_slug=None` is technically an unvalidated edge case.

**Required guard (after the `scanner_cls is None` check):**
```python
if platform_slug is None:
    # Null slug = platform opted in but no category mapping configured
    # scan_niche() would receive None — skip silently
    continue
```

**Pattern:** Defensive guard with inline comment explaining semantics. Mirror the existing `scanner_cls is None` guard style directly above it.

**What to verify:** `grep -n "platform_slug is None" mis/scanner.py` returns a match.

### Item 2: Styled Platform Badges in `unified_table.html`

**Location:** `mis/web/templates/unified_table.html`, line 24.

**Current code:**
```html
<td class="px-4 py-3 text-gray-300">
  {{ product.platform_name }}{% if product.is_stale %} <span title="Dados desatualizados">&#9888;&#65039;</span>{% endif %}
</td>
```

**The gap:** `product.platform_name` is rendered as bare text. The success criterion requires it to be a `<span>` with a CSS class (styled badge element).

**Required pattern (Tailwind badge, consistent with existing `<span>` badges in the template):**
```html
<td class="px-4 py-3">
  <span class="platform-badge bg-gray-700 text-gray-200 text-xs px-2 py-0.5 rounded">{{ product.platform_name }}</span>{% if product.is_stale %} <span title="Dados desatualizados">&#9888;&#65039;</span>{% endif %}
</td>
```

**Existing badge precedent in the same file (line 21):**
```html
<span class="bg-yellow-600 text-xs px-1 rounded ml-1">Pendente</span>
```
This is the established badge pattern in the codebase. The platform badge should follow the same `<span>` + Tailwind utility classes pattern.

**Class choice:** `bg-gray-700 text-gray-200 text-xs px-2 py-0.5 rounded` — neutral style that doesn't clash with product title styling. Adding class `platform-badge` as a semantic identifier for the element type.

**What to verify:** `grep -n "platform-badge" mis/web/templates/unified_table.html` returns a match.

### Item 3: REQUIREMENTS.md INFRA-03 Correction

**Location:** `.planning/REQUIREMENTS.md`, line 13.

**Current text:**
```
- [x] **INFRA-03**: Campo `rank_type` adicionado à tabela `products` para identificar a semântica do rank por plataforma (posição, gravity, EPC, upvotes, enrollment, etc.)
```

**The gap:** The description says "tabela `products`" but INFRA-03 as implemented in Phase 13 added `rank_type` to the `platforms` table (as a column defining the rank semantics per platform), not the `products` table per row.

**Verification of the actual schema:** Check `mis/migrations/_006_v2_platforms.py` or the actual SQLite schema to confirm which table received `rank_type`. The ROADMAP Phase 13 description says "Cada plataforma no DB tem campo `rank_type` preenchido" — "cada plataforma" confirms it is the `platforms` table, not `products`.

**Required correction:**
```
- [x] **INFRA-03**: Campo `rank_type` adicionado à tabela `platforms` para identificar a semântica do rank por plataforma (posição, gravity, EPC, upvotes, enrollment, etc.)
```

**What to verify:** `grep "INFRA-03" .planning/REQUIREMENTS.md` shows "tabela \`platforms\`".

### Item 4: Fallback Scanner Documentation

**Location:** `mis/scanner.py` module docstring (top of file, lines 1–7) OR a dedicated README in `mis/`.

**Current module docstring:**
```
"""Platform scanner abstractions for MIS.

Provides:
- Product dataclass with all required and optional fields
- PlatformScanner ABC extending BaseScraper with abstract scan_niche()
- run_all_scanners() coroutine that runs all configured scanners in parallel
"""
```

**The gap:** The docstring does not mention the fallback scanner pattern established in Phase 14 (Eduzz, Monetizze, PerfectPay are fallback-only scanners that return `[]` + `marketplace_unavailable` alert).

**Recommended approach:** Extend the module docstring to include a "Fallback Pattern" section — more discoverable than a README because it lives next to the code. A README in `mis/` would also work.

**Required content (docstring addition):**
```python
"""Platform scanner abstractions for MIS.

Provides:
- Product dataclass with all required and optional fields
- PlatformScanner ABC extending BaseScraper with abstract scan_niche()
- run_all_scanners() coroutine that runs all configured scanners in parallel

Fallback Scanner Pattern (BR Platforms):
    Eduzz, Monetizze, and PerfectPay require authentication — their public
    marketplaces are not accessible. These scanners implement the fallback
    pattern: scan_niche() always returns [] and emits a structured warning
    log with alert='marketplace_unavailable'. run_all_scanners() detects the
    empty return and calls mark_stale() to flag existing DB records.

    When a marketplace becomes publicly accessible:
        1. Re-implement scan_niche() in the scanner class.
        2. Remove the marketplace_unavailable log.warning() call.
        3. Add fixtures and tests following the Phase 14 pattern.
"""
```

**What to verify:** `grep -n "marketplace_unavailable" mis/scanner.py` returns a match in the module docstring.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Badge styling | Custom CSS file | Tailwind utility classes | Already loaded via CDN in base.html — no new stylesheet needed |
| Null check | Complex validation layer | Single `if platform_slug is None: continue` | One guard clause is sufficient — over-engineering is the anti-pattern here |

## Common Pitfalls

### Pitfall 1: Guard Clause Placement
**What goes wrong:** Placing the `platform_slug is None` guard before the `scanner_cls is None` guard, or after the `key` assignment — causing the wrong log message or failing to skip.
**How to avoid:** Insert the guard AFTER the `scanner_cls is None` block and BEFORE `key = f"{niche_slug}.{platform_name}"`. This way, we already know the scanner class exists before checking the slug.

**Correct order:**
```python
scanner_cls = SCANNER_MAP.get(platform_name)
if scanner_cls is None:
    log.warning(...)
    continue
if platform_slug is None:       # <-- here, after scanner_cls check
    continue
key = f"{niche_slug}.{platform_name}"
```

### Pitfall 2: Wrong Table Name in REQUIREMENTS.md
**What goes wrong:** Correcting "tabela `products`" to "tabela `platforms`" without verifying which table actually has the column in the live schema.
**How to avoid:** Inspect `mis/migrations/_006_v2_platforms.py` before writing the correction — confirm the column is on `platforms`, not `products`.

### Pitfall 3: Over-styling Badges
**What goes wrong:** Adding per-platform color logic (e.g., Hotmart=green, ClickBank=orange) which requires mapping maintenance.
**How to avoid:** Use a single neutral style for all platforms. The success criterion says "elementos HTML estilizados (`<span>` com classe CSS)" — one class is sufficient, color variety is out of scope.

### Pitfall 4: Redundant Documentation
**What goes wrong:** Adding fallback documentation both in scanner.py docstring AND a new README, creating duplication.
**How to avoid:** Pick one location — scanner.py module docstring is preferred (co-located with code, no new file).

## Code Examples

### Guard clause — exact insertion point in scanner.py
```python
# Source: mis/scanner.py lines 260-273 (current code)
for platform_name, platform_slug in platforms.items():
    scanner_cls = SCANNER_MAP.get(platform_name)
    if scanner_cls is None:
        log.warning(
            "scanner.platform.not_implemented",
            platform=platform_name,
            niche=niche_slug,
        )
        continue
    if platform_slug is None:
        # Null slug: platform opted in to config.yaml but no category mapping
        # provided. Passing None to scan_niche() is not supported — skip.
        continue
    key = f"{niche_slug}.{platform_name}"
    keys.append(key)
    coroutines.append(
        _run_one(scanner_cls, niche_slug, platform_slug, key)
    )
```

### Badge span — exact replacement in unified_table.html
```html
<!-- Source: mis/web/templates/unified_table.html line 23-25 -->
<!-- BEFORE -->
<td class="px-4 py-3 text-gray-300">
  {{ product.platform_name }}{% if product.is_stale %} <span title="Dados desatualizados">&#9888;&#65039;</span>{% endif %}
</td>

<!-- AFTER -->
<td class="px-4 py-3">
  <span class="platform-badge bg-gray-700 text-gray-200 text-xs px-2 py-0.5 rounded">{{ product.platform_name }}</span>{% if product.is_stale %} <span title="Dados desatualizados">&#9888;&#65039;</span>{% endif %}
</td>
```

## State of the Art

All changes in Phase 19 are purely additive/corrective within established patterns. No paradigm shifts.

| Item | Pattern | Already Used In |
|------|---------|----------------|
| Guard clause | `if x is None: continue` | Lines 247-252 of scanner.py (niche_id_map check) |
| Badge span | `<span class="bg-* text-xs px-* rounded">` | Line 21 of unified_table.html (Pendente badge) |
| Fallback docstring | Module-level docstring pattern | eduzz.py, monetizze.py, perfectpay.py (already have fallback docs in module docstrings) |

## Open Questions

1. **Which table actually has `rank_type` column — `platforms` or `products`?**
   - What we know: ROADMAP.md Phase 13 success criterion says "Cada plataforma no DB tem campo `rank_type` preenchido" (platforms table). REQUIREMENTS.md says "tabela `products`" (appears to be an error).
   - What's unclear: Whether the migration added it to both tables or only one.
   - Recommendation: Read `mis/migrations/_006_v2_platforms.py` at plan execution time to confirm before writing the REQUIREMENTS.md correction.

2. **Should the null slug guard emit a log.warning() or skip silently?**
   - What we know: The existing `scanner_cls is None` check logs a warning. The null slug case is different — it's a configuration decision, not an error.
   - Recommendation: Skip silently (no log) — null slug is a valid opt-in-without-category-mapping configuration state, not an error. Add inline comment explaining semantics.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (already configured) |
| Config file | `mis/pytest.ini` or `pyproject.toml` (project standard) |
| Quick run command | `pytest mis/tests/ -x -q` |
| Full suite command | `pytest mis/tests/ -q` |

### Phase Requirements to Test Map

Phase 19 has no formal REQ-IDs. Verification is by direct inspection:

| Item | Behavior | Test Type | Automated Command |
|------|----------|-----------|-------------------|
| Null slug guard | Guard exists in scanner.py | grep check | `grep -n "platform_slug is None" mis/scanner.py` |
| Platform badge | `<span>` with CSS class in unified_table.html | grep check | `grep -n "platform-badge" mis/web/templates/unified_table.html` |
| REQUIREMENTS.md INFRA-03 | "tabela \`platforms\`" in text | grep check | `grep "INFRA-03" .planning/REQUIREMENTS.md` |
| Fallback docs | Fallback pattern documented | grep check | `grep -n "marketplace_unavailable" mis/scanner.py` |

### Sampling Rate

- **Per task commit:** `grep` checks above (instant, no server needed)
- **Per wave merge:** `pytest mis/tests/test_scanner_niche_id.py mis/tests/test_scanner_alerts.py -q` (ensures no regressions in scanner.py changes)
- **Phase gate:** All 4 grep checks pass + existing scanner tests GREEN

### Wave 0 Gaps

None — no new test files required. All success criteria are verifiable by `grep`. The scanner.py change (guard clause) must not break existing tests in `test_scanner_niche_id.py` and `test_scanner_alerts.py`.

## Sources

### Primary (HIGH confidence)

- Direct code inspection: `mis/scanner.py` — current dispatch loop structure at lines 260–273
- Direct code inspection: `mis/web/templates/unified_table.html` — current platform name rendering at line 24
- Direct code inspection: `.planning/REQUIREMENTS.md` — current INFRA-03 text at line 13
- Direct code inspection: `mis/scanners/eduzz.py`, `monetizze.py`, `perfectpay.py` — fallback pattern reference implementations
- Direct code inspection: `mis/web/templates/base.html` — confirms Tailwind CSS loaded via CDN

### Secondary (MEDIUM confidence)

- `.planning/ROADMAP.md` Phase 13 success criteria — confirms `rank_type` is "per platform" (platforms table semantics)
- `.planning/STATE.md` Phase 14-02 decision — confirms null config.yaml entries are intentional opt-in

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new libraries, all patterns extracted from existing code
- Architecture: HIGH — exact insertion points identified from source inspection
- Pitfalls: HIGH — derived from existing code structure and established patterns

**Research date:** 2026-03-17
**Valid until:** Stable — no external dependencies, all internal code
