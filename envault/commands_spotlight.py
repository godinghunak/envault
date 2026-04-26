"""CLI commands for the spotlight feature."""
from __future__ import annotations

import argparse
import getpass
import sys

from envault.env_spotlight import spotlight_key, spotlight_keys, format_spotlight


def cmd_spotlight(args: argparse.Namespace) -> None:
    """Highlight a key's history across all vault versions."""
    password = getpass.getpass("Vault password: ")
    keys = args.keys

    if not keys:
        print("Error: at least one key must be specified.", file=sys.stderr)
        sys.exit(1)

    results = spotlight_keys(args.vault_dir, keys, password)

    for key, result in results.items():
        print(format_spotlight(result))
        print()


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "spotlight",
        help="Track specific keys across all vault versions",
    )
    parser.add_argument(
        "keys",
        nargs="+",
        metavar="KEY",
        help="Key name(s) to spotlight",
    )
    parser.set_defaults(func=cmd_spotlight)
