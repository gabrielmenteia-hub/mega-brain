"""Query functions for the v3 niche/subniche hierarchy.

All functions accept a db_path string and return plain dicts.
The database must have been initialised with run_migrations() before
any of these functions are called.

Exported functions:
    list_niches       - return all top-level niches
    list_subniches    - return subniches for a given niche slug
    get_platform_slug - return the search slug for a subniche on a platform
"""
import sqlite_utils


def list_niches(db_path: str) -> list[dict]:
    """Return all v3 niches ordered by id.

    Args:
        db_path: Path to the SQLite database file.

    Returns:
        List of dicts with keys 'id', 'name', 'slug', ordered by id.
        Returns an empty list if the niches_v3 table has no rows.
    """
    db = sqlite_utils.Database(db_path)
    rows = db.execute("SELECT id, name, slug FROM niches_v3 ORDER BY id").fetchall()
    return [{"id": r[0], "name": r[1], "slug": r[2]} for r in rows]


def list_subniches(db_path: str, niche_slug: str) -> list[dict]:
    """Return all subniches for a given niche slug, ordered by id.

    Args:
        db_path: Path to the SQLite database file.
        niche_slug: The slug of the parent niche (e.g. 'saude').

    Returns:
        List of dicts with keys 'id', 'name', 'slug', ordered by id.
        Returns an empty list if the niche slug does not exist.
    """
    db = sqlite_utils.Database(db_path)
    rows = db.execute(
        """
        SELECT s.id, s.name, s.slug
          FROM subniches s
          JOIN niches_v3 n ON n.id = s.niche_id
         WHERE n.slug = ?
         ORDER BY s.id
        """,
        [niche_slug],
    ).fetchall()
    return [{"id": r[0], "name": r[1], "slug": r[2]} for r in rows]


def get_platform_slug(db_path: str, subniche_id: int, platform_slug: str) -> str | None:
    """Return the search slug for a subniche on a specific platform.

    Args:
        db_path: Path to the SQLite database file.
        subniche_id: The integer ID of the subniche (e.g. 201 for Emagrecimento).
        platform_slug: The slug of the platform (e.g. 'hotmart', 'clickbank').

    Returns:
        The search_slug string if a mapping exists, or None if the subniche or
        platform has no mapping in subniche_platform_slugs.
    """
    db = sqlite_utils.Database(db_path)
    row = db.execute(
        """
        SELECT sps.search_slug
          FROM subniche_platform_slugs sps
          JOIN platforms pl ON pl.id = sps.platform_id
         WHERE sps.subniche_id = ? AND pl.slug = ?
        """,
        [subniche_id, platform_slug],
    ).fetchone()
    return row[0] if row else None
