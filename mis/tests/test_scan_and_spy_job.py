"""Tests for mis/scheduler.py — _scan_and_spy_job() pipeline.

Two test scenarios covering BUG-03:
    test_scan_and_spy_saves_products    — verifies save_batch_with_alerts() is called
    test_scan_and_spy_triggers_spy_pipeline — verifies run_spy_batch receives product IDs
"""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def test_scan_and_spy_saves_products():
    """_scan_and_spy_job() must call save_batch_with_alerts() to persist products before spy."""
    mock_product = MagicMock()
    mock_product.platform_id = 1
    mock_product.external_id = "TEST001"
    mock_product.rank = 1

    scanner_results = {"hotmart.digital": [mock_product]}

    with patch("mis.scheduler.run_all_scanners", new=AsyncMock(return_value=scanner_results)), \
         patch("mis.scheduler.save_batch_with_alerts") as mock_save, \
         patch("mis.scheduler.get_db") as mock_get_db, \
         patch("mis.scheduler.run_spy_batch", new=AsyncMock(return_value=None)):

        # Simulate DB returning a row after save
        mock_db = MagicMock()
        mock_db.execute.return_value = iter([[42]])
        mock_get_db.return_value = mock_db

        asyncio.run(__import__("mis.scheduler", fromlist=["_scan_and_spy_job"])._scan_and_spy_job())

    assert mock_save.called, "save_batch_with_alerts() must be called to persist products before spy"


def test_scan_and_spy_triggers_spy_pipeline():
    """_scan_and_spy_job() must call run_spy_batch with a non-empty list of product dicts with 'id' key."""
    mock_product = MagicMock()
    mock_product.platform_id = 1
    mock_product.external_id = "TEST002"
    mock_product.rank = 1

    scanner_results = {"hotmart.digital": [mock_product]}

    spy_calls = []

    async def capture_spy_batch(products):
        spy_calls.extend(products)

    with patch("mis.scheduler.run_all_scanners", new=AsyncMock(return_value=scanner_results)), \
         patch("mis.scheduler.save_batch_with_alerts"), \
         patch("mis.scheduler.get_db") as mock_get_db, \
         patch("mis.scheduler.run_spy_batch", side_effect=capture_spy_batch):

        # Simulate DB returning a row with db id=99 after save
        mock_db = MagicMock()
        mock_db.execute.return_value = iter([[99]])
        mock_get_db.return_value = mock_db

        asyncio.run(__import__("mis.scheduler", fromlist=["_scan_and_spy_job"])._scan_and_spy_job())

    assert len(spy_calls) > 0, "run_spy_batch must receive at least one product"
    assert all("id" in p for p in spy_calls), "each product dict must have an 'id' key"
