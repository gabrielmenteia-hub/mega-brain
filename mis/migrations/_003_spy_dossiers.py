"""Migration 003 — Spy dossiers schema expansion.

Extends the dossiers table with spy-specific columns and creates two new
tables (reviews, llm_calls) required by the Phase 3 espionage pipeline.

Idempotent: uses add_column() checks and IF NOT EXISTS guards throughout.
Safe to run multiple times without side effects or errors.
"""
import sqlite_utils


def run_migration_003(db_path: str) -> None:
    """Apply spy dossiers migration.

    Adds the following columns to dossiers table if absent:
        status       (str)  — 'pending'|'running'|'done'|'failed'
        dossier_json (str)  — canonical structured JSON dossier
        ads_json     (str)  — Meta Ad Library JSON (MVP: not a separate table)
        incomplete   (int)  — BOOL as int (SQLite); 1 = partial dossier
        updated_at   (str)  — ISO-8601 timestamp of last update

    Creates tables if they do not already exist:
        reviews   — product reviews from any source
        llm_calls — LLM call tracking for cost/audit

    Args:
        db_path: Path to the SQLite database file.

    Raises:
        RuntimeError: If dossiers table is absent (migration _001 must run first).
    """
    db = sqlite_utils.Database(db_path)

    if "dossiers" not in db.table_names():
        raise RuntimeError(
            "dossiers table not found — run migration _001 first"
        )

    # --- Extend dossiers table (additive, never DROP) ---
    existing_cols = {col.name for col in db["dossiers"].columns}
    new_cols: dict[str, type] = {
        "status": str,       # 'pending'|'running'|'done'|'failed'
        "dossier_json": str, # JSON estruturado (campo canônico)
        "ads_json": str,     # JSON dos anúncios Meta Ad Library (MVP)
        "incomplete": int,   # BOOL como int (SQLite)
        "updated_at": str,
    }
    for col_name, col_type in new_cols.items():
        if col_name not in existing_cols:
            db["dossiers"].add_column(col_name, col_type)

    # --- Create reviews table if it does not exist ---
    if "reviews" not in db.table_names():
        db["reviews"].create(
            {
                "id": int,
                "product_id": int,
                "text": str,
                "valence": str,    # 'positive'|'negative'
                "rating": float,
                "source": str,     # 'hotmart'|'clickbank'|'kiwify'|'google'|'sales_page'
                "created_at": str,
            },
            pk="id",
            foreign_keys=[("product_id", "products", "id")],
        )
        db.execute(
            "CREATE INDEX IF NOT EXISTS idx_reviews_product_valence "
            "ON reviews(product_id, valence)"
        )

    # --- Create llm_calls table if it does not exist ---
    if "llm_calls" not in db.table_names():
        db["llm_calls"].create(
            {
                "id": int,
                "dossier_id": int,
                "model": str,
                "stage": str,
                "input_tokens": int,
                "output_tokens": int,
                "cost_usd": float,
                "created_at": str,
            },
            pk="id",
            foreign_keys=[("dossier_id", "dossiers", "id")],
        )
