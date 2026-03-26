"""Manual search orchestrator for v3.0.

Provides run_manual_search() that scans all platforms with a mapped slug
for a given subniche, persisting results to search_sessions +
search_session_products tables.

_TASK_REGISTRY holds asyncio.Task references for cancellation via
DELETE /search/{id}. Registry is in-memory only; server restart clears it.
The startup hook in web/app.py marks any 'running' session as 'timeout'.
"""
import asyncio

import structlog

from .db import get_db
from .search_repository import update_session_status
from .spy_orchestrator import run_spy_batch, get_top_products_for_spy, SPY_V3_TOP_N

_log = structlog.get_logger(__name__)
_TASK_REGISTRY: dict[int, asyncio.Task] = {}


def register_task(session_id: int, task: asyncio.Task) -> None:
    """Register an asyncio.Task for a session so it can be cancelled later.

    Args:
        session_id: The search_sessions.id this task corresponds to.
        task:       The asyncio.Task running run_manual_search().
    """
    _TASK_REGISTRY[session_id] = task


def cancel_task(session_id: int) -> bool:
    """Cancel a running search task by session id.

    Removes the task from the registry and calls task.cancel() if the
    task is still running.

    Args:
        session_id: The session whose task to cancel.

    Returns:
        True if a running task was found and cancelled; False otherwise
        (including when session_id was never registered or task already done).
    """
    task = _TASK_REGISTRY.pop(session_id, None)
    if task and not task.done():
        task.cancel()
        return True
    return False


async def run_manual_search(session_id: int, subniche_id: int, db_path: str) -> None:
    """Scan all platforms for a subniche and persist results.

    Lifecycle:
        1. Mark session as 'running'.
        2. Gather scan tasks from all platforms that have a slug for this subniche.
        3. Persist each product found via upsert_product + search_session_products.
        4. Mark session as 'done' (or 'timeout' / 'cancelled' on error).

    The asyncio.gather runs with a 120-second timeout. On TimeoutError, all
    sub-tasks are cancelled and the session is marked 'timeout'. On
    CancelledError (external cancellation via cancel_task()), the session is
    marked 'cancelled' and the error is re-raised so the asyncio runtime can
    clean up properly.

    PITFALL — niche_id legado:
        products.niche_id is a FK to the legacy 'niches' table (v1/v2 IDs 1-4).
        niches_v3 uses the same IDs 1-4 (verified in migration _008).
        subniches.niche_id is a FK to niches_v3(id) — same integer value as
        the legacy niches.id for niches 1-4. So we can use it directly.

    Args:
        session_id:  search_sessions.id to update throughout the run.
        subniche_id: subniches.id to scan (determines platform slugs).
        db_path:     Path to the SQLite database file.
    """
    # Lazy imports — avoid circular dependency with scanner.py
    from .scanners.kiwify import KiwifyScanner
    from .scanners.hotmart import HotmartScanner
    from .scanners.clickbank import ClickBankScanner
    from .scanners.eduzz import EduzzScanner
    from .scanners.monetizze import MonetizzeScanner
    from .scanners.perfectpay import PerfectPayScanner
    from .scanners.braip import BraipScanner
    from .scanners.product_hunt import ProductHuntScanner
    from .scanners.udemy import UdemyScanner
    from .scanners.jvzoo import JVZooScanner
    from .scanners.gumroad import GumroadScanner
    from .scanners.appsumo import AppSumoScanner
    from .niche_repository import get_platform_slug
    from .product_repository import upsert_product

    SCANNER_MAP = {
        "kiwify": KiwifyScanner,
        "hotmart": HotmartScanner,
        "clickbank": ClickBankScanner,
        "eduzz": EduzzScanner,
        "monetizze": MonetizzeScanner,
        "perfectpay": PerfectPayScanner,
        "braip": BraipScanner,
        "product_hunt": ProductHuntScanner,
        "udemy": UdemyScanner,
        "jvzoo": JVZooScanner,
        "gumroad": GumroadScanner,
        "appsumo": AppSumoScanner,
    }

    # Resolve niche_id from subniches table
    # subniches.niche_id -> niches_v3(id), which uses IDs 1-4 matching legacy niches
    db = get_db(db_path)
    row = db.execute(
        "SELECT niche_id FROM subniches WHERE id = ?", [subniche_id]
    ).fetchone()
    if row is None:
        _log.error(
            "run_manual_search.subniche_not_found",
            session_id=session_id,
            subniche_id=subniche_id,
        )
        update_session_status(db_path, session_id, "timeout", {}, 0)
        return

    niche_id_v3 = row[0]
    # Verify the same ID exists in the legacy niches table
    # niche_id: uses legacy niches table (same IDs 1-4 as niches_v3)
    legacy_row = db.execute(
        "SELECT id FROM niches WHERE id = ?", [niche_id_v3]
    ).fetchone()
    if legacy_row:
        niche_id = legacy_row[0]
    else:
        _log.warning(
            "run_manual_search.niche_id_mismatch",
            niche_id_v3=niche_id_v3,
            fallback=1,
        )
        niche_id = 1  # fallback

    # Build list of (platform_slug, scanner_class, search_slug)
    tasks_spec = []
    for platform_slug, scanner_class in SCANNER_MAP.items():
        search_slug = get_platform_slug(db_path, subniche_id, platform_slug)
        if search_slug is None:
            # Platform has no slug mapping for this subniche (e.g. eduzz, monetizze, perfectpay)
            continue
        tasks_spec.append((platform_slug, scanner_class, search_slug))

    # Mark session as running
    update_session_status(db_path, session_id, "running", {}, 0)

    platform_statuses: dict[str, str] = {}
    total_products = 0

    async def _scan_platform(platform_slug: str, scanner_class, search_slug: str):
        """Run a single platform scan and return (platform_slug, products)."""
        try:
            async with scanner_class() as scanner:
                products = await scanner.scan_niche(
                    niche_slug=str(subniche_id),
                    platform_slug=search_slug,
                )
            return platform_slug, products
        except Exception as exc:
            _log.error(
                "run_manual_search.platform_error",
                platform=platform_slug,
                error=str(exc),
            )
            return platform_slug, exc

    coros = [
        _scan_platform(ps, sc, ss) for ps, sc, ss in tasks_spec
    ]

    try:
        results = await asyncio.wait_for(
            asyncio.gather(*coros, return_exceptions=True),
            timeout=120.0,
        )
    except asyncio.TimeoutError:
        _log.warning(
            "run_manual_search.timeout",
            session_id=session_id,
            subniche_id=subniche_id,
        )
        update_session_status(
            db_path, session_id, "timeout", platform_statuses, total_products
        )
        return
    except asyncio.CancelledError:
        update_session_status(
            db_path, session_id, "cancelled", platform_statuses, total_products
        )
        raise

    # Persist products and build platform_statuses
    db2 = get_db(db_path)
    rank_counter: dict[str, int] = {}

    for result in results:
        if isinstance(result, BaseException):
            # gather(return_exceptions=True) — shouldn't happen since we
            # already handle inside _scan_platform, but guard anyway
            continue

        platform_slug, products = result
        if isinstance(products, BaseException):
            platform_statuses[platform_slug] = "error"
            continue

        platform_statuses[platform_slug] = "done"
        for product in products:
            # Set niche_id to the legacy niches.id before persisting
            product.niche_id = niche_id
            try:
                upsert_product(db2, product)
                # Fetch the inserted/updated products.id
                prod_row = db2.execute(
                    "SELECT id FROM products WHERE platform_id = ? AND external_id = ?",
                    [product.platform_id, product.external_id],
                ).fetchone()
                if prod_row:
                    rank_counter[platform_slug] = rank_counter.get(platform_slug, 0) + 1
                    rank_at_scan = product.rank
                    db2.execute(
                        """
                        INSERT OR IGNORE INTO search_session_products
                            (session_id, product_id, rank_at_scan, platform_slug)
                        VALUES (?, ?, ?, ?)
                        """,
                        [session_id, prod_row[0], rank_at_scan, platform_slug],
                    )
                    total_products += 1
            except Exception as exc:
                _log.error(
                    "run_manual_search.upsert_error",
                    platform=platform_slug,
                    external_id=product.external_id,
                    error=str(exc),
                )

    update_session_status(
        db_path, session_id, "done", platform_statuses, total_products
    )
    _log.info(
        "run_manual_search.complete",
        session_id=session_id,
        subniche_id=subniche_id,
        total_products=total_products,
    )

    # --- SPY WIRING (v3.0) ---
    # Transition to 'spying' and run spy batch on top products
    update_session_status(db_path, session_id, "spying", platform_statuses, total_products)
    products_to_spy = get_top_products_for_spy(db_path, session_id)
    _log.info(
        "run_manual_search.spy_start",
        session_id=session_id,
        products_to_spy=len(products_to_spy),
    )
    if products_to_spy:
        await run_spy_batch(products_to_spy, max_concurrent=SPY_V3_TOP_N)
    update_session_status(db_path, session_id, "spy_done", platform_statuses, total_products)
    _log.info("run_manual_search.spy_done", session_id=session_id)
