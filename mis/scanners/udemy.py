"""Udemy top courses scanner via REST API v2.0 (with graceful fallback).

Fetches top courses per niche from Udemy's affiliate REST API.
Authenticates with Basic Auth (UDEMY_CLIENT_ID + UDEMY_CLIENT_SECRET env vars).

IMPORTANT: Udemy Affiliate API was officially discontinued on 2025-01-01.
The endpoint may return 401/403/404. Scanner handles this gracefully:
- API returns 401/403/404 -> return [] with alert='api_discontinued'
- Credentials absent -> return [] with alert='missing_credentials'

When API is available (legacy tokens may still work):
- external_id = str(course["id"]) — numeric ID as string, stable
- rank = ordinal position in most-reviewed ordering (1=top)
- rank_type = 'enrollment' (most-reviewed ordering reflects enrollment)
- price = price_detail.amount in USD (float or None)
- rating = avg_rating 0-5 scale (float or None)
- thumbnail_url = image_480x270 field
- url = "https://www.udemy.com" + course["url"] (API returns relative paths)

NOTE: This is a stub implementation (TDD RED phase).
scan_niche() checks credentials and makes GET request, handles errors,
but does NOT parse the response body (returns [] intentionally).
Full implementation is in plan 15-02.
"""
from __future__ import annotations

import base64
import os

import structlog

from mis.scanner import PlatformScanner, Product
from mis.platform_ids import UDEMY_PLATFORM_ID

log = structlog.get_logger(__name__)

UDEMY_API_URL = "https://www.udemy.com/api-2.0/courses/"


class UdemyScanner(PlatformScanner):
    """Udemy top courses scanner via REST API v2.0.

    Uses Basic Auth with UDEMY_CLIENT_ID:UDEMY_CLIENT_SECRET.
    Gracefully handles API deprecation (2025-01-01) via fallback on 401/403/404.

    external_id = str(course id) — numeric ID as string
    rank = position in most-reviewed ordering
    price = price_detail.amount USD (float or None)
    rating = avg_rating 0-5 (float or None)
    thumbnail_url = image_480x270
    """

    async def scan_niche(
        self,
        niche_slug: str,
        platform_slug: str,
        niche_id: int = 0,
    ) -> list[Product]:
        """Scan Udemy for top courses in a category and return ranked products.

        NOTE: This is a STUB implementation for TDD RED phase.
        Checks credentials; if present, makes GET request; handles
        HTTP errors (especially 401 for deprecated API) but does NOT
        parse the response body (returns [] intentionally).
        Full parse implementation is in plan 15-02.

        Args:
            niche_slug:    MIS niche slug (e.g. "marketing-digital") — for logging
            platform_slug: Udemy category (e.g. "Marketing", "Health & Fitness")
            niche_id:      FK to niches table (default 0)

        Returns:
            [] always in stub phase (RED). Will return products after GREEN implementation.
        """
        import httpx as _httpx

        client_id = os.environ.get("UDEMY_CLIENT_ID")
        client_secret = os.environ.get("UDEMY_CLIENT_SECRET")

        if not client_id or not client_secret:
            log.warning(
                "udemy_scanner.missing_credentials",
                alert="missing_credentials",
                niche=niche_slug,
                platform_slug=platform_slug,
                reason="UDEMY_CLIENT_ID or UDEMY_CLIENT_SECRET not set",
            )
            return []

        credentials = base64.b64encode(
            f"{client_id}:{client_secret}".encode()
        ).decode()
        headers = {
            "Authorization": f"Basic {credentials}",
            "Accept": "application/json",
        }
        params = {
            "search": niche_slug,
            "ordering": "most-reviewed",
            "category": platform_slug,
            "page_size": 20,
            "fields[course]": "id,title,url,price_detail,avg_rating,image_480x270",
        }

        try:
            client: _httpx.AsyncClient = self._base._client
            response = await client.get(
                UDEMY_API_URL,
                headers=headers,
                params=params,
            )
            response.raise_for_status()
        except _httpx.HTTPStatusError as exc:
            if exc.response.status_code in (401, 403, 404):
                log.warning(
                    "udemy_scanner.api_discontinued",
                    alert="api_discontinued",
                    niche=niche_slug,
                    platform_slug=platform_slug,
                    status_code=exc.response.status_code,
                    reason="Udemy Affiliate API deprecated 2025-01-01",
                )
                return []
            log.error(
                "udemy_scanner.fetch_failed",
                niche=niche_slug,
                platform_slug=platform_slug,
                status_code=exc.response.status_code,
                error=str(exc),
            )
            return []
        except Exception as exc:
            log.error(
                "udemy_scanner.fetch_failed",
                niche=niche_slug,
                platform_slug=platform_slug,
                error=str(exc),
            )
            return []

        # Intentional stub return — full parse in plan 15-02
        return []
