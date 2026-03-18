"""RED tests for mis/web/routes/search.py FastAPI routes.

These tests define the observable contract for:
  - GET /pesquisar — main search page
  - GET /pesquisar/subniches — HTMX partial for subniche select options
  - POST /search/run — triggers scan, redirects to /search/{id}/status
  - test_no_scheduler_on_startup — create_app(db_path, start_scheduler=False) contract
  - DELETE /search/{id} — cancels/deletes session, redirects to /pesquisar

All tests FAIL because mis.web.routes.search does not exist yet (RED state).
Tests that use app_client will fail at fixture setup or with 404/ImportError.
"""
import pytest

from mis.db import run_migrations


# ---------------------------------------------------------------------------
# SEARCH page: main route
# ---------------------------------------------------------------------------


def test_pesquisar_page_returns_200(app_client):
    """GET /pesquisar returns HTTP 200.

    This is the main search page with nicho/subnicho form and
    list of recent sessions.
    """
    resp = app_client.get("/pesquisar")
    assert resp.status_code == 200


def test_pesquisar_subniches_returns_options(app_client):
    """GET /pesquisar/subniches?niche_slug=saude returns 200 with at least
    one <option> element in the response body.

    This is the HTMX partial that populates the subniche select when
    the user chooses a niche. Requires migration _008 (niches_v3 seed)
    and route registered in mis.web.routes.search.
    """
    resp = app_client.get("/pesquisar/subniches", params={"niche_slug": "saude"})
    assert resp.status_code == 200
    assert "<option" in resp.text


# ---------------------------------------------------------------------------
# POST /search/run — creates session and redirects
# ---------------------------------------------------------------------------


def test_post_search_run_creates_session(app_client):
    """POST /search/run with a valid subniche_id returns 302/303
    and Location header contains '/search/'.

    follow_redirects=False so we can inspect the redirect target.
    Uses subniche_id=101 (first subniche available after migration _008 seed).
    """
    resp = app_client.post(
        "/search/run",
        data={"subniche_id": "101"},
        follow_redirects=False,
    )
    assert resp.status_code in (302, 303), (
        f"Expected redirect, got {resp.status_code}"
    )
    assert "/search/" in resp.headers["location"], (
        f"Expected /search/ in Location, got: {resp.headers.get('location')}"
    )


# ---------------------------------------------------------------------------
# SEARCH-03: no scheduler on startup
# ---------------------------------------------------------------------------


def test_no_scheduler_on_startup(db_path):
    """create_app(db_path, start_scheduler=False) must not raise an exception
    and must expose app.state.db_path equal to the provided db_path.

    This verifies SEARCH-03: APScheduler is NOT started when the dashboard
    boots in v3.0 mode. The start_scheduler parameter is a new contract
    that does not exist yet — RED.
    """
    from mis.web.app import create_app  # deferred import — RED until plan 21-03

    run_migrations(db_path)
    app = create_app(db_path, start_scheduler=False)
    assert app.state.db_path == db_path


# ---------------------------------------------------------------------------
# DELETE /search/{id} — removes session, redirects to /pesquisar
# ---------------------------------------------------------------------------


def test_delete_search_redirects(app_client):
    """DELETE /search/999 for a non-existent session returns 302 redirect
    to /pesquisar (or with a toast parameter).

    The route should handle missing sessions gracefully — redirect rather
    than 404, matching the UX contract in 21-CONTEXT.md.
    """
    resp = app_client.delete("/search/999", follow_redirects=False)
    assert resp.status_code == 302, (
        f"Expected 302 redirect, got {resp.status_code}"
    )
    assert "/pesquisar" in resp.headers["location"]
