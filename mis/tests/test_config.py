"""Tests for mis.config — niche config loader.

Coverage: FOUND-03
"""
import pytest
import yaml
from pathlib import Path
from mis.config import load_config


def test_load_3_niches(temp_config_yaml):
    # temp_config_yaml fixture returns a str path to a tmp yaml with 3 niches
    cfg = load_config(config_path=Path(temp_config_yaml))
    assert len(cfg["niches"]) == 3


def test_too_many_niches(tmp_path):
    yaml_path = tmp_path / "config.yaml"
    data = {
        "niches": [
            {"name": f"Niche {i}", "slug": f"niche-{i}", "keywords": []}
            for i in range(6)
        ],
        "settings": {"proxy_url": "", "request_delay_s": 2.0, "max_retries": 3},
    }
    yaml_path.write_text(yaml.dump(data), encoding="utf-8")
    with pytest.raises(ValueError, match="3-5"):
        load_config(config_path=yaml_path)


def test_proxy_env_override(temp_config_yaml, monkeypatch):
    monkeypatch.setenv("PROXY_URL", "http://proxy:8080")
    cfg = load_config(config_path=Path(temp_config_yaml))
    assert cfg["settings"]["proxy_url"] == "http://proxy:8080"
