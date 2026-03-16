"""MIS/MEGABRAIN bridge — único ponto de integração entre os dois sistemas.

Funções públicas:
    get_briefing_data()        -> dict com dados para /mis-briefing
    export_to_megabrain(dest)  -> dict com resultado da exportação

Import deste módulo chama run_migrations() automaticamente, garantindo
que o DB esteja sempre atualizado antes de qualquer uso.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import pathlib
import sqlite3
from datetime import datetime, timezone, timedelta
from typing import Any

import structlog

log = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# DB initialisation on import (idempotente)
# ---------------------------------------------------------------------------


def _init_db() -> None:
    """Call run_migrations() on import to ensure DB schema is up-to-date.

    Swallows all exceptions — if the DB path does not exist yet or migrations
    fail, the error will surface later in the actual data-access calls.
    """
    db_path = os.environ.get("MIS_DB_PATH", "data/mis.db")
    try:
        from mis.db import run_migrations

        run_migrations(db_path)
        log.debug("mis_agent.init_db.ok", db_path=db_path)
    except Exception as exc:
        log.warning("mis_agent.init_db.skipped", error=str(exc))


_init_db()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_briefing_data() -> dict[str, Any]:
    """Aggregate MIS data for the /mis-briefing dashboard view.

    Queries:
    - Top-10 products ordered by opportunity_score DESC
    - Top-5 pains per niche (from latest pain_report)
    - Count of unseen alerts
    - Health score (0-100) based on scraper canary, data freshness, and dossier count

    Returns:
        dict with keys:
            status           'ok' | 'error'
            products         list[dict] — top-10 by opportunity_score
            pains_by_niche   dict[niche_slug -> list[dict]] — top-5 pains per niche
            unseen_alerts    int
            health           dict — score (0-100) and component breakdown
            last_cycle       str | None — ISO timestamp of most recent dossier
            data_stale       bool — True if last_cycle > 2h ago
            db_path          str

    On any exception, returns:
        {'status': 'error', 'message': str, 'setup_hint': str}
    """
    db_path = os.environ.get("MIS_DB_PATH", "data/mis.db")

    try:
        from mis.dossier_repository import list_dossiers_by_rank
        from mis.alert_repository import get_unseen_count
        from mis.health_monitor import run_canary_check
        from mis.config import load_config
        from mis.pain_repository import get_latest_report

        # --- Top-10 products by opportunity_score ---
        # list_dossiers_by_rank uses p.{order_by} prefix (products table only).
        # opportunity_score lives in dossiers, so we fetch more rows and
        # sort in Python to get the correct top-10 by opportunity.
        raw_products = list_dossiers_by_rank(
            db_path,
            order_by="rank",
            order_dir="asc",
            per_page=100,
        )
        products = sorted(
            raw_products,
            key=lambda r: (r.get("opportunity_score") or 0.0),
            reverse=True,
        )[:10]

        # --- Pains by niche ---
        pains_by_niche: dict[str, list[dict]] = {}
        try:
            cfg = load_config()
            niches = cfg.get("niches", [])
            # Resolve niche IDs from DB (niches may not have ids in config)
            with sqlite3.connect(db_path) as conn:
                for niche in niches:
                    slug = niche.get("slug", "")
                    row = conn.execute(
                        "SELECT id FROM niches WHERE slug = ?", [slug]
                    ).fetchone()
                    if row is None:
                        continue
                    niche_id = row[0]
                    report = get_latest_report(db_path, niche_id)
                    if report is None:
                        pains_by_niche[slug] = []
                        continue
                    # Extract pains from parsed report JSON
                    report_data = report.get("report") or {}
                    raw_pains = report_data.get("pains", [])
                    top5 = raw_pains[:5]
                    pains_by_niche[slug] = [
                        {
                            "title": p.get("title", ""),
                            "interest_level": p.get("interest_level", 0),
                            "language": niche.get("language", "pt"),
                        }
                        for p in top5
                    ]
        except Exception as pains_exc:
            log.warning("mis_agent.pains.error", error=str(pains_exc))
            # pains_by_niche stays as partially built dict or empty

        # --- Unseen alerts ---
        try:
            unseen_alerts = get_unseen_count(db_path)
        except Exception:
            unseen_alerts = 0

        # --- Last cycle (most recent dossier generated_at) ---
        last_cycle: str | None = None
        try:
            with sqlite3.connect(db_path) as conn:
                row = conn.execute(
                    "SELECT MAX(generated_at) FROM dossiers"
                ).fetchone()
                last_cycle = row[0] if row and row[0] else None
        except Exception:
            last_cycle = None

        # --- Data stale flag ---
        data_stale = True
        if last_cycle:
            try:
                lc_dt = datetime.fromisoformat(last_cycle)
                if lc_dt.tzinfo is None:
                    lc_dt = lc_dt.replace(tzinfo=timezone.utc)
                data_stale = (datetime.now(timezone.utc) - lc_dt) > timedelta(hours=2)
            except Exception:
                data_stale = True

        # --- Health score (0-100) ---
        health = asyncio.run(_compute_health(
            db_path=db_path,
            last_cycle=last_cycle,
            data_stale=data_stale,
            unseen_alerts=unseen_alerts,
            run_canary_check=run_canary_check,
        ))

        return {
            "status": "ok",
            "products": products,
            "pains_by_niche": pains_by_niche,
            "unseen_alerts": unseen_alerts,
            "health": health,
            "last_cycle": last_cycle,
            "data_stale": data_stale,
            "db_path": db_path,
        }

    except Exception as exc:
        log.error("mis_agent.get_briefing_data.error", error=str(exc))
        return {
            "status": "error",
            "message": str(exc),
            "setup_hint": "Execute python -m mis para inicializar.",
        }


async def _compute_health(
    db_path: str,
    last_cycle: str | None,
    data_stale: bool,
    unseen_alerts: int,
    run_canary_check: Any,
) -> dict[str, Any]:
    """Compute a 0-100 health score from component checks.

    Components:
        scraper_ok   (40 pts) — run_canary_check() returns True
        cycle_fresh  (30 pts) — last_cycle within 2h
        dossiers_today (20 pts) — at least one dossier created today
        alerts_ok    (10 pts) — always 10 (no critical alert failure tracking yet)

    Returns:
        dict with keys: score, scraper_ok, cycle_fresh, dossiers_today, alerts_ok
    """
    # Scraper canary (async) — await directly, no nested asyncio.run
    scraper_ok = False
    try:
        scraper_ok = await run_canary_check()
    except Exception:
        scraper_ok = False

    scraper_pts = 40 if scraper_ok else 0
    cycle_pts = 30 if not data_stale else 0

    # Dossiers created today
    dossiers_today = False
    try:
        today_str = datetime.now(timezone.utc).date().isoformat()
        with sqlite3.connect(db_path) as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM dossiers WHERE generated_at >= ?",
                [today_str],
            ).fetchone()
            dossiers_today = (row[0] > 0) if row else False
    except Exception:
        dossiers_today = False

    dossiers_pts = 20 if dossiers_today else 0
    alerts_pts = 10  # conservative: no critical failure detection yet

    score = scraper_pts + cycle_pts + dossiers_pts + alerts_pts

    return {
        "score": score,
        "scraper_ok": scraper_ok,
        "cycle_fresh": not data_stale,
        "dossiers_today": dossiers_today,
        "alerts_ok": True,
    }


def export_to_megabrain(dest: str | None = None) -> dict[str, Any]:
    """Export dossiers and pain reports as Markdown files to the MEGABRAIN knowledge base.

    Idempotency: each file is only written (or overwritten) if the MD5 of its
    rendered content differs from the existing file. Files with unchanged
    content are counted as ``skipped``.

    Args:
        dest: Destination directory path. Resolution order:
              1. ``dest`` parameter
              2. ``$MEGABRAIN_PATH/knowledge/mis``
              3. Raises ValueError if neither is available.

    Returns:
        dict with keys:
            status    'ok' | 'error'
            exported  int — files written (new or updated)
            skipped   int — files unchanged
            dest      str — resolved destination path

    On any exception, returns:
        {'status': 'error', 'message': str, 'setup_hint': str}
    """
    db_path = os.environ.get("MIS_DB_PATH", "data/mis.db")

    try:
        # --- Resolve destination ---
        if dest is None:
            megabrain_path = os.environ.get("MEGABRAIN_PATH", "")
            if not megabrain_path:
                raise ValueError(
                    "dest parameter is required when MEGABRAIN_PATH env var is not set."
                )
            dest = str(pathlib.Path(megabrain_path) / "knowledge" / "mis")

        dest_path = pathlib.Path(dest)
        dest_path.mkdir(parents=True, exist_ok=True)

        exported = 0
        skipped = 0

        # --- Export dossiers ---
        sql = """
            SELECT
                d.id          AS dossier_id,
                d.dossier_json,
                d.opportunity_score,
                d.confidence_score,
                d.created_at,
                d.generated_at,
                p.id          AS product_id,
                p.external_id,
                p.title       AS product_name,
                pl.slug       AS platform_slug,
                n.slug        AS niche_slug
            FROM dossiers d
            JOIN products p  ON p.id  = d.product_id
            JOIN platforms pl ON pl.id = p.platform_id
            JOIN niches    n  ON n.id  = p.niche_id
            WHERE d.status = 'done'
        """
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute(sql)
            columns = [desc[0] for desc in cursor.description]
            dossier_rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

        for row in dossier_rows:
            filename = f"dossier_{row['platform_slug']}_{row['external_id']}.md"
            file_path = dest_path / filename

            content = _render_dossier_markdown(row)
            new_hash = _md5(content)

            if file_path.exists():
                existing_hash = _md5(file_path.read_text(encoding="utf-8"))
                if existing_hash == new_hash:
                    skipped += 1
                    log.debug(
                        "mis_agent.export_file.skipped",
                        file=str(file_path),
                        type="dossier",
                    )
                    continue

            file_path.write_text(content, encoding="utf-8")
            exported += 1
            log.info(
                "mis_agent.export_file",
                file=str(file_path),
                type="dossier",
            )

        # --- Export pain reports (last 7 days) ---
        cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        pain_sql = """
            SELECT
                pr.id,
                pr.niche_id,
                pr.cycle_at,
                pr.report_json,
                pr.created_at,
                n.slug AS niche_slug
            FROM pain_reports pr
            JOIN niches n ON n.id = pr.niche_id
            WHERE pr.created_at >= ?
        """
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute(pain_sql, [cutoff])
            columns = [desc[0] for desc in cursor.description]
            pain_rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

        for row in pain_rows:
            # Format date from cycle_at (ISO timestamp -> YYYYMMDD)
            try:
                date_str = row["cycle_at"][:10].replace("-", "")
            except (TypeError, IndexError):
                date_str = "00000000"

            filename = f"pain_{row['niche_slug']}_{date_str}.md"
            file_path = dest_path / filename

            content = _render_pain_markdown(row)
            new_hash = _md5(content)

            if file_path.exists():
                existing_hash = _md5(file_path.read_text(encoding="utf-8"))
                if existing_hash == new_hash:
                    skipped += 1
                    log.debug(
                        "mis_agent.export_file.skipped",
                        file=str(file_path),
                        type="pain_report",
                    )
                    continue

            file_path.write_text(content, encoding="utf-8")
            exported += 1
            log.info(
                "mis_agent.export_file",
                file=str(file_path),
                type="pain_report",
            )

        # --- README summary ---
        readme_path = dest_path / "README.md"
        readme_content = _render_readme(dest_path, exported, skipped)
        readme_path.write_text(readme_content, encoding="utf-8")

        log.info(
            "mis_agent.export_to_megabrain.complete",
            exported=exported,
            skipped=skipped,
            dest=str(dest_path),
        )
        return {
            "status": "ok",
            "exported": exported,
            "skipped": skipped,
            "dest": str(dest_path),
        }

    except Exception as exc:
        log.error("mis_agent.export_to_megabrain.error", error=str(exc))
        return {
            "status": "error",
            "message": str(exc),
            "setup_hint": "Execute python -m mis para inicializar.",
        }


# ---------------------------------------------------------------------------
# Rendering helpers (private)
# ---------------------------------------------------------------------------


def _md5(text: str) -> str:
    """Return MD5 hex digest of a UTF-8 encoded string."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def _render_dossier_markdown(row: dict) -> str:
    """Render a dossier row as a Markdown document with YAML frontmatter.

    Args:
        row: Dict with dossier fields from the export query.

    Returns:
        Markdown string with frontmatter and structured sections.
    """
    dossier_data: dict = {}
    if row.get("dossier_json"):
        try:
            dossier_data = json.loads(row["dossier_json"])
        except (json.JSONDecodeError, TypeError):
            dossier_data = {}

    date_str = (row.get("generated_at") or row.get("created_at") or "")[:10]
    score = row.get("opportunity_score") or 0.0

    frontmatter = (
        "---\n"
        f"source: mis\n"
        f"type: dossier\n"
        f"platform: {row.get('platform_slug', '')}\n"
        f"niche: {row.get('niche_slug', '')}\n"
        f"score: {score}\n"
        f"date: {date_str}\n"
        f"product_id: {row.get('product_id', '')}\n"
        "---\n"
    )

    sections = [
        frontmatter,
        f"# {row.get('product_name', 'Produto')}\n",
        "## Por que Vende\n",
        f"{dossier_data.get('why_sells', '_Sem dados_')}\n",
        "## Copy\n",
        f"{dossier_data.get('copy', '_Sem dados_')}\n",
        "## Anuncios\n",
        f"{json.dumps(dossier_data.get('ads', []), ensure_ascii=False, indent=2)}\n",
        "## Reviews\n",
        f"{json.dumps(dossier_data.get('reviews', []), ensure_ascii=False, indent=2)}\n",
        "## Template\n",
        f"{dossier_data.get('template', '_Sem dados_')}\n",
    ]
    return "\n".join(sections)


def _render_pain_markdown(row: dict) -> str:
    """Render a pain_report row as a Markdown document with YAML frontmatter.

    Args:
        row: Dict with pain_report fields from the export query.

    Returns:
        Markdown string with frontmatter and pains list.
    """
    report_data: dict = {}
    if row.get("report_json"):
        try:
            report_data = json.loads(row["report_json"])
        except (json.JSONDecodeError, TypeError):
            report_data = {}

    date_str = (row.get("cycle_at") or "")[:10]
    niche_slug = row.get("niche_slug", "unknown")

    frontmatter = (
        "---\n"
        f"source: mis\n"
        f"type: pain_report\n"
        f"niche: {niche_slug}\n"
        f"date: {date_str}\n"
        "---\n"
    )

    pains = report_data.get("pains", [])
    pains_section = "\n".join(
        f"- **{p.get('title', '')}** (interest: {p.get('interest_level', 0)})"
        for p in pains
    ) or "_Sem dores identificadas_"

    return f"{frontmatter}\n# Pain Report — {niche_slug}\n\n## Dores Identificadas\n\n{pains_section}\n"


def _render_readme(dest_path: pathlib.Path, exported: int, skipped: int) -> str:
    """Render a README.md summary for the export directory.

    Args:
        dest_path: Path to the export directory.
        exported:  Number of files written in this run.
        skipped:   Number of files unchanged in this run.

    Returns:
        Markdown string summarising the export.
    """
    now_str = datetime.now(timezone.utc).isoformat()
    # Count total files in dest (excluding README itself)
    total = sum(1 for f in dest_path.iterdir() if f.is_file() and f.name != "README.md")

    return (
        "# MIS Knowledge Export\n\n"
        f"**Last export:** {now_str}\n\n"
        f"| Metric | Value |\n"
        f"|--------|-------|\n"
        f"| Files exported (this run) | {exported} |\n"
        f"| Files skipped (unchanged) | {skipped} |\n"
        f"| Total files in directory  | {total} |\n"
    )
