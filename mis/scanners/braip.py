"""Braip marketplace scanner via Nuxt.js SSR parsing.

URL: https://marketplace.braip.com/search?categorySlug={slug}

Braip uses Nuxt 2 SSR — product data is embedded in the page as:
    window.__NUXT__ = (function(a,b,c,...){...})(arg1,arg2,...);

This is a JavaScript IIFE (Immediately Invoked Function Expression) with
variable substitution. The parser resolves the argument bindings and extracts
state.search.products from the returned object.

external_id = "hash" field (e.g. "proown9j") — most stable identifier.
price = centavos integer / 100.0 (e.g. 2990 -> R$29.90)

Fallback: if NUXT data cannot be parsed, returns [] with alert='schema_drift'.
Only page 1 (top ~12 products) is fetched — pagination is a future enhancement.
"""
from __future__ import annotations

import json
import re
from typing import Optional

import structlog

from mis.scanner import PlatformScanner, Product
from mis.platform_ids import BRAIP_PLATFORM_ID

log = structlog.get_logger(__name__)

BRAIP_MARKETPLACE_URL = "https://marketplace.braip.com/search"
# Braip uses Nuxt.js SSR — data embedded via window.__NUXT__ (Nuxt 2 IIFE format)
# or window.__NUXT_DATA__ (Nuxt 3 array format). Fixture confirms Nuxt 2 is active.


def _resolve_iife_vars(iife_text: str) -> Optional[dict]:
    """Extract the variable binding map from a window.__NUXT__ IIFE.

    Parses:
        window.__NUXT__ = (function(a,b,c,...){ ... })(arg1,arg2,...);

    Returns a dict mapping variable names to their resolved Python values,
    or None if the IIFE structure cannot be parsed.
    """
    # Extract parameter names from function definition
    params_match = re.search(r'window\.__NUXT__=\(function\(([^)]+)\)', iife_text)
    if not params_match:
        return None
    params = [p.strip() for p in params_match.group(1).split(",")]

    # Extract call arguments from the IIFE invocation at the end
    # The closing pattern is: }}}}(arg1,arg2,...));
    # Use a flexible pattern for varying numbers of closing braces
    args_match = re.search(r'\}\}\}\}\((.+?)\)\);', iife_text, re.DOTALL)
    if not args_match:
        return None

    args_raw = args_match.group(1)

    # Parse args as JSON array (Braip uses JSON-compatible literals)
    # {} placeholders are valid JSON objects
    try:
        args = json.loads("[" + args_raw + "]")
    except json.JSONDecodeError:
        return None

    if len(args) != len(params):
        return None

    return dict(zip(params, args))


def _parse_nuxt_products(html: str, niche_id: int) -> list[Product]:
    """Parse products from Braip window.__NUXT__ SSR state.

    Handles Nuxt 2 IIFE format (window.__NUXT__ = (function(...){})(args)).
    Falls back to window.__NUXT_DATA__ check (Nuxt 3) but returns [] as
    Nuxt 3 array format is not yet implemented (fixture confirms Nuxt 2).

    Returns [] if no recognized format is found.
    """
    # Locate the <script> block containing window.__NUXT__
    idx = html.find("window.__NUXT__")
    if idx == -1:
        # Check for Nuxt 3 format (not yet implemented)
        if "window.__NUXT_DATA__" in html:
            # Nuxt 3 format detected but not parsed — caller will emit schema_drift
            return []
        return []

    end_script = html.find("</script>", idx)
    if end_script == -1:
        end_script = len(html)
    iife_text = html[idx:end_script]

    # Resolve variable bindings from the IIFE
    var_map = _resolve_iife_vars(iife_text)
    if var_map is None:
        return []

    # Extract the products array using regex
    # Pattern: products:[{...}],categories: (within the IIFE body)
    prod_match = re.search(r"products:\[(\{.+?\})\],categories:", iife_text, re.DOTALL)
    if not prod_match:
        return []

    products_raw = "[" + prod_match.group(1) + "]"

    # Convert JS object literal to valid JSON:
    # 1. Quote unquoted object keys
    products_json = re.sub(r"([{,])(\w+):", r'\1"\2":', products_raw)

    # 2. Substitute variable references (single-letter vars used as values)
    #    Pattern: :var followed by , or } (value position, not key position)
    for var, val in sorted(var_map.items(), key=lambda x: -len(x[0])):
        json_val = json.dumps(val)
        products_json = re.sub(
            r":" + re.escape(var) + r"(?=[,\}])",
            ":" + json_val,
            products_json,
        )

    try:
        raw_products = json.loads(products_json)
    except json.JSONDecodeError:
        return []

    return _build_products(raw_products, niche_id)


def _build_products(raw: list[dict], niche_id: int) -> list[Product]:
    """Convert raw Nuxt product dicts to Product dataclasses."""
    products = []
    for rank, item in enumerate(raw, start=1):
        hash_id = item.get("hash")
        if not hash_id:
            continue
        price_cents = item.get("price")
        slug = item.get("slug", hash_id)
        products.append(
            Product(
                external_id=hash_id,
                title=item.get("title") or hash_id,
                url=f"https://marketplace.braip.com/{slug}",
                platform_id=BRAIP_PLATFORM_ID,
                niche_id=niche_id,
                rank=rank,
                price=price_cents / 100.0 if price_cents else None,
                rating=item.get("star") or None,
                thumbnail_url=item.get("src") or None,
            )
        )
    return products


class BraipScanner(PlatformScanner):
    """Braip marketplace scanner via Nuxt.js SSR parsing.

    Fetches https://marketplace.braip.com/search?categorySlug={platform_slug}
    and extracts products from the embedded window.__NUXT__ state object.

    external_id = "hash" field (most stable identifier).
    price = centavos / 100.0 (R$ float).
    Only page 1 (~12 products) is fetched per call.
    """

    async def scan_niche(
        self,
        niche_slug: str,
        platform_slug: str,
        niche_id: int = 0,
    ) -> list[Product]:
        """Scan Braip marketplace for a category and return ranked products.

        Args:
            niche_slug:    MIS niche slug (e.g. "marketing-digital")
            platform_slug: Braip category slug (e.g. "cursos-online")
            niche_id:      FK to niches table (default 0)

        Returns:
            List of Product dataclasses ordered by rank (rank=1 is top).
            Returns [] on schema drift, fetch error, or empty results.
        """
        url = f"{BRAIP_MARKETPLACE_URL}?categorySlug={platform_slug}"
        try:
            html = await self.fetch(url)
        except Exception as exc:
            log.error(
                "braip_scanner.fetch_failed",
                niche=niche_slug,
                platform_slug=platform_slug,
                error=str(exc),
            )
            return []

        products = _parse_nuxt_products(html, niche_id)

        if not products:
            log.warning(
                "braip_scanner.schema_drift",
                alert="schema_drift",
                niche=niche_slug,
                platform_slug=platform_slug,
                url=url,
                reason="window.__NUXT__ not found or state.search.products empty",
            )
            return []

        log.info(
            "braip_scanner.scan_complete",
            niche=niche_slug,
            platform_slug=platform_slug,
            count=len(products),
        )
        return products
