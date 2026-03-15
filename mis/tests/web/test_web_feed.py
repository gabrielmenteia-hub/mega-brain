"""Test contracts for pain feed route (DASH-03).

RED: All tests fail because app_client fixture requires mis.web.app.create_app
which does not exist until plan 05-02.
"""
import pytest


def test_feed_page_returns_200(app_client):
    """GET /feed returns HTTP 200."""
    response = app_client.get("/feed")
    assert response.status_code == 200


def test_feed_niche_partial(app_client):
    """GET /feed/niche/emagrecimento with HX-Request:true returns partial without <nav."""
    response = app_client.get(
        "/feed/niche/emagrecimento",
        headers={"HX-Request": "true"},
    )
    assert response.status_code == 200
    assert "<nav" not in response.text
