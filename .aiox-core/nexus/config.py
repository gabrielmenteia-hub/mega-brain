"""NEXUS externalized configuration.

All settings are loaded from a .env file with the NEXUS_ prefix.
Using pydantic-settings BaseSettings for automatic type coercion,
startup validation, and precedence rules (env var > .env file > default).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class NexusConfig(BaseSettings):
    """All NEXUS configuration. Loaded from .env with NEXUS_ prefix.

    Precedence (highest to lowest):
      1. System environment variables (e.g. export NEXUS_MIN_COPY_SCORE=9)
      2. Values in .env file
      3. Default values defined here

    Usage:
        config = NexusConfig()            # loads from .env in cwd
        config = NexusConfig(_env_file=path)  # loads from explicit path
    """

    # ── Required ────────────────────────────────────────────────────────────
    anthropic_api_key: str

    # ── Review thresholds ───────────────────────────────────────────────────
    min_copy_score: int = 7
    min_tech_score: int = 6
    min_compliance_score: int = 8
    min_performance_score: int = 6

    # ── Pipeline control ────────────────────────────────────────────────────
    max_review_attempts: int = 3
    review_model: str = "claude-sonnet-4-20250514"

    # ── Paths ────────────────────────────────────────────────────────────────
    output_dir: str = "output"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="NEXUS_",
        env_file_encoding="utf-8",
    )
