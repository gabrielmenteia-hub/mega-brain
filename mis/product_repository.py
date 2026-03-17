"""Product persistence layer for MIS.

Provides upsert_product() and save_batch() for storing scraped products
into the SQLite database using a composite unique key (platform_id, external_id).

The products table uses 'id' as autoincrement PK (from migration _001), but
deduplication is done by (platform_id, external_id). We implement this via
a manual UPDATE-then-INSERT pattern so the constraint is enforced in Python
without requiring a schema migration that changes the PK.
"""
from __future__ import annotations

import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import sqlite_utils
import structlog

if TYPE_CHECKING:
    from .scanner import Product

log = structlog.get_logger(__name__)

# Minimum number of products a platform must have in a niche to be included
# in the unified ranking calculation.
MIN_PRODUCTS_PER_PLATFORM = 5


def upsert_product(db: sqlite_utils.Database, product: "Product") -> None:
    """Upsert a single product using (platform_id, external_id) as unique key.

    Strategy:
        1. Try to UPDATE existing row by (platform_id, external_id).
        2. If rowcount == 0, INSERT a new row.

    This correctly handles the case where the products table has 'id' as
    autoincrement PK (from migration _001) while deduplication is by composite
    key (platform_id, external_id).

    Args:
        db:      sqlite-utils Database instance (from get_db()).
        product: Product dataclass to persist.
    """
    updated_at = datetime.now(timezone.utc).isoformat()

    # Attempt UPDATE first
    cursor = db.execute(
        """
        UPDATE products
           SET title          = :title,
               url            = :url,
               niche_id       = :niche_id,
               rank           = :rank,
               price          = :price,
               commission_pct = :commission_pct,
               rating         = :rating,
               thumbnail_url  = :thumbnail_url,
               is_stale       = 0,
               updated_at     = :updated_at
         WHERE platform_id = :platform_id
           AND external_id = :external_id
        """,
        {
            "platform_id": product.platform_id,
            "external_id": product.external_id,
            "title": product.title,
            "url": product.url,
            "niche_id": product.niche_id,
            "rank": product.rank,
            "price": product.price,
            "commission_pct": product.commission_pct,
            "rating": product.rating,
            "thumbnail_url": product.thumbnail_url,
            "updated_at": updated_at,
        },
    )

    if cursor.rowcount == 0:
        # No existing row — INSERT
        db["products"].insert(
            {
                "platform_id": product.platform_id,
                "external_id": product.external_id,
                "title": product.title,
                "url": product.url,
                "niche_id": product.niche_id,
                "rank": product.rank,
                "price": product.price,
                "commission_pct": product.commission_pct,
                "rating": product.rating,
                "thumbnail_url": product.thumbnail_url,
                "is_stale": 0,
                "updated_at": updated_at,
            },
            alter=True,
        )


def save_batch(db: sqlite_utils.Database, products: list["Product"]) -> None:
    """Upsert a batch of products.

    Guard: if products list is empty, logs a warning and returns without
    touching the DB — preserves existing data on schema drift.

    Args:
        db:       sqlite-utils Database instance (from get_db()).
        products: List of Product dataclasses to persist.
    """
    if not products:
        log.warning("product_repository.save_batch.zero_products_detected")
        return

    for product in products:
        upsert_product(db, product)

    log.info(
        "product_repository.save_batch.saved",
        count=len(products),
    )


def mark_stale(db: sqlite_utils.Database, platform_id: int, niche_id: int) -> None:
    """Mark all products for a platform+niche as is_stale=True.

    Called by fallback scanners when scan_niche() returns [].
    Preserves existing data — apenas marca como desatualizado.

    Args:
        db:          sqlite-utils Database instance.
        platform_id: FK da plataforma.
        niche_id:    FK do nicho.
    """
    db.execute(
        "UPDATE products SET is_stale = 1 WHERE platform_id = ? AND niche_id = ?",
        [platform_id, niche_id],
    )
    log.info(
        "product_repository.mark_stale",
        platform_id=platform_id,
        niche_id=niche_id,
    )


# ---------------------------------------------------------------------------
# Unified Ranking
# ---------------------------------------------------------------------------

def _normalize_title(title: str) -> str:
    """Return a canonical form of title for cross-platform matching.

    Applies NFKD decomposition, strips non-ASCII bytes, lowercases, and strips
    leading/trailing whitespace so "Café Marketing" and "cafe marketing" compare equal.
    """
    return (
        unicodedata.normalize("NFKD", title)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
        .strip()
    )


def _compute_unified_scores(rows: list[dict]) -> list[dict]:
    """Compute unified_score for every row in a single-platform group.

    For ``positional`` rank_type the score is percentile-based:
        score = (1 - rank / total) * 100

    For ``gravity``, ``upvotes``, and ``enrollment`` the score is relative
    to the maximum value in the group:
        score = (rank / max_val) * 100

    Args:
        rows: List of product dicts for one platform group.  Each dict must
              have keys ``rank`` (float) and ``rank_type`` (str).

    Returns:
        The same list with ``unified_score`` key added to every dict.
    """
    if not rows:
        return rows

    rank_type = rows[0]["rank_type"]
    total = len(rows)

    if rank_type == "positional":
        for row in rows:
            row["unified_score"] = round((1 - row["rank"] / total) * 100, 1)
    else:
        # gravity / upvotes / enrollment — higher is better
        max_val = max(row["rank"] for row in rows)
        for row in rows:
            if max_val > 0:
                row["unified_score"] = round((row["rank"] / max_val) * 100, 1)
            else:
                row["unified_score"] = 0.0

    return rows


def list_unified_ranking(
    db_path: str,
    niche: str | None,
    multi_platform_only: int,
    per_page: int,
    page: int,
) -> dict:
    """Return a unified ranking of products across all platforms for a niche.

    Products are normalised to a 0-100 ``unified_score`` using percentile
    ranking within each platform group so that positional ranks (rank #1 is
    best) and gravity/upvotes/enrollment ranks (higher is better) are
    comparable.

    Algorithm
    ---------
    1. Fetch all products with rank IS NOT NULL (optionally filtered by niche).
    2. Group by platform_slug.
    3. Drop groups with fewer than MIN_PRODUCTS_PER_PLATFORM products.
    4. Compute unified_score per group.
    5. Flatten into a single list; detect warning_single_platform.
    6. If multi_platform_only: keep only products whose normalised title
       appears in 2+ platforms.
    7. Sort by unified_score DESC, then rank ASC (tiebreaker).
    8. Count total (pre-pagination).
    9. Paginate in Python (NEVER in SQL — Pitfall 1).
    10. Fetch niches list + last_updated for template context.
    11. Return result dict.

    Args:
        db_path:              Absolute path to the SQLite database file.
        niche:                Niche slug to filter by, or None for all niches.
        multi_platform_only:  Non-zero to keep only multi-platform titles.
        per_page:             Page size.
        page:                 1-based page number.

    Returns:
        Dict with keys: products, total, warning_single_platform, niches,
        last_updated, selected_niche, multi_platform_only, per_page, page.
    """
    db = sqlite_utils.Database(db_path)

    # ------------------------------------------------------------------
    # Step 1: Fetch all qualifying products (no LIMIT — Pitfall 1)
    # ------------------------------------------------------------------
    params: list = []
    where_clauses: list[str] = ["p.rank IS NOT NULL"]

    if niche:
        where_clauses.append("n.slug = ?")
        params.append(niche)

    where_sql = "WHERE " + " AND ".join(where_clauses)

    sql = f"""
        SELECT p.id, p.title, pl.name AS platform_name, pl.slug AS platform_slug,
               pl.rank_type, n.name AS niche_name, p.rank, p.is_stale,
               CASE WHEN d.id IS NOT NULL THEN 1 ELSE 0 END AS has_dossier
          FROM products p
          JOIN platforms pl ON pl.id = p.platform_id
          JOIN niches    n  ON n.id  = p.niche_id
     LEFT JOIN dossiers  d  ON d.product_id = p.id
         {where_sql}
      ORDER BY pl.slug, p.rank ASC
    """

    cursor = db.execute(sql, params)
    columns = [desc[0] for desc in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # ------------------------------------------------------------------
    # Step 2: Group by platform_slug
    # ------------------------------------------------------------------
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[row["platform_slug"]].append(row)

    # ------------------------------------------------------------------
    # Step 3: Filter groups with < MIN_PRODUCTS_PER_PLATFORM (Pitfall 2)
    # ------------------------------------------------------------------
    qualified_groups = {
        slug: group
        for slug, group in groups.items()
        if len(group) >= MIN_PRODUCTS_PER_PLATFORM
    }

    # ------------------------------------------------------------------
    # Step 4 + 5: Compute scores and flatten
    # ------------------------------------------------------------------
    all_products: list[dict] = []
    for group in qualified_groups.values():
        scored = _compute_unified_scores(group)
        all_products.extend(scored)

    # Detect single-platform warning
    warning_single_platform: bool = len(qualified_groups) == 1

    # Normalise boolean fields
    for p in all_products:
        p["is_stale"] = bool(p["is_stale"])
        p["has_dossier"] = bool(p["has_dossier"])

    # ------------------------------------------------------------------
    # Step 6: Multi-platform filter
    # ------------------------------------------------------------------
    if bool(multi_platform_only):
        # Map normalised title → set of platform slugs
        title_platforms: dict[str, set[str]] = defaultdict(set)
        for p in all_products:
            title_platforms[_normalize_title(p["title"])].add(p["platform_slug"])

        all_products = [
            p for p in all_products
            if len(title_platforms[_normalize_title(p["title"])]) >= 2
        ]

    # ------------------------------------------------------------------
    # Step 7: Sort by unified_score DESC, rank ASC (tiebreaker)
    # ------------------------------------------------------------------
    all_products.sort(key=lambda r: (-r["unified_score"], r["rank"] or 999_999))

    # ------------------------------------------------------------------
    # Step 8: Total count (before pagination)
    # ------------------------------------------------------------------
    total = len(all_products)

    # ------------------------------------------------------------------
    # Step 9: Paginate in Python
    # ------------------------------------------------------------------
    offset = (page - 1) * per_page
    paginated = all_products[offset : offset + per_page]

    # ------------------------------------------------------------------
    # Step 10: Niches list + last_updated
    # ------------------------------------------------------------------
    try:
        niches_rows = db.execute("SELECT slug, name FROM niches ORDER BY name").fetchall()
        niches_list = [{"slug": row[0], "name": row[1]} for row in niches_rows]
    except Exception:
        niches_list = []

    try:
        row = db.execute("SELECT MAX(updated_at) FROM products").fetchone()
        last_updated = row[0] if row else None
    except Exception:
        last_updated = None

    # ------------------------------------------------------------------
    # Step 11: Return
    # ------------------------------------------------------------------
    return {
        "products": paginated,
        "total": total,
        "warning_single_platform": warning_single_platform,
        "niches": niches_list,
        "last_updated": last_updated,
        "selected_niche": niche,
        "multi_platform_only": multi_platform_only,
        "per_page": per_page,
        "page": page,
    }
