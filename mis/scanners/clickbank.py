"""ClickBank platform scanner.

Scrapes the ClickBank marketplace via GraphQL API (no authentication required).
The marketplace at accounts.clickbank.com uses a React SPA backed by GraphQL.
Product data (including gravity scores) is accessible via POST /graphql without auth.

Platform ID convention:
    1 = Hotmart
    2 = ClickBank  ← this scanner
    3 = Kiwify

Key fields:
    external_id = 'site' field — ClickBank vendor ID (e.g. "BRAINSONGX"), stable and unique
    rank        = int(gravity) when gravity is available; positional (1-indexed) as fallback
    price       = averageDollarsPerSale from marketplaceStats (USD float or None)

Usage:
    async with ClickBankScanner() as scanner:
        products = await scanner.scan_niche("health", "Health & Fitness")
"""
from __future__ import annotations

import json
from typing import Optional

import structlog

from mis.scanner import PlatformScanner, Product

log = structlog.get_logger(__name__)

CLICKBANK_PLATFORM_ID = 2  # Convention: 1=Hotmart, 2=ClickBank, 3=Kiwify
CLICKBANK_GRAPHQL_URL = "https://accounts.clickbank.com/graphql"

# GraphQL query for marketplace search — same query used by the marketplace React app
MARKETPLACE_QUERY = """query ($parameters: MarketplaceSearchParameters!) {
    marketplaceSearch(parameters: $parameters) {
        totalHits
        offset
        hits {
            site
            title
            description
            url
            offerImageUrl
            marketplaceStats {
                category
                gravity
                rank
                biGravity
                averageDollarsPerSale
                initialDollarsPerSale
                activateDate
                standard
                physical
                rebill
                upsell
            }
        }
    }
}"""

# Default number of products per category scan
DEFAULT_RESULTS_PER_PAGE = 50


def _gravity_to_rank(gravity: float | None, positional_rank: int) -> int:
    """Convert gravity score to int rank.

    ClickBank gravity is a float score (higher = more affiliates selling recently).
    We store it as int for the rank field (floor/truncate).

    Falls back to positional rank (1-indexed position in the result list)
    when gravity is None (e.g. missing from response).

    Args:
        gravity:         gravity score from marketplaceStats (float or None)
        positional_rank: 1-indexed position in the sorted result list (fallback)

    Returns:
        int rank value
    """
    if gravity is not None:
        return int(gravity)
    return positional_rank


def _parse_product(
    hit: dict,
    positional_rank: int,
    niche_id: int,
) -> Product | None:
    """Parse a single GraphQL hit into a Product dataclass.

    Args:
        hit:             GraphQL hit object from marketplaceSearch.hits
        positional_rank: 1-indexed position in the result list (fallback rank)
        niche_id:        DB niche ID for the Product dataclass (0 if unknown)

    Returns:
        Product dataclass, or None if the hit is missing required fields.
    """
    site = hit.get("site")
    if not site:
        return None

    title = hit.get("title") or site
    url = hit.get("url") or ""
    if not url:
        return None

    stats = hit.get("marketplaceStats") or {}
    gravity = stats.get("gravity")
    rank = _gravity_to_rank(gravity, positional_rank)

    # price: use averageDollarsPerSale (USD float)
    price_raw = stats.get("averageDollarsPerSale")
    price: Optional[float] = float(price_raw) if price_raw is not None else None

    # thumbnail from offerImageUrl
    thumbnail_url: Optional[str] = hit.get("offerImageUrl") or None

    return Product(
        external_id=site,          # e.g. "BRAINSONGX" — stable vendor ID
        title=title,
        url=url,
        platform_id=CLICKBANK_PLATFORM_ID,
        niche_id=niche_id,
        rank=rank,
        price=price,
        thumbnail_url=thumbnail_url,
    )


class ClickBankScanner(PlatformScanner):
    """ClickBank marketplace scanner using GraphQL API.

    Queries the public ClickBank GraphQL endpoint (no auth required) to fetch
    products sorted by gravity score for a given category.

    Attributes:
        CLICKBANK_PLATFORM_ID: DB platform ID for ClickBank (= 2)
        niche_id:              Override per-scan; default 0 (caller must set)
    """

    def __init__(
        self,
        proxy_url: Optional[str] = None,
        niche_id: int = 0,
    ) -> None:
        super().__init__(proxy_url=proxy_url)
        self._default_niche_id = niche_id

    async def scan_niche(
        self,
        niche_slug: str,
        platform_slug: str,
        niche_id: int = 0,
    ) -> list[Product]:
        """Scan a ClickBank marketplace category and return ranked products.

        Sends a POST request to https://accounts.clickbank.com/graphql with a
        MarketplaceSearchParameters query. Products are sorted by gravity score
        (descending) by default.

        Emits alert='schema_drift' and returns [] when:
        - Response hits list is empty
        - GraphQL response is invalid/unexpected structure

        Never raises exceptions — errors are caught and logged.

        Args:
            niche_slug:    MIS niche slug (e.g. "health") — used for logging
            platform_slug: ClickBank category name (e.g. "Health & Fitness")
            niche_id:      DB niche ID for the Product dataclass (0 if unknown)

        Returns:
            List of Product dataclasses ordered by gravity (desc), or [] on drift/error.
        """
        effective_niche_id = niche_id or self._default_niche_id

        payload = json.dumps({
            "query": MARKETPLACE_QUERY,
            "variables": {
                "parameters": {
                    "category": platform_slug,
                    "sortField": "gravity",
                    "resultsPerPage": DEFAULT_RESULTS_PER_PAGE,
                    "offset": 0,
                }
            },
        })

        try:
            # Use self.fetch() but we need POST — delegate directly to BaseScraper's client
            # BaseScraper.fetch() only supports GET; we access the underlying httpx client
            # via self._base._client for POST requests
            response_text = await self._post_graphql(payload)
        except Exception as exc:
            log.error(
                "clickbank_scanner.fetch_failed",
                niche=niche_slug,
                platform_slug=platform_slug,
                url=CLICKBANK_GRAPHQL_URL,
                error=str(exc),
            )
            return []

        try:
            data = json.loads(response_text)
            marketplace = data["data"]["marketplaceSearch"]
            hits = marketplace.get("hits") or []
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            log.warning(
                "clickbank_scanner.parse_error",
                alert="schema_drift",
                niche=niche_slug,
                platform_slug=platform_slug,
                error=str(exc),
            )
            return []

        if not hits:
            log.warning(
                "clickbank_scanner.empty_results",
                alert="schema_drift",
                niche=niche_slug,
                platform_slug=platform_slug,
                url=CLICKBANK_GRAPHQL_URL,
                total_hits=marketplace.get("totalHits", 0),
            )
            return []

        # Check if gravity is available (log if not, fallback to positional rank)
        first_gravity = (hits[0].get("marketplaceStats") or {}).get("gravity")
        if first_gravity is None:
            log.info(
                "clickbank_scanner.gravity_not_available_using_rank_position",
                niche=niche_slug,
                platform_slug=platform_slug,
            )

        products: list[Product] = []
        for positional_rank, hit in enumerate(hits, start=1):
            product = _parse_product(hit, positional_rank, effective_niche_id)
            if product is not None:
                products.append(product)

        if products:
            log.info(
                "clickbank_scanner.scan_complete",
                niche=niche_slug,
                platform_slug=platform_slug,
                count=len(products),
                gravity_available=(first_gravity is not None),
            )
        else:
            # All hits had missing required fields → treat as schema_drift
            log.warning(
                "clickbank_scanner.all_hits_invalid",
                alert="schema_drift",
                niche=niche_slug,
                platform_slug=platform_slug,
                hits_count=len(hits),
            )

        return products

    async def _post_graphql(self, payload: str) -> str:
        """POST JSON payload to the ClickBank GraphQL endpoint.

        Uses the underlying BaseScraper httpx client (with retry/rate limiting).
        Returns response text string.

        Raises:
            Exception: if request fails after retries (propagated from BaseScraper)
        """
        import httpx as _httpx

        # Access the BaseScraper's httpx client directly for POST support
        # BaseScraper exposes _client after __aenter__ is called
        client: _httpx.AsyncClient = self._base._client

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Referer": "https://accounts.clickbank.com/marketplace.htm",
            "Origin": "https://accounts.clickbank.com",
        }

        response = await client.post(
            CLICKBANK_GRAPHQL_URL,
            content=payload,
            headers=headers,
        )
        response.raise_for_status()
        return response.text
