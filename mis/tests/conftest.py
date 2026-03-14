"""Shared fixtures for mis test suite."""
import pytest
import yaml


@pytest.fixture
def db_path(tmp_path):
    """Return path to a temporary SQLite database file."""
    return str(tmp_path / "mis.db")


@pytest.fixture
def temp_config_yaml(tmp_path):
    """Create a temporary config.yaml with 3 valid niches."""
    config = {
        "niches": [
            {
                "name": "Marketing Digital",
                "slug": "marketing-digital",
                "keywords": ["marketing digital", "trafego pago", "infoproduto"],
            },
            {
                "name": "Emagrecimento",
                "slug": "emagrecimento",
                "keywords": ["emagrecer", "dieta", "perda de peso"],
            },
            {
                "name": "Financas Pessoais",
                "slug": "financas-pessoais",
                "keywords": ["investimento", "renda passiva", "independencia financeira"],
            },
        ],
        "settings": {
            "proxy_url": "",
            "request_delay_s": 2.0,
            "max_retries": 3,
        },
    }
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.dump(config, allow_unicode=True), encoding="utf-8")
    return str(config_path)
