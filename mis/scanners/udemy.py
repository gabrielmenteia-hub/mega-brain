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
"""
from __future__ import annotations

import base64
import os
from typing import Optional

import structlog

from mis.scanner import PlatformScanner, Product
from mis.platform_ids import UDEMY_PLATFORM_ID

log = structlog.get_logger(__name__)

UDEMY_API_URL = "https://www.udemy.com/api-2.0/courses/"


def _parse_course(course: dict, rank: int, niche_id: int) -> Optional[Product]:
    """Parse a Udemy course dict into a Product.

    Args:
        course:   Course dict from Udemy REST API results array.
        rank:     Ordinal position (1-based) in most-reviewed ordering.
        niche_id: FK to niches table.

    Returns:
        Product if course_id present, None otherwise.
    """
    course_id = course.get("id")
    if not course_id:
        return None

    url_path = course.get("url") or ""
    url = "https://www.udemy.com" + url_path

    price_raw = (course.get("price_detail") or {}).get("amount")
    price = float(price_raw) if price_raw is not None else None

    rating_raw = course.get("avg_rating")
    rating = float(rating_raw) if rating_raw is not None else None

    thumbnail_url = course.get("image_480x270") or None

    return Product(
        external_id=str(course_id),
        title=course.get("title") or str(course_id),
        url=url,
        platform_id=UDEMY_PLATFORM_ID,
        niche_id=niche_id,
        rank=rank,
        price=price,
        rating=rating,
        thumbnail_url=thumbnail_url,
    )


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

        Uses platform_slug as the Udemy category (e.g. "Marketing", "Health & Fitness").
        Handles HTTP 401/403/404 as api_discontinued gracefully.

        Args:
            niche_slug:    MIS niche slug (e.g. "marketing-digital") — for logging
            platform_slug: Udemy category (e.g. "Marketing", "Health & Fitness")
            niche_id:      FK to niches table (default 0)

        Returns:
            List of Product objects sorted by rank (1=top).
            Returns [] if credentials missing, API discontinued, or any error occurs.
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
            "search": platform_slug,
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
            log.warning(
                "udemy_scanner.schema_drift",
                alert="schema_drift",
                niche=niche_slug,
                platform_slug=platform_slug,
                status_code=exc.response.status_code,
                error=str(exc),
            )
            return []
        except Exception as exc:
            log.warning(
                "udemy_scanner.schema_drift",
                alert="schema_drift",
                niche=niche_slug,
                platform_slug=platform_slug,
                error=str(exc),
            )
            return []

        data = response.json()
        results = data.get("results") or []

        if not results:
            return []

        products: list[Product] = []
        for rank, course in enumerate(results, start=1):
            product = _parse_course(course, rank=rank, niche_id=niche_id)
            if product is not None:
                products.append(product)

        log.info(
            "udemy_scanner.scan_complete",
            niche=niche_slug,
            platform_slug=platform_slug,
            count=len(products),
        )
        return products
