"""Initial database migration — creates the 5 core MIS tables.

Idempotent: each table is created only if it does not already exist.
Safe to run multiple times without side effects.
"""
import sqlite_utils


def run_migrations(db_path: str) -> None:
    """Apply initial schema. Creates 5 tables if they do not already exist.

    Tables created:
        platforms  — scraping source platforms (Hotmart, Kiwify, etc.)
        niches     — target market niches
        products   — scraped product listings (FK -> platforms, niches)
        pains      — market pain points and community signals (FK -> niches)
        dossiers   — AI-generated product analysis (FK -> products)

    Args:
        db_path: Path to the SQLite database file (use ':memory:' for tests).
    """
    db = sqlite_utils.Database(db_path)

    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")

    if "platforms" not in db.table_names():
        db["platforms"].create(
            {
                "id": int,
                "name": str,
                "slug": str,
                "base_url": str,
                "created_at": str,
            },
            pk="id",
            not_null={"name", "slug"},
        )
        db["platforms"].create_index(["slug"], unique=True)

    if "niches" not in db.table_names():
        db["niches"].create(
            {
                "id": int,
                "name": str,
                "slug": str,
                "created_at": str,
            },
            pk="id",
            not_null={"name", "slug"},
        )
        db["niches"].create_index(["slug"], unique=True)

    if "products" not in db.table_names():
        db["products"].create(
            {
                "id": int,
                "platform_id": int,
                "niche_id": int,
                "external_id": str,
                "title": str,
                "url": str,
                "rank_score": float,
                "price": float,
                "currency": str,
                "scraped_at": str,
                "raw_data": str,  # JSON blob for future-proofing
            },
            pk="id",
            foreign_keys=[
                ("platform_id", "platforms", "id"),
                ("niche_id", "niches", "id"),
            ],
        )
        db["products"].create_index(["platform_id", "niche_id", "scraped_at"])

    if "pains" not in db.table_names():
        db["pains"].create(
            {
                "id": int,
                "niche_id": int,
                "source": str,       # reddit, quora, youtube, trends
                "content": str,
                "sentiment": str,    # positive, negative, neutral
                "detected_at": str,
            },
            pk="id",
            foreign_keys=[
                ("niche_id", "niches", "id"),
            ],
        )

    if "dossiers" not in db.table_names():
        db["dossiers"].create(
            {
                "id": int,
                "product_id": int,
                "analysis": str,           # JSON: factors, pains, template
                "opportunity_score": float,
                "confidence_score": float,
                "generated_at": str,
            },
            pk="id",
            foreign_keys=[
                ("product_id", "products", "id"),
            ],
        )
