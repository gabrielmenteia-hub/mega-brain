"""Tests for mis/niche_repository.py — list_niches, list_subniches, get_platform_slug.

These tests are written RED first (TDD): they fail with ImportError because
niche_repository.py does not exist yet. Plan 02 implements the repository.

Covers:
  NICHE-01: list_niches returns 4 items with correct structure
  NICHE-01: list_subniches('saude') returns at least 10 subniches
  NICHE-02: get_platform_slug returns correct slug per platform or None
"""
import pytest

from mis.niche_repository import list_niches, list_subniches, get_platform_slug
from mis.db import run_migrations


def test_list_niches_returns_4(db_path):
    """list_niches() must return exactly 4 niches after run_migrations()."""
    run_migrations(db_path)
    niches = list_niches(db_path)
    assert len(niches) == 4, f"Expected 4 niches, got {len(niches)}"


def test_list_niches_structure(db_path):
    """Each niche returned by list_niches() must have 'id', 'name', 'slug' keys."""
    run_migrations(db_path)
    niches = list_niches(db_path)
    assert len(niches) > 0, "list_niches() returned empty list"
    for niche in niches:
        assert "id" in niche, f"Niche missing 'id' key: {niche}"
        assert "name" in niche, f"Niche missing 'name' key: {niche}"
        assert "slug" in niche, f"Niche missing 'slug' key: {niche}"


def test_list_subniches_saude(db_path):
    """list_subniches(db_path, 'saude') must return at least 10 subniches."""
    run_migrations(db_path)
    subniches = list_subniches(db_path, "saude")
    assert len(subniches) >= 10, (
        f"Expected at least 10 subniches for 'saude', got {len(subniches)}"
    )


def test_list_subniches_unknown_niche(db_path):
    """list_subniches() for a non-existent niche slug must return an empty list."""
    run_migrations(db_path)
    subniches = list_subniches(db_path, "nicho-inexistente")
    assert subniches == [], (
        f"Expected empty list for unknown niche, got {subniches}"
    )


def test_get_platform_slug_hotmart(db_path):
    """get_platform_slug(db_path, 201, 'hotmart') must return 'saude-e-fitness'.

    subniche_id=201 is Emagrecimento.
    """
    run_migrations(db_path)
    slug = get_platform_slug(db_path, 201, "hotmart")
    assert slug == "saude-e-fitness", (
        f"Expected 'saude-e-fitness' for subniche 201 on hotmart, got '{slug}'"
    )


def test_get_platform_slug_clickbank(db_path):
    """get_platform_slug(db_path, 201, 'clickbank') must return 'health'.

    subniche_id=201 is Emagrecimento.
    """
    run_migrations(db_path)
    slug = get_platform_slug(db_path, 201, "clickbank")
    assert slug == "health", (
        f"Expected 'health' for subniche 201 on clickbank, got '{slug}'"
    )


def test_get_platform_slug_unknown_platform_returns_none(db_path):
    """get_platform_slug() for a platform with no mapping must return None.

    PerfectPay has no marketplace search — no subniche_platform_slugs row expected.
    """
    run_migrations(db_path)
    slug = get_platform_slug(db_path, 201, "perfectpay")
    assert slug is None, (
        f"Expected None for subniche 201 on perfectpay (unmapped platform), got '{slug}'"
    )


def test_get_platform_slug_unknown_subniche_returns_none(db_path):
    """get_platform_slug() for a non-existent subniche_id must return None."""
    run_migrations(db_path)
    slug = get_platform_slug(db_path, 9999, "hotmart")
    assert slug is None, (
        f"Expected None for unknown subniche_id=9999, got '{slug}'"
    )
