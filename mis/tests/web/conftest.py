"""Fixtures for mis web layer tests.

Provides TestClient + ephemeral SQLite DB for testing FastAPI routes.
The import of create_app is deferred inside the fixture so that repository
tests (test_alert_repository, test_dossier_repository, test_pain_repository)
can be collected and fail with ImportError on their own imports — not on
the web layer import that is only needed for route tests.
"""
import pytest
from fastapi.testclient import TestClient

from mis.db import run_migrations


@pytest.fixture
def db_path(tmp_path):
    """Return path to a temporary SQLite database file for web tests."""
    return str(tmp_path / "web_mis.db")


@pytest.fixture
def app_client(db_path):
    """Return a TestClient backed by a fresh SQLite DB with full schema.

    Importing create_app here (deferred) means collection works even before
    mis.web.app exists — only tests that USE this fixture will fail at setup.
    """
    from mis.web.app import create_app  # RED until plan 05-02

    run_migrations(db_path)
    app = create_app(db_path=db_path)
    with TestClient(app) as client:
        yield client
