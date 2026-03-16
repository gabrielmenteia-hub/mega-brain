---
phase: 12-meta-ads-pain-radar
plan: 01
subsystem: radar
tags: [meta-ads, apscheduler, sqlite-utils, httpx, respx, tdd, pain-signals]

requires:
  - phase: 04-pain-radar
    provides: "pain_signals schema, APScheduler register_radar_jobs() pattern, INSERT OR IGNORE idempotency via url_hash"
provides:
  - "mis/radar/meta_ads_collector.py — collect_ad_comments(niche, db_path) coletor Meta Ads"
  - "mis/radar/__init__.py — 6th APScheduler job: radar_meta_ads com CronTrigger(minute=0)"
  - "RADAR-04 closed: criativos de anuncios Meta entram no radar horário automaticamente"
affects: [phase-13, mis-integration, pain-radar-dashboard]

tech-stack:
  added: []
  patterns:
    - "INSERT OR IGNORE via sqlite_utils ignore=True on url_hash UNIQUE index"
    - "Graceful degradation without token: return [] + log.warning (not raise)"
    - "bodies = ad.get('ad_creative_bodies') or [] for silent skip on empty/None"
    - "HTTPStatusError per-keyword: log.error + continue (niche not aborted)"
    - "_run_all_meta_ads helper async func before register_radar_jobs"

key-files:
  created:
    - mis/radar/meta_ads_collector.py
    - mis/tests/test_meta_ads_radar.py
    - mis/tests/fixtures/meta_ads/ads_archive_radar_response.json
  modified:
    - mis/radar/__init__.py
    - mis/tests/test_radar_jobs.py

key-decisions:
  - "collect_ad_comments retorna [] sem propagar excecao quando META_ACCESS_TOKEN ausente (graceful degradation)"
  - "ad_countries extraido de niche.get('ad_countries', ['BR']) — flexivel por niche, default BR"
  - "title recebe texto completo do criativo sem truncamento (SQLite TEXT sem limite)"
  - "score=0 para anuncios Meta (sem metrica de engajamento equivalente ao Reddit score)"
  - "HTTPStatusError por keyword: log.error + continue (nao abortar o niche inteiro)"

patterns-established:
  - "Pattern: asyncio.sleep monkeypatched como AsyncMock em TODOS testes de meta_ads_radar"
  - "Pattern: respx.get(META_API_URL).mock() exatamente como test_meta_ads_spy.py"
  - "Pattern: sqlite3.connect direct verification apos collect (consistente com outros testes de radar)"

requirements-completed: [RADAR-04]

duration: 12min
completed: 2026-03-16
---

# Phase 12 Plan 01: Meta Ads Pain Radar Summary

**Meta Ad Library radar collector (RADAR-04) via collect_ad_comments() com INSERT OR IGNORE, graceful degradation sem token, e 6 jobs registrados no APScheduler**

## Performance

- **Duration:** 12 min
- **Started:** 2026-03-16T19:12:16Z
- **Completed:** 2026-03-16T19:24:30Z
- **Tasks:** 2 (TDD: RED + GREEN)
- **Files modified:** 5

## Accomplishments

- Implementado `mis/radar/meta_ads_collector.py` com `collect_ad_comments(niche, db_path)` completo
- Coletor busca criativos de anuncios ativos na Meta Ad Library API por keyword/nicho
- Persiste em `pain_signals` com `source='meta_ads'` via INSERT OR IGNORE (idempotencia por url_hash)
- Wired no APScheduler como 6 job: `radar_meta_ads` com `CronTrigger(minute=0)`, executando apos `_run_all_meta_ads`
- Suite 167 testes GREEN (1 falha pre-existente `test_cli_spy_help` — issue de PYTHONPATH em subprocess, out-of-scope)

## Task Commits

1. **Task 1: Wave 0 — Scaffolds de teste e fixture (RED)** - `7e6ccdb` (test)
2. **Task 2: Implementacao — meta_ads_collector.py + wiring no __init__.py (GREEN)** - `7edefd7` (feat)

**Plan metadata:** (docs commit — this summary)

## Files Created/Modified

- `mis/radar/meta_ads_collector.py` — Novo: coletor Meta Ads com collect_ad_comments(), graceful degradation, INSERT OR IGNORE
- `mis/radar/__init__.py` — Modificado: import collect_ad_comments, _run_all_meta_ads helper, 6th job radar_meta_ads, job_count=6
- `mis/tests/test_meta_ads_radar.py` — Novo: 4 cenarios TDD (happy path, no token, idempotencia, skip empty body)
- `mis/tests/fixtures/meta_ads/ads_archive_radar_response.json` — Novo: fixture com 3 anuncios (radar001, radar002, radar003)
- `mis/tests/test_radar_jobs.py` — Modificado: test_radar_meta_ads_job_registered + test_six_jobs_registered

## Decisions Made

- `collect_ad_comments` retorna `[]` sem propagar excecao quando `META_ACCESS_TOKEN` ausente — graceful degradation compativel com environments sem credenciais Meta
- `ad_countries` extraido de `niche.get("ad_countries", ["BR"])` — flexivel por niche, default BR obrigatorio para Meta API
- `title` recebe texto completo do criativo sem truncamento (SQLite TEXT sem limite de tamanho)
- `score=0` para anuncios Meta — sem metrica de engajamento equivalente ao Reddit score
- HTTPStatusError por keyword: `log.error + continue` — nao abortar o niche inteiro por falha de uma keyword

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None — implementacao seguiu as interfaces do plano diretamente.

## User Setup Required

`META_ACCESS_TOKEN` deve ser configurado em `.env` para o coletor funcionar. Sem o token, `collect_ad_comments` retorna `[]` graciosamente — o sistema continua operando com os outros 5 coletores.

## Next Phase Readiness

- RADAR-04 fechado: 6/6 coletores do Pain Radar implementados e integrados ao APScheduler
- Cobertura completa de fontes: Google Trends + Reddit + Quora + YouTube + Meta Ads
- Suite completa GREEN (167 tests, exceto 1 pre-existing PYTHONPATH issue out-of-scope)

---
*Phase: 12-meta-ads-pain-radar*
*Completed: 2026-03-16*
