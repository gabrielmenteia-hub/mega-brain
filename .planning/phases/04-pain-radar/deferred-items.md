# Deferred Items — Phase 04 Pain Radar

## Pre-existing issues (out of scope for this plan)

### test_spy_orchestrator.py::test_cli_spy_help

**Status:** Failing before Plan 04-01 (confirmed via git stash test)
**Cause:** `subprocess.run([sys.executable, "-m", "mis", "spy", "--help"])` uses the system Python without PYTHONPATH set to the project root. Returns exit code 1 with "No module named mis".
**Impact:** None for Phase 4 — this is a test environment issue in Phase 3 work.
**Recommendation:** Fix in a future maintenance plan by either:
1. Setting `PYTHONPATH` in the subprocess call, or
2. Using `python -m pytest --import-mode=importlib` and invoking via `subprocess.run` with correct `cwd`/env.
