"""Config loader for MIS niche configuration.

Loads mis/config.yaml, validates niche count (3-5), and applies
.env overrides (e.g. PROXY_URL).
"""
from pathlib import Path
import os
import yaml
from dotenv import load_dotenv

load_dotenv()

CONFIG_PATH = Path(__file__).parent / "config.yaml"


def load_config(config_path: Path | None = None) -> dict:
    """Load and validate the niche configuration file.

    Args:
        config_path: Optional path override — defaults to mis/config.yaml.
                     Useful for tests without needing to mock CONFIG_PATH.

    Returns:
        dict with keys "niches" (list) and "settings" (dict).

    Raises:
        ValueError: If niche count is not between 3 and 5, or any niche is
                    missing a "slug" field.
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
    proxy = os.getenv("PROXY_URL", "").strip()
    if proxy:
        cfg.setdefault("settings", {})["proxy_url"] = proxy
    return cfg
