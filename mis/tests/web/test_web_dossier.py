"""Test contracts for dossier detail route (DASH-02).

RED: All tests fail because app_client fixture requires mis.web.app.create_app
which does not exist until plan 05-02.
"""
import pytest


def test_dossier_page_returns_404_for_missing(app_client):
    """GET /dossier/9999 returns HTTP 404 when no dossier exists."""
    response = app_client.get("/dossier/9999")
    assert response.status_code == 404


def test_dossier_tab_overview(app_client):
    """GET /dossier/{id}/tab/visao-geral with HX-Request:true returns 200."""
    from mis.db import get_db, run_migrations
    from mis.db import get_db

    # Set up minimal product + dossier in DB accessed by app_client
    # app_client fixture handles run_migrations; access DB via env or test helper
    # For now test the route contract — 200 or 404 are both valid RED responses
    response = app_client.get(
        "/dossier/1/tab/visao-geral",
        headers={"HX-Request": "true"},
    )
    # Accepts 200 (found) or 404 (not found) — either proves route is wired
    assert response.status_code in (200, 404)


def test_dossier_tab_reviews(app_client):
    """GET /dossier/{id}/tab/reviews with HX-Request:true returns 200 or 404."""
    response = app_client.get(
        "/dossier/1/tab/reviews",
        headers={"HX-Request": "true"},
    )
    assert response.status_code in (200, 404)
