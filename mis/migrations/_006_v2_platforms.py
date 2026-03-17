"""Migration 006 — v2.0 platform rows + rank_type column.

Inserts all 12 MIS platforms into the platforms table using INSERT OR IGNORE.
Also adds rank_type column to platforms table if not present.

Idempotent: safe to run multiple times.
IDs here MUST match constants in mis/platform_ids.py.
"""
from datetime import datetime
import sqlite_utils


_PLATFORMS = [
    (1,  "Hotmart",      "hotmart",      "https://hotmart.com",            "positional"),
    (2,  "ClickBank",    "clickbank",    "https://www.clickbank.com",       "gravity"),
    (3,  "Kiwify",       "kiwify",       "https://kiwify.com.br",           "positional"),
    (4,  "Eduzz",        "eduzz",        "https://eduzz.com",               "positional"),
    (5,  "Monetizze",    "monetizze",    "https://monetizze.com.br",        "positional"),
    (6,  "PerfectPay",   "perfectpay",   "https://perfectpay.com.br",       "positional"),
    (7,  "Braip",        "braip",        "https://braip.com",               "positional"),
    (8,  "Product Hunt", "product_hunt", "https://www.producthunt.com",     "upvotes"),
    (9,  "Udemy",        "udemy",        "https://www.udemy.com",           "enrollment"),
    (10, "JVZoo",        "jvzoo",        "https://www.jvzoo.com",           "gravity"),
    (11, "Gumroad",      "gumroad",      "https://gumroad.com",             "positional"),
    (12, "AppSumo",      "appsumo",      "https://appsumo.com",             "positional"),
]


def run_migration_006(db_path: str) -> None:
    """Apply v2.0 platform rows migration.

    1. Adds rank_type column to platforms table if not present.
    2. Inserts 12 platform rows with INSERT OR IGNORE (idempotent).

    Args:
        db_path: Path to the SQLite database file.
    """
    db = sqlite_utils.Database(db_path)

    # Add rank_type column to platforms if not present (idempotent)
    if "platforms" in db.table_names():
        existing_cols = {col.name for col in db["platforms"].columns}
        if "rank_type" not in existing_cols:
            db["platforms"].add_column("rank_type", str)

    # Insert platform rows — INSERT OR IGNORE ensures idempotency
    created_at = datetime.utcnow().isoformat()
    for pid, name, slug, base_url, rank_type in _PLATFORMS:
        db.execute(
            "INSERT OR IGNORE INTO platforms (id, name, slug, base_url, rank_type, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (pid, name, slug, base_url, rank_type, created_at),
        )
    db.conn.commit()
