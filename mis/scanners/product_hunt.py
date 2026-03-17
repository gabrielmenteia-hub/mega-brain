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
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Optional

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


def _parse_post(node: dict, rank: int, niche_id: int) -> Optional[Product]:
    """Parse a GraphQL post node into a Product.

    Args:
        node:     GraphQL post node dict with id, name, slug, url, thumbnail fields.
        rank:     Ordinal position (1-based) in trending list.
        niche_id: FK to niches table.

    Returns:
        Product if slug present, None otherwise (nodes without slug are skipped).
    """
    slug = node.get("slug")
    if not slug:
        return None

    thumbnail_data = node.get("thumbnail") or {}
    thumbnail_url = thumbnail_data.get("url") or None

    url = node.get("url") or f"https://www.producthunt.com/posts/{slug}"

    return Product(
        external_id=slug,
        title=node.get("name") or slug,
        url=url,
        platform_id=PRODUCT_HUNT_PLATFORM_ID,
        niche_id=niche_id,
        rank=rank,
        price=None,
        thumbnail_url=thumbnail_url,
    )


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

        Authenticates with Bearer token. Paginates up to 2 pages if hasNextPage=true.
        rank = ordinal position (1=top), NOT votesCount.
        price = None always (PH does not expose monetary price in public API).

        Args:
            niche_slug:    MIS niche slug (ignored — PH returns global trending)
            platform_slug: Platform-specific slug (ignored — PH is niche-agnostic)
            niche_id:      FK to niches table (default 0)

        Returns:
            List of Product objects sorted by rank (1=top trending).
            Returns [] if credentials missing or any error occurs.
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
        products: list[Product] = []
        rank_counter = 1

        # Page 1: after=None
        try:
            response_text = await self._post_graphql(query, variables={"after": None})
            data = json.loads(response_text)
            posts_data = data.get("data", {}).get("posts", {})
            edges = posts_data.get("edges") or []
            page_info = posts_data.get("pageInfo") or {}

            for edge in edges:
                node = edge.get("node") or {}
                product = _parse_post(node, rank=rank_counter, niche_id=niche_id)
                if product is not None:
                    products.append(product)
                    rank_counter += 1

            # Page 2: if hasNextPage=True
            has_next = page_info.get("hasNextPage", False)
            end_cursor = page_info.get("endCursor")

            if has_next and end_cursor:
                try:
                    response_text2 = await self._post_graphql(
                        query, variables={"after": end_cursor}
                    )
                    data2 = json.loads(response_text2)
                    posts_data2 = data2.get("data", {}).get("posts", {})
                    edges2 = posts_data2.get("edges") or []

                    for edge in edges2:
                        node = edge.get("node") or {}
                        product = _parse_post(node, rank=rank_counter, niche_id=niche_id)
                        if product is not None:
                            products.append(product)
                            rank_counter += 1
                except Exception as exc:
                    log.error(
                        "product_hunt_scanner.schema_drift",
                        alert="schema_drift",
                        niche=niche_slug,
                        page=2,
                        error=str(exc),
                    )

        except Exception as exc:
            log.error(
                "product_hunt_scanner.schema_drift",
                alert="schema_drift",
                niche=niche_slug,
                error=str(exc),
            )
            return []

        log.info(
            "product_hunt_scanner.scan_complete",
            niche=niche_slug,
            count=len(products),
        )
        return products

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
