"""Test contracts for alerts route (DASH-04).

RED: All tests fail because app_client fixture requires mis.web.app.create_app
which does not exist until plan 05-02.
"""
import pytest


def test_alerts_page_returns_200(app_client):
    """GET /alerts returns HTTP 200."""
    response = app_client.get("/alerts")
    assert response.status_code == 200


def test_alerts_badge_returns_fragment(app_client):
    """GET /alerts/badge with HX-Request:true returns HTTP 200."""
    response = app_client.get("/alerts/badge", headers={"HX-Request": "true"})
    assert response.status_code == 200


def test_alerts_mark_seen(app_client):
    """POST /alerts/1/mark-seen returns 200 or 404 (alert may not exist)."""
    response = app_client.post("/alerts/1/mark-seen")
    assert response.status_code in (200, 404)
