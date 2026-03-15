"""CLI entrypoint for the MIS (Market Intelligence System).

Usage:
    python -m mis spy --url <URL>
    python -m mis spy --product-id <ID>
    python -m mis radar --niche <SLUG>
    python -m mis dashboard [--host HOST] [--port PORT]
    python -m mis export [--dest PATH]

Subcommands:
    spy        Spy on a product by URL or by its DB product-id.
    radar      Run a full pain radar cycle for a specific niche.
    dashboard  Start the web dashboard server.
    export     Export dossiers and pain reports to MEGABRAIN knowledge pipeline.
"""
import argparse
import asyncio
import sys


def main() -> None:
    """Parse CLI arguments and dispatch to the appropriate command."""
    parser = argparse.ArgumentParser(
        prog="mis",
        description="MIS — Market Intelligence System CLI",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ── spy subcommand ──────────────────────────────────────────────────────
    spy_parser = subparsers.add_parser(
        "spy",
        help="Spy on a product to generate a competitive intelligence dossier",
    )
    spy_group = spy_parser.add_mutually_exclusive_group(required=True)
    spy_group.add_argument(
        "--url",
        metavar="URL",
        help="URL of the product sales page to spy",
    )
    spy_group.add_argument(
        "--product-id",
        type=int,
        metavar="ID",
        help="DB product ID to spy (use force=True — always re-spies)",
    )

    # ── radar subcommand ────────────────────────────────────────────────────
    radar_parser = subparsers.add_parser(
        "radar",
        help="Run a full pain radar cycle for a specific niche",
    )
    radar_parser.add_argument(
        "--niche",
        required=True,
        metavar="SLUG",
        help="Niche slug as configured in config.yaml (e.g. 'emagrecimento')",
    )

    # ── dashboard subcommand ────────────────────────────────────────────────
    dashboard_parser = subparsers.add_parser(
        "dashboard",
        help="Start the web dashboard server",
    )
    dashboard_parser.add_argument(
        "--host",
        default="127.0.0.1",
        metavar="HOST",
        help="Bind host (default: 127.0.0.1)",
    )
    dashboard_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        metavar="PORT",
        help="Bind port (default: 8000)",
    )

    # ── export subcommand ────────────────────────────────────────────────────
    export_parser = subparsers.add_parser(
        "export",
        help="Export dossiers and pain reports to MEGABRAIN knowledge pipeline",
    )
    export_parser.add_argument(
        "--dest",
        default=None,
        metavar="PATH",
        help="Destination directory (default: MEGABRAIN_PATH/knowledge/mis/)",
    )

    # ── Parse and dispatch ──────────────────────────────────────────────────
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "spy":
        _handle_spy(args)
    elif args.command == "radar":
        _handle_radar(args)
    elif args.command == "dashboard":
        _handle_dashboard(args)
    elif args.command == "export":
        _handle_export(args)
    else:
        parser.print_help()
        sys.exit(1)


def _handle_spy(args) -> None:
    """Handle the spy subcommand."""
    from mis.spy_orchestrator import run_spy, run_spy_url

    if args.url:
        asyncio.run(run_spy_url(args.url))
    else:
        asyncio.run(run_spy(args.product_id, force=True))


def _handle_radar(args) -> None:
    """Handle the radar subcommand."""
    from mis.config import load_config
    from mis.db import run_migrations
    from mis.radar import run_radar_cycle
    import os

    config = load_config()
    db_path = os.environ.get("MIS_DB_PATH", "data/mis.db")
    run_migrations(db_path)

    result = asyncio.run(run_radar_cycle(args.niche, config, db_path))
    if result:
        import json
        print(f"\nRadar cycle completed for niche: {args.niche}")
        pains = result.get("pains", [])
        print(f"Top {len(pains)} pains identified:")
        for i, pain in enumerate(pains, 1):
            print(f"  {i}. [{pain.get('interest_level', '?')}] {pain.get('description', '')}")
        print(f"\nSources: {result.get('sources_used', {})}")
        print(f"Cost: ${result.get('cost_usd', 0):.4f}")
    else:
        print(f"No report generated for niche '{args.niche}' (no signals or niche not found)")
        sys.exit(1)


def _handle_dashboard(args) -> None:
    """Handle the dashboard subcommand."""
    import os

    import uvicorn

    from mis.web.app import create_app

    db_path = os.environ.get("MIS_DB_PATH", "data/mis.db")
    app = create_app(db_path=db_path)
    uvicorn.run(app, host=args.host, port=args.port)


def _handle_export(args) -> None:
    """Handle the export subcommand."""
    from mis.mis_agent import export_to_megabrain

    result = export_to_megabrain(dest=args.dest)
    if result["status"] == "ok":
        print(
            f"Exported: {result['exported']} dossiers/reports, "
            f"{result['skipped']} skipped to {result['dest']}"
        )
    else:
        print(f"Export failed: {result['message']}")
        print(f"Hint: {result.get('setup_hint', '')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
