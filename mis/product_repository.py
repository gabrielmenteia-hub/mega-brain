"""Product persistence layer for MIS.

Provides upsert_product() and save_batch() for storing scraped products
into the SQLite database using a composite primary key (platform_id, external_id).
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
    """Upsert a single product using (platform_id, external_id) as PK.

    Updates all fields including updated_at on conflict.
    Requires migration _002 to have been run (adds rank, commission_pct,
    rating, thumbnail_url, updated_at columns).

    Args:
        db:      sqlite-utils Database instance (from get_db()).
        product: Product dataclass to persist.
    """
    from .scanner import Product as ProductClass  # noqa: F401 (type check only)

    record = {
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
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    db["products"].upsert(
        record,
        pk=("platform_id", "external_id"),
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
