---
phase: 14-br-scanners
plan: "02"
subsystem: scanners
tags: [braip, perfectpay, nuxt-ssr, iife-parser, fallback-scanner, marketplace, python]

requires:
  - phase: 14-01
    provides: "PlatformScanner ABC, EduzzScanner/MonetizzeScanner fallback pattern, mark_stale(), upsert_product(), migration _007 is_stale"

provides:
  - "PerfectPayScanner fallback-only (returns [] + alert='marketplace_unavailable')"
  - "BraipScanner with window.__NUXT__ IIFE parser (Nuxt 2 SSR format)"
  - "_parse_nuxt_products() + _resolve_iife_vars() parsing utilities"
  - "Fixture HTML mis/tests/fixtures/braip/catalog_cursos-online.html (live capture)"
  - "SCANNER_MAP updated with perfectpay + braip entries in scanner.py"
  - "config.yaml with braip slugs and explicit null for perfectpay/eduzz/monetizze in 3 niches"
  - "DOMAIN_DELAYS entry for marketplace.braip.com (2.0s rate limiting)"
  - "12 tests GREEN (6 SCAN-BR-03 + 6 SCAN-BR-04)"

affects:
  - phase-15-udemy-producthunt
  - phase-16-jvzoo
  - run_all_scanners scheduling

tech-stack:
  added: []
  patterns:
    - "IIFE variable binding resolution: extract function params + call args, build var_map, substitute in JS object literal"
    - "JS-to-JSON conversion: regex key quoting + variable substitution"
    - "Braip Nuxt 2 SSR: window.__NUXT__=(function(a,b,...){...})(args) with state.search.products"

key-files:
  created:
    - mis/scanners/perfectpay.py
    - mis/scanners/braip.py
    - mis/tests/test_perfectpay_scanner.py
    - mis/tests/test_braip_scanner.py
    - mis/tests/fixtures/braip/catalog_cursos-online.html
    - mis/tests/fixtures/perfectpay/.gitkeep
  modified:
    - mis/scanner.py
    - mis/base_scraper.py
    - mis/config.yaml

key-decisions:
  - "Braip window.__NUXT__ is a Nuxt 2 IIFE — parse as (function(params){...})(args), not raw JSON"
  - "IIFE variable substitution via regex after quoting keys — no external JS engine needed"
  - "Single product in cursos-online fixture (Braip hml/staging bucket) — sufficient for test_happy_path (>= 1)"
  - "braip/financas-pessoais maps to cursos-online slug (no specific finance slug confirmed)"
  - "config.yaml null entries for perfectpay/eduzz/monetizze are explicit opt-in — absence = scanner ignored by scheduler"

patterns-established:
  - "Fallback scanner pattern: return [] + log alert='marketplace_unavailable' (PerfectPay, Eduzz, Monetizze)"
  - "SSR IIFE parser pattern: params extraction + args JSON.loads + var substitution (Braip)"
  - "TDD commits: test (RED) commit -> feat (GREEN) commit per scanner"

requirements-completed:
  - SCAN-BR-03
  - SCAN-BR-04

duration: 10min
completed: "2026-03-17"
---

# Phase 14 Plan 02: BR Scanners — PerfectPay + Braip Summary

**PerfectPayScanner fallback + BraipScanner via Nuxt 2 IIFE parser (window.__NUXT__ variable binding resolution), 12 tests GREEN, config.yaml updated with explicit BR platform entries for all 3 niches**

## Performance

- **Duration:** 10 min
- **Started:** 2026-03-17T03:54:50Z
- **Completed:** 2026-03-17T04:04:58Z
- **Tasks:** 2 (TDD: 4 commits — 2 RED + 2 GREEN)
- **Files modified:** 9

## Accomplishments

- PerfectPayScanner implemented as fallback-only (checkout platform with no public marketplace) — mirrors Eduzz/Monetizze pattern from 14-01
- BraipScanner successfully parses window.__NUXT__ Nuxt 2 IIFE format — live fixture captured from marketplace.braip.com/search?categorySlug=cursos-online
- IIFE parser handles variable substitution (e.g., `star:c` where c=0) without external JS engine — pure Python re + json
- config.yaml updated: braip slugs added for all 3 niches, explicit null entries for perfectpay/eduzz/monetizze document intentional opt-out
- 29/29 Phase 14 suite GREEN (14-01 + 14-02 combined)

## Task Commits

Each task was committed atomically (TDD: RED then GREEN):

1. **Task 1 RED: PerfectPayScanner failing tests** - `11d52a8` (test)
2. **Task 1 GREEN: PerfectPayScanner implementation** - `a0587fc` (feat)
3. **Task 2 RED: BraipScanner failing tests + live fixture** - `f96e0cf` (test)
4. **Task 2 GREEN: BraipScanner SSR implementation + config.yaml** - `5e6ef18` (feat)

**Plan metadata:** (docs commit follows)

_Note: TDD tasks have 2 commits each (RED test → GREEN implementation)_

## Files Created/Modified

- `mis/scanners/perfectpay.py` — PerfectPayScanner fallback-only, alert='marketplace_unavailable'
- `mis/scanners/braip.py` — BraipScanner with _resolve_iife_vars(), _parse_nuxt_products(), _build_products()
- `mis/tests/test_perfectpay_scanner.py` — 6 tests SCAN-BR-03
- `mis/tests/test_braip_scanner.py` — 6 tests SCAN-BR-04
- `mis/tests/fixtures/braip/catalog_cursos-online.html` — Live fixture (60KB, 1 product, Nuxt 2 IIFE)
- `mis/tests/fixtures/perfectpay/.gitkeep` — Empty fixture dir for future use
- `mis/scanner.py` — SCANNER_MAP updated with perfectpay + braip imports
- `mis/base_scraper.py` — DOMAIN_DELAYS: marketplace.braip.com: 2.0
- `mis/config.yaml` — All 3 niches now have braip slugs + explicit null for 3 fallback platforms

## Decisions Made

- **Braip uses Nuxt 2 IIFE format** — `window.__NUXT__=(function(a,b,c,...){...})(null,"",0,...)`. Not raw JSON. IIFE params (a,b,c...) are resolved from call arguments to build a var_map for substitution.
- **Pure Python parser, no external JS engine** — `re` + `json` sufficient. Key quoting regex + variable substitution handles all observed field patterns.
- **Single product in live fixture** — Braip hml bucket (s3.amazonaws.com) visible in thumbnail URL suggests staging environment serving test data. test_happy_path passes at `>= 1`.
- **financas-pessoais uses braip: cursos-online** — No dedicated finance slug confirmed. Proxy mapping documented in config.yaml comment.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] IIFE variable binding required non-trivial parser**
- **Found during:** Task 2 (BraipScanner implementation) — PASSO 0 fixture capture
- **Issue:** Plan assumed `window.__NUXT__` would be parseable as raw JSON. Actual format is IIFE `(function(a,b,c,...){...})(args)` with variable substitution (e.g., `star:c` where `c=0`)
- **Fix:** Implemented `_resolve_iife_vars()` to extract params/args and build var_map; `_parse_nuxt_products()` does JS-to-JSON conversion (key quoting + var substitution) before json.loads
- **Files modified:** mis/scanners/braip.py (parsing approach redesigned vs. plan sketch)
- **Verification:** 6 BraipScanner tests GREEN including test_happy_path returning product with price=29.90 (2990/100)
- **Committed in:** 5e6ef18 (Task 2 GREEN commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - Bug in assumed JSON format)
**Impact on plan:** Parser redesign necessary for correctness — plan sketch assumed raw JSON which doesn't apply to Nuxt 2 IIFE format. No scope creep.

## Issues Encountered

- None beyond the IIFE format deviation above — fixture capture and test execution were straightforward once parser was correct.

## User Setup Required

None — no external service configuration required.

## Self-Check: PASSED

All created files exist on disk. All 4 task commits verified in git log (11d52a8, a0587fc, f96e0cf, 5e6ef18). 29/29 tests GREEN.

## Next Phase Readiness

- All 4 BR scanners complete: EduzzScanner, MonetizzeScanner (fallback), PerfectPayScanner (fallback), BraipScanner (SSR)
- Phase 14 fully complete: 29/29 tests GREEN
- config.yaml BR platform coverage complete for 3 niches
- Ready for Phase 15 (Udemy + Product Hunt)

---
*Phase: 14-br-scanners*
*Completed: 2026-03-17*
