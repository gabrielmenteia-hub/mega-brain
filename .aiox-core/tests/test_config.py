"""Unit tests for nexus.config — NexusConfig BaseSettings."""
import os
import pytest
from pydantic import ValidationError

from nexus.config import NexusConfig


def test_config_loads_from_env(tmp_path, monkeypatch):
    """NexusConfig loads values from .env file with NEXUS_ prefix."""
    env_file = tmp_path / ".env"
    env_file.write_text(
        "NEXUS_ANTHROPIC_API_KEY=test-key-123\n"
        "NEXUS_MIN_COPY_SCORE=9\n"
        "NEXUS_MAX_REVIEW_ATTEMPTS=5\n"
    )
    monkeypatch.chdir(tmp_path)
    config = NexusConfig(_env_file=str(env_file))
    assert config.anthropic_api_key == "test-key-123"
    assert config.min_copy_score == 9
    assert config.max_review_attempts == 5


def test_config_uses_defaults_when_env_missing(tmp_path):
    """NexusConfig uses defined defaults for optional variables not in .env."""
    env_file = tmp_path / ".env"
    env_file.write_text("NEXUS_ANTHROPIC_API_KEY=test-key\n")
    config = NexusConfig(_env_file=str(env_file))
    assert config.min_copy_score == 7       # default
    assert config.max_review_attempts == 3  # default
    assert config.min_tech_score == 6       # default


def test_config_rejects_missing_required_key(tmp_path):
    """NexusConfig raises an error when NEXUS_ANTHROPIC_API_KEY is absent."""
    env_file = tmp_path / ".env"
    env_file.write_text("")  # No API key
    with pytest.raises(Exception):  # ValidationError or similar
        NexusConfig(_env_file=str(env_file))


def test_config_env_override(monkeypatch, tmp_path):
    """System env var takes priority over value in .env file."""
    env_file = tmp_path / ".env"
    env_file.write_text(
        "NEXUS_ANTHROPIC_API_KEY=from-file\n"
        "NEXUS_MIN_COPY_SCORE=5\n"
    )
    monkeypatch.setenv("NEXUS_MIN_COPY_SCORE", "9")
    config = NexusConfig(_env_file=str(env_file))
    assert config.min_copy_score == 9  # env var wins over .env value
