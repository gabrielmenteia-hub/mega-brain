"""Migration 004 — Pain Radar schema.

Creates three new tables for the Phase 4 Pain Radar pipeline:
  pain_signals     — raw signals collected from Reddit, Quora, YouTube, Trends
  pain_reports     — synthesized reports per niche per cycle
  youtube_quota_log — daily quota usage tracking for YouTube Data API

Idempotent: uses IF NOT EXISTS guards throughout.
Safe to run multiple times without side effects or errors.
"""
import sqlite_utils


def run_migration_004(db_path: str) -> None:
    """Apply Pain Radar migration.

    Creates the following tables if they do not already exist:

        pain_signals:
            id           (int PK autoincrement)
            url_hash     (str UNIQUE) — SHA-256 of the URL; used for upsert
            url          (str)
            title        (str)
            source       (str) — 'reddit'|'quora'|'youtube'|'google_trends'
            niche_slug   (str)
            score        (int) — upvotes / view_count / peak_index / 0 for Quora
            extra_json   (str) — JSON with source-specific fields
            collected_at (str) — ISO-8601 timestamp

        pain_reports:
            id          (int PK autoincrement)
            niche_id    (int FK -> niches.id)
            cycle_at    (str) — ISO-8601 truncated to minute
            report_json (str)
            created_at  (str) — ISO-8601

        youtube_quota_log:
            id         (int PK autoincrement)
            units      (int)
            operation  (str) — 'search.list'|'commentThreads.list'|'videos.list'
            logged_at  (str) — ISO-8601

    Args:
        db_path: Path to the SQLite database file.
    """
    db = sqlite_utils.Database(db_path)

    # --- pain_signals ---
    if "pain_signals" not in db.table_names():
        db["pain_signals"].create(
            {
                "id": int,
                "url_hash": str,
                "url": str,
                "title": str,
                "source": str,
                "niche_slug": str,
                "score": int,
                "extra_json": str,
                "collected_at": str,
            },
            pk="id",
            not_null={"url_hash", "url", "source", "niche_slug"},
        )
        db.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_pain_signals_url_hash "
            "ON pain_signals(url_hash)"
        )
        db.execute(
            "CREATE INDEX IF NOT EXISTS idx_pain_signals_niche_collected "
            "ON pain_signals(niche_slug, collected_at)"
        )

    # --- pain_reports ---
    if "pain_reports" not in db.table_names():
        db["pain_reports"].create(
            {
                "id": int,
                "niche_id": int,
                "cycle_at": str,
                "report_json": str,
                "created_at": str,
            },
            pk="id",
            not_null={"niche_id", "cycle_at"},
        )
        db.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_pain_reports_niche_cycle "
            "ON pain_reports(niche_id, cycle_at)"
        )

    # --- youtube_quota_log ---
    if "youtube_quota_log" not in db.table_names():
        db["youtube_quota_log"].create(
            {
                "id": int,
                "units": int,
                "operation": str,
                "logged_at": str,
            },
            pk="id",
            not_null={"units", "operation", "logged_at"},
        )
        db.execute(
            "CREATE INDEX IF NOT EXISTS idx_youtube_quota_log_at "
            "ON youtube_quota_log(logged_at)"
        )
