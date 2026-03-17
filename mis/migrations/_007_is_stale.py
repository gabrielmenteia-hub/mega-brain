"""Migration 007 — is_stale column on products table.

Adds is_stale BOOLEAN DEFAULT FALSE to the products table.
This column tracks whether a product's data became stale because
a scanner returned an empty result (marketplace_unavailable).

Used by mark_stale() in product_repository to flag products that
were NOT refreshed in the latest scan cycle.

Idempotent: safe to run multiple times.
"""
import sqlite_utils


def run_migration_007(db_path: str) -> None:
    """Apply is_stale column migration.

    Adds is_stale BOOLEAN DEFAULT FALSE to products if not present.

    Args:
        db_path: Path to the SQLite database file.
    """
    db = sqlite_utils.Database(db_path)

    if "products" in db.table_names():
        existing_cols = {col.name for col in db["products"].columns}
        if "is_stale" not in existing_cols:
            db["products"].add_column("is_stale", bool, not_null_default=False)

    db.conn.commit()
