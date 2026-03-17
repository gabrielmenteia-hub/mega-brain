"""Tests for mis.platform_ids — centralized platform ID constants (INFRA-02).

Verifies that all 12 platform ID constants are present, importable,
and consistent with the IDs inserted by migration _006.
"""
import sqlite_utils
import pytest

import mis.platform_ids as platform_ids
from mis.db import run_migrations


def test_all_constants_importable():
    """Importing HOTMART_PLATFORM_ID from mis.platform_ids must not raise ImportError."""
    from mis.platform_ids import HOTMART_PLATFORM_ID  # noqa: F401
    assert HOTMART_PLATFORM_ID is not None


def test_ids_match_db(db_path):
    """For each constant in platform_ids, the ID must exist as a row in platforms."""
    run_migrations(db_path)
    db = sqlite_utils.Database(db_path)
    existing_ids = {
        row[0] for row in db.execute("SELECT id FROM platforms")
    }
    constants = {
        name: getattr(platform_ids, name)
        for name in dir(platform_ids)
        if name.endswith("_PLATFORM_ID")
    }
    for name, pid in constants.items():
        assert pid in existing_ids, (
            f"Constant {name}={pid} has no matching row in platforms table"
        )


def test_hotmart_id_is_1():
    """HOTMART_PLATFORM_ID must equal 1 (canonical Hotmart ID)."""
    assert platform_ids.HOTMART_PLATFORM_ID == 1


def test_all_12_constants_present():
    """platform_ids module must export exactly 12 *_PLATFORM_ID constants."""
    constants = [
        name for name in dir(platform_ids) if name.endswith("_PLATFORM_ID")
    ]
    assert len(constants) == 12, (
        f"Expected 12 PLATFORM_ID constants, found {len(constants)}: {constants}"
    )
