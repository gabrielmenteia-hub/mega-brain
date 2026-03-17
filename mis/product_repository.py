"""Product persistence layer for MIS.

Provides upsert_product() and save_batch() for storing scraped products
into the SQLite database using a composite unique key (platform_id, external_id).

The products table uses 'id' as autoincrement PK (from migration _001), but
deduplication is done by (platform_id, external_id). We implement this via
a manual UPDATE-then-INSERT pattern so the constraint is enforced in Python
without requiring a schema migration that changes the PK.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

import sqlite_utils
import structlog

if TYPE_CHECKING:
    from .scanner import Product

log = structlog.get_logger(__name__)


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
