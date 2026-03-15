"""Test contracts for ranking dashboard route (DASH-01, SCAN-05).

RED: All tests fail because app_client fixture requires mis.web.app.create_app
which does not exist until plan 05-02.
"""
import pytest


def test_ranking_page_returns_200(app_client):
    """GET /ranking returns HTTP 200 with 'Ranking' in the body."""
    response = app_client.get("/ranking")
    assert response.status_code == 200
    assert "Ranking" in response.text


def test_ranking_filter_by_platform(app_client):
    """GET /ranking?platform=hotmart returns HTTP 200."""
    response = app_client.get("/ranking?platform=hotmart")
    assert response.status_code == 200


def test_ranking_filter_by_niche(app_client):
    """GET /ranking?niche=emagrecimento returns HTTP 200."""
    response = app_client.get("/ranking?niche=emagrecimento")
    assert response.status_code == 200


def test_ranking_table_partial_htmx(app_client):
    """GET /ranking/table with HX-Request:true returns partial HTML without <nav."""
    response = app_client.get("/ranking/table", headers={"HX-Request": "true"})
    assert response.status_code == 200
    assert "<nav" not in response.text


def test_ranking_pagination_per_page(app_client):
    """GET /ranking?per_page=10&page=1 returns HTTP 200."""
    response = app_client.get("/ranking?per_page=10&page=1")
    assert response.status_code == 200
