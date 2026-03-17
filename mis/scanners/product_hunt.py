"""Product Hunt trending scanner via GraphQL API v2.

Fetches today's trending products from Product Hunt using the GraphQL v2 API.
Authenticates with Bearer token (PRODUCT_HUNT_API_TOKEN env var).

Paginates up to 2 pages (first: 20 per page) for top 40 products.
rank = position (1=top), NOT votesCount.
external_id = slug (e.g. 'jarvis-ai-assistant') — stable and readable.
price = None always (Product Hunt API does not return monetary price).
thumbnail_url = thumbnail.url (Media.url — NOT imageUrl, which does not exist in schema).

Graceful degradation:
- PRODUCT_HUNT_API_TOKEN absent -> return [] with alert='missing_credentials'
- API error / schema drift -> return [] with structured error log

NOTE: This is a stub implementation (TDD RED phase).
scan_niche() checks credentials but does NOT parse responses.
Full implementation is in plan 15-02.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import structlog

from mis.scanner import PlatformScanner, Product
from mis.platform_ids import PRODUCT_HUNT_PLATFORM_ID

log = structlog.get_logger(__name__)

PRODUCT_HUNT_GRAPHQL_URL = "https://api.producthunt.com/v2/api/graphql"

# GraphQL query for today's trending products.
# Source: github.com/producthunt/producthunt-api/blob/master/schema.graphql
# CRITICAL: thumbnail uses { url } — NOT { imageUrl } (Media type has url: String!)
TRENDING_TODAY_QUERY = """
query TrendingToday($after: String) {
  posts(
    featured: true
    postedAfter: "%s"
    postedBefore: "%s"
    order: VOTES
    first: 20
    after: $after
  ) {
    edges {
      node {
        id
        name
        tagline
        slug
        url
        votesCount
        thumbnail {
          url
        }
      }
    }
    pageInfo {
      endCursor
      hasNextPage
    }
  }
}
"""


def _build_query_with_dates() -> str:
    """Build TRENDING_TODAY_QUERY with today's UTC date range substituted."""
    today = datetime.now(timezone.utc)
    posted_after = today.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    posted_before = today.replace(hour=23, minute=59, second=59, microsecond=0).isoformat()
    return TRENDING_TODAY_QUERY % (posted_after, posted_before)


class ProductHuntScanner(PlatformScanner):
    """Product Hunt trending scanner via GraphQL API v2.

    Fetches today's trending posts using Bearer token authentication.
    Paginates up to 2 pages (top 40 products).

    external_id = slug (stable, readable)
    rank = ordinal position (1=first in trending)
    price = None (Product Hunt does not expose monetary price in public API)
    """

    async def scan_niche(
        self,
        niche_slug: str,
        platform_slug: str,
        niche_id: int = 0,
    ) -> list[Product]:
        """Scan Product Hunt trending today and return ranked products.

        NOTE: This is a STUB implementation for TDD RED phase.
        Credentials are checked; if present, makes a GraphQL POST but
        does NOT parse the response (returns [] intentionally).
        Full parse implementation is in plan 15-02.

        Args:
            niche_slug:    MIS niche slug (ignored — PH returns global trending)
            platform_slug: Platform-specific slug (ignored — PH is niche-agnostic)
            niche_id:      FK to niches table (default 0)

        Returns:
            [] always in stub phase (RED). Will return products after GREEN implementation.
        """
        token = os.environ.get("PRODUCT_HUNT_API_TOKEN")
        if not token:
            log.warning(
                "product_hunt_scanner.missing_credentials",
                alert="missing_credentials",
                niche=niche_slug,
                reason="PRODUCT_HUNT_API_TOKEN not set",
            )
            return []

        query = _build_query_with_dates()

        try:
            # Stub: make the POST request but do NOT parse response
            await self._post_graphql(query, variables={})
        except Exception as exc:
            log.error(
                "product_hunt_scanner.fetch_failed",
                niche=niche_slug,
                platform_slug=platform_slug,
                error=str(exc),
            )
            return []

        # Intentional stub return — full parse in plan 15-02
        return []

    async def _post_graphql(self, query: str, variables: dict) -> str:
        """POST GraphQL query to the Product Hunt API v2 endpoint.

        Args:
            query:     GraphQL query string
            variables: GraphQL variables dict

        Returns:
            Response text string.

        Raises:
            Exception: if request fails (propagated to caller)
        """
        import httpx as _httpx

        client: _httpx.AsyncClient = self._base._client

        headers = {
            "Authorization": f"Bearer {os.environ.get('PRODUCT_HUNT_API_TOKEN', '')}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = json.dumps({"query": query, "variables": variables})

        response = await client.post(
            PRODUCT_HUNT_GRAPHQL_URL,
            content=payload,
            headers=headers,
        )
        response.raise_for_status()
        return response.text
