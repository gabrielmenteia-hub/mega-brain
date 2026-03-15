"""CLI entrypoint for the MIS (Market Intelligence System).

Usage:
    python -m mis spy --url <URL>
    python -m mis spy --product-id <ID>

Subcommands:
    spy   Spy on a product by URL or by its DB product-id.
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

    # ── Parse and dispatch ──────────────────────────────────────────────────
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "spy":
        _handle_spy(args)
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


if __name__ == "__main__":
    main()
