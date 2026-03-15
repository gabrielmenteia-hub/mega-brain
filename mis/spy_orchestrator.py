"""spy_orchestrator — Orchestrates the full product espionage pipeline.

Public API:
    run_spy(product_id, force=False) — Spy a product by its DB ID.
    run_spy_url(url)                 — Spy any URL without a pre-registered product.
    run_spy_batch(products, max_concurrent) — Batch spy with priority queue.

Pipeline per product:
    SalesPageScraper → MetaAdsScraper → ReviewsScraper
    → completeness_gate → analyze_copy → generate_dossier
    → persist dossier in DB

Constants:
    SPY_TOP_N = 10  (hardcoded, not configurable — top products per niche/platform)
"""
import asyncio
import json
import os
from datetime import datetime
from itertools import count
from typing import Optional

import structlog

from .config import load_config
from .db import get_db, run_migrations
from .intelligence.copy_analyzer import analyze_copy, CopyAnalysisError
from .intelligence.dossier_generator import generate_dossier, DossierGenerationError
from .spies.completeness_gate import SpyData, check_completeness
from .spies.meta_ads import MetaAdsScraper
from .spies.reviews import ReviewsScraper
from .spies.sales_page import SalesPageScraper

log = structlog.get_logger()
_spy_counter = count()

# Hardcoded per user decision: top 10 per niche per platform — not configurable
SPY_TOP_N = 10

# Default DB path: env var MIS_DB_PATH → falls back to data/mis.db
_DEFAULT_DB_PATH = "data/mis.db"


def _get_db_path() -> str:
    """Return DB path from env or default."""
    return os.environ.get("MIS_DB_PATH", _DEFAULT_DB_PATH)


def _get_spy_config() -> dict:
    """Return spy-specific config values with defaults."""
    try:
        cfg = load_config()
    except Exception:
        return {"max_concurrent_spy": 3, "min_reviews": 10}
    spy = cfg.get("spy", {})
    return {
        "max_concurrent_spy": spy.get("max_concurrent_spy", 3),
        "min_reviews": spy.get("min_reviews", 10),
    }


async def run_spy(product_id: int, force: bool = False) -> None:
    """Spy a product by its DB ID.

    If a 'done' dossier already exists and force=False, skip silently.
    On any pipeline error, logs alert='spy_failed' and marks status='failed'.

    Args:
        product_id: PK in the products table.
        force: If True, re-spy even if a done dossier exists.
    """
    db_path = _get_db_path()
    run_migrations(db_path)
    db = get_db(db_path)
    spy_cfg = _get_spy_config()

    product = dict(db["products"].get(product_id))

    # Check for existing dossier — skip if done and not forced
    existing = list(db["dossiers"].rows_where("product_id = ?", [product_id]))
    if existing and existing[0]["status"] == "done" and not force:
        log.info("spy.skipped", product_id=product_id, reason="dossier_exists")
        return

    # Create or update dossier record as 'running'
    dossier_id = _upsert_dossier_status(db, product_id, "running")

    try:
        await _execute_spy_pipeline(product, dossier_id, spy_cfg, db_path, db)
    except Exception as e:
        log.error("spy.failed", alert="spy_failed", product_id=product_id, error=str(e))
        _upsert_dossier_status(db, product_id, "failed", dossier_id=dossier_id)


async def run_spy_url(url: str) -> None:
    """Spy any product URL without a pre-registered product.

    Creates a minimal product record in the DB to obtain a product_id,
    then runs the full pipeline. Always re-spies (no skip logic).

    Args:
        url: Full URL of the sales page to spy.
    """
    db_path = _get_db_path()
    run_migrations(db_path)
    db = get_db(db_path)
    spy_cfg = _get_spy_config()

    # Create minimal product if not exists
    existing_products = list(db["products"].rows_where("external_id = ?", [url]))
    if existing_products:
        product_id = existing_products[0]["id"]
        product = dict(existing_products[0])
    else:
        now = datetime.utcnow().isoformat()
        # Temporarily disable FK enforcement to allow null platform/niche for URL-based spy
        db.execute("PRAGMA foreign_keys=OFF")
        product_data = {
            "external_id": url,
            "url": url,
            "title": "",
            "platform_id": None,
            "niche_id": None,
            "rank_score": 0.0,
            "scraped_at": now,
            "raw_data": "{}",
        }
        product_id = db["products"].insert(product_data).last_pk
        db.execute("PRAGMA foreign_keys=ON")
        product = dict(db["products"].get(product_id))

    dossier_id = _upsert_dossier_status(db, product_id, "running")

    try:
        await _execute_spy_pipeline(product, dossier_id, spy_cfg, db_path, db)
    except Exception as e:
        log.error("spy.failed", alert="spy_failed", product_url=url, error=str(e))
        _upsert_dossier_status(db, product_id, "failed", dossier_id=dossier_id)


async def run_spy_batch(products: list[dict], max_concurrent: int = 3) -> None:
    """Execute batch spying with bounded concurrency via semaphore + priority queue.

    Manual products (is_manual=True) get priority=0 (highest).
    Automatic products are ordered by rank (lower rank = higher priority).

    Args:
        products: List of dicts with at least 'id' and 'rank' keys.
                  Optional 'is_manual' key for priority=0.
        max_concurrent: Maximum number of concurrent spy operations.
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    queue: asyncio.PriorityQueue = asyncio.PriorityQueue()

    for p in products:
        priority = 0 if p.get("is_manual") else p.get("rank", 999)
        await queue.put((priority, next(_spy_counter), p["id"]))

    async def _worker():
        while not queue.empty():
            try:
                _, _, product_id = queue.get_nowait()
            except asyncio.QueueEmpty:
                break
            async with semaphore:
                await run_spy(product_id)
            queue.task_done()

    workers = [_worker() for _ in range(max_concurrent)]
    await asyncio.gather(*workers)


# ─── Internal helpers ───────────────────────────────────────────────────────────


async def _execute_spy_pipeline(
    product: dict,
    dossier_id: int,
    spy_cfg: dict,
    db_path: str,
    db,
) -> None:
    """Run the full espionage pipeline for one product.

    Steps:
    1. Collect data (SalesPageScraper, MetaAdsScraper, ReviewsScraper)
    2. Build SpyData container
    3. Run completeness gate
    4. Run LLM pipeline (copy_analyzer → dossier_generator)
    5. Persist dossier to DB

    Raises:
        Any exception from scrapers or LLM pipeline — caller handles logging.
    """
    min_reviews = spy_cfg.get("min_reviews", 10)
    product_url = product.get("url", "")
    product_title = product.get("title", "")
    platform_id = product.get("platform_id", 0)

    # 1. Collect data from all spies
    async with SalesPageScraper() as sp_scraper:
        extracted = await sp_scraper.extract(product_url)

    meta_scraper = MetaAdsScraper()
    ads = await meta_scraper.fetch_ads(product_title)

    async with ReviewsScraper() as rev_scraper:
        reviews = await rev_scraper.collect(
            platform=_platform_slug(platform_id),
            product_url=product_url,
            product_title=product_title,
        )

    # 2. Build SpyData
    full_copy = " ".join(filter(None, [
        " ".join(extracted.get("headlines", [])),
        " ".join(extracted.get("sub_headlines", [])),
        " ".join(extracted.get("arguments", [])),
        extracted.get("narrative_structure", ""),
    ]))

    spy_data = SpyData(
        copy_text=full_copy,
        offer_data={
            k: extracted[k]
            for k in ("price", "bonuses", "guarantees", "upsells", "downsells")
            if k in extracted
        },
        reviews=reviews,
        ads=ads,
    )

    # 3. Completeness gate
    gate_passed, confidence = check_completeness(spy_data, min_reviews=min_reviews)

    if not spy_data.copy_text or len(spy_data.copy_text) < 100:
        raise RuntimeError("Copy ausente ou insuficiente — não é possível gerar dossiê")

    # 4. LLM pipeline (always runs if copy is adequate)
    copy_analysis = await analyze_copy(spy_data)
    dossier_data = await generate_dossier(spy_data, copy_analysis, dossier_id, db_path)

    # Enrich dossier with analysis metadata
    dossier_data["copy_analysis"] = copy_analysis
    dossier_data["confidence_score"] = confidence
    dossier_data["incomplete"] = not gate_passed

    # 5. Persist dossier
    db["dossiers"].update(dossier_id, {
        "status": "done",
        "dossier_json": json.dumps(dossier_data, ensure_ascii=False),
        "ads_json": json.dumps(ads, ensure_ascii=False),
        "confidence_score": confidence,
        "incomplete": int(not gate_passed),
        "updated_at": datetime.utcnow().isoformat(),
    })
    log.info("spy.done", dossier_id=dossier_id, confidence=confidence, incomplete=not gate_passed)


def _upsert_dossier_status(
    db,
    product_id: int,
    status: str,
    dossier_id: Optional[int] = None,
) -> int:
    """Insert or update a dossier record with the given status.

    If dossier_id is provided, updates that record.
    Otherwise, finds existing by product_id or creates a new one.

    Returns:
        The dossier ID (int).
    """
    now = datetime.utcnow().isoformat()

    if dossier_id is not None:
        db["dossiers"].update(dossier_id, {"status": status, "updated_at": now})
        return dossier_id

    existing = list(db["dossiers"].rows_where("product_id = ?", [product_id]))
    if existing:
        existing_id = existing[0]["id"]
        db["dossiers"].update(existing_id, {"status": status, "updated_at": now})
        return existing_id

    # Create new dossier record (schema from _001: no created_at, uses generated_at)
    return db["dossiers"].insert({
        "product_id": product_id,
        "status": status,
        "analysis": "{}",
        "opportunity_score": 0.0,
        "confidence_score": 0.0,
        "generated_at": now,
    }).last_pk


def _platform_slug(platform_id: int) -> str:
    """Map platform_id to platform slug for ReviewsScraper."""
    return {1: "hotmart", 2: "clickbank", 3: "kiwify"}.get(platform_id, "unknown")
