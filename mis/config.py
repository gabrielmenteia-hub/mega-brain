"""Config loader for MIS niche configuration.

Loads mis/config.yaml, validates niche count (3-5), and applies
.env overrides (e.g. PROXY_URL).

Extended in Phase 2 to validate platform slugs per niche and
read new settings: max_products_per_niche, scan_schedule, parallel_scanners.
"""
from pathlib import Path
import os
import yaml
import structlog
from dotenv import load_dotenv

load_dotenv()

log = structlog.get_logger(__name__)

CONFIG_PATH = Path(__file__).parent / "config.yaml"

VALID_PLATFORMS = {
    # v1.0
    "hotmart", "clickbank", "kiwify",
    # v2.0 BR
    "eduzz", "monetizze", "perfectpay", "braip",
    # v2.0 International
    "product_hunt", "udemy", "jvzoo", "gumroad", "appsumo",
}

SETTINGS_DEFAULTS = {
    "proxy_url": "",
    "request_delay_s": 2.0,
    "max_retries": 3,
    "max_products_per_niche": 50,
    "scan_schedule": "0 3 * * *",
    "parallel_scanners": True,
}


def load_config(config_path: Path | None = None) -> dict:
    """Load and validate the niche configuration file.

    Args:
        config_path: Optional path override — defaults to mis/config.yaml.
                     Useful for tests without needing to mock CONFIG_PATH.

    Returns:
        dict with keys "niches" (list) and "settings" (dict).

    Raises:
        ValueError: If niche count is not between 3 and 5, any niche is
                    missing a "slug" field, any platform name is invalid,
                    or a niche has a platforms block with zero valid platforms.
        FileNotFoundError: If config_path does not exist.
    """
    path = config_path or CONFIG_PATH
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    niches = cfg.get("niches", [])
    if not (3 <= len(niches) <= 5):
        raise ValueError(
            f"config.yaml must define 3-5 niches, got {len(niches)}"
        )

    for niche in niches:
        if not niche.get("slug"):
            raise ValueError(
                f"Each niche must have a 'slug' field. Missing in: {niche}"
            )

        # Phase 2: validate platforms block (backward compatible — optional)
        platforms = niche.get("platforms")
        if platforms is None:
            log.warning(
                "config.niche.no_platforms_block",
                niche=niche["slug"],
            )
            continue

        # Validate platform names (typos like 'hotmrt' raise ValueError)
        invalid = set(platforms.keys()) - VALID_PLATFORMS
        if invalid:
            raise ValueError(
                f"Niche '{niche['slug']}' has invalid platform(s): {invalid}. "
                f"Valid platforms: {VALID_PLATFORMS}"
            )

        # At least one platform must be mapped
        if not platforms:
            raise ValueError(
                f"Niche '{niche['slug']}' has an empty platforms block. "
                "At least one platform must be configured."
            )

    # Apply .env PROXY_URL override
    proxy = os.getenv("PROXY_URL", "").strip()
    if proxy:
        cfg.setdefault("settings", {})["proxy_url"] = proxy

    # Apply settings defaults for new keys (backward compatible)
    settings = cfg.setdefault("settings", {})
    for key, default_val in SETTINGS_DEFAULTS.items():
        if key not in settings:
            settings[key] = default_val

    return cfg
