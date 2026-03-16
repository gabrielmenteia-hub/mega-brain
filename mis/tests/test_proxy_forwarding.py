"""Tests for proxy_list forwarding through PlatformScanner -> BaseScraper chain.

These tests verify FOUND-02 gap closure: PlatformScanner and its subclasses
must accept proxy_list and propagate it to BaseScraper._proxy_list.

Wave 0 (RED): All 5 tests fail before the fix because HotmartScanner,
KiwifyScanner, and ClickBankScanner do not accept proxy_list yet.
"""
from unittest.mock import AsyncMock, patch

import pytest

from mis.scanners.hotmart import HotmartScanner
from mis.scanners.kiwify import KiwifyScanner
from mis.scanners.clickbank import ClickBankScanner


def test_hotmart_accepts_proxy_list():
    """HotmartScanner(proxy_list=...) must not raise TypeError."""
    # RED: TypeError before fix — proxy_list not in __init__ signature
    scanner = HotmartScanner(proxy_url=None, proxy_list=["http://p:8080"])
    assert scanner is not None


def test_kiwify_accepts_proxy_list():
    """KiwifyScanner(proxy_list=...) must not raise TypeError."""
    # RED: TypeError before fix
    scanner = KiwifyScanner(proxy_url=None, proxy_list=["http://p:8080"])
    assert scanner is not None


def test_clickbank_accepts_proxy_list():
    """ClickBankScanner(proxy_list=...) must not raise TypeError."""
    # RED: TypeError before fix
    scanner = ClickBankScanner(proxy_url=None, proxy_list=["http://p:8080"])
    assert scanner is not None


def test_proxy_list_reaches_base_scraper():
    """proxy_list passed to HotmartScanner must arrive in _base._proxy_list."""
    proxy_list = ["http://p1:8080", "http://p2:8080"]
    # RED: proxy_list not forwarded before fix
    scanner = HotmartScanner(proxy_list=proxy_list)
    assert scanner._base._proxy_list == proxy_list


@pytest.mark.asyncio
async def test_run_all_scanners_proxy_list_no_typeerror(tmp_path):
    """run_all_scanners with proxy_list must not raise TypeError."""
    import asyncio
    from mis.scanner import run_all_scanners

    db_path = str(tmp_path / "mis.db")

    # Minimal config with proxy_list populated
    config = {
        "niches": [
            {
                "slug": "emagrecimento",
                "platforms": [{"name": "hotmart", "slug": "saude"}],
            }
        ],
        "settings": {
            "proxy_list": ["http://proxy:8080"],
            "proxy_url": None,
        },
    }

    # Mock all scanner scan_niche methods to avoid real HTTP calls
    with patch("mis.scanners.hotmart.HotmartScanner.scan_niche", new_callable=AsyncMock, return_value=[]):
        # RED: TypeError before fix
        result = await run_all_scanners(config=config, db_path=db_path)
        assert isinstance(result, dict)
