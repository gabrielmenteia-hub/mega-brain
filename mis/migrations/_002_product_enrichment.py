"""Migration 002 — Product enrichment columns.

Adds rank, commission_pct, rating, thumbnail_url, updated_at columns
to the existing products table.

Idempotent: each column is added only if it does not already exist.
Safe to run multiple times without side effects or errors.
"""
import sqlite_utils


def run_migration_002(db_path: str) -> None:
    """Apply product enrichment migration.

    Adds the following columns to products table if absent:
        rank           (int)   — position in ranking list
        commission_pct (float) — affiliate commission percentage
        rating         (float) — average user rating
        thumbnail_url  (str)   — URL of product thumbnail image
        updated_at     (str)   — ISO-8601 timestamp of last upsert

    Args:
        db_path: Path to the SQLite database file.
    """
    db = sqlite_utils.Database(db_path)

    # Ensure products table exists (migration _001 must run first)
    if "products" not in db.table_names():
        raise RuntimeError(
            "products table not found — run migration _001 first"
        )

    existing_cols = {col.name for col in db["products"].columns}

    columns_to_add: list[tuple[str, type]] = [
        ("rank", int),
        ("commission_pct", float),
        ("rating", float),
        ("thumbnail_url", str),
        ("updated_at", str),
    ]

    for col_name, col_type in columns_to_add:
        if col_name not in existing_cols:
            db["products"].add_column(col_name, col_type)
